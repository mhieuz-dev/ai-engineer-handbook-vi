"""Chương 32 Dự án Phần III: huấn luyện lại ResNet-18 tinh chỉnh (trang 3), vẽ hình 32.1 tới 32.3.

Chạy:  .venv/bin/python scripts/hinh/ch32_du_an.py      (khoảng 10 phút trên CPU 16 nhân)
Kết quả: public/hinh/ch32/h1_mau.svg, h2_ma_tran_nham_lan.svg, h3_anh_sai.svg. EuroSAT tải về ~/.cache/eurosat.
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
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split
from torchvision import models
from torchvision.datasets import EuroSAT

GOC = Path(__file__).resolve().parents[2]
OUT = GOC / "public" / "hinh" / "ch32"
OUT.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- dữ liệu và cách chia, y hệt trang 1
ds = EuroSAT(Path.home() / ".cache" / "eurosat", download=True)
X = torch.from_numpy(np.stack([np.array(ds.loader(p)) for p, _ in ds.samples])).permute(0, 3, 1, 2).contiguous()
y = torch.tensor(ds.targets)
chi_so = np.arange(len(y))
i_tr, i_con = train_test_split(chi_so, test_size=0.3, stratify=y.numpy(), random_state=0)
i_va, i_te = train_test_split(i_con, test_size=0.5, stratify=y.numpy()[i_con], random_state=0)
i_tr, i_va, i_te = torch.from_numpy(i_tr), torch.from_numpy(i_va), torch.from_numpy(i_te)

# ---------------------------------------------------------------- huấn luyện, y hệt trang 2 và trang 3
ce = nn.CrossEntropyLoss()
tb_in = torch.tensor([0.485, 0.456, 0.406]).view(1, 3, 1, 1)
dl_in = torch.tensor([0.229, 0.224, 0.225]).view(1, 3, 1, 1)


def chuan_in(xb):
    return (xb.float().div(255) - tb_in) / dl_in


@torch.no_grad()
def du_doan(m, idx, bs=500):
    m.eval()
    return torch.cat([m(chuan_in(X[idx[i:i + bs]])) for i in range(0, len(idx), bs)])


def lat_xoay(x):
    x = x.clone()
    m = torch.rand(len(x)) < 0.5
    x[m] = x[m].flip(3)
    m = torch.rand(len(x)) < 0.5
    x[m] = x[m].flip(2)
    m = torch.rand(len(x)) < 0.5
    x[m] = x[m].transpose(2, 3)
    return x


torch.manual_seed(0)
net = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)
net.fc = nn.Linear(512, 10)
so_epoch, bs, lr = 5, 128, 1e-3
torch.manual_seed(1)
opt = torch.optim.AdamW(net.parameters(), lr=lr, weight_decay=1e-4, fused=True)
lich = torch.optim.lr_scheduler.OneCycleLR(opt, max_lr=lr, total_steps=so_epoch * ((len(i_tr) + bs - 1) // bs))
for ep in range(so_epoch):
    net.train()
    thu_tu = i_tr[torch.randperm(len(i_tr))]
    for i in range(0, len(thu_tu), bs):
        loss = ce(net(chuan_in(lat_xoay(X[thu_tu[i:i + bs]]))), y[thu_tu[i:i + bs]])
        opt.zero_grad()
        loss.backward()
        opt.step()
        lich.step()

P = du_doan(net, i_te).softmax(1)
doan = P.argmax(1)
dung = doan == y[i_te]
M = confusion_matrix(y[i_te], doan)
assert round(dung.float().mean().item(), 4) == 0.9753 and int((~dung).sum()) == 100, dung.float().mean()
assert M[6, 2] == 14 and M[6, 0] == 7 and M[5, 2] == 7 and M[0, 6] == 7, M
khoi = [0, 2, 5, 6]
print(M.tolist(), sum(M[i, j] for i in khoi for j in khoi if i != j))
tin = P.max(1).values

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
    "savefig.bbox": "tight", "svg.hashsalt": "ch32",
})
TEN = ["cây hằng năm", "rừng", "thảm cỏ", "cao tốc", "công nghiệp", "đồng cỏ", "cây lâu năm", "dân cư", "sông", "biển, hồ"]


def bo_truc(ax):
    ax.set_xticks([])
    ax.set_yticks([])
    ax.grid(False)
    for s in ax.spines.values():
        s.set_visible(False)


def anh(i):
    return X[i].permute(1, 2, 0).numpy()


# Hình 32.1: sáu ảnh train đầu tiên của mỗi lớp
fig, axs = plt.subplots(10, 6, figsize=(6.6, 11.4))
for c in range(10):
    cua_lop = i_tr[y[i_tr] == c][:6]
    for k in range(6):
        axs[c, k].imshow(anh(cua_lop[k]))
        bo_truc(axs[c, k])
    axs[c, 0].set_ylabel(TEN[c], rotation=0, ha="right", va="center", fontsize=12)
fig.subplots_adjust(wspace=0.06, hspace=0.06)
fig.savefig(OUT / "h1_mau.svg", metadata={"Date": None}, dpi=150)

# Hình 32.2: ma trận nhầm lẫn, đường chéo và ngoài đường chéo tô theo hai thang
cheo = np.eye(10, dtype=bool)
fig, ax = plt.subplots(figsize=(8.4, 7.2))
ax.imshow(np.ma.masked_where(~cheo, M), cmap="Blues", vmin=0, vmax=500)
ax.imshow(np.ma.masked_where(cheo | (M == 0), M), cmap="Oranges", vmin=0, vmax=14)
for i in range(10):
    for j in range(10):
        if M[i, j]:
            ax.text(j, i, str(M[i, j]), ha="center", va="center", fontsize=10.5,
                    color="white" if (i == j or M[i, j] > 9) else CHU)
ax.set_xticks(range(10))
ax.set_xticklabels(TEN, rotation=40, ha="right")
ax.set_yticks(range(10))
ax.set_yticklabels(TEN)
ax.set_xlabel("Mô hình đoán")
ax.set_ylabel("Lớp thật")
ax.grid(False)
fig.savefig(OUT / "h2_ma_tran_nham_lan.svg", metadata={"Date": None})

# Hình 32.3: mười ảnh test sai mà mô hình tin nhất
sai = (~dung).nonzero().flatten()
sai = sai[tin[sai].argsort(descending=True)][:10]
for s in sai.tolist():
    print(i_te[s].item(), TEN[y[i_te[s]]], TEN[doan[s]], round(tin[s].item(), 3))
fig, axs = plt.subplots(2, 5, figsize=(10.4, 5.8))
for k, s in enumerate(sai.tolist()):
    ax = axs.flat[k]
    ax.imshow(anh(i_te[s]))
    bo_truc(ax)
    ax.set_title(f"thật: {TEN[y[i_te[s]]]}", fontsize=11)
    ax.set_xlabel(f"đoán: {TEN[doan[s]]}\n{tin[s].item():.3f}".replace(".", ","), fontsize=11, color=DO)
fig.subplots_adjust(wspace=0.25, hspace=0.45)
fig.savefig(OUT / "h3_anh_sai.svg", metadata={"Date": None}, dpi=150)
print("OK")
