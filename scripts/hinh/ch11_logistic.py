"""Chương 11 Hồi quy logistic: tính lại các con số dùng trong bài và vẽ hình.

Chạy:  .venv/bin/python scripts/hinh/ch11_logistic.py
Kết quả: các file SVG trong public/hinh/ch11/. Con số nào trong bài sai thì một câu assert báo lỗi.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
from matplotlib.ticker import FuncFormatter
from sklearn.linear_model import LogisticRegression

GOC = Path(__file__).resolve().parents[2]
OUT = GOC / "public" / "hinh" / "ch11"
OUT.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- số liệu (Bảng 11.1)
gio = np.array([1, 2, 2, 3, 3, 4, 4, 5, 6, 7.0])
do = np.array([0, 0, 1, 0, 0, 1, 0, 1, 1, 1.0])
sig = lambda z: 1 / (1 + np.exp(-z))


def bce(w, b):
    p = sig(w * gio + b)
    return float(-np.mean(do * np.log(p) + (1 - do) * np.log(1 - p)))


assert round(bce(0, 0), 4) == 0.6931
assert np.allclose([np.mean((sig(0) - do) * gio), np.mean(sig(0) - do)], [-0.55, 0.0])
w = b = 0.0
for _ in range(5000):
    p = sig(w * gio + b)
    w, b = w - 0.1 * np.mean((p - do) * gio), b - 0.1 * np.mean(p - do)
assert round(w, 4) == 1.0204 and round(b, 4) == -3.6696
m = LogisticRegression(C=np.inf).fit(gio.reshape(-1, 1), do)
W, B = m.coef_[0, 0], m.intercept_[0]
assert round(W, 2) == 1.02 and round(B, 2) == -3.67 and round(-B / W, 2) == 3.6
assert round(bce(W, B), 3) == 0.468 and (m.predict(gio.reshape(-1, 1)) == do).mean() == 0.8

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
    "savefig.bbox": "tight", "svg.hashsalt": "ch11",
})
PHAY = FuncFormatter(lambda v, _: f"{v:g}".replace(".", ","))


def luu(fig, ten):
    fig.savefig(OUT / ten, metadata={"Date": None})  # bỏ ngày giờ để file không đổi giữa các lần chạy
    plt.close(fig)


# Hình 11.1: mười bạn, đường sigmoid đã khớp, ranh giới quyết định
fig, ax = plt.subplots(figsize=(6.8, 3.9))
t = np.linspace(0, 8, 300)
ax.plot(t, sig(W * t + B), color=XANH, lw=2.2, label="xác suất đỗ đoán ra")
lech = np.array([0, 0, 0.04, -0.04, 0.04, 0.04, -0.04, 0, 0, 0])  # tách các chấm trùng tọa độ
ax.scatter(gio, do + lech, s=70, color=[CAM if v else DO for v in do], zorder=3)
ax.axvline(-B / W, color=XAM, ls="--", lw=1.4)
ax.text(-B / W + 0.1, 0.55, "ranh giới ≈ 3,6 giờ", fontsize=11, color=XAM)
ax.axhline(0.5, color=LUOI, lw=1)
ax.set_xlim(0, 8)
ax.set_ylim(-0.1, 1.1)
ax.set_xlabel("Giờ tự học mỗi tuần")
ax.set_ylabel("Xác suất đỗ")
ax.yaxis.set_major_formatter(PHAY)
ax.legend(loc="lower right", fontsize=10.5, facecolor=NEN, edgecolor=LUOI, framealpha=1)
luu(fig, "h1_sigmoid.svg")

# Hình 11.2: mức phạt của cross-entropy theo xác suất gán cho đáp án đúng
fig, ax = plt.subplots(figsize=(6.4, 3.7))
p = np.linspace(0.005, 1, 400)
ax.plot(p, -np.log(p), color=DO, lw=2.2, label="cross-entropy: -log p")
ax.plot(p, (1 - p) ** 2, color=XANH, lw=2.2, label="bình phương sai số: (1 - p)²")
for pp in (0.5, 0.1, 0.01):
    ax.plot([pp], [-np.log(pp)], "o", color=DO, ms=5)
    ax.annotate(f"p = {pp:g}: {-np.log(pp):.2f}".replace(".", ","), (pp, -np.log(pp)), xytext=(8, 0), textcoords="offset points", fontsize=10.5)
ax.set_ylim(0, 5.2)
ax.set_xlabel("Xác suất mô hình gán cho đáp án đúng")
ax.set_ylabel("Mức phạt")
ax.xaxis.set_major_formatter(PHAY)
ax.legend(loc="upper right", fontsize=10.5, facecolor=NEN, edgecolor=LUOI, framealpha=1)
luu(fig, "h2_cross_entropy.svg")
print("Đã vẽ 2 hình vào", OUT)
