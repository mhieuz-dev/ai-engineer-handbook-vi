"""Chương 23 Nơ-ron và mạng nhiều lớp: tính lại các con số dùng trong bài và vẽ hình.

Chạy:  .venv/bin/python scripts/hinh/ch23_no_ron.py
Kết quả: các file SVG trong public/hinh/ch23/. Con số nào trong bài sai thì một câu assert báo lỗi.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
from matplotlib.colors import ListedColormap
from matplotlib.ticker import FuncFormatter
from sklearn.datasets import make_moons
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier

GOC = Path(__file__).resolve().parents[2]
OUT = GOC / "public" / "hinh" / "ch23"
OUT.mkdir(parents=True, exist_ok=True)

relu = lambda z: np.maximum(0, z)
sig = lambda z: 1 / (1 + np.exp(-z))

# ---------------------------------------------------------------- 1. XOR bằng tay
X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]], float)
W1, b1 = np.array([[1, 1], [1, 1]], float), np.array([0, -1.0])
W2, b2 = np.array([1, -2.0]), 0.0
H = relu(X @ W1 + b1)
assert np.allclose(H, [[0, 0], [1, 0], [1, 0], [2, 1]]) and np.allclose(H @ W2 + b2, [0, 1, 1, 0])

# ---------------------------------------------------------------- 2. MLP trên hai vầng trăng
Xm, ym = make_moons(300, noise=0.3, random_state=0)
a, b, c, e = train_test_split(Xm, ym, test_size=0.3, random_state=0)
mlp = {h: MLPClassifier(h, max_iter=3000, random_state=0).fit(a, c) for h in ((2,), (32, 32))}
assert round(mlp[(32, 32)].score(b, e), 4) == 0.9444

# ---------------------------------------------------------------- vẽ hình (bảng màu Chương 10)
NEN = "#FBF8F1"
XANH, CAM, DO, XAM, CHU, LUOI = "#1F5F8B", "#E07A1F", "#C0392B", "#8A8170", "#2B2B2B", "#E6DECD"
LUC = "#2E8B57"
co_sans = {f.name for f in font_manager.fontManager.ttflist}
FONT = "Be Vietnam Pro" if "Be Vietnam Pro" in co_sans else "DejaVu Sans"
plt.rcParams.update({
    "font.family": FONT, "font.size": 12.5, "mathtext.fontset": "dejavusans",
    "text.color": CHU, "axes.labelcolor": CHU, "xtick.color": CHU, "ytick.color": CHU,
    "axes.edgecolor": XAM, "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": LUOI, "grid.alpha": 0.8, "axes.axisbelow": True,
    "figure.facecolor": NEN, "axes.facecolor": NEN, "savefig.facecolor": NEN,
    "savefig.bbox": "tight", "svg.hashsalt": "ch23",
})
PHAY = FuncFormatter(lambda v, _: f"{v:g}".replace(".", ","))


def luu(fig, ten):
    fig.savefig(OUT / ten, metadata={"Date": None})  # bỏ ngày giờ để file không đổi giữa các lần chạy
    plt.close(fig)


# Hình 23.1: ba hàm kích hoạt
fig, ax = plt.subplots(figsize=(6.6, 3.8))
z = np.linspace(-4, 4, 400)
ax.plot(z, sig(z), color=XANH, lw=2.2, label="sigmoid")
ax.plot(z, np.tanh(z), color=CAM, lw=2.2, label="tanh")
ax.plot(z, relu(z), color=DO, lw=2.2, label="ReLU")
ax.axhline(0, color=CHU, lw=0.8)
ax.axvline(0, color=CHU, lw=0.8)
ax.set_ylim(-1.3, 3)
ax.set_xlabel("z = w · x + b")
ax.set_ylabel("đầu ra của nơ-ron")
ax.xaxis.set_major_formatter(PHAY)
ax.yaxis.set_major_formatter(PHAY)
ax.legend(loc="upper left", fontsize=10.5, facecolor=NEN, edgecolor=LUOI, framealpha=1)
luu(fig, "h1_kich_hoat.svg")

# Hình 23.2: sơ đồ mạng giải XOR
fig, ax = plt.subplots(figsize=(7.4, 3.8))
ax.axis("off")
ax.set_xlim(-0.6, 4.6)
ax.set_ylim(-0.4, 3.4)
nut = {"x₁": (0, 2.4), "x₂": (0, 0.6), "h₁": (2, 2.4), "h₂": (2, 0.6), "ŷ": (4, 1.5)}
noi = [("x₁", "h₁", "1"), ("x₂", "h₁", "1"), ("x₁", "h₂", "1"), ("x₂", "h₂", "1"), ("h₁", "ŷ", "1"), ("h₂", "ŷ", "-2")]
for u, v, w in noi:
    (x0, y0), (x1, y1) = nut[u], nut[v]
    ax.annotate("", xy=(x1 - 0.28, y1 + (y0 - y1) * 0.14), xytext=(x0 + 0.28, y0), arrowprops=dict(arrowstyle="-|>", color=XAM, lw=1.3))
    tx, ty = x0 + (x1 - x0) * 0.32, y0 + (y1 - y0) * 0.32 + 0.12
    ax.text(tx, ty, w, fontsize=11, color=DO if w.startswith("-") else XANH, ha="center")
for ten, (x0, y0) in nut.items():
    ax.add_patch(plt.Circle((x0, y0), 0.28, fc="#F1ECE2", ec=XAM, lw=1.4, zorder=3))
    ax.text(x0, y0, ten, ha="center", va="center", fontsize=13, zorder=4)
ax.text(2, 2.95, "b = 0, ReLU", ha="center", fontsize=10.5, color=XAM)
ax.text(2, 0.05, "b = -1, ReLU", ha="center", fontsize=10.5, color=XAM)
ax.text(4, 2.05, "b = 0", ha="center", fontsize=10.5, color=XAM)
ax.text(0, 3.15, "lớp vào", ha="center", fontsize=11)
ax.text(2, 3.3, "lớp ẩn", ha="center", fontsize=11)
ax.text(4, 2.45, "lớp ra", ha="center", fontsize=11)
luu(fig, "h2_mang_xor.svg")

# Hình 23.3: ranh giới của MLP 2 nơ-ron và MLP 32-32
nen = ListedColormap(["#F6DAD5", "#D6E4F0"])
xx, yy = np.meshgrid(np.linspace(-2, 3, 300), np.linspace(-1.6, 2.1, 300))
fig, truc = plt.subplots(1, 2, figsize=(9.2, 3.8), sharey=True)
for ax, (h, m) in zip(truc, mlp.items()):
    zz = m.predict(np.c_[xx.ravel(), yy.ravel()]).reshape(xx.shape)
    ax.contourf(xx, yy, zz, levels=[-0.5, 0.5, 1.5], cmap=nen)
    ax.scatter(a[c == 1, 0], a[c == 1, 1], s=12, color=XANH)
    ax.scatter(a[c == 0, 0], a[c == 0, 1], s=12, color=DO)
    ten = "1 lớp ẩn 2 nơ-ron" if h == (2,) else "2 lớp ẩn 32 nơ-ron"
    ax.set_title(f"{ten}: test {m.score(b, e):.0%}", fontsize=12)
    ax.set_xlabel("đặc trưng 1")
    ax.grid(False)
truc[0].set_ylabel("đặc trưng 2")
luu(fig, "h3_mlp_moons.svg")
print("Đã vẽ 3 hình vào", OUT)
