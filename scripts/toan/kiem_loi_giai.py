"""Chạy lời giải mẫu các bài Toán code và kiểm cấu trúc bài chứng minh.

Chạy: .venv/bin/python scripts/toan/kiem_loi_giai.py
"""
from __future__ import annotations

import contextlib
import glob
import io
import sys
import traceback
from pathlib import Path

import yaml

GOC = Path(__file__).resolve().parents[2]


def chay(ten: str, ma: str, g: dict, can_ok: bool) -> tuple[bool, str]:
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            exec(ma, g)
    except Exception:  # noqa: BLE001
        return False, f"{ten}:\n{traceback.format_exc()}"
    ra = buf.getvalue().strip()
    if can_ok and "OK" not in ra:
        return False, f"{ten}: không in OK (ra {ra!r})"
    return True, ""


def main() -> int:
    loi = 0
    tong = 0
    for tep in sorted(glob.glob(str(GOC / "src/data/toan/*.yaml"))):
        d = yaml.safe_load(open(tep, encoding="utf-8"))
        ten = Path(tep).name
        if d["loai"] == "code":
            g = {}
            ok, tb = chay(f"{ten} lời giải", d["loi_giai"], g, False)
            if not ok:
                print(tb); loi += 1; continue
            for khoa in ("test_vi_du", "test_an"):
                tong += 1
                ok, tb = chay(f"{ten} {khoa}", d[khoa], g, True)
                if not ok:
                    print(tb); loi += 1
        else:
            for k in ("loi_giai", "chung_minh"):
                if not str(d.get(k, "")).strip():
                    print(f"{ten}: thiếu {k}"); loi += 1
            if len(d.get("goi_y", [])) != 3:
                print(f"{ten}: không đủ 3 gợi ý"); loi += 1
            if d.get("rubric"):
                tong_r = sum(x["diem"] for x in d["rubric"])
                if abs(tong_r - 10) > 1e-9:
                    print(f"{ten}: rubric cộng {tong_r} != 10"); loi += 1
    print(f"xong {tong} bộ test code, {loi} lỗi")
    return 1 if loi else 0


if __name__ == "__main__":
    sys.exit(main())
