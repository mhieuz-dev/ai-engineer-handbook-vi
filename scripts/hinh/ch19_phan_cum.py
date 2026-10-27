"""Chương 19 Phân cụm: tính lại các con số dùng trong bài và vẽ hình.

Chạy:  .venv/bin/python scripts/hinh/ch19_phan_cum.py
Kết quả: các file SVG trong public/hinh/ch19/. Con số nào trong bài sai thì một câu assert báo lỗi.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
from matplotlib.ticker import FuncFormatter
from sklearn.cluster import DBSCAN, KMeans
from sklearn.datasets import make_blobs, make_moons
from sklearn.metrics import adjusted_rand_score, silhouette_score

GOC = Path(__file__).resolve().parents[2]
OUT = GOC / "public" / "hinh" / "ch19"
OUT.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- 1. bảy điểm, k-means tay với tâm khởi đầu (1; 1) và (5; 7)
P = np.array([[1, 1], [1.5, 2], [3, 4], [5, 7], [3.5, 5], [4.5, 5], [3.5, 4.5]], float)
tam = P[[0, 3]].copy()
lich_su = [(tam.copy(), None)]
for _ in range(3):
    nhan = ((P[:, None, :] - tam[None]) ** 2).sum(axis=2).argmin(axis=1)
    tam = np.array([P[nhan == k].mean(axis=0) for k in range(2)])
    lich_su.append((tam.copy(), nhan))
assert lich_su[1][1].tolist() == [0, 0, 0, 1, 1, 1, 1] and np.allclose(lich_su[1][0], [[11 / 6, 7 / 3], [4.125, 5.375]])
assert lich_su[2][1].tolist() == [0, 0, 1, 1, 1, 1, 1] and np.allclose(lich_su[2][0], [[1.25, 1.5], [3.9, 5.1]])
quan_tinh = sum(((P[lich_su[2][1] == k] - lich_su[2][0][k]) ** 2).sum() for k in range(2))
assert np.isclose(quan_tinh, 8.525)

# ---------------------------------------------------------------- 2. bốn đám điểm: elbow và silhouette
Xb, yb = make_blobs(n_samples=300, centers=4, cluster_std=0.8, random_state=0)
ks = list(range(1, 9))
qt = [KMeans(k, n_init=10, random_state=0).fit(Xb).inertia_ for k in ks]
sil = [silhouette_score(Xb, KMeans(k, n_init=10, random_state=0).fit(Xb).labels_) for k in ks[1:]]
assert round(qt[3], 1) == 369.5 and round(max(sil), 4) == 0.5801 and int(np.argmax(sil)) + 2 == 4

# ---------------------------------------------------------------- 3. hai vầng trăng: k-means và DBSCAN
Xm, ym = make_moons(300, noise=0.06, random_state=0)
km = KMeans(2, n_init=10, random_state=0).fit_predict(Xm)
db = DBSCAN(eps=0.2, min_samples=5).fit_predict(Xm)
assert round(adjusted_rand_score(ym, km), 4) == 0.2343 and adjusted_rand_score(ym, db) == 1.0

# ---------------------------------------------------------------- vẽ hình (bảng màu Chương 10)
NEN = "#FBF8F1"
XANH, CAM, DO, XAM, CHU, LUOI = "#1F5F8B", "#E07A1F", "#C0392B", "#8A8170", "#2B2B2B", "#E6DECD"
LUC, TIM = "#2E8B57", "#7B5EA7"
co_sans = {f.name for f in font_manager.fontManager.ttflist}
FONT = "Be Vietnam Pro" if "Be Vietnam Pro" in co_sans else "DejaVu Sans"
plt.rcParams.update({
    "font.family": FONT, "font.size": 12.5, "mathtext.fontset": "dejavusans",
    "text.color": CHU, "axes.labelcolor": CHU, "xtick.color": CHU, "ytick.color": CHU,
    "axes.edgecolor": XAM, "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": LUOI, "grid.alpha": 0.8, "axes.axisbelow": True,
    "figure.facecolor": NEN, "axes.facecolor": NEN, "savefig.facecolor": NEN,
    "savefig.bbox": "tight", "svg.hashsalt": "ch19",
})
PHAY = FuncFormatter(lambda v, _: f"{v:g}".replace(".", ","))
MAU = np.array([XANH, CAM, LUC, TIM])


def luu(fig, ten):
    fig.savefig(OUT / ten, metadata={"Date": None})  # bỏ ngày giờ để file không đổi giữa các lần chạy
    plt.close(fig)


# Hình 19.1: ba bước k-means
fig, truc = plt.subplots(1, 3, figsize=(11.0, 3.9), sharey=True)
for ax, (i, ten) in zip(truc, ((0, "bước 0: hai tâm khởi đầu"), (1, "vòng 1: gán rồi dời tâm"), (2, "vòng 2: hội tụ"))):
    tam_cu = lich_su[i][0] if i == 0 else lich_su[i - 1][0]
    nhan = lich_su[i][1]
    ax.scatter(P[:, 0], P[:, 1], s=80, color=XAM if nhan is None else MAU[nhan], zorder=3)
    ax.scatter(tam_cu[:, 0], tam_cu[:, 1], s=220, marker="X", color=CHU, zorder=4, label="tâm dùng để gán")
    if i > 0:
        ax.scatter(lich_su[i][0][:, 0], lich_su[i][0][:, 1], s=220, marker="X", facecolor="white", edgecolor=CHU, lw=1.5, zorder=5, label="tâm mới")
    ax.set_title(ten, fontsize=12)
    ax.set_xlim(0, 6)
    ax.set_ylim(0, 8)
    ax.set_aspect("equal")
    ax.set_xlabel("x₁")
truc[0].set_ylabel("x₂")
truc[1].legend(loc="upper left", fontsize=9.5, facecolor=NEN, edgecolor=LUOI, framealpha=1)
luu(fig, "h1_kmeans_tay.svg")

# Hình 19.2: elbow và silhouette
fig, (trai, phai) = plt.subplots(1, 2, figsize=(10.0, 3.8))
trai.plot(ks, qt, "o-", color=XANH, lw=2)
trai.axvline(4, color=XAM, ls="--", lw=1.2)
trai.set_xlabel("số cụm k")
trai.set_ylabel("inertia")
trai.set_title("Phương pháp khuỷu tay", fontsize=12.5)
phai.plot(ks[1:], sil, "o-", color=CAM, lw=2)
phai.axvline(4, color=XAM, ls="--", lw=1.2)
phai.set_xlabel("số cụm k")
phai.set_ylabel("silhouette trung bình")
phai.yaxis.set_major_formatter(PHAY)
phai.set_title("Hệ số silhouette", fontsize=12.5)
luu(fig, "h2_chon_k.svg")

# Hình 19.3: k-means và DBSCAN trên hai vầng trăng
fig, (trai, phai) = plt.subplots(1, 2, figsize=(10.0, 3.9), sharey=True)
for ax, nhan, ten in ((trai, km, "k-means, k = 2"), (phai, db, "DBSCAN, eps = 0,2")):
    ax.scatter(Xm[:, 0], Xm[:, 1], s=14, color=MAU[nhan])
    ax.set_title(f"{ten}: ARI {adjusted_rand_score(ym, nhan):.2f}".replace(".", ","), fontsize=12)
    ax.set_xlabel("x₁")
trai.set_ylabel("x₂")
luu(fig, "h3_kmeans_dbscan.svg")
print("Đã vẽ 3 hình vào", OUT)
