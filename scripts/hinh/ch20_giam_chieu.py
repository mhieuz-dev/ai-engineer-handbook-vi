"""Chương 20 Giảm chiều: tính lại các con số dùng trong bài và vẽ hình.

Chạy:  .venv/bin/python scripts/hinh/ch20_giam_chieu.py
Kết quả: các file SVG trong public/hinh/ch20/. Con số nào trong bài sai thì một câu assert báo lỗi.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
from matplotlib.ticker import FuncFormatter
from sklearn.datasets import load_breast_cancer, load_digits
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.preprocessing import StandardScaler

GOC = Path(__file__).resolve().parents[2]
OUT = GOC / "public" / "hinh" / "ch20"
OUT.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- 1. bốn điểm của Chương 3 và 5
D = np.array([[1, 2], [2, 1], [3, 4], [4, 3]], float)
p2 = PCA(2).fit(D)
assert np.allclose(np.abs(p2.components_), 0.7071, atol=1e-4) and np.allclose(p2.explained_variance_ratio_, [0.8, 0.2])
p1 = PCA(1).fit(D)
z = p1.transform(D)
tai = p1.inverse_transform(z)
assert np.allclose(np.abs(z.ravel()), np.sqrt(2)) and np.allclose(tai, [[1.5, 1.5], [1.5, 1.5], [3.5, 3.5], [3.5, 3.5]])

# ---------------------------------------------------------------- 2. phương sai tích lũy
Xb = StandardScaler().fit_transform(load_breast_cancer().data)
cb = np.cumsum(PCA().fit(Xb).explained_variance_ratio_)
dg = load_digits()
cd = np.cumsum(PCA().fit(dg.data).explained_variance_ratio_)
assert int(np.argmax(cb >= 0.95)) + 1 == 10 and int(np.argmax(cd >= 0.9)) + 1 == 21

# ---------------------------------------------------------------- 3. chữ số viết tay trong 2 chiều
P2 = PCA(2).fit_transform(dg.data)
E2 = TSNE(2, random_state=0, init="pca", perplexity=30).fit_transform(dg.data)

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
    "savefig.bbox": "tight", "svg.hashsalt": "ch20",
})
PHAY = FuncFormatter(lambda v, _: f"{v:g}".replace(".", ","))


def luu(fig, ten):
    fig.savefig(OUT / ten, metadata={"Date": None})  # bỏ ngày giờ để file không đổi giữa các lần chạy
    plt.close(fig)


# Hình 20.1: chiếu bốn điểm lên thành phần chính thứ nhất
fig, ax = plt.subplots(figsize=(5.0, 5.0))
t = np.linspace(-0.5, 5.5, 2)
ax.plot(t, t, color=XANH, lw=2, label="thành phần chính 1")
for (a, b), (u, v), ten in zip(D, tai, "ABCD"):
    ax.plot([a, u], [b, v], color=DO, ls="--", lw=1.3)
    ax.annotate(ten, (a, b), xytext=(6, 4), textcoords="offset points", fontsize=11.5)
ax.scatter(D[:, 0], D[:, 1], s=80, color=CAM, zorder=3, label="điểm gốc")
ax.scatter(tai[:, 0], tai[:, 1], s=60, facecolor="white", edgecolor=XANH, lw=1.8, zorder=4, label="hình chiếu")
ax.plot(2.5, 2.5, "+", color=CHU, ms=14, mew=2)
ax.set_xlim(0, 5)
ax.set_ylim(0, 5)
ax.set_aspect("equal")
ax.set_xlabel("giờ học")
ax.set_ylabel("giờ ngủ")
ax.legend(loc="upper left", fontsize=10, facecolor=NEN, edgecolor=LUOI, framealpha=1)
luu(fig, "h1_chieu.svg")

# Hình 20.2: phương sai tích lũy
fig, ax = plt.subplots(figsize=(6.8, 3.9))
ax.plot(range(1, 31), cb, "o-", ms=3.5, color=DO, lw=1.8, label="ung thư vú (30 đặc trưng, đã chuẩn hóa)")
ax.plot(range(1, 65), cd, "o-", ms=3, color=XANH, lw=1.8, label="chữ số viết tay (64 điểm ảnh)")
for muc in (0.9, 0.95):
    ax.axhline(muc, color=XAM, ls=":", lw=1)
ax.set_xlabel("số thành phần chính giữ lại")
ax.set_ylabel("tỷ lệ phương sai tích lũy")
ax.yaxis.set_major_formatter(PHAY)
ax.set_ylim(0, 1.02)
ax.legend(loc="lower right", fontsize=10.5, facecolor=NEN, edgecolor=LUOI, framealpha=1)
luu(fig, "h2_phuong_sai.svg")

# Hình 20.3: chữ số trong 2 chiều, PCA và t-SNE
cmap = plt.get_cmap("tab10")
fig, (trai, phai) = plt.subplots(1, 2, figsize=(10.4, 4.6))
for ax, Z, ten in ((trai, P2, "PCA 2 chiều"), (phai, E2, "t-SNE 2 chiều")):
    ax.scatter(Z[:, 0], Z[:, 1], c=dg.target, cmap=cmap, s=6, alpha=0.8)
    for so in range(10):
        tx, ty = np.median(Z[dg.target == so], axis=0)
        ax.text(tx, ty, str(so), fontsize=15, weight="bold", ha="center", va="center",
                bbox=dict(boxstyle="round,pad=0.15", fc="white", ec=cmap(so), alpha=0.85))
    ax.set_title(ten, fontsize=12.5)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.grid(False)
luu(fig, "h3_pca_tsne.svg")

# Hình 20.4: tái tạo một chữ số từ 2, 10, 40 thành phần
fig, truc = plt.subplots(1, 4, figsize=(8.0, 2.4))
anh = dg.data[0]
for ax, k in zip(truc, (None, 2, 10, 40)):
    if k is None:
        hien, ten = anh, "gốc, 64 số"
    else:
        q = PCA(k).fit(dg.data)
        hien, ten = q.inverse_transform(q.transform(anh[None]))[0], f"{k} thành phần"
    ax.imshow(hien.reshape(8, 8), cmap="gray_r", vmin=0, vmax=16)
    ax.set_title(ten, fontsize=11)
    ax.axis("off")
luu(fig, "h4_tai_tao.svg")
print("Đã vẽ 4 hình vào", OUT)
