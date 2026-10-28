"""Chương 31 GAN và Diffusion: huấn luyện lại GAN (trang 1) và mô hình diffusion (trang 4), vẽ hình 31.1 tới 31.3.

Chạy:  .venv/bin/python scripts/hinh/ch31_gan_diffusion.py      (khoảng 6 phút trên CPU 16 nhân)
Kết quả: public/hinh/ch31/h1_gan_theo_epoch.svg, h2_them_nhieu.svg, h3_sinh_anh.svg. MNIST tải về ~/.cache/mnist.
Con số nào trong bài sai thì một câu assert báo lỗi.
"""
import math
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
OUT = GOC / "public" / "hinh" / "ch31"
OUT.mkdir(parents=True, exist_ok=True)
DATA = Path.home() / ".cache" / "mnist"

# ---------------------------------------------------------------- dữ liệu và bộ chấm, y hệt trang 1
tr = datasets.MNIST(DATA, train=True, download=True)
te = datasets.MNIST(DATA, train=False, download=True)
Xtr = tr.data.float().div(255).view(-1, 784)
Xte = te.data.float().div(255).view(-1, 784)
ytr, yte = tr.targets, te.targets
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
    return round((p.max(1).values > 0.9).float().mean().item(), 3), torch.bincount(p.argmax(1), minlength=10).tolist()


# ---------------------------------------------------------------- GAN, y hệt trang 1
Z = 64
torch.manual_seed(0)
G = nn.Sequential(nn.Linear(Z, 256), nn.LeakyReLU(0.2), nn.Linear(256, 512), nn.LeakyReLU(0.2),
                  nn.Linear(512, 784), nn.Tanh())
D = nn.Sequential(nn.Linear(784, 512), nn.LeakyReLU(0.2), nn.Linear(512, 256), nn.LeakyReLU(0.2),
                  nn.Linear(256, 1))
opt_G = torch.optim.Adam(G.parameters(), lr=2e-4, betas=(0.5, 0.999))
opt_D = torch.optim.Adam(D.parameters(), lr=2e-4, betas=(0.5, 0.999))
torch.manual_seed(1)
dl = DataLoader(TensorDataset(Xtr * 2 - 1), batch_size=128, shuffle=True)
z_co_dinh = torch.randn(1000, Z, generator=torch.Generator().manual_seed(0))
mot, khong = torch.ones(128, 1), torch.zeros(128, 1)
theo_epoch = []
for ep in range(20):
    for (that,) in dl:
        n = len(that)
        gia = G(torch.randn(n, Z))
        loss_D = F.binary_cross_entropy_with_logits(D(that), mot[:n]) + F.binary_cross_entropy_with_logits(D(gia.detach()), khong[:n])
        opt_D.zero_grad()
        loss_D.backward()
        opt_D.step()
        loss_G = F.binary_cross_entropy_with_logits(D(gia), mot[:n])
        opt_G.zero_grad()
        loss_G.backward()
        opt_G.step()
    with torch.no_grad():
        theo_epoch.append(cham_diem((G(z_co_dinh) + 1) / 2))
print(theo_epoch[-1])
assert theo_epoch[0] == (0.0, [0, 2, 1, 93, 0, 0, 0, 0, 904, 0])
assert theo_epoch[-1] == (0.47, [19, 138, 135, 132, 110, 71, 33, 168, 128, 66])
with torch.no_grad():
    anh_gan = (G(z_co_dinh) + 1) / 2

# ---------------------------------------------------------------- diffusion, y hệt trang 3 và 4
T = 1000
beta = torch.linspace(1e-4, 0.02, T)
alpha = 1 - beta
ab = torch.cumprod(alpha, dim=0)


def them_nhieu(x0, t, eps):
    a = ab[t].view(-1, *[1] * (x0.dim() - 1))
    return a.sqrt() * x0 + (1 - a).sqrt() * eps


def nhung_t(t, d=32):
    f = torch.exp(-math.log(10000) * torch.arange(d // 2) / (d // 2))
    a = t.float()[:, None] * f[None]
    return torch.cat([a.sin(), a.cos()], dim=1)


class KhuNhieu(nn.Module):
    def __init__(self, c=32):
        super().__init__()
        self.t1 = nn.Sequential(nn.Linear(32, c), nn.SiLU(), nn.Linear(c, c))
        self.vao = nn.Conv2d(1, c, 3, padding=1)
        self.k1 = nn.Sequential(nn.SiLU(), nn.Conv2d(c, c, 3, padding=1))
        self.xuong = nn.Conv2d(c, c, 4, stride=2, padding=1)
        self.k2 = nn.Sequential(nn.SiLU(), nn.Conv2d(c, c, 3, padding=1), nn.SiLU(), nn.Conv2d(c, c, 3, padding=1))
        self.len = nn.ConvTranspose2d(c, c, 4, stride=2, padding=1)
        self.ra = nn.Sequential(nn.SiLU(), nn.Conv2d(2 * c, c, 3, padding=1), nn.SiLU(), nn.Conv2d(c, 1, 3, padding=1))

    def forward(self, x, t):
        e = self.t1(nhung_t(t))[:, :, None, None]
        h1 = self.k1(self.vao(x) + e)
        h2 = self.xuong(h1)
        h2 = h2 + self.k2(h2 + e)
        return self.ra(torch.cat([self.len(h2), h1], dim=1))


torch.manual_seed(0)
khu = KhuNhieu()
opt = torch.optim.Adam(khu.parameters(), lr=1e-3)
torch.manual_seed(1)
dl = DataLoader(TensorDataset((Xtr * 2 - 1).view(-1, 1, 28, 28)), batch_size=128, shuffle=True)
for ep in range(3):
    khu.train()
    for (x0,) in dl:
        t = torch.randint(0, T, (len(x0),))
        eps = torch.randn_like(x0)
        loss = F.mse_loss(khu(them_nhieu(x0, t, eps), t), eps)
        opt.zero_grad()
        loss.backward()
        opt.step()
khu.eval()
assert round(loss.item(), 4) == 0.0327


@torch.no_grad()
def sinh(n, so_buoc=25, seed=0, ghi=False):
    g = torch.Generator().manual_seed(seed)
    x = torch.randn(n, 1, 28, 28, generator=g)
    cac_t = torch.linspace(T - 1, 0, so_buoc).long()
    vet = []
    for i, t in enumerate(cac_t):
        eps = khu(x, torch.full((n,), int(t)))
        x0 = ((x - (1 - ab[t]).sqrt() * eps) / ab[t].sqrt()).clamp(-1, 1)
        eps = (x - ab[t].sqrt() * x0) / (1 - ab[t]).sqrt()
        vet.append((int(t), x0[0].clone()))
        if i + 1 < len(cac_t):
            t_sau = cac_t[i + 1]
            x = ab[t_sau].sqrt() * x0 + (1 - ab[t_sau]).sqrt() * eps
        else:
            x = x0
    return ((x.view(n, 784) + 1) / 2, vet) if ghi else (x.view(n, 784) + 1) / 2


anh_dif, vet = sinh(1000, ghi=True)
diem_dif = cham_diem(anh_dif)
print(diem_dif)
assert diem_dif == (0.373, [27, 28, 193, 72, 181, 95, 29, 97, 267, 11])

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
    "savefig.bbox": "tight", "svg.hashsalt": "ch31",
})


def bo_truc(ax):
    ax.set_xticks([])
    ax.set_yticks([])
    ax.grid(False)
    for s in ax.spines.values():
        s.set_visible(False)


# Hình 31.1: số ảnh mỗi lớp qua 20 epoch của GAN
M = np.array([d for _, d in theo_epoch]).T                     # 10 lớp x 20 epoch
fig, ax = plt.subplots(figsize=(9.6, 4.4))
ax.imshow(M, cmap="Blues", aspect="auto", vmin=0, vmax=300)
for i in range(10):
    for j in range(20):
        ax.text(j, i, str(M[i, j]), ha="center", va="center", fontsize=8.5,
                color="white" if M[i, j] > 180 else CHU)
ax.set_xticks(range(20))
ax.set_xticklabels(range(1, 21))
ax.set_yticks(range(10))
ax.set_xlabel("Epoch")
ax.set_ylabel("Chữ số CNN nhận ra")
ax.grid(False)
fig.savefig(OUT / "h1_gan_theo_epoch.svg", metadata={"Date": None})

# Hình 31.2: một chữ số qua quá trình thêm nhiễu, và hai hệ số của công thức đóng
torch.manual_seed(0)
x0 = Xte[0] * 2 - 1
eps = torch.randn(784)
cac_t = [0, 50, 100, 250, 500, 750, 999]
fig = plt.figure(figsize=(10.4, 5.2))
luoi = fig.add_gridspec(2, len(cac_t), height_ratios=[1, 1.35], hspace=0.45)
for j, t in enumerate(cac_t):
    ax = fig.add_subplot(luoi[0, j])
    ax.imshow(((them_nhieu(x0, torch.tensor([t]), eps) + 1) / 2).clamp(0, 1).view(28, 28).numpy(), cmap="Greys", vmin=0, vmax=1)
    ax.set_title(f"t = {t + 1}", fontsize=11.5)
    bo_truc(ax)
ax = fig.add_subplot(luoi[1, :])
buoc = np.arange(1, T + 1)
ax.plot(buoc, ab.sqrt().numpy(), color=XANH, lw=2.2, label="hệ số của ảnh gốc, căn của alpha ngang")
ax.plot(buoc, (1 - ab).sqrt().numpy(), color=CAM, lw=2.2, label="hệ số của nhiễu, căn của 1 trừ alpha ngang")
ax.set_xlim(1, T)
ax.set_ylim(0, 1.02)
ax.set_xlabel("Bước t")
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:g}".replace(".", ",")))
ax.legend(frameon=False, loc="center right", fontsize=11)
fig.savefig(OUT / "h2_them_nhieu.svg", metadata={"Date": None}, dpi=150)

# Hình 31.3: ảnh sinh ra, và ảnh sạch mà mô hình diffusion đoán qua các bước
chon = [0, 3, 6, 9, 12, 15, 18, 21, 23, 24]                   # 10 trong 25 bước DDIM
hang = [("GAN, 20 epoch", [anh_gan[i] for i in range(10)]),
        ("Diffusion, 3 epoch", [anh_dif[i] for i in range(10)]),
        ("Diffusion: ảnh sạch\nmạng đoán ở mỗi bước", [(vet[k][1].view(784) + 1) / 2 for k in chon])]
fig, axs = plt.subplots(3, 10, figsize=(10.4, 3.9))
for r, (ten, anh) in enumerate(hang):
    for c in range(10):
        axs[r, c].imshow(anh[c].view(28, 28).numpy(), cmap="Greys", vmin=0, vmax=1)
        bo_truc(axs[r, c])
        if r == 2:
            axs[r, c].set_title(f"t = {vet[chon[c]][0] + 1}", fontsize=9.5, y=-0.32)
    axs[r, 0].set_ylabel(ten, rotation=0, ha="right", va="center", fontsize=11.5)
fig.subplots_adjust(wspace=0.05, hspace=0.15)
fig.savefig(OUT / "h3_sinh_anh.svg", metadata={"Date": None}, dpi=150)
print("OK")
