"""Chương 5 Đại số tuyến tính: tính lại các con số dùng trong bài và vẽ hình.

Chạy:  .venv/bin/python scripts/hinh/ch05_dai_so.py
Kết quả: các file SVG trong public/hinh/ch05/. Con số nào trong bài sai thì một câu assert báo lỗi.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
from matplotlib.patches import Polygon

GOC = Path(__file__).resolve().parents[2]
OUT = GOC / "public" / "hinh" / "ch05"
OUT.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- số liệu
u, v = np.array([3.0, 4.0]), np.array([4.0, 3.0])
assert np.linalg.norm(u) == 5 and u @ v == 24 and np.isclose(u @ v / 25, 0.96)
M = np.array([[2.0, 0.0], [0.0, 1.0]])   # kéo giãn gấp đôi theo trục ngang
R = np.array([[0.0, -1.0], [1.0, 0.0]])  # quay 90 độ ngược chiều kim đồng hồ
assert np.allclose(R @ M @ [1, 1], [-1, 2]) and np.allclose(M @ R @ [1, 1], [-2, 1])
assert np.isclose(np.linalg.det(M), 2) and np.isclose(np.linalg.det(R), 1)
x, y = np.array([1, 2, 3, 4.0]), np.array([2, 4, 5, 7.0])
X = np.column_stack([np.ones(4), x])
assert np.allclose(np.linalg.solve(X.T @ X, X.T @ y), [0.5, 1.6])  # khớp nghiệm Chương 10
D = np.array([[1, 2], [2, 1], [3, 4], [4, 3]], float)
Dc = D - D.mean(axis=0)
C = Dc.T @ Dc / 4
assert np.allclose(C, [[1.25, 0.75], [0.75, 1.25]])
gia_tri, vec = np.linalg.eigh(C)
assert np.allclose(gia_tri, [0.5, 2.0])

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
    "savefig.bbox": "tight", "svg.hashsalt": "ch05",
})


def luu(fig, ten):
    fig.savefig(OUT / ten, metadata={"Date": None})  # bỏ ngày giờ để file không đổi giữa các lần chạy
    plt.close(fig)


def mui_ten(ax, dau, cuoi, mau, nhan=None, lech=(6, 6)):
    ax.annotate("", xy=cuoi, xytext=dau, arrowprops=dict(arrowstyle="-|>", color=mau, lw=2, shrinkA=0, shrinkB=0))
    if nhan:
        ax.annotate(nhan, cuoi, xytext=lech, textcoords="offset points", color=mau, fontsize=12)


# Hình 5.1: hình vuông đơn vị qua hai phép biến đổi M (kéo giãn) và R (quay)
vuong = np.array([[0, 0], [1, 0], [1, 1], [0, 1]], float)
fig, truc = plt.subplots(1, 2, figsize=(8.6, 4.0))
VI_TRI = {"M": ((-30, -20), (-104, 4), (-30, 12)), "R": ((6, -4), (-40, -20), (-20, 10))}  # chỗ đặt nhãn (hai mũi tên, điểm (1, 1)), tránh đè nhau
for ax, (ten, ma_tran, tieu_de) in zip(truc, [("M", M, "M kéo giãn trục ngang gấp đôi"), ("R", R, "R quay 90 độ")]):
    ax.add_patch(Polygon(vuong, closed=True, fc=XANH, alpha=0.18, ec=XANH, lw=1.5, ls="--"))
    ax.add_patch(Polygon(vuong @ ma_tran.T, closed=True, fc=CAM, alpha=0.28, ec=CAM, lw=2))
    mui_ten(ax, (0, 0), ma_tran @ [1, 0], DO, "ảnh của (1, 0)", VI_TRI[ten][0])
    mui_ten(ax, (0, 0), ma_tran @ [0, 1], XANH, "ảnh của (0, 1)", VI_TRI[ten][1])
    ax.plot(*(ma_tran @ [1, 1]), "o", color=CHU, ms=6)
    dich = ma_tran @ [1, 1]
    ax.annotate(f"(1, 1) đi tới ({dich[0]:g}, {dich[1]:g})", dich, xytext=VI_TRI[ten][2], textcoords="offset points", fontsize=11)
    ax.set_xlim(-1.8, 3.2)
    ax.set_ylim(-0.8, 2.0)
    ax.set_aspect("equal")
    ax.set_title(tieu_de, fontsize=12.5)
luu(fig, "h1_bien_doi.svg")

# Hình 5.2: dữ liệu đã trừ trung bình và hai vector riêng của ma trận hiệp phương sai
fig, ax = plt.subplots(figsize=(5.2, 5.0))
ax.scatter(Dc[:, 0], Dc[:, 1], s=70, color=CAM, zorder=3)
for ten, (a, b) in zip("ABCD", Dc):
    ax.annotate(ten, (a, b), xytext=(7, -4), textcoords="offset points", fontsize=11.5)
lon, nho = vec[:, 1], vec[:, 0]
mui_ten(ax, (0, 0), tuple(lon * np.sqrt(gia_tri[1]) * 1.6), XANH, "λ = 2", (4, 4))
mui_ten(ax, (0, 0), tuple(nho * np.sqrt(gia_tri[0]) * 1.6), DO, "λ = 0,5", (-50, 4))
ax.set_xlim(-2.3, 2.3)
ax.set_ylim(-2.3, 2.3)
ax.set_aspect("equal")
ax.set_xlabel("giờ học (đã trừ trung bình)")
ax.set_ylabel("giờ ngủ (đã trừ trung bình)")
luu(fig, "h2_vector_rieng.svg")
print("Đã vẽ 2 hình vào", OUT)
