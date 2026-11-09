"""Chương 41 Phân loại văn bản: chạy code của trang 1 tới 3 (đọc thẳng từ trang), vẽ hình 41.1 (ma trận nhầm lẫn của hai SVM).

Chạy:  .venv/bin/python scripts/hinh/ch41_phan_loai.py      (khoảng 40 giây; dữ liệu ở ~/.cache/vsfc)
Kết quả: public/hinh/ch41/h1_nham_lan.svg. Con số nào trong bài sai thì một câu assert báo lỗi.
"""
import contextlib
import io
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager

GOC = Path(__file__).resolve().parents[2]
OUT = GOC / "public" / "hinh" / "ch41"
OUT.mkdir(parents=True, exist_ok=True)
TRANG = GOC / "src/content/docs/ai-engineer/ch41-phan-loai-van-ban"
g = {}
for ten in ("01-bai-toan-va-baseline.mdx", "02-am-tiet-tu-va-n-gram.mdx", "03-doc-loi-va-lop-hiem.mdx"):
    for khoi in re.findall(r"```python\n(.*?)```", (TRANG / ten).read_text(encoding="utf-8"), re.S):
        if not khoi.startswith("!"):
            with contextlib.redirect_stdout(io.StringIO()):
                exec(khoi, g)
cm = g["confusion_matrix"]
M1, M2 = cm(g["y_va"], g["p_svm"]), cm(g["y_va"], g["p_cb"])
assert M1.tolist() == [[667, 2, 36], [27, 24, 22], [37, 4, 764]], M1
assert M2.tolist() == [[663, 8, 34], [22, 34, 17], [36, 12, 757]], M2

NEN = "#FBF8F1"
CHU, XAM = "#2B2B2B", "#8A8170"
co_sans = {f.name for f in font_manager.fontManager.ttflist}
FONT = "Be Vietnam Pro" if "Be Vietnam Pro" in co_sans else "DejaVu Sans"
plt.rcParams.update({"font.family": FONT, "font.size": 12.5, "text.color": CHU, "axes.labelcolor": CHU,
                     "xtick.color": CHU, "ytick.color": CHU, "figure.facecolor": NEN, "axes.facecolor": NEN,
                     "savefig.facecolor": NEN, "savefig.bbox": "tight", "svg.hashsalt": "ch41"})
TEN = ["tiêu cực", "trung tính", "tích cực"]
fig, axs = plt.subplots(1, 2, figsize=(12, 5))
for ax, M, tieu_de in ((axs[0], M1, "SVM"), (axs[1], M2, "SVM, trọng số lớp cân bằng")):
    ty_le = M / M.sum(1, keepdims=True)                  # tô màu theo tỷ lệ trong hàng để lớp hiếm cũng thấy rõ
    ax.imshow(ty_le, cmap="Blues", vmin=0, vmax=1)
    for i in range(3):
        for j in range(3):
            ax.text(j, i, str(M[i, j]), ha="center", va="center", fontsize=14, color="#FFFFFF" if ty_le[i, j] > 0.6 else CHU)
    ax.set_xticks(range(3), TEN)
    ax.set_yticks(range(3), TEN)
    ax.set_xlabel("nhãn đoán")
    ax.set_ylabel("nhãn thật")
    ax.set_title(tieu_de, fontsize=12.5)
    for sp in ax.spines.values():
        sp.set_visible(False)
fig.tight_layout()
fig.savefig(OUT / "h1_nham_lan.svg", metadata={"Date": None})
print("xong", sorted(p.name for p in OUT.iterdir()))
