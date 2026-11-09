"""Chương 43 Seq2Seq và attention: chạy code của trang 1 tới 4 (đọc thẳng từ trang, bỏ phần huấn luyện mô hình không attention),
vẽ hình 43.1 (ma trận attention của hai câu val đầu tiên).

Chạy:  .venv/bin/python scripts/hinh/ch43_attention.py      (khoảng 5 phút trên 4 luồng CPU; dữ liệu ở ~/.cache/iwslt15)
Kết quả: public/hinh/ch43/h1_attention.svg. Con số nào trong bài sai thì một câu assert báo lỗi.
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
OUT = GOC / "public" / "hinh" / "ch43"
OUT.mkdir(parents=True, exist_ok=True)
TRANG = GOC / "src/content/docs/ai-engineer/ch43-seq2seq-attention"
g = {}
for ten in ("01-dich-may-va-du-lieu.mdx", "02-encoder-decoder.mdx", "03-bleu-va-huan-luyen.mdx", "04-attention.mdx"):
    for khoi in re.findall(r"```python\n(.*?)```", (TRANG / ten).read_text(encoding="utf-8"), re.S):
        if khoi.startswith("!") or "ung_vien" in khoi:
            continue
        khoi = khoi.replace("mh_tron, gm_tron = huan_luyen(chu_y=False)", "pass")   # không cần mô hình không attention
        with contextlib.redirect_stdout(io.StringIO()):
            exec(khoi, g)
mh, gm, C_va = g["mh_cy"], g["gm_cy"], g["C_va"]
assert g["bleu"]([v for _, v in C_va], g["dich"](mh, gm, C_va)) == 12.81
khoi_luong = [A[:, -1].mean() for A in (g["dich_kem_attention"](mh, gm, e)[1] for e, _ in C_va[:300]) if len(A)]
assert round(float(np.mean(khoi_luong)), 3) == 0.692, np.mean(khoi_luong)

NEN = "#FBF8F1"
CHU = "#2B2B2B"
co_sans = {f.name for f in font_manager.fontManager.ttflist}
FONT = "Be Vietnam Pro" if "Be Vietnam Pro" in co_sans else "DejaVu Sans"
plt.rcParams.update({"font.family": FONT, "font.size": 12, "text.color": CHU, "axes.labelcolor": CHU,
                     "xtick.color": CHU, "ytick.color": CHU, "figure.facecolor": NEN, "axes.facecolor": NEN,
                     "savefig.facecolor": NEN, "savefig.bbox": "tight", "svg.hashsalt": "ch43"})
fig, axs = plt.subplots(1, 2, figsize=(13, 5.6))
for ax, (e, _) in zip(axs, C_va[:2]):
    tu, A = g["dich_kem_attention"](mh, gm, e)
    ax.imshow(A, cmap="Blues", vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(range(len(e)), e, rotation=45, ha="right")
    ax.set_yticks(range(len(tu)), tu)
    ax.set_xlabel("câu nguồn (tiếng Anh)")
    ax.set_ylabel("bản dịch của mô hình")
    for sp in ax.spines.values():
        sp.set_visible(False)
    print(" ".join(e), "|", " ".join(tu))
fig.tight_layout()
fig.savefig(OUT / "h1_attention.svg", metadata={"Date": None})
print("xong", sorted(p.name for p in OUT.iterdir()))
