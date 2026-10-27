"""Chương 7 Xác suất và thống kê: tính lại các con số dùng trong bài và vẽ hình.

Chạy:  .venv/bin/python scripts/hinh/ch07_xac_suat.py
Kết quả: các file SVG trong public/hinh/ch07/. Con số nào trong bài sai thì một câu assert báo lỗi.
Các con số mô phỏng phụ thuộc phiên bản NumPy (bài chạy với NumPy 2.5.4).
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
from matplotlib.ticker import FuncFormatter

GOC = Path(__file__).resolve().parents[2]
OUT = GOC / "public" / "hinh" / "ch07"
OUT.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- số liệu
tung = np.random.default_rng(0).integers(0, 2, size=10000)       # 1 là ngửa
assert [tung[:n].mean() for n in (10, 100, 1000, 10000)] == [0.4, 0.56, 0.537, 0.503]
z = np.random.default_rng(1).normal(0, 1, size=100000)
assert [round(float(np.mean(np.abs(z) < k)), 4) for k in (1, 2, 3)] == [0.6841, 0.955, 0.9971]
p_duong = 0.99 * 0.01 + 0.05 * 0.99
assert round(p_duong, 4) == 0.0594 and round(0.99 * 0.01 / p_duong, 4) == 0.1667
p = np.linspace(0.01, 0.99, 99)
ll = 7 * np.log(p) + 3 * np.log(1 - p)
assert np.isclose(p[np.argmax(ll)], 0.7)

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
    "savefig.bbox": "tight", "svg.hashsalt": "ch07",
})
PHAY = FuncFormatter(lambda v, _: f"{v:g}".replace(".", ","))


def luu(fig, ten):
    fig.savefig(OUT / ten, metadata={"Date": None})  # bỏ ngày giờ để file không đổi giữa các lần chạy
    plt.close(fig)


# Hình 7.1: tỷ lệ mặt ngửa cộng dồn theo số lần tung
n = np.arange(1, 10001)
fig, ax = plt.subplots(figsize=(6.6, 3.6))
ax.plot(n, np.cumsum(tung) / n, color=XANH, lw=1.6)
ax.axhline(0.5, color=CAM, lw=1.6, ls="--")
ax.text(12000, 0.5, "0,5", color=CAM, va="center", fontsize=11)
ax.set_xscale("log")
ax.set_ylim(0, 1)
ax.set_xlabel("Số lần tung (thang log)")
ax.set_ylabel("Tỷ lệ mặt ngửa")
ax.yaxis.set_major_formatter(PHAY)
luu(fig, "h1_luat_so_lon.svg")

# Hình 7.2: histogram 100 000 mẫu chuẩn và đường mật độ lý thuyết
fig, ax = plt.subplots(figsize=(6.6, 3.8))
ax.hist(z, bins=60, range=(-4, 4), density=True, color=XANH, alpha=0.55, edgecolor=NEN)
t = np.linspace(-4, 4, 400)
ax.plot(t, np.exp(-t ** 2 / 2) / np.sqrt(2 * np.pi), color=CAM, lw=2.2)
for k, a in ((1, 0.16), (2, 0.08)):
    ax.axvspan(-k, k, color=CAM, alpha=a, lw=0)
ax.text(0, 0.43, "68%", ha="center", fontsize=11.5)
ax.text(1.5, 0.2, "95%\n(cả hai bên)", ha="left", fontsize=10.5, color=XAM)
ax.set_xlabel("z")
ax.set_ylabel("Mật độ")
ax.yaxis.set_major_formatter(PHAY)
luu(fig, "h2_phan_phoi_chuan.svg")

# Hình 7.3: log-likelihood của 7 ngửa trong 10 lần theo p
fig, ax = plt.subplots(figsize=(6.6, 3.8))
pp = np.linspace(0.05, 0.95, 300)
ax.plot(pp, 7 * np.log(pp) + 3 * np.log(1 - pp), color=XANH, lw=2.2)
ax.plot([0.7], [7 * np.log(0.7) + 3 * np.log(0.3)], "o", color=DO, ms=7, zorder=4)
ax.annotate("cực đại tại p = 0,7", (0.7, 7 * np.log(0.7) + 3 * np.log(0.3)), xytext=(-40, 14), textcoords="offset points", color=DO, fontsize=11)
ax.plot([0.5], [10 * np.log(0.5)], "o", color=CHU, ms=6, zorder=4)
ax.annotate("p = 0,5", (0.5, 10 * np.log(0.5)), xytext=(-60, -4), textcoords="offset points", fontsize=11)
ax.set_ylim(-20, -4)
ax.set_xlabel("p (xác suất ra mặt ngửa)")
ax.set_ylabel("log-likelihood")
ax.xaxis.set_major_formatter(PHAY)
ax.yaxis.set_major_formatter(PHAY)
luu(fig, "h3_log_likelihood.svg")
print("Đã vẽ 3 hình vào", OUT)
