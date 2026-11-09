"""Chương 42 Gán nhãn chuỗi: chạy code của trang 1 tới 3 (đọc thẳng từ trang), vẽ hình 42.1.

Chạy:  .venv/bin/python scripts/hinh/ch42_gan_nhan.py      (vài giây; dữ liệu ở ~/.cache/ud_vi)
Kết quả: public/hinh/ch42/h1_da_gap_chua_gap.svg. Con số nào trong bài sai thì một câu assert báo lỗi.
"""
import contextlib
import io
import os
import re
import tempfile
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager

GOC = Path(__file__).resolve().parents[2]
OUT = GOC / "public" / "hinh" / "ch42"
OUT.mkdir(parents=True, exist_ok=True)
TRANG = GOC / "src/content/docs/ai-engineer/ch42-gan-nhan-chuoi"
g = {}
os.chdir(tempfile.mkdtemp())                         # trang 3 ghi tệp mô hình CRF ra thư mục hiện tại
for ten in ("01-gan-nhan-chuoi.mdx", "02-hmm-va-viterbi.mdx", "03-crf.mdx"):
    for khoi in re.findall(r"```python\n(.*?)```", (TRANG / ten).read_text(encoding="utf-8"), re.S):
        if not khoi.startswith("!"):
            with contextlib.redirect_stdout(io.StringIO()):
                exec(khoi, g)


def tach_do(gan):                                    # độ chính xác trên từ đã gặp và từ chưa gặp của dev
    d = {True: [0, 0], False: [0, 0]}
    for c in g["dv"]:
        for (w, t), q in zip(c, gan(c)):
            k = w.lower() in g["nhan_cua"]
            d[k][0] += t == q
            d[k][1] += 1
    return d[True][0] / d[True][1], d[False][0] / d[False][1]


mo_hinh = {"baseline": g["baseline"], "HMM": lambda c: g["viterbi"](c, g["phat_hapax"]), "CRF": g["crf"]}
kq = {k: tach_do(f) for k, f in mo_hinh.items()}
assert [round(v[1], 4) for v in kq.values()] == [0.43, 0.4026, 0.6267], kq
print({k: (round(a, 4), round(b, 4)) for k, (a, b) in kq.items()})

NEN = "#FBF8F1"
XANH, CAM, XAM, CHU, LUOI = "#1F5F8B", "#E07A1F", "#8A8170", "#2B2B2B", "#E6DECD"
co_sans = {f.name for f in font_manager.fontManager.ttflist}
FONT = "Be Vietnam Pro" if "Be Vietnam Pro" in co_sans else "DejaVu Sans"
plt.rcParams.update({"font.family": FONT, "font.size": 12.5, "text.color": CHU, "axes.labelcolor": CHU,
                     "xtick.color": CHU, "ytick.color": CHU, "axes.edgecolor": XAM,
                     "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": LUOI,
                     "axes.axisbelow": True, "figure.facecolor": NEN, "axes.facecolor": NEN,
                     "savefig.facecolor": NEN, "savefig.bbox": "tight", "svg.hashsalt": "ch42"})
fig, ax = plt.subplots(figsize=(8.5, 4.8))
x = np.arange(3)
for k, (nhom, mau) in enumerate((("từ đã gặp trong train", XANH), ("từ chưa gặp", CAM))):
    v = [kq[m][k] * 100 for m in mo_hinh]
    cot = ax.bar(x + (k - 0.5) * 0.36, v, 0.36, color=mau, label=nhom)
    for xx, vv in zip(x + (k - 0.5) * 0.36, v):
        ax.text(xx, vv + 1, f"{vv:.1f}".replace(".", ","), ha="center", va="bottom", fontsize=11.5)
ax.set_xticks(x, list(mo_hinh))
ax.set_ylabel("độ chính xác trên dev (%)")
ax.set_ylim(0, 118)
ax.legend(loc="upper center", frameon=False, ncol=2)
fig.tight_layout()
fig.savefig(OUT / "h1_da_gap_chua_gap.svg", metadata={"Date": None})
print("xong", sorted(p.name for p in OUT.iterdir()))
