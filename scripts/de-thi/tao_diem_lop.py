"""Tạo public/du-lieu-thi/diem_lop.csv có bẫy Unicode và số.

Chạy: .venv/bin/python scripts/de-thi/tao_diem_lop.py
Bẫy: một tên viết NFD (trông giống hệt NFC), tên có khoảng trắng thừa,
một điểm dùng dấu phẩy thập phân, một ô trống, một ô chữ "chưa thi".
Dữ liệu bịa, không có thông tin cá nhân thật.
"""
from __future__ import annotations

import csv
import hashlib
import unicodedata
from pathlib import Path

GOC = Path(__file__).resolve().parents[2]
RA = GOC / "public" / "du-lieu-thi" / "diem_lop.csv"

HANG = [
    ("An", "8.5"),
    ("Bình", "7,5"),
    ("Chi", "9"),
    ("Dũng", ""),
    ("Giang", "chưa thi"),
    ("Hà", "6.5"),
    ("Hùng", "7"),
    ("Lan", "8"),
    ("Minh", "9.5"),
    ("Nga", "7.5"),
    ("Phúc", "6"),
    ("Quỳnh", "8"),
    ("  An ", "8.5"),  # trùng sau khi strip
    ("Nguyễn Văn An", "8.5"),
    (unicodedata.normalize("NFD", "Nguyễn Văn An"), "8.5"),  # trùng sau khi NFC
]


def main() -> None:
    RA.parent.mkdir(parents=True, exist_ok=True)
    with RA.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["ho_ten", "diem", "mon"])
        for ten, diem in HANG:
            w.writerow([ten, diem, "Toán"])

    # Thống kê sau khi chuẩn hóa để ghi vào đề
    def chuan(s: str) -> str:
        return unicodedata.normalize("NFC", s).strip()

    def so(s: str) -> float | None:
        s = s.strip().replace(",", ".")
        try:
            return float(s)
        except ValueError:
            return None

    ten = [chuan(r[0]) for r in HANG]
    duy_nhat = sorted(set(ten))
    diem = [so(r[1]) for r in HANG]
    hop_le = [x for x in diem if x is not None]
    print("so dong", len(HANG), "ten duy nhat sau chuan hoa", len(duy_nhat))
    print("so dong thieu/khong phai so", sum(1 for x in diem if x is None))
    print("diem trung binh tren dong hop le", round(sum(hop_le) / len(hop_le), 3))
    print("sha256", hashlib.sha256(RA.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
