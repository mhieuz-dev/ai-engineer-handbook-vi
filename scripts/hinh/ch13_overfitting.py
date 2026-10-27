"""Chương 13 Overfitting, bias-variance và regularization: tính lại các con số và vẽ hình.

Chạy:  .venv/bin/python scripts/hinh/ch13_overfitting.py
Kết quả: các file SVG trong public/hinh/ch13/. Con số nào trong bài sai thì một câu assert báo lỗi.
"""
import warnings
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
from matplotlib.ticker import FuncFormatter
from sklearn.datasets import load_diabetes
from sklearn.linear_model import Lasso, LinearRegression
from sklearn.metrics import mean_squared_error as mse
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import PolynomialFeatures, StandardScaler

warnings.filterwarnings("ignore")
GOC = Path(__file__).resolve().parents[2]
OUT = GOC / "public" / "hinh" / "ch13"
OUT.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- 1. 15 điểm từ sin(2πx) cộng nhiễu
f = lambda t: np.sin(2 * np.pi * t)
rng = np.random.default_rng(0)
x = rng.uniform(0, 1, 15)
y = f(x) + rng.normal(0, 0.3, 15)
xv = rng.uniform(0, 1, 200)
yv = f(xv) + rng.normal(0, 0.3, 200)
khop = lambda d: make_pipeline(PolynomialFeatures(d), LinearRegression()).fit(x[:, None], y)
loi = {d: (mse(y, khop(d).predict(x[:, None])), mse(yv, khop(d).predict(xv[:, None]))) for d in range(1, 13)}
assert [round(v, 4) for v in loi[1]] == [0.1682, 0.4381]
assert [round(v, 4) for v in loi[3]] == [0.038, 0.1047]
assert [round(v, 4) for v in loi[9]] == [0.0273, 0.7235]

# ---------------------------------------------------------------- 2. lasso trên tiểu đường (cách chia của Chương 9)
X, yd = load_diabetes(return_X_y=True, as_frame=True, scaled=False)
Xtr, Xte, ytr, yte = train_test_split(X, yd, test_size=0.2, random_state=42)
Xtr2, Xva, ytr2, yva = train_test_split(Xtr, ytr, test_size=0.25, random_state=42)
alphas = np.logspace(-2, 1.6, 60)
he_so = np.array([make_pipeline(StandardScaler(), Lasso(alpha=a)).fit(Xtr2, ytr2)[-1].coef_ for a in alphas])
assert (make_pipeline(StandardScaler(), Lasso(alpha=10)).fit(Xtr2, ytr2)[-1].coef_ == 0).sum() == 6

# ---------------------------------------------------------------- vẽ hình (bảng màu Chương 10)
NEN = "#FBF8F1"
XANH, CAM, DO, XAM, CHU, LUOI = "#1F5F8B", "#E07A1F", "#C0392B", "#8A8170", "#2B2B2B", "#E6DECD"
LUC = "#2E8B57"
co_sans = {f_.name for f_ in font_manager.fontManager.ttflist}
FONT = "Be Vietnam Pro" if "Be Vietnam Pro" in co_sans else "DejaVu Sans"
plt.rcParams.update({
    "font.family": FONT, "font.size": 12.5, "mathtext.fontset": "dejavusans",
    "text.color": CHU, "axes.labelcolor": CHU, "xtick.color": CHU, "ytick.color": CHU,
    "axes.edgecolor": XAM, "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": LUOI, "grid.alpha": 0.8, "axes.axisbelow": True,
    "figure.facecolor": NEN, "axes.facecolor": NEN, "savefig.facecolor": NEN,
    "savefig.bbox": "tight", "svg.hashsalt": "ch13",
})
PHAY = FuncFormatter(lambda v, _: f"{v:g}".replace(".", ","))


def luu(fig, ten):
    fig.savefig(OUT / ten, metadata={"Date": None})  # bỏ ngày giờ để file không đổi giữa các lần chạy
    plt.close(fig)


# Hình 13.1: ba đa thức bậc 1, 3, 9 trên cùng 15 điểm
fig, truc = plt.subplots(1, 3, figsize=(11, 3.6), sharey=True)
t = np.linspace(0, 1, 400)
for ax, d, ten in zip(truc, (1, 3, 9), ("bậc 1: quá đơn giản", "bậc 3: vừa", "bậc 9: quá phức tạp")):
    ax.plot(t, f(t), color=XAM, ls="--", lw=1.4, label="hàm thật")
    ax.plot(t, khop(d).predict(t[:, None]), color=XANH, lw=2.2, label="mô hình")
    ax.scatter(x, y, s=36, color=CAM, zorder=3)
    ax.set_ylim(-2, 2)
    ax.set_title(ten, fontsize=12.5)
    ax.set_xlabel("x")
    ax.xaxis.set_major_formatter(PHAY)
truc[0].legend(loc="lower left", fontsize=10, facecolor=NEN, edgecolor=LUOI, framealpha=1)
luu(fig, "h1_ba_do_phuc_tap.svg")

# Hình 13.2: lỗi train và validation theo bậc đa thức
fig, ax = plt.subplots(figsize=(6.6, 3.8))
bac = list(loi)
ax.plot(bac, [loi[d][0] for d in bac], "o-", color=XANH, lw=2, label="train (15 điểm)")
ax.plot(bac, [loi[d][1] for d in bac], "o-", color=DO, lw=2, label="validation (200 điểm)")
ax.axhline(0.09, color=XAM, ls=":", lw=1.2)
ax.text(12.3, 0.09, "nhiễu 0,09", va="center", fontsize=10.5, color=XAM)
ax.set_yscale("log")
ax.set_xticks(bac)
ax.set_xlabel("Bậc đa thức")
ax.set_ylabel("MSE (thang log)")
ax.yaxis.set_major_formatter(PHAY)
ax.legend(loc="upper left", fontsize=10.5, facecolor=NEN, edgecolor=LUOI, framealpha=1)
luu(fig, "h2_train_validation.svg")

# Hình 13.3: đường hệ số lasso theo alpha
fig, ax = plt.subplots(figsize=(6.8, 4.0))
mau = {"bmi": DO, "s5": CAM, "bp": XANH, "s3": LUC}
for j, ten in enumerate(X.columns):
    ax.plot(alphas, he_so[:, j], lw=2 if ten in mau else 1.2, color=mau.get(ten, XAM), alpha=1 if ten in mau else 0.7)
    if ten in mau:
        ax.text(alphas[0] * 0.75, he_so[0, j], ten, ha="right", va="center", fontsize=10.5, color=mau[ten])
ax.axhline(0, color=CHU, lw=0.8)
ax.axvline(10, color=XAM, ls="--", lw=1.2)
ax.text(10.5, -38, "α = 10: còn 4 đặc trưng", fontsize=10.5, color=XAM)
ax.set_xscale("log")
ax.set_xlabel("α (độ mạnh regularization, thang log)")
ax.set_ylabel("Hệ số (đặc trưng đã chuẩn hóa)")
luu(fig, "h3_lasso.svg")
print("Đã vẽ 3 hình vào", OUT)
