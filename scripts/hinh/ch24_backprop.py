"""Chương 24 Backpropagation: tính lại các con số dùng trong bài và vẽ hình.

Chạy:  .venv/bin/python scripts/hinh/ch24_backprop.py
Kết quả: các file SVG trong public/hinh/ch24/. Con số nào trong bài sai thì một câu assert báo lỗi.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch
from matplotlib.ticker import FuncFormatter
from sklearn.datasets import make_moons
from sklearn.model_selection import train_test_split

GOC = Path(__file__).resolve().parents[2]
OUT = GOC / "public" / "hinh" / "ch24"
OUT.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- 1. một nơ-ron: x = 2, w = 0,5, b = 0,1, y = 1
x, w, b, y = 2.0, 0.5, 0.1, 1.0
z = w * x + b
a = 1 / (1 + np.exp(-z))
L = (a - y) ** 2
dL_da = 2 * (a - y)
dL_dz = dL_da * a * (1 - a)
assert round(z, 4) == 1.1 and round(a, 4) == 0.7503 and round(L, 4) == 0.0624
assert round(dL_dz, 4) == -0.0936 and round(dL_dz * x, 4) == -0.1872

# ---------------------------------------------------------------- 2. mạng 2-32-1 bằng NumPy trên hai vầng trăng
Xm, ym = make_moons(300, noise=0.3, random_state=0)
Xtr, Xte, ytr, yte = train_test_split(Xm, ym, test_size=0.3, random_state=0)
r = np.random.default_rng(0)
P = [r.normal(0, 1.0, (2, 32)), np.zeros(32), r.normal(0, np.sqrt(2 / 32), (32, 1)), np.zeros(1)]


def truyen_xuoi(P, X):
    W1, b1, W2, b2 = P
    Z1 = X @ W1 + b1
    A1 = np.maximum(0, Z1)
    return Z1, A1, (1 / (1 + np.exp(-(A1 @ W2 + b2)))).ravel()


def mat_mat(P, X, y):
    p = np.clip(truyen_xuoi(P, X)[2], 1e-12, 1 - 1e-12)
    return float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))


def truyen_nguoc(P, X, y):
    W1, b1, W2, b2 = P
    Z1, A1, p = truyen_xuoi(P, X)
    dZ2 = (p - y)[:, None] / len(y)
    dZ1 = (dZ2 @ W2.T) * (Z1 > 0)
    return [X.T @ dZ1, dZ1.sum(0), A1.T @ dZ2, dZ2.sum(0)]


ls = []
for _ in range(3001):
    ls.append(mat_mat(P, Xtr, ytr))
    P = [p_ - 0.5 * g for p_, g in zip(P, truyen_nguoc(P, Xtr, ytr))]
dung = lambda X, y: float(np.mean((truyen_xuoi(P, X)[2] > 0.5) == y))
assert round(dung(Xte, yte), 4) == 0.9333

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
    "savefig.bbox": "tight", "svg.hashsalt": "ch24",
})
PHAY = FuncFormatter(lambda v, _: f"{v:g}".replace(".", ","))
s = lambda v: f"{v:.4f}".replace(".", ",")


def luu(fig, ten):
    fig.savefig(OUT / ten, metadata={"Date": None})  # bỏ ngày giờ để file không đổi giữa các lần chạy
    plt.close(fig)


# Hình 24.1: đồ thị tính toán của một nơ-ron, giá trị xuôi (xanh) và gradient ngược (đỏ)
fig, ax = plt.subplots(figsize=(9.6, 3.4))
ax.axis("off")
ax.set_xlim(0, 9.4)
ax.set_ylim(-0.9, 3.2)
o = {"w": (0.9, 2.5), "x": (0.9, 0.5), "b": (3.6, -0.1), "z": (3.6, 1.5), "a": (6.0, 1.5), "L": (8.4, 1.5)}
nhan = {"w": f"w = 0,5", "x": "x = 2", "b": "b = 0,1", "z": f"z = w·x + b\n= {s(z)}", "a": f"a = σ(z)\n= {s(a)}", "L": f"L = (a - y)²\n= {s(L)}"}
dao = {"w": f"∂L/∂w = {s(dL_dz * x)}", "b": f"∂L/∂b = {s(dL_dz)}", "z": f"∂L/∂z = {s(dL_dz)}", "a": f"∂L/∂a = {s(dL_da)}", "L": "∂L/∂L = 1"}
for k, (cx, cy) in o.items():
    ax.add_patch(FancyBboxPatch((cx - 0.75, cy - 0.38), 1.5, 0.76, boxstyle="round,pad=0.03,rounding_size=0.1", fc="#F1ECE2", ec=XAM, lw=1.2))
    ax.text(cx, cy, nhan[k], ha="center", va="center", fontsize=10.5, color=XANH, linespacing=1.3)
    if k in dao:
        ax.text(cx + (1.5 if k == "b" else 0), cy - 0.62 if k not in ("w", "b", "z") else (cy if k == "b" else cy + 0.58), dao[k], ha="center", va="center", fontsize=10, color=DO)
for u, v in (("w", "z"), ("x", "z"), ("z", "a"), ("a", "L")):
    (x0, y0), (x1, y1) = o[u], o[v]
    ax.annotate("", xy=(x1 - 0.78, y1), xytext=(x0 + 0.78, y0), arrowprops=dict(arrowstyle="-|>", color=XAM, lw=1.3))
ax.annotate("", xy=(o["z"][0], o["z"][1] - 0.4), xytext=(o["b"][0], o["b"][1] + 0.4), arrowprops=dict(arrowstyle="-|>", color=XAM, lw=1.3))
luu(fig, "h1_do_thi_tinh.svg")

# Hình 24.2: loss của mạng tự cài theo số bước
fig, ax = plt.subplots(figsize=(6.6, 3.6))
ax.plot(np.arange(1, len(ls) + 1), ls, color=XANH, lw=1.8)
ax.axhline(np.log(2), color=XAM, ls=":", lw=1.2)
ax.text(3050, np.log(2), "log 2", va="center", fontsize=10.5, color=XAM)
ax.set_xscale("log")
ax.set_xlabel("bước (thang log, bước 1 là trước khi cập nhật)")
ax.set_ylabel("cross-entropy trên train")
ax.yaxis.set_major_formatter(PHAY)
luu(fig, "h2_loss.svg")
print("Đã vẽ 2 hình vào", OUT)
