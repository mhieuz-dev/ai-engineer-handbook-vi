"""Chương 27 CNN: tính lại các con số dùng trong bài và vẽ hình.

Chạy:  .venv/bin/python scripts/hinh/ch27_cnn.py
Kết quả: các file SVG trong public/hinh/ch27/. Con số nào trong bài sai thì một câu assert báo lỗi.
MNIST tải về ~/.cache/mnist (khoảng 10 MB, lần đầu), không nằm trong repo.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch
import torch.nn as nn
from matplotlib import font_manager
from torch.utils.data import DataLoader, TensorDataset
from torchvision import datasets

GOC = Path(__file__).resolve().parents[2]
OUT = GOC / "public" / "hinh" / "ch27"
OUT.mkdir(parents=True, exist_ok=True)
DATA = Path.home() / ".cache" / "mnist"

# ---------------------------------------------------------------- 1. tích chập bằng tay, y hệt trang 1
anh = np.zeros((6, 6))
anh[:, 3:] = 1
k = np.array([[-1, 0, 1]] * 3)
ra = np.array([[(anh[i:i + 3, j:j + 3] * k).sum() for j in range(4)] for i in range(4)])
assert ra.tolist() == [[0, 3, 3, 0]] * 4

# ---------------------------------------------------------------- 2. CNN trên MNIST, y hệt trang 2 và 3
tr = datasets.MNIST(DATA, train=True, download=True)
te = datasets.MNIST(DATA, train=False, download=True)
Xtr, ytr = tr.data.float().div(255).unsqueeze(1), tr.targets
Xte, yte = te.data.float().div(255).unsqueeze(1), te.targets
torch.manual_seed(0)
cnn = nn.Sequential(nn.Conv2d(1, 16, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
                    nn.Conv2d(16, 32, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
                    nn.Flatten(), nn.Linear(32 * 7 * 7, 10))
torch.manual_seed(1)
dl = DataLoader(TensorDataset(Xtr, ytr), batch_size=64, shuffle=True)
opt = torch.optim.Adam(cnn.parameters(), lr=1e-3)
ce = nn.CrossEntropyLoss()
for ep in range(2):
    cnn.train()
    for xb, yb in dl:
        opt.zero_grad()
        ce(cnn(xb), yb).backward()
        opt.step()
cnn.eval()
with torch.no_grad():
    assert round((cnn(Xte).argmax(1) == yte).float().mean().item(), 4) == 0.9817
    W = cnn[0].weight[:, 0].numpy()                      # 16 bộ lọc 3x3
    so = Xte[0:1]                                        # ảnh test đầu tiên
    ban_do = cnn[1](cnn[0](so))[0].numpy()               # 16 bản đồ đặc trưng sau ReLU
assert int(yte[0]) == 7

# ---------------------------------------------------------------- vẽ hình
NEN = "#FBF8F1"
XANH, CAM, DO, XAM, CHU, LUOI = "#1F5F8B", "#E07A1F", "#C0392B", "#8A8170", "#2B2B2B", "#E6DECD"
co_sans = {f.name for f in font_manager.fontManager.ttflist}
FONT = "Be Vietnam Pro" if "Be Vietnam Pro" in co_sans else "DejaVu Sans"
plt.rcParams.update({
    "font.family": FONT, "font.size": 12.5, "text.color": CHU,
    "figure.facecolor": NEN, "axes.facecolor": NEN, "savefig.facecolor": NEN,
    "savefig.bbox": "tight", "svg.hashsalt": "ch27",
})
META = {"Date": None}


def luoi_so(ax, M, tieu_de, cmap, vmin, vmax, khung=None):
    ax.imshow(M, cmap=cmap, vmin=vmin, vmax=vmax)
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            v = M[i, j]
            sang = (v - vmin) / (vmax - vmin) > 0.55
            ax.text(j, i, f"{v:g}", ha="center", va="center", fontsize=12, color=NEN if sang else CHU)
    ax.set_xticks(np.arange(-0.5, M.shape[1]), minor=True)
    ax.set_yticks(np.arange(-0.5, M.shape[0]), minor=True)
    ax.grid(which="minor", color=XAM, lw=0.8)
    ax.tick_params(which="both", length=0, labelbottom=False, labelleft=False)
    for s in ax.spines.values():
        s.set_visible(False)
    if khung:
        r, c, n = khung
        ax.add_patch(plt.Rectangle((c - 0.5, r - 0.5), n, n, fill=False, ec=CAM, lw=3))
    ax.set_title(tieu_de, fontsize=13)


# hình 27.1: ảnh 6x6, bộ lọc, kết quả
fig, axs = plt.subplots(1, 3, figsize=(10, 3.6), gridspec_kw={"width_ratios": [6, 3, 4]})
luoi_so(axs[0], anh, "Ảnh 6×6", "Blues", 0, 1.6, khung=(0, 1, 3))
luoi_so(axs[1], k, "Bộ lọc 3×3", "RdBu", -2, 2)
luoi_so(axs[2], ra, "Kết quả 4×4", "Oranges", 0, 4, khung=(0, 1, 1))
fig.savefig(OUT / "h1_tich_chap.svg", metadata=META)
plt.close(fig)

# hình 27.2: 16 bộ lọc đã học và 16 bản đồ đặc trưng của một chữ số 7
fig = plt.figure(figsize=(10, 5.2))
g = fig.add_gridspec(4, 9, width_ratios=[2.2] + [1] * 8, hspace=0.35, wspace=0.15)
ax = fig.add_subplot(g[1:3, 0])
ax.imshow(so[0, 0].numpy(), cmap="Greys")
ax.set_title("Ảnh vào", fontsize=12)
ax.axis("off")
m = np.abs(W).max()
for i in range(16):
    ax = fig.add_subplot(g[(i // 8) * 2, 1 + i % 8])
    ax.imshow(W[i], cmap="RdBu_r", vmin=-m, vmax=m)
    ax.set_title(f"{i + 1}", fontsize=10, color=XAM)
    ax.axis("off")
    ax = fig.add_subplot(g[(i // 8) * 2 + 1, 1 + i % 8])
    ax.imshow(ban_do[i], cmap="magma")
    ax.axis("off")
fig.savefig(OUT / "h2_bo_loc.svg", metadata=META)
plt.close(fig)
print("OK")
