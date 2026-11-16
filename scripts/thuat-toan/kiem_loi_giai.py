"""Chạy lời giải mẫu của cả 40 bài với test ví dụ và test ẩn.

Chạy: .venv/bin/python scripts/thuat-toan/kiem_loi_giai.py
Mỗi bài chạy trong không gian tên riêng; yêu cầu in ra OK, không lỗi.
"""
from __future__ import annotations

import contextlib
import io
import sys
import time
import traceback
from pathlib import Path

import yaml

GOC = Path(__file__).resolve().parents[2]
THU_MUC = GOC / "src" / "data" / "thuat-toan"


def chay(ten: str, ma: str, g: dict, can_ok: bool = True) -> tuple[bool, str]:
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
    for tep in sorted(THU_MUC.glob("*.yaml")):
        d = yaml.safe_load(tep.read_text(encoding="utf-8"))
        g: dict = {}
        ok, tb = chay(f"{tep.name} lời giải", d["loi_giai"], g, can_ok=False)
        if not ok:
            print(tb)
            loi += 1
            continue
        for khoa in ("test_vi_du", "test_an"):
            tong += 1
            t0 = time.perf_counter()
            ok, tb = chay(f"{tep.name} {khoa}", d[khoa], g)
            dt = time.perf_counter() - t0
            if not ok:
                print(tb)
                loi += 1
            elif dt > 5:
                print(f"{tep.name} {khoa}: chậm {dt:.1f}s")
    print(f"xong {tong} bộ test, {loi} lỗi")
    return 1 if loi else 0


if __name__ == "__main__":
    sys.exit(main())
