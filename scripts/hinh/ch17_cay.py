"""Chương 17 Cây quyết định: tính lại các con số dùng trong bài và vẽ hình.

Chạy:  .venv/bin/python scripts/hinh/ch17_cay.py
Kết quả: các file SVG trong public/hinh/ch17/. Con số nào trong bài sai thì một câu assert báo lỗi.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
from matplotlib.colors import ListedColormap
from matplotlib.patches import FancyBboxPatch
from sklearn.datasets import make_moons
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

GOC = Path(__file__).resolve().parents[2]
OUT = GOC / "public" / "hinh" / "ch17"
OUT.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- 1. 10 bạn: (giờ học, giờ ngủ), đạt khi điểm từ 5
X = np.array([[1, 7], [2, 6], [3, 8], [4, 7], [5, 6], [2, 7], [6, 8], [3, 5], [7, 7], [4, 6]], float)
y = (np.array([2, 4, 5, 7, 6, 3.5, 8.5, 4, 9, 6.5]) >= 5).astype(int)
cay = DecisionTreeClassifier(random_state=0).fit(X, y)
t = cay.tree_
assert t.feature[0] == 0 and t.threshold[0] == 3.5 and cay.get_depth() == 2 and cay.get_n_leaves() == 3
assert np.isclose(t.impurity[0], 0.48) and np.isclose(t.impurity[1], 0.32)

# ---------------------------------------------------------------- 2. hai vầng trăng
Xm, ym = make_moons(300, noise=0.3, random_state=0)
a, b, c, e = train_test_split(Xm, ym, test_size=0.3, random_state=0)
moon = {d: DecisionTreeClassifier(max_depth=d, random_state=0).fit(a, c) for d in (1, 3, None)}
assert round(moon[None].score(b, e), 4) == 0.8444 and moon[None].score(a, c) == 1.0

# ---------------------------------------------------------------- vẽ hình (bảng màu Chương 10)
NEN = "#FBF8F1"
XANH, CAM, DO, XAM, CHU, LUOI = "#1F5F8B", "#E07A1F", "#C0392B", "#8A8170", "#2B2B2B", "#E6DECD"
co_sans = {f.name for f in font_manager.fontManager.ttflist}
FONT = "Be Vietnam Pro" if "Be Vietnam Pro" in co_sans else "DejaVu Sans"
plt.rcParams.update({
    "font.family": FONT, "font.size": 12.5, "mathtext.fontset": "dejavusans",
    "text.color": CHU, "axes.labelcolor": CHU, "xtick.color": CHU, "ytick.color": CHU,
    "axes.edgecolor": XAM, "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": LUOI, "grid.alpha": 0.8, "axes.axisbelow": True,
    "figure.facecolor": NEN, "axes.facecolor": NEN, "savefig.facecolor": NEN,
    "savefig.bbox": "tight", "svg.hashsalt": "ch17",
})


def luu(fig, ten):
    fig.savefig(OUT / ten, metadata={"Date": None})  # bỏ ngày giờ để file không đổi giữa các lần chạy
    plt.close(fig)


def hop(ax, x, y_, chu, mau):
    ax.add_patch(FancyBboxPatch((x - 1.7, y_ - 0.6), 3.4, 1.2, boxstyle="round,pad=0.04,rounding_size=0.12", fc=mau, ec=XAM, lw=1.2))
    ax.text(x, y_, chu, ha="center", va="center", fontsize=11, linespacing=1.45)


# Hình 17.1: sơ đồ cây của 10 bạn (vẽ tay theo đúng cây scikit-learn đã học)
fig, ax = plt.subplots(figsize=(8.4, 4.4))
ax.set_xlim(-0.6, 10.6)
ax.set_ylim(0.1, 5.8)
ax.axis("off")
hop(ax, 5, 5, "giờ học ≤ 3,5 ?\n10 bạn: 6 đạt, 4 không\nGini 0,48", "#F1ECE2")
hop(ax, 2.4, 3, "giờ ngủ ≤ 7,5 ?\n5 bạn: 1 đạt, 4 không\nGini 0,32", "#F1ECE2")
hop(ax, 7.9, 3, "ĐẠT\n5 bạn: D E G I K\nGini 0", "#D6E4F0")
hop(ax, 1.6, 0.9, "KHÔNG ĐẠT\n4 bạn: A B F H\nGini 0", "#F6DAD5")
hop(ax, 5.6, 0.9, "ĐẠT\n1 bạn: C\nGini 0", "#D6E4F0")
for (x0, y0, x1, y1, nhan) in ((5, 4.4, 2.4, 3.6, "đúng"), (5, 4.4, 7.9, 3.6, "sai"), (2.4, 2.4, 1.6, 1.5, "đúng"), (2.4, 2.4, 5.6, 1.5, "sai")):
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0), arrowprops=dict(arrowstyle="-|>", color=XAM, lw=1.3))
    ax.text((x0 + x1) / 2 + (0.25 if x1 > x0 else -0.25), (y0 + y1) / 2, nhan, fontsize=10.5, color=XAM, ha="center")
luu(fig, "h1_so_do_cay.svg")

# Hình 17.2: ranh giới của cây trên hai vầng trăng
nen = ListedColormap(["#F6DAD5", "#D6E4F0"])
xx, yy = np.meshgrid(np.linspace(-2, 3, 400), np.linspace(-1.6, 2.1, 400))
fig, truc = plt.subplots(1, 3, figsize=(11.4, 3.7), sharey=True)
for ax, d in zip(truc, (1, 3, None)):
    m = moon[d]
    zz = m.predict(np.c_[xx.ravel(), yy.ravel()]).reshape(xx.shape)
    ax.contourf(xx, yy, zz, levels=[-0.5, 0.5, 1.5], cmap=nen)
    ax.scatter(a[c == 1, 0], a[c == 1, 1], s=12, color=XANH)
    ax.scatter(a[c == 0, 0], a[c == 0, 1], s=12, color=DO)
    ten = "không giới hạn" if d is None else f"độ sâu {d}"
    ax.set_title(f"{ten}: train {m.score(a, c):.0%}, test {m.score(b, e):.0%}", fontsize=12)
    ax.set_xlabel("đặc trưng 1")
    ax.grid(False)
truc[0].set_ylabel("đặc trưng 2")
luu(fig, "h2_ranh_gioi_cay.svg")
print("Đã vẽ 2 hình vào", OUT)
