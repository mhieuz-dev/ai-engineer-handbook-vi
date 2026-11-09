"""Chương 39 BoW, TF-IDF và n-gram: đếm unigram, bigram, trigram trên tập train UIT-VSFC như trang 3, vẽ hình 39.1 (perplexity trên val theo k).

Chạy:  .venv/bin/python scripts/hinh/ch39_ngram.py      (khoảng 15 giây; dữ liệu ở ~/.cache/vsfc, tải ở Chương 38)
Kết quả: public/hinh/ch39/h1_perplexity.svg. Con số nào trong bài sai thì một câu assert báo lỗi.
"""
import math
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
OUT = GOC / "public" / "hinh" / "ch39"
OUT.mkdir(parents=True, exist_ok=True)
doc = lambda p: pd.read_parquet(os.path.expanduser(f"~/.cache/vsfc/{p}.parquet"))
noi = lambda ds: [" ".join(w.replace(" ", "_") for w in word_tokenize(c)) for c in ds]
S_tr, S_va = noi(doc("train").sentence), noi(doc("validation").sentence)


def them_dau(s, n):
    return ["<s>"] * (n - 1) + s.split() + ["</s>"]


def dem(ds, n):
    c, h = Counter(), Counter()
    for s in ds:
        t = them_dau(s, n)
        for i in range(n - 1, len(t)):
            g = tuple(t[i - n + 1:i + 1])
            c[g] += 1
            h[g[:-1]] += 1
    return c, h


mo_hinh = {n: dem(S_tr, n) for n in (1, 2, 3)}
V = len(mo_hinh[1][0])


def perplexity(ds, n, k):
    c, h = mo_hinh[n]
    L, N = 0.0, 0
    for s in ds:
        t = them_dau(s, n)
        for i in range(n - 1, len(t)):
            g = tuple(t[i - n + 1:i + 1])
            L += math.log((c[g] + k) / (h[g[:-1]] + k * V))
        N += len(s.split()) + 1
    return math.exp(-L / N)


ks = np.logspace(-4, 0, 17)
pp = {n: [perplexity(S_va, n, k) for k in ks] for n in (1, 2, 3)}
assert round(perplexity(S_va, 2, 0.01), 2) == 70.61 and round(perplexity(S_va, 3, 0.001), 2) == 197.03
assert round(perplexity(S_va, 1, 1), 2) == 218.18 and round(perplexity(S_va, 3, 1), 2) == 896.02
assert round(min(pp[3]), 2) == 189.43 and round(ks[int(np.argmin(pp[2]))], 4) == 0.01
print({n: round(min(v), 2) for n, v in pp.items()})

NEN = "#FBF8F1"
XANH, CAM, XAM, CHU, LUOI = "#1F5F8B", "#E07A1F", "#8A8170", "#2B2B2B", "#E6DECD"
co_sans = {f.name for f in font_manager.fontManager.ttflist}
FONT = "Be Vietnam Pro" if "Be Vietnam Pro" in co_sans else "DejaVu Sans"
plt.rcParams.update({
    "font.family": FONT, "font.size": 12.5, "text.color": CHU, "axes.labelcolor": CHU,
    "xtick.color": CHU, "ytick.color": CHU, "axes.edgecolor": XAM,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": LUOI, "grid.alpha": 0.8, "axes.axisbelow": True,
    "figure.facecolor": NEN, "axes.facecolor": NEN, "savefig.facecolor": NEN,
    "savefig.bbox": "tight", "svg.hashsalt": "ch39",
})
fig, ax = plt.subplots(figsize=(9, 5))
for n, ten, mau in ((1, "unigram", XAM), (2, "bigram", XANH), (3, "trigram", CAM)):
    ax.plot(ks, pp[n], color=mau, lw=2.4, marker="o", ms=4, label=ten)
ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xlabel("hệ số làm trơn k")
ax.set_ylabel("perplexity trên val")
ax.xaxis.set_major_formatter(lambda v, p: f"{v:g}".replace(".", ","))
ax.yaxis.set_major_formatter(lambda v, p: f"{v:g}")
ax.legend(loc="upper center", frameon=False, ncol=3)
fig.tight_layout()
fig.savefig(OUT / "h1_perplexity.svg", metadata={"Date": None})
print("xong", sorted(p.name for p in OUT.iterdir()))
