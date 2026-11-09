"""Chương 38 Tổng quan NLP: tách từ tập train UIT-VSFC như trang 3 và 4, vẽ hình 38.1 (luật Zipf và tốc độ tăng từ vựng).

Chạy:  .venv/bin/python scripts/hinh/ch38_tong_quan_nlp.py      (khoảng 10 giây; dữ liệu đọc từ ~/.cache/vsfc, tải ở trang 1)
Kết quả: public/hinh/ch38/h1_zipf.svg. Con số nào trong bài sai thì một câu assert báo lỗi.
"""
import os
from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import font_manager
from underthesea import word_tokenize

GOC = Path(__file__).resolve().parents[2]
OUT = GOC / "public" / "hinh" / "ch38"
OUT.mkdir(parents=True, exist_ok=True)

tr = pd.read_parquet(os.path.expanduser("~/.cache/vsfc/train.parquet"))
tu_tr = [word_tokenize(c) for c in tr.sentence]
dem_tu = Counter(x for c in tu_tr for x in c)
f = np.array(sorted(dem_tu.values(), reverse=True))
hang = np.arange(1, len(f) + 1)
giua = (hang >= 10) & (hang <= 1000)
doc, chan = np.polyfit(np.log(hang[giua]), np.log(f[giua]), 1)
assert round(np.exp(chan)) > 100_000 > f[0] == 11009                      # đầu bảng nằm dưới đường khớp
assert len(dem_tu) == 4009 and round(doc, 3) == -1.387 and int((f == 1).sum()) == 1932
da_gap, n, diem = set(), 0, []
for c in tu_tr:
    for x in c:
        n += 1
        da_gap.add(x)
    diem.append((n, len(da_gap)))
assert diem[999] == (11075, 1236) and diem[-1] == (127413, 4009)

NEN = "#FBF8F1"
XANH, CAM, XAM, CHU, LUOI = "#1F5F8B", "#E07A1F", "#8A8170", "#2B2B2B", "#E6DECD"
co_sans = {f_.name for f_ in font_manager.fontManager.ttflist}
FONT = "Be Vietnam Pro" if "Be Vietnam Pro" in co_sans else "DejaVu Sans"
plt.rcParams.update({
    "font.family": FONT, "font.size": 12.5, "text.color": CHU, "axes.labelcolor": CHU,
    "xtick.color": CHU, "ytick.color": CHU, "axes.edgecolor": XAM,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": LUOI, "grid.alpha": 0.8, "axes.axisbelow": True,
    "figure.facecolor": NEN, "axes.facecolor": NEN, "savefig.facecolor": NEN,
    "savefig.bbox": "tight", "svg.hashsalt": "ch38",
})
fig, axs = plt.subplots(1, 2, figsize=(12, 4.8))
axs[0].loglog(hang, f, ".", color=XANH, ms=3, label="từng từ")
x = np.array([1, len(f)])
axs[0].loglog(x, np.exp(chan) * x ** doc, color=CAM, lw=2, label="đường khớp, độ dốc −1,39")
axs[0].set_xlabel("hạng của từ")
axs[0].set_ylabel("số lần xuất hiện")
axs[0].legend(loc="upper right", frameon=False)
nn_, vv = zip(*diem)
axs[1].plot(nn_, vv, color=XANH, lw=2)
axs[1].set_xticks([0, 40_000, 80_000, 120_000])
axs[1].set_xlabel("số token đã đọc")
axs[1].set_ylabel("số từ khác nhau")
axs[1].xaxis.set_major_formatter(lambda v, p: f"{int(v):,}".replace(",", " "))
axs[1].yaxis.set_major_formatter(lambda v, p: f"{int(v):,}".replace(",", " "))
fig.tight_layout()
fig.savefig(OUT / "h1_zipf.svg", metadata={"Date": None})
print("xong", sorted(p.name for p in OUT.iterdir()))
