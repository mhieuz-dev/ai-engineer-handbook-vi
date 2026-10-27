"""Chương 18 Ensemble: tính lại các con số dùng trong bài và vẽ hình.

Chạy:  .venv/bin/python scripts/hinh/ch18_ensemble.py
Kết quả: các file SVG trong public/hinh/ch18/. Con số nào trong bài sai thì một câu assert báo lỗi.
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
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor

GOC = Path(__file__).resolve().parents[2]
OUT = GOC / "public" / "hinh" / "ch18"
OUT.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- 1. hai vầng trăng
Xm, ym = make_moons(300, noise=0.3, random_state=0)
a, b, c, e = train_test_split(Xm, ym, test_size=0.3, random_state=0)
mo_hinh = {
    "một cây": DecisionTreeClassifier(random_state=0).fit(a, c),
    "random forest 100 cây": RandomForestClassifier(n_estimators=100, random_state=0).fit(a, c),
    "gradient boosting": GradientBoostingClassifier(random_state=0).fit(a, c),
}
assert [round(m.score(b, e), 4) for m in mo_hinh.values()] == [0.8444, 0.9333, 0.9]

# ---------------------------------------------------------------- 2. boosting tay trên 10 bạn: giờ học -> điểm
gio = np.array([1, 2, 3, 4, 5, 2, 6, 3, 7, 4.0])
diem = np.array([2, 4, 5, 7, 6, 3.5, 8.5, 4, 9, 6.5])
X = gio[:, None]
f = np.full(10, diem.mean())
buoc = [f.copy()]
for _ in range(10):
    goc = DecisionTreeRegressor(max_depth=1).fit(X, diem - f)       # gốc cây khớp phần dư
    f = f + 0.5 * goc.predict(X)
    buoc.append(f.copy())
mse = [round(float(np.mean((diem - v) ** 2)), 4) for v in buoc]
assert mse[:4] == [4.5725, 2.0056, 1.0352, 0.5787]

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
    "savefig.bbox": "tight", "svg.hashsalt": "ch18",
})
PHAY = FuncFormatter(lambda v, _: f"{v:g}".replace(".", ","))


def luu(fig, ten):
    fig.savefig(OUT / ten, metadata={"Date": None})  # bỏ ngày giờ để file không đổi giữa các lần chạy
    plt.close(fig)


# Hình 18.1: một cây, random forest, gradient boosting
nen = ListedColormap(["#F6DAD5", "#D6E4F0"])
xx, yy = np.meshgrid(np.linspace(-2, 3, 300), np.linspace(-1.6, 2.1, 300))
fig, truc = plt.subplots(1, 3, figsize=(11.4, 3.7), sharey=True)
for ax, (ten, m) in zip(truc, mo_hinh.items()):
    zz = m.predict_proba(np.c_[xx.ravel(), yy.ravel()])[:, 1].reshape(xx.shape)
    ax.contourf(xx, yy, zz, levels=np.linspace(0, 1, 11), cmap="RdBu", alpha=0.32)
    ax.contour(xx, yy, zz, levels=[0.5], colors=CHU, linewidths=1.4)
    ax.scatter(a[c == 1, 0], a[c == 1, 1], s=10, color=XANH)
    ax.scatter(a[c == 0, 0], a[c == 0, 1], s=10, color=DO)
    ax.set_title(f"{ten}: test {m.score(b, e):.0%}", fontsize=12)
    ax.set_xlabel("đặc trưng 1")
    ax.grid(False)
truc[0].set_ylabel("đặc trưng 2")
luu(fig, "h1_ba_mo_hinh.svg")

# Hình 18.2: dự đoán của boosting sau 0, 1, 3, 10 vòng
fig, ax = plt.subplots(figsize=(6.8, 4.0))
t = np.linspace(0.5, 7.5, 400)[:, None]
f_t = np.full(len(t), diem.mean())
ve = {0: f_t.copy()}
ft = np.full(10, diem.mean())
for k in range(1, 11):
    goc = DecisionTreeRegressor(max_depth=1).fit(X, diem - ft)
    ft = ft + 0.5 * goc.predict(X)
    f_t = f_t + 0.5 * goc.predict(t)
    if k in (1, 3, 10):
        ve[k] = f_t.copy()
for (k, v), mau in zip(ve.items(), (XAM, CAM, XANH, DO)):
    ax.step(t[:, 0], v, where="mid", color=mau, lw=1.8, label=f"sau {k} vòng: MSE {mse[k]:g}".replace(".", ","))
ax.scatter(gio, diem, s=60, color=CHU, zorder=4)
ax.set_xlabel("Giờ tự học mỗi tuần")
ax.set_ylabel("Điểm thi")
ax.yaxis.set_major_formatter(PHAY)
ax.legend(loc="upper left", fontsize=10.5, facecolor=NEN, edgecolor=LUOI, framealpha=1)
luu(fig, "h2_boosting.svg")
print("Đã vẽ 2 hình vào", OUT)
