"""Chạy mọi khối ```python trên các trang web của một chương và so với khối Output ngay sau nó.

Chạy:  .venv/bin/python -W ignore scripts/kiem_trang.py ch05 ch06 ...   (không đối số: mọi chương đã có thư mục)
Chạy trong một thư mục tạm vì code của bài có thể ghi file (lop.csv...).
Các trang của một chương chạy nối tiếp trong cùng một không gian biến, theo thứ tự tên file,
giống người đọc đi từ trang 1 tới trang cuối. Khối không có Output theo sau vẫn được chạy
(để tạo biến cho khối sau) nhưng lỗi của nó không tính. Khối bắt đầu bằng "!" (lệnh Colab)
và khối có title="Đề bài" (code để người đọc tự đoán, output nằm trong đáp án) bị bỏ qua.
"""
import contextlib
import io
import os
import re
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
GOC = Path(__file__).resolve().parents[1] / "src/content/docs/ai-engineer"
KHOI = re.compile(r"```(python|text)([^\n]*)\n(.*?)```", re.S)


def kiem_chuong(thu_muc: Path):
    g, ok, sai = {}, 0, []
    for trang in sorted(thu_muc.glob("*.mdx")):
        khoi = KHOI.findall(trang.read_text(encoding="utf-8"))
        for i, (loai, _, nguon) in enumerate(khoi):
            if loai != "python" or nguon.lstrip().startswith("!") or "Đề bài" in khoi[i][1]:
                continue
            ke = khoi[i + 1] if i + 1 < len(khoi) else None
            co_output = ke is not None and ke[0] == "text" and 'title="Output"' in ke[1]
            buf = io.StringIO()
            try:
                with contextlib.redirect_stdout(buf):
                    exec(nguon, g)
                ra = buf.getvalue().strip()
            except Exception as e:  # noqa: BLE001
                ra = buf.getvalue() + f"{type(e).__name__}: {e}"
                if not co_output:
                    continue
            if not co_output:
                continue
            mong = ke[2].strip()
            # khối Output chỉ ghi dòng lỗi cuối (NameError...): so dòng cuối
            if mong.splitlines()[-1].split(":")[0].endswith("Error") and len(mong.splitlines()) == 1:
                ra = ra.strip().splitlines()[-1] if ra.strip() else ra
            if ra.strip() == mong:
                ok += 1
            else:
                sai.append((trang.name, nguon.strip().splitlines()[0][:70], mong, ra.strip()))
    return ok, sai


def main():
    ten = sys.argv[1:] or sorted(p.name.split("-")[0] for p in GOC.iterdir() if p.is_dir())
    tong_sai = 0
    for t in ten:
        tm = next(GOC.glob(f"{t}-*"))
        ok, sai = kiem_chuong(tm)
        tong_sai += len(sai)
        print(f"{tm.name}: khớp {ok}, lệch {len(sai)}")
        for trang, dau, mong, ra in sai:
            print(f"  [{trang}] {dau}\n    mong đợi: {mong[:300]!r}\n    thực tế : {ra[:300]!r}")
    sys.exit(1 if tong_sai else 0)


if __name__ == "__main__":
    os.chdir(os.environ.get("THU_MUC_CHAY", "."))
    main()
