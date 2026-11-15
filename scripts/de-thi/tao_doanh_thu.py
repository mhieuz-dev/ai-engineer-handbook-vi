"""Tạo public/du-lieu-thi/doanh_thu_2026.csv có bẫy, tất định.

Chạy: .venv/bin/python scripts/de-thi/tao_doanh_thu.py
Bẫy: ngày trộn 3 định dạng, số tiền có dấu phẩy thập phân, 6 ô trống,
3 dòng trùng, 2 khoản hoàn tiền âm, 1 đơn sỉ rất lớn (ngoại lai).
Không có thông tin cá nhân thật: mã đơn và kênh đều bịa.
"""
from __future__ import annotations

import csv
import hashlib
import random
from datetime import date, timedelta
from pathlib import Path

GOC = Path(__file__).resolve().parents[2]
RA = GOC / "public" / "du-lieu-thi" / "doanh_thu_2026.csv"
THANG = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]


def ngay(d: date) -> str:
    """Ba định dạng ngày khác nhau, chia đều theo chỉ số dòng."""
    return (d.isoformat(), d.strftime("%d/%m/%Y"), f"{d.day}-{THANG[d.month - 1]}-{d.year}")


def tien(x: float, kieu: int) -> str:
    if kieu == 0:
        return f"{x:.2f}"
    return f"{x:.2f}".replace(".", ",")


def main() -> None:
    rng = random.Random(20261115)
    kenh = ["web", "ung_dung", "cua_hang", "doi_tac"]
    dong: list[list[str]] = []
    dau = date(2026, 1, 1)
    for i in range(120):
        d = dau + timedelta(days=i // 2)
        so = round(rng.uniform(80_000, 2_500_000), 2)
        k = rng.randrange(4)
        dong.append([f"DH{1000 + i}", ngay(d)[i % 3], tien(so, i % 2), kenh[k], ""])

    # 6 ô trống có chủ đích
    for i in (7, 23, 48, 61, 88, 109):
        dong[i][2] = ""
    # 2 khoản hoàn tiền âm
    dong[15][2] = tien(-320_000, 1)
    dong[77][2] = tien(-145_500, 0)
    dong[15][4] = "hoan_tien"
    dong[77][4] = "hoan_tien"
    # 1 đơn sỉ rất lớn (ngoại lai)
    dong[42][2] = tien(99_999_999, 0)
    dong[42][4] = "don_si"
    # 3 dòng trùng y nguyên
    for i in (10, 55, 100):
        dong.append(list(dong[i]))

    RA.parent.mkdir(parents=True, exist_ok=True)
    with RA.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["ma_don", "ngay", "so_tien", "kenh", "ghi_chu"])
        w.writerows(dong)

    # Thống kê sau khi làm sạch để ghi vào đề
    def so_tien(s: str) -> float | None:
        s = s.strip()
        if not s:
            return None
        if "," in s and "." in s:
            s = s.replace(".", "").replace(",", ".")
        elif "," in s:
            s = s.replace(",", ".")
        return float(s)

    def ngay_iso(s: str) -> date:
        for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
            try:
                from datetime import datetime

                return datetime.strptime(s, fmt).date()
            except ValueError:
                pass
        from datetime import datetime

        return datetime.strptime(s, "%d-%b-%Y").date()

    sach = {}
    for r in dong:
        t = so_tien(r[2])
        if t is None:
            continue
        khoa = (r[0], ngay_iso(r[1]).isoformat(), f"{t:.2f}", r[3], r[4])
        sach[khoa] = t
    tong = sum(sach.values())
    print("tong dong", len(dong), "sau khi bo trong + trung", len(sach))
    print("so dong trung", len(dong) - sum(1 for r in dong if not r[2].strip()) - len(sach))
    print("tong tien", round(tong, 2))
    print("theo kenh", {k: round(sum(v for kk, v in sach.items() if kk[3] == k), 2) for k in kenh})
    print("so dong trong so_tien", sum(1 for r in dong if not r[2].strip()))
    ma = hashlib.sha256(RA.read_bytes()).hexdigest()
    print("sha256", ma)


if __name__ == "__main__":
    main()
