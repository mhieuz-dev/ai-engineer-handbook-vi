"""Chương 30 Autoencoder và VAE: huấn luyện lại các mô hình của trang 1, 3, 4 và vẽ hình 30.1, 30.2.

Chạy:  .venv/bin/python scripts/hinh/ch30_vae.py      (khoảng 3 phút trên CPU 16 nhân)
Kết quả: public/hinh/ch30/h1_khong_gian_an.svg, h2_sinh_anh.svg. MNIST tải về ~/.cache/mnist (lần đầu).
Con số nào trong bài sai thì một câu assert báo lỗi.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from matplotlib import font_manager
from torch.utils.data import DataLoader, TensorDataset
from torchvision import datasets

GOC = Path(__file__).resolve().parents[2]
OUT = GOC / "public" / "hinh" / "ch30"
OUT.mkdir(parents=True, exist_ok=True)
DATA = Path.home() / ".cache" / "mnist"

# ---------------------------------------------------------------- dữ liệu và mô hình, y hệt các trang
tr = datasets.MNIST(DATA, train=True, download=True)
te = datasets.MNIST(DATA, train=False, download=True)
Xtr = tr.data.float().div(255).view(-1, 784)
Xte = te.data.float().div(255).view(-1, 784)
ytr, yte = tr.targets, te.targets


def tao_ae(k):
    ma_hoa = nn.Sequential(nn.Linear(784, 256), nn.ReLU(), nn.Linear(256, k))
    giai_ma = nn.Sequential(nn.Linear(k, 256), nn.ReLU(), nn.Linear(256, 784), nn.Sigmoid())
    return ma_hoa, giai_ma


def huan_luyen_ae(ma_hoa, giai_ma, so_epoch=5, nhieu=0.0):
    torch.manual_seed(1)
    dl = DataLoader(TensorDataset(Xtr), batch_size=128, shuffle=True)
    opt = torch.optim.Adam([*ma_hoa.parameters(), *giai_ma.parameters()], lr=1e-3)
    for ep in range(so_epoch):
        for (xb,) in dl:
            vao = (xb + nhieu * torch.randn_like(xb)).clamp(0, 1)
            loss = ((giai_ma(ma_hoa(vao)) - xb) ** 2).mean()
            opt.zero_grad()
            loss.backward()
            opt.step()
    with torch.no_grad():
        return round(((giai_ma(ma_hoa(Xte)) - Xte) ** 2).mean().item(), 4)


class VAE(nn.Module):
    def __init__(self, k, bien_phan=True):
        super().__init__()
        self.ma_hoa = nn.Sequential(nn.Linear(784, 256), nn.ReLU())
        self.mu = nn.Linear(256, k)
        self.log_var = nn.Linear(256, k)
        self.giai_ma = nn.Sequential(nn.Linear(k, 256), nn.ReLU(), nn.Linear(256, 784))
        self.bien_phan = bien_phan

    def forward(self, x):
        h = self.ma_hoa(x)
        mu, log_var = self.mu(h), self.log_var(h)
        z = mu + torch.exp(0.5 * log_var) * torch.randn_like(mu) if self.bien_phan else mu
        return self.giai_ma(z), mu, log_var


def loss_vae(m, x):
    logit, mu, log_var = m(x)
    tai_tao = F.binary_cross_entropy_with_logits(logit, x, reduction="sum") / len(x)
    kl = 0.5 * (log_var.exp() + mu ** 2 - 1 - log_var).sum() / len(x) if m.bien_phan else torch.tensor(0.0)
    return tai_tao, kl


def huan_luyen_vae(m, so_epoch):
    torch.manual_seed(1)
    dl = DataLoader(TensorDataset(Xtr), batch_size=128, shuffle=True)
    opt = torch.optim.Adam(m.parameters(), lr=1e-3)
    for ep in range(so_epoch):
        m.train()
        for (xb,) in dl:
            tai_tao, kl = loss_vae(m, xb)
            opt.zero_grad()
            (tai_tao + kl).backward()
            opt.step()
    m.eval()
    with torch.no_grad():
        tai_tao, kl = loss_vae(m, Xte)
    return round(tai_tao.item(), 1), round(kl.item(), 1)


torch.manual_seed(0)
ma2, giai2 = tao_ae(2)
assert huan_luyen_ae(ma2, giai2) == 0.0451
torch.manual_seed(0)
vae2 = VAE(2)
assert huan_luyen_vae(vae2, 10) == (151.3, 5.6)
with torch.no_grad():
    z_ae2 = ma2(Xte).numpy()
    z_vae2 = vae2.mu(vae2.ma_hoa(Xte)).numpy()

torch.manual_seed(0)
cham = nn.Sequential(nn.Conv2d(1, 16, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
                     nn.Conv2d(16, 32, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
                     nn.Flatten(), nn.Linear(32 * 7 * 7, 10))
torch.manual_seed(1)
opt = torch.optim.Adam(cham.parameters(), lr=1e-3)
for ep in range(2):
    for xb, yb in DataLoader(TensorDataset(Xtr.view(-1, 1, 28, 28), ytr), batch_size=64, shuffle=True):
        opt.zero_grad()
        F.cross_entropy(cham(xb), yb).backward()
        opt.step()
cham.eval()


def cham_diem(anh):
    with torch.no_grad():
        p = cham(anh.view(-1, 1, 28, 28)).softmax(1)
    return round((p.max(1).values > 0.9).float().mean().item(), 3)


torch.manual_seed(0)
ae16 = VAE(16, bien_phan=False)
assert huan_luyen_vae(ae16, 20) == (72.1, 0.0)
torch.manual_seed(0)
vae16 = VAE(16)
assert huan_luyen_vae(vae16, 20) == (82.7, 23.2)
with torch.no_grad():
    z_ae = ae16.mu(ae16.ma_hoa(Xtr))
    z = torch.randn(1000, 16, generator=torch.Generator().manual_seed(0))
    L = torch.linalg.cholesky(torch.cov(z_ae.T))
    anh_ae0 = torch.sigmoid(ae16.giai_ma(z))
    anh_ae_khop = torch.sigmoid(ae16.giai_ma(z @ L.T + z_ae.mean(0)))
    anh_vae = torch.sigmoid(vae16.giai_ma(z))
    diem = [cham_diem(a) for a in (Xte[:1000], anh_ae0, anh_ae_khop, anh_vae)]
    print(diem)
    assert diem == [0.927, 0.007, 0.408, 0.365]
    a, b = int((yte == 3).nonzero()[0]), int((yte == 8).nonzero()[0])   # ảnh số 3 và số 8 đầu tiên của tập test
    mu_a, mu_b = vae16.mu(vae16.ma_hoa(Xte[[a, b]]))
    noi_suy = torch.sigmoid(vae16.giai_ma(torch.stack([(1 - t) * mu_a + t * mu_b for t in np.linspace(0, 1, 10)])))

# ---------------------------------------------------------------- vẽ hình
NEN = "#FBF8F1"
XANH, CAM, DO, XAM, CHU, LUOI = "#1F5F8B", "#E07A1F", "#C0392B", "#8A8170", "#2B2B2B", "#E6DECD"
co_sans = {f.name for f in font_manager.fontManager.ttflist}
FONT = "Be Vietnam Pro" if "Be Vietnam Pro" in co_sans else "DejaVu Sans"
plt.rcParams.update({
    "font.family": FONT, "font.size": 12.5, "text.color": CHU, "axes.labelcolor": CHU,
    "xtick.color": CHU, "ytick.color": CHU, "axes.edgecolor": XAM,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": LUOI, "grid.alpha": 0.8, "axes.axisbelow": True,
    "figure.facecolor": NEN, "axes.facecolor": NEN, "savefig.facecolor": NEN,
    "savefig.bbox": "tight", "svg.hashsalt": "ch30",
})

# Hình 30.1: không gian ẩn 2 chiều của autoencoder và VAE, 3000 ảnh test đầu tiên
cmap = plt.get_cmap("tab10")
nhan = yte[:3000].numpy()
fig, (trai, phai) = plt.subplots(1, 2, figsize=(10.4, 4.8))
for ax, Z, ten in ((trai, z_ae2[:3000], "Autoencoder"), (phai, z_vae2[:3000], "VAE (trung bình mu)")):
    ax.scatter(Z[:, 0], Z[:, 1], c=nhan, cmap=cmap, s=5, alpha=0.75, rasterized=True)
    for so in range(10):
        tx, ty = np.median(Z[nhan == so], axis=0)
        ax.text(tx, ty, str(so), fontsize=14, weight="bold", ha="center", va="center",
                bbox=dict(boxstyle="round,pad=0.15", fc="white", ec=cmap(so), alpha=0.85))
    ax.set_title(ten, fontsize=12.5)
    ax.set_xlabel("z₁")
    ax.set_ylabel("z₂")
phai.add_patch(plt.Circle((0, 0), 2, fill=False, ls="--", color=CHU, lw=1.2))   # 2 độ lệch chuẩn của N(0, I)
phai.set_aspect("equal", adjustable="datalim")
trai.set_aspect("equal", adjustable="datalim")
fig.savefig(OUT / "h1_khong_gian_an.svg", metadata={"Date": None}, dpi=150)

# Hình 30.2: ảnh sinh ra theo ba cách, và nội suy của VAE
hang = [("Ảnh thật", Xte[:10]), ("AE, z ~ N(0, I)", anh_ae0[:10]),
        ("AE, phân phối khớp", anh_ae_khop[:10]), ("VAE, z ~ N(0, I)", anh_vae[:10]),
        ("VAE, nội suy 3 → 8", noi_suy)]
fig, axs = plt.subplots(len(hang), 10, figsize=(10.4, 5.9))
for r, (ten, anh) in enumerate(hang):
    for c in range(10):
        ax = axs[r, c]
        ax.imshow(anh[c].view(28, 28).numpy(), cmap="Greys", vmin=0, vmax=1)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.grid(False)
        for s in ax.spines.values():
            s.set_visible(False)
    axs[r, 0].set_ylabel(ten, rotation=0, ha="right", va="center", fontsize=11.5)
fig.subplots_adjust(wspace=0.05, hspace=0.12)
fig.savefig(OUT / "h2_sinh_anh.svg", metadata={"Date": None}, dpi=150)
print("OK")
