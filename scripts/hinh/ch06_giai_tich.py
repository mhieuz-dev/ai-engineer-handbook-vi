"""Chương 6 Giải tích: tính lại các con số dùng trong bài và vẽ hình.

Chạy:  .venv/bin/python scripts/hinh/ch06_giai_tich.py
Kết quả: các file SVG trong public/hinh/ch06/. Con số nào trong bài sai thì một câu assert báo lỗi.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
from matplotlib.ticker import FuncFormatter

GOC = Path(__file__).resolve().parents[2]
OUT = GOC / "public" / "hinh" / "ch06"
OUT.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- số liệu
f = lambda t: t ** 2
assert np.isclose((f(4) - f(3)) / 1, 7) and np.isclose((f(3.1) - f(3)) / 0.1, 6.1)
x, y = np.array([1, 2, 3, 4.0]), np.array([2, 4, 5, 7.0])
L = lambda w, b: np.mean((y - (w * x + b)) ** 2)


def grad(w, b):
    e = y - (w * x + b)
    return -2 * np.mean(x * e), -2 * np.mean(e)


assert np.allclose(grad(0, 0), (-26.5, -9.0)) and np.allclose(grad(1.6, 0.5), (0, 0))
assert np.allclose(grad(1.325, 0.45), (-4.375, -1.475))  # bước 2 của Chương 10
w0 = 0.5
doc = grad(w0, 0.5)[0]
assert np.isclose(doc, -16.5) and np.isclose(L(w0, 0.5), 9.125)

# ---------------------------------------------------------------- vẽ hình (bảng màu Chương 10)
NEN = "#FBF8F1"
XANH, CAM, DO, XAM, CHU, LUOI = "#1F5F8B", "#E07A1F", "#C0392B", "#8A8170", "#2B2B2B", "#E6DECD"
co_sans = {f_.name for f_ in font_manager.fontManager.ttflist}
FONT = "Be Vietnam Pro" if "Be Vietnam Pro" in co_sans else "DejaVu Sans"
plt.rcParams.update({
    "font.family": FONT, "font.size": 12.5, "mathtext.fontset": "dejavusans",
    "text.color": CHU, "axes.labelcolor": CHU, "xtick.color": CHU, "ytick.color": CHU,
    "axes.edgecolor": XAM, "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": LUOI, "grid.alpha": 0.8, "axes.axisbelow": True,
    "figure.facecolor": NEN, "axes.facecolor": NEN, "savefig.facecolor": NEN,
    "savefig.bbox": "tight", "svg.hashsalt": "ch06",
})
PHAY = FuncFormatter(lambda v, _: f"{v:g}".replace(".", ","))


def luu(fig, ten):
    fig.savefig(OUT / ten, metadata={"Date": None})  # bỏ ngày giờ để file không đổi giữa các lần chạy
    plt.close(fig)


fig, (trai, phai) = plt.subplots(1, 2, figsize=(9.6, 4.0))
# Trái: f(x) = x^2, cát tuyến qua x = 3 và x = 4 (độ dốc 7), tiếp tuyến tại x = 3 (độ dốc 6)
t = np.linspace(0, 5, 200)
trai.plot(t, f(t), color=XANH, lw=2.2, label="f(x) = x²")
trai.plot(t, 9 + 7 * (t - 3), color=XAM, lw=1.4, ls="--", label="cát tuyến, độ dốc 7")
trai.plot(t, 9 + 6 * (t - 3), color=CAM, lw=2, label="tiếp tuyến, độ dốc 6")
trai.plot([3, 4], [9, 16], "o", color=CHU, ms=6, zorder=4)
trai.annotate("(3; 9)", (3, 9), xytext=(8, -14), textcoords="offset points", fontsize=11)
trai.annotate("(4; 16)", (4, 16), xytext=(-52, 4), textcoords="offset points", fontsize=11)
trai.set_xlim(0, 5)
trai.set_ylim(-2, 25)
trai.set_xlabel("x")
trai.legend(loc="upper left", fontsize=10.5, facecolor=NEN, edgecolor=LUOI, framealpha=1)
trai.set_title("Đạo hàm là độ dốc của tiếp tuyến", fontsize=12.5)
# Phải: loss theo w khi giữ b = 0,5; tiếp tuyến tại w = 0,5 dốc -16,5
ww = np.linspace(0, 3.2, 200)
phai.plot(ww, [L(v, 0.5) for v in ww], color=XANH, lw=2.2)
phai.plot(ww, L(w0, 0.5) + doc * (ww - w0), color=CAM, lw=2)
phai.plot([w0], [L(w0, 0.5)], "o", color=CHU, ms=6, zorder=4)
phai.plot([1.6], [L(1.6, 0.5)], "o", color=DO, ms=6, zorder=4)
phai.annotate("w = 0,5: độ dốc -16,5", (w0, L(w0, 0.5)), xytext=(10, 4), textcoords="offset points", fontsize=11)
phai.annotate("đáy: w = 1,6", (1.6, L(1.6, 0.5)), xytext=(-20, 12), textcoords="offset points", fontsize=11, color=DO)
phai.set_xlim(0, 3.2)
phai.set_ylim(-1, 12)
phai.set_xlabel("w (giữ b = 0,5)")
phai.set_ylabel("MSE")
phai.xaxis.set_major_formatter(PHAY)
phai.set_title("Độ dốc âm: tăng w thì loss giảm", fontsize=12.5)
luu(fig, "h1_do_doc.svg")
print("Đã vẽ 1 hình vào", OUT)
