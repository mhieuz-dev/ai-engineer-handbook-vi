"""Chương 8 Tối ưu hóa: tính lại các con số dùng trong bài và vẽ hình.

Chạy:  .venv/bin/python scripts/hinh/ch08_toi_uu.py
Kết quả: các file SVG trong public/hinh/ch08/. Con số nào trong bài sai thì một câu assert báo lỗi.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
from matplotlib.ticker import FuncFormatter

GOC = Path(__file__).resolve().parents[2]
OUT = GOC / "public" / "hinh" / "ch08"
OUT.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------- 1. một chiều: f(x) = (x - 3)^2
def gd_1d(lr, x=0.0, n=20):
    xs = [x]
    for _ in range(n):
        x = x - lr * 2 * (x - 3)
        xs.append(x)
    return np.array(xs)


assert np.allclose(gd_1d(0.05)[:4], [0, 0.3, 0.57, 0.813]) and round(gd_1d(0.05)[20], 4) == 2.6353
assert np.allclose(gd_1d(0.5)[1:], 3)
assert np.allclose(gd_1d(0.9)[:4], [0, 5.4, 1.08, 4.536])
assert round(gd_1d(1.1)[20], 4) == -112.0128

# ---------------------------------------------------------------- 2. 10 sinh viên (Bảng 4.1): GD, mini-batch, SGD
gio = np.array([1, 2, 3, 4, 5, 2, 6, 3, 7, 4.0])
diem = np.array([2, 4, 5, 7, 6, 3.5, 8.5, 4, 9, 6.5])
mse = lambda w, b: float(np.mean((diem - (w * gio + b)) ** 2))


def train(bs, lr, ep=100, seed=0):
    rng = np.random.default_rng(seed)
    w = b = 0.0
    L = [mse(w, b)]
    for _ in range(ep):
        idx = rng.permutation(10)
        for s in range(0, 10, bs):
            j = idx[s:s + bs]
            e = diem[j] - (w * gio[j] + b)
            w -= lr * (-2 * np.mean(gio[j] * e))
            b -= lr * (-2 * np.mean(e))
        L.append(mse(w, b))
    return w, b, np.array(L)


chay = {"GD (cả 10 bạn)": train(10, 0.03), "mini-batch 5 bạn": train(5, 0.03), "SGD (1 bạn)": train(1, 0.01)}
assert round(chay["GD (cả 10 bạn)"][2][100], 4) == 0.4103
assert round(chay["SGD (1 bạn)"][2][100], 4) == 0.4298 and round(chay["SGD (1 bạn)"][2].min(), 4) == 0.3882
assert round(mse(1.1416667, 1.3254998), 4) == 0.388  # đáy thật, từ Bài tập 4.2

# ---------------------------------------------------------------- 3. bát dẹt f = x^2 + 50 y^2: GD, momentum, Adam
K = 50
g2 = lambda p: np.array([2 * p[0], 2 * K * p[1]])
f2 = lambda p: p[0] ** 2 + K * p[1] ** 2


def duong(kieu, lr, n, beta=0.9):
    p = np.array([-8.0, 1.0])
    v, m, s = np.zeros(2), np.zeros(2), np.zeros(2)
    P = [p.copy()]
    for t in range(1, n + 1):
        gr = g2(p)
        if kieu == "gd":
            p = p - lr * gr
        elif kieu == "momentum":
            v = beta * v + gr
            p = p - lr * v
        else:
            m = 0.9 * m + 0.1 * gr
            s = 0.999 * s + 0.001 * gr ** 2
            p = p - lr * (m / (1 - 0.9 ** t)) / (np.sqrt(s / (1 - 0.999 ** t)) + 1e-8)
        P.append(p.copy())
    return np.array(P)


assert f2(np.array([-8.0, 1.0])) == 114
assert round(float(f2(duong("gd", 0.019, 100)[-1])), 5) == 0.02762
assert float(f2(duong("gd", 0.021, 100)[-1])) > 1e9
assert round(float(f2(duong("momentum", 0.01, 100)[-1])), 5) == 0.00124
assert round(float(f2(duong("adam", 0.3, 100)[-1])), 5) == 0.00051

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
    "savefig.bbox": "tight", "svg.hashsalt": "ch08",
})
PHAY = FuncFormatter(lambda v, _: f"{v:g}".replace(".", ","))


def luu(fig, ten):
    fig.savefig(OUT / ten, metadata={"Date": None})  # bỏ ngày giờ để file không đổi giữa các lần chạy
    plt.close(fig)


# Hình 8.1: x theo số bước với bốn learning rate
fig, ax = plt.subplots(figsize=(6.8, 3.9))
for lr, mau in ((0.05, XAM), (0.5, LUC), (0.9, CAM), (1.1, DO)):
    ax.plot(range(21), gd_1d(lr), "o-", ms=3.5, lw=1.6, color=mau, label=f"η = {lr:g}".replace(".", ","))
ax.axhline(3, color=CHU, lw=1, ls=":")
ax.text(20.4, 3, "đáy x = 3", va="center", fontsize=10.5)
ax.set_ylim(-4, 10)
ax.set_xticks(range(0, 21, 5))
ax.set_xlabel("Số bước")
ax.set_ylabel("x")
ax.legend(loc="upper left", fontsize=10.5, ncol=2, facecolor=NEN, edgecolor=LUOI, framealpha=1)
luu(fig, "h1_learning_rate.svg")

# Hình 8.2: MSE theo epoch, ba cách lấy dữ liệu
fig, ax = plt.subplots(figsize=(6.8, 3.9))
for (ten, (_, _, L)), mau in zip(chay.items(), (XANH, CAM, DO)):
    ax.plot(range(len(L)), L, lw=1.8, color=mau, label=ten)
ax.axhline(0.388, color=CHU, lw=1, ls=":")
ax.text(101, 0.388, "đáy 0,388", va="center", fontsize=10.5)
ax.set_yscale("log")
ax.set_ylim(0.3, 40)
ax.set_xlabel("Epoch (một lượt qua cả 10 bạn)")
ax.set_ylabel("MSE (thang log)")
ax.yaxis.set_major_formatter(PHAY)
ax.legend(loc="upper right", fontsize=10.5, facecolor=NEN, edgecolor=LUOI, framealpha=1)
luu(fig, "h2_sgd.svg")

# Hình 8.3: đường đi trên bát dẹt
fig, ax = plt.subplots(figsize=(7.4, 3.6))
X, Y = np.meshgrid(np.linspace(-9, 3, 300), np.linspace(-1.4, 1.4, 300))
ax.contour(X, Y, X ** 2 + K * Y ** 2, levels=[0.5, 2, 6, 15, 30, 60, 114], colors=LUOI, linewidths=1)
for (kieu, lr), mau, ten in ((("gd", 0.019), XAM, "GD, η = 0,019"), (("momentum", 0.01), CAM, "momentum, η = 0,01"), (("adam", 0.3), XANH, "Adam, η = 0,3")):
    P = duong(kieu, lr, 50)
    ax.plot(P[:, 0], P[:, 1], "o-", ms=2.5, lw=1.3, color=mau, label=ten)
ax.plot([0], [0], "*", color=DO, ms=13, zorder=5)
ax.set_xlim(-9, 3)
ax.plot([-8], [1], "o", color=CHU, ms=6)
ax.annotate("xuất phát", (-8, 1), xytext=(6, 6), textcoords="offset points", fontsize=10.5)
ax.set_xlabel("x")
ax.set_ylabel("y")
ax.legend(loc="lower left", fontsize=10.5, facecolor=NEN, edgecolor=LUOI, framealpha=1)
ax.set_title("50 bước trên f(x, y) = x² + 50y²", fontsize=12.5)
luu(fig, "h3_momentum_adam.svg")
print("Đã vẽ 3 hình vào", OUT)
