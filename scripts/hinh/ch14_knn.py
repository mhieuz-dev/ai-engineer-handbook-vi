"""Chương 14 KNN: tính lại các con số dùng trong bài và vẽ hình.

Chạy:  .venv/bin/python scripts/hinh/ch14_knn.py
Kết quả: các file SVG trong public/hinh/ch14/. Con số nào trong bài sai thì một câu assert báo lỗi.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
from matplotlib.colors import ListedColormap
from matplotlib.patches import Circle
from sklearn.datasets import make_moons
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

GOC = Path(__file__).resolve().parents[2]
OUT = GOC / "public" / "hinh" / "ch14"
OUT.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- 1. 10 bạn của Bảng 4.1 (giờ học, giờ ngủ đã điền), nhãn đạt khi điểm từ 5
TEN = list("ABCDEFGHIK")
X = np.array([[1, 7], [2, 6], [3, 8], [4, 7], [5, 6], [2, 7], [6, 8], [3, 5], [7, 7], [4, 6]], float)
y = (np.array([2, 4, 5, 7, 6, 3.5, 8.5, 4, 9, 6.5]) >= 5).astype(int)
q = np.array([3.4, 6.3])
d = np.sqrt(((X - q) ** 2).sum(axis=1))
thu_tu = np.argsort(d)
assert [TEN[i] for i in thu_tu[:5]] == ["K", "D", "H", "B", "F"]
assert [round(d[i], 4) for i in thu_tu[:5]] == [0.6708, 0.922, 1.3601, 1.4318, 1.5652]
assert [int(y[thu_tu[:k]].mean() > 0.5) for k in (1, 3, 5)] == [1, 1, 0]

# ---------------------------------------------------------------- 2. hai nửa vầng trăng
Xm, ym = make_moons(n_samples=300, noise=0.3, random_state=0)
a, b, c, e = train_test_split(Xm, ym, test_size=0.3, random_state=0)
diem = {k: (KNeighborsClassifier(k).fit(a, c).score(a, c), KNeighborsClassifier(k).fit(a, c).score(b, e)) for k in (1, 15, 100)}
assert [round(v, 4) for v in diem[1]] == [1.0, 0.8889] and [round(v, 4) for v in diem[15]] == [0.9429, 0.9222]

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
    "savefig.bbox": "tight", "svg.hashsalt": "ch14",
})


def luu(fig, ten):
    fig.savefig(OUT / ten, metadata={"Date": None})  # bỏ ngày giờ để file không đổi giữa các lần chạy
    plt.close(fig)


# Hình 14.1: bạn mới và các vòng 3, 5 láng giềng
fig, ax = plt.subplots(figsize=(6.2, 4.6))
for k, mau, goc in ((3, CAM, -2.4), (5, XAM, 0.8)):          # goc: hướng đặt nhãn (radian), để hai nhãn không đè nhau
    r = d[thu_tu[k - 1]] + 0.03
    ax.add_patch(Circle(q, r, fill=False, ls="--", lw=1.4, ec=mau))
    ax.text(q[0] + (r + 0.15) * np.cos(goc), q[1] + (r + 0.15) * np.sin(goc), f"k = {k}", color=mau, fontsize=11, ha="center", va="center")
ax.scatter(X[y == 1, 0], X[y == 1, 1], s=80, color=XANH, label="đạt", zorder=3)
ax.scatter(X[y == 0, 0], X[y == 0, 1], s=80, color=DO, marker="s", label="không đạt", zorder=3)
for t, (u, v) in zip(TEN, X):
    ax.annotate(t, (u, v), xytext=(7, 5), textcoords="offset points", fontsize=11)
ax.plot(*q, "*", ms=16, color=CHU, zorder=4)
ax.annotate("bạn mới", q, xytext=(-30, -20), textcoords="offset points", fontsize=11)
ax.set_aspect("equal")
ax.set_xlim(0, 8)
ax.set_ylim(4, 9)
ax.set_xlabel("Giờ tự học mỗi tuần")
ax.set_ylabel("Giờ ngủ mỗi đêm")
ax.legend(loc="lower right", fontsize=10.5, facecolor=NEN, edgecolor=LUOI, framealpha=1)
luu(fig, "h1_lang_gieng.svg")

# Hình 14.2: ranh giới quyết định với k = 1, 15, 100
nen = ListedColormap(["#F6DAD5", "#D6E4F0"])
xx, yy = np.meshgrid(np.linspace(-2, 3, 300), np.linspace(-1.6, 2.1, 300))
fig, truc = plt.subplots(1, 3, figsize=(11.4, 3.7), sharey=True)
for ax, k in zip(truc, (1, 15, 100)):
    m = KNeighborsClassifier(k).fit(a, c)
    zz = m.predict(np.c_[xx.ravel(), yy.ravel()]).reshape(xx.shape)
    ax.contourf(xx, yy, zz, levels=[-0.5, 0.5, 1.5], cmap=nen)
    ax.scatter(a[c == 1, 0], a[c == 1, 1], s=12, color=XANH)
    ax.scatter(a[c == 0, 0], a[c == 0, 1], s=12, color=DO)
    tr, te = diem[k]
    ax.set_title(f"k = {k}: train {tr:.0%}, test {te:.0%}", fontsize=12)
    ax.set_xlabel("đặc trưng 1")
    ax.grid(False)
truc[0].set_ylabel("đặc trưng 2")
luu(fig, "h2_ranh_gioi.svg")
print("Đã vẽ 2 hình vào", OUT)
