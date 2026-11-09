"""Chương 45 Tokenization: vẽ hình 45.1 (số token trên mỗi âm tiết của UIT-VSFC val theo số lần gộp BPE), đúng hoc_bpe, ma_hoa của trang 2.

Chạy:  .venv/bin/python scripts/hinh/ch45_bpe.py      (khoảng 15 giây, cần ~/.cache/vsfc từ chương 38)
Kết quả: public/hinh/ch45/h1_bpe.svg. Con số nào trong bài sai thì một câu assert báo lỗi.
"""
import os
from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import font_manager

GOC = Path(__file__).resolve().parents[2]
OUT = GOC / "public" / "hinh" / "ch45"
OUT.mkdir(parents=True, exist_ok=True)

tai = lambda p: pd.read_parquet(os.path.expanduser(f"~/.cache/vsfc/{p}.parquet"))
tr, va = tai("train"), tai("validation")
dem = Counter(w for s in tr.sentence for w in s.split())


def gop(t, a, b):
    ra, i = [], 0
    while i < len(t):
        if i < len(t) - 1 and t[i] == a and t[i + 1] == b:
            ra.append(a + b)
            i += 2
        else:
            ra.append(t[i])
            i += 1
    return tuple(ra)


def hoc_bpe(dem, so_lan):
    tach = {w: tuple(w) + ("_",) for w in dem}
    quy_tac = []
    for _ in range(so_lan):
        cap = Counter()
        for w, n in dem.items():
            t = tach[w]
            for a, b in zip(t, t[1:]):
                cap[a, b] += n
        if not cap:
            break
        (a, b), n = cap.most_common(1)[0]
        quy_tac.append((a, b))
        tach = {w: gop(t, a, b) for w, t in tach.items()}
    return quy_tac


def ma_hoa(w, quy_tac):
    t = tuple(w) + ("_",)
    for a, b in quy_tac:
        if a in t:
            t = gop(t, a, b)
    return t


quy_tac = hoc_bpe(dem, 3000)
am_va = [w for s in va.sentence for w in s.split()]
dem_va = Counter(am_va)
K = [0, 25, 50, 100, 200, 300, 500, 750, 1000, 1500, 2000, 2500, 3000]
y = [sum(n * len(ma_hoa(w, quy_tac[:k])) for w, n in dem_va.items()) / len(am_va) for k in K]
moc = dict(zip(K, (round(v, 3) for v in y)))
assert [moc[k] for k in (0, 100, 500, 1000, 2000, 3000)] == [4.196, 1.96, 1.207, 1.056, 1.013, 1.01], moc

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
    "savefig.bbox": "tight", "svg.hashsalt": "ch45",
})
fig, ax = plt.subplots(figsize=(9, 4.6))
ax.plot(K, y, color=XANH, lw=2.6, marker="o", ms=5)
ax.axhline(1, color=CAM, lw=1.6, ls="--")
ax.text(3000, 1.08, "1 token cho mỗi âm tiết", color=CAM, ha="right", va="bottom")
for k in (0, 100, 500, 1000):
    ax.annotate(f"{moc[k]:.2f}".replace(".", ","), (k, moc[k]), xytext=(8, 6), textcoords="offset points")
ax.set_xlabel("số lần gộp BPE")
ax.set_ylabel("token trên mỗi âm tiết (val)")
ax.set_ylim(0, 4.6)
fig.tight_layout()
fig.savefig(OUT / "h1_bpe.svg", metadata={"Date": None})
print("xong", moc)
