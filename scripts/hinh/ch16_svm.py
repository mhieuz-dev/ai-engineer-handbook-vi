"""Chương 16 SVM và kernel: tính lại các con số dùng trong bài và vẽ hình.

Chạy:  .venv/bin/python scripts/hinh/ch16_svm.py
Kết quả: các file SVG trong public/hinh/ch16/. Con số nào trong bài sai thì một câu assert báo lỗi.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
from matplotlib.colors import ListedColormap
from sklearn.datasets import make_moons
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC

GOC = Path(__file__).resolve().parents[2]
OUT = GOC / "public" / "hinh" / "ch16"
OUT.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- 1. tám điểm tách được (Bảng 16.1)
X = np.array([[1, 1], [2, 1], [1, 2], [2, 3], [4, 4], [5, 4], [4, 5], [5, 6]], float)
y = np.array([0, 0, 0, 0, 1, 1, 1, 1])
cung = SVC(kernel="linear", C=1e6).fit(X, y)
assert np.allclose(cung.coef_[0], [0.8, 0.4]) and np.isclose(cung.intercept_[0], -3.8)
assert cung.support_.tolist() == [3, 4] and np.isclose(2 / np.linalg.norm(cung.coef_[0]), np.sqrt(5))

# ---------------------------------------------------------------- 2. thêm một điểm lạc (3,2; 3,6) nhãn 0
X2 = np.vstack([X, [[3.2, 3.6]]])
y2 = np.append(y, 0)
mem = {C: SVC(kernel="linear", C=C).fit(X2, y2) for C in (1000, 1, 0.1)}
assert np.allclose(mem[1000].coef_[0], [2, 1]) and mem[1000].score(X2, y2) == 1
assert np.allclose(mem[1].coef_[0], [0.8, 0.4]) and round(mem[1].score(X2, y2), 4) == 0.8889

# ---------------------------------------------------------------- 3. hai vầng trăng với kernel RBF
Xm, ym = make_moons(300, noise=0.3, random_state=0)
a, b, c, e = train_test_split(Xm, ym, test_size=0.3, random_state=0)
rbf = {g: SVC(kernel="rbf", gamma=g).fit(a, c) for g in (0.1, 1, 100)}
assert round(rbf[1].score(b, e), 4) == 0.9444 and round(rbf[100].score(a, c), 4) == 0.9857

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
    "savefig.bbox": "tight", "svg.hashsalt": "ch16",
})


def luu(fig, ten):
    fig.savefig(OUT / ten, metadata={"Date": None})  # bỏ ngày giờ để file không đổi giữa các lần chạy
    plt.close(fig)


def ve_le(ax, m, Xd, yd, gioi=(0, 6.5)):
    """Vẽ điểm, đường quyết định (đậm) và hai đường lề (đứt), khoanh vector hỗ trợ."""
    xx, yy = np.meshgrid(np.linspace(*gioi, 200), np.linspace(*gioi, 200))
    zz = m.decision_function(np.c_[xx.ravel(), yy.ravel()]).reshape(xx.shape)
    ax.contour(xx, yy, zz, levels=[-1, 0, 1], colors=[XAM, CHU, XAM], linestyles=["--", "-", "--"], linewidths=[1.3, 2, 1.3])
    ax.scatter(Xd[yd == 1, 0], Xd[yd == 1, 1], s=70, color=XANH, zorder=3)
    ax.scatter(Xd[yd == 0, 0], Xd[yd == 0, 1], s=70, color=DO, marker="s", zorder=3)
    sv = Xd[m.support_]
    ax.scatter(sv[:, 0], sv[:, 1], s=260, facecolors="none", edgecolors=CAM, linewidths=2, zorder=4)
    ax.set_xlim(*gioi)
    ax.set_ylim(*gioi)
    ax.set_aspect("equal")


# Hình 16.1: lề cứng trên tám điểm
fig, ax = plt.subplots(figsize=(5.2, 5.0))
ve_le(ax, cung, X, y)
ax.annotate("lề rộng √5 ≈ 2,24", (3.2, 3.6), xytext=(3.6, 1.2), fontsize=11, arrowprops=dict(arrowstyle="-", color=XAM))
ax.set_xlabel("đặc trưng 1")
ax.set_ylabel("đặc trưng 2")
luu(fig, "h1_le_cuc_dai.svg")

# Hình 16.2: ba mức C với một điểm lạc
fig, truc = plt.subplots(1, 3, figsize=(11.4, 4.0), sharey=True)
for ax, C in zip(truc, (1000, 1, 0.1)):
    m = mem[C]
    ve_le(ax, m, X2, y2)
    ax.set_title(f"C = {C:g}: lề {2 / np.linalg.norm(m.coef_[0]):.2f}, đúng {m.score(X2, y2):.0%}".replace(".", ","), fontsize=12)
    ax.set_xlabel("đặc trưng 1")
truc[0].set_ylabel("đặc trưng 2")
luu(fig, "h2_le_mem.svg")

# Hình 16.3: kernel RBF với ba giá trị gamma
nen = ListedColormap(["#F6DAD5", "#D6E4F0"])
xx, yy = np.meshgrid(np.linspace(-2, 3, 300), np.linspace(-1.6, 2.1, 300))
fig, truc = plt.subplots(1, 3, figsize=(11.4, 3.7), sharey=True)
for ax, g in zip(truc, (0.1, 1, 100)):
    m = rbf[g]
    zz = m.predict(np.c_[xx.ravel(), yy.ravel()]).reshape(xx.shape)
    ax.contourf(xx, yy, zz, levels=[-0.5, 0.5, 1.5], cmap=nen)
    ax.scatter(a[c == 1, 0], a[c == 1, 1], s=12, color=XANH)
    ax.scatter(a[c == 0, 0], a[c == 0, 1], s=12, color=DO)
    ax.set_title(f"γ = {g:g}: train {m.score(a, c):.0%}, test {m.score(b, e):.0%}".replace(".", ","), fontsize=12)
    ax.set_xlabel("đặc trưng 1")
    ax.grid(False)
truc[0].set_ylabel("đặc trưng 2")
luu(fig, "h3_rbf_gamma.svg")
print("Đã vẽ 3 hình vào", OUT)
