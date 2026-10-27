"""Chương 22 Dự án Phần II: tính lại các con số dùng trong bài và vẽ hình.

Chạy:  .venv/bin/python scripts/hinh/ch22_du_an.py   (cần mạng lần đầu để tải California housing)
Kết quả: các file SVG trong public/hinh/ch22/. Con số nào trong bài sai thì một câu assert báo lỗi.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
from matplotlib.ticker import FuncFormatter
from sklearn.datasets import fetch_california_housing
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split

GOC = Path(__file__).resolve().parents[2]
OUT = GOC / "public" / "hinh" / "ch22"
OUT.mkdir(parents=True, exist_ok=True)

d = fetch_california_housing(as_frame=True)
X, y = d.frame.drop(columns="MedHouseVal"), d.frame["MedHouseVal"]
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42)
m = HistGradientBoostingRegressor(learning_rate=0.05, max_iter=600, max_leaf_nodes=63, random_state=0).fit(Xtr, ytr)
p = m.predict(Xte)
assert round(mean_absolute_error(yte, p), 4) == 0.2887 and int((y >= 5).sum()) == 992

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
    "savefig.bbox": "tight", "svg.hashsalt": "ch22",
})
PHAY = FuncFormatter(lambda v, _: f"{v:g}".replace(".", ","))


def luu(fig, ten):
    fig.savefig(OUT / ten, metadata={"Date": None})  # bỏ ngày giờ để file không đổi giữa các lần chạy
    plt.close(fig)


# Hình 22.1: bản đồ giá nhà theo kinh độ, vĩ độ
fig, ax = plt.subplots(figsize=(6.2, 5.6))
sc = ax.scatter(X["Longitude"], X["Latitude"], c=y, s=3, cmap="viridis", alpha=0.6, rasterized=True)
cb = fig.colorbar(sc, ax=ax, shrink=0.8)
cb.set_label("giá trị nhà trung vị (100 000 USD)")
for ten, (lo, la) in {"San Francisco": (-122.42, 37.77), "Los Angeles": (-118.24, 34.05), "San Diego": (-117.16, 32.72)}.items():
    ax.annotate(ten, (lo, la), xytext=(14, 6), textcoords="offset points", fontsize=10.5, bbox=dict(boxstyle="round,pad=0.2", fc="white", ec=XAM, alpha=0.9),
                arrowprops=dict(arrowstyle="-", color=CHU, lw=0.8))
ax.set_xlabel("kinh độ")
ax.set_ylabel("vĩ độ")
ax.set_aspect("equal")
luu(fig, "h1_ban_do.svg")

# Hình 22.2: dự đoán so với giá trị thật trên tập test
fig, ax = plt.subplots(figsize=(5.6, 5.0))
ax.scatter(yte, p, s=4, alpha=0.35, color=XANH, rasterized=True)
ax.plot([0, 5.2], [0, 5.2], color=DO, lw=1.4, ls="--")
ax.axvline(5.0, color=XAM, ls=":", lw=1.2)
ax.text(4.95, 0.4, "trần 5,0", ha="right", fontsize=10.5, color=XAM)
ax.set_xlim(0, 5.3)
ax.set_ylim(0, 5.8)
ax.set_xlabel("giá trị thật")
ax.set_ylabel("giá trị dự đoán")
ax.xaxis.set_major_formatter(PHAY)
ax.yaxis.set_major_formatter(PHAY)
luu(fig, "h2_du_doan.svg")
print("Đã vẽ 2 hình vào", OUT)
