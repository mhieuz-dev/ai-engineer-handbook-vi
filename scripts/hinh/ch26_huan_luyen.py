"""Chương 26 Huấn luyện mạng sâu: tính lại các con số dùng trong bài và vẽ hình.

Chạy:  .venv/bin/python scripts/hinh/ch26_huan_luyen.py
Kết quả: các file SVG trong public/hinh/ch26/. Con số nào trong bài sai thì một câu assert báo lỗi.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.ticker import FuncFormatter

GOC = Path(__file__).resolve().parents[2]
OUT = GOC / "public" / "hinh" / "ch26"
OUT.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- thí nghiệm, y hệt code trong bài
import torch
import torch.nn as nn
import numpy as np
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
dg = load_digits()
A, B, C, E = train_test_split(dg.data / 16.0, dg.target, test_size=0.2, random_state=0, stratify=dg.target)
Xtr, ytr = torch.tensor(A, dtype=torch.float32), torch.tensor(C)
Xte, yte = torch.tensor(B, dtype=torch.float32), torch.tensor(E)
ce = nn.CrossEntropyLoss()

def sau(kich_hoat, bn=False):                 # 10 lớp ẩn, mỗi lớp 64 nơ-ron
    lop = []
    for _ in range(10):
        lop.append(nn.Linear(64, 64))
        if bn:
            lop.append(nn.BatchNorm1d(64))
        lop.append(kich_hoat())
    lop.append(nn.Linear(64, 10))
    return nn.Sequential(*lop)

def chuan_grad(m):                             # độ lớn gradient của lớp 1, 3, 5, 7, 9, 11
    ce(m(Xtr), ytr).backward()
    lin = [l for l in m if isinstance(l, nn.Linear)]
    return [f"{l.weight.grad.norm().item():.1e}" for l in lin[::2]]

def he(m):                                     # khởi tạo He cho mọi lớp Linear
    for l in m:
        if isinstance(l, nn.Linear):
            nn.init.kaiming_normal_(l.weight, nonlinearity="relu")
            nn.init.zeros_(l.bias)
    return m

from torch.utils.data import TensorDataset, DataLoader

def huan_luyen(m, opt, so_epoch=30, X=Xtr, y=ytr, lich=None):
    torch.manual_seed(1)                       # cố định thứ tự xáo trộn
    dl = DataLoader(TensorDataset(X, y), batch_size=64, shuffle=True)
    ls = []
    for ep in range(so_epoch):
        m.train()                              # chế độ huấn luyện: dropout bật, BN dùng thống kê của lô
        for xb, yb in dl:
            opt.zero_grad()
            ce(m(xb), yb).backward()
            opt.step()
        if lich:
            lich.step()                        # cập nhật learning rate sau mỗi epoch
        m.eval()                               # chế độ đánh giá
        with torch.no_grad():
            ls.append((ce(m(X), y).item(), ce(m(Xte), yte).item(), (m(Xte).argmax(1) == yte).float().mean().item()))
    return ls                                  # mỗi epoch: loss train, loss test, độ chính xác test

Xit, yit = Xtr[:300], ytr[:300]                # chỉ 300 ảnh train
def rong(p=0.0):                               # 64 -> 256 -> 256 -> 10, dropout p sau mỗi lớp ẩn
    return nn.Sequential(nn.Linear(64, 256), nn.ReLU(), nn.Dropout(p),
                         nn.Linear(256, 256), nn.ReLU(), nn.Dropout(p), nn.Linear(256, 10))
kq = {}
for ten, p, wd in [("không gì", 0.0, 0.0), ("dropout 0.5", 0.5, 0.0), ("weight decay 0.1", 0.0, 0.1)]:
    torch.manual_seed(0)
    m = rong(p)
    kq[ten] = huan_luyen(m, torch.optim.AdamW(m.parameters(), lr=1e-3, weight_decay=wd), so_epoch=200, X=Xit, y=yit)
gn = {}
for ten, tao in [("Sigmoid", lambda: sau(nn.Sigmoid)), ("ReLU, khởi tạo mặc định", lambda: sau(nn.ReLU)),
                 ("ReLU, khởi tạo He", lambda: he(sau(nn.ReLU)))]:
    torch.manual_seed(0)
    m = tao()
    ce(m(Xtr), ytr).backward()
    gn[ten] = [l.weight.grad.norm().item() for l in m if isinstance(l, nn.Linear)]
assert f"{gn['Sigmoid'][0]:.1e}" == "1.3e-09" and f"{gn['ReLU, khởi tạo He'][0]:.1e}" == "5.4e-01"
assert round(kq["không gì"][-1][1], 4) == 0.3208 and round(kq["dropout 0.5"][-1][1], 4) == 0.2135
assert int(np.argmin([l[1] for l in kq["không gì"]])) + 1 == 42

# ---------------------------------------------------------------- vẽ hình
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
    "savefig.bbox": "tight", "svg.hashsalt": "ch26",
})
PHAY = FuncFormatter(lambda v, _: f"{v:g}".replace(".", ","))
META = {"Date": None}

# hình 26.1: độ lớn gradient theo lớp
fig, ax = plt.subplots(figsize=(8, 4.6))
for (ten, g), mau in zip(gn.items(), (DO, CAM, XANH)):
    ax.plot(range(1, 12), g, "o-", color=mau, lw=2, label=ten)
ax.set_yscale("log")
ax.set_xticks(range(1, 12))
ax.set_xlabel("Lớp (1 là lớp đầu vào, 11 là lớp ra)")
ax.set_ylabel("Độ dài gradient của trọng số")
ax.legend(frameon=False, loc="lower right")
fig.savefig(OUT / "h1_gradient_theo_lop.svg", metadata=META)
plt.close(fig)

# hình 26.2: loss test theo epoch, 300 ảnh train
fig, ax = plt.subplots(figsize=(8, 4.6))
for (ten, ls), mau in zip(kq.items(), (DO, XANH, CAM)):
    te = [l[1] for l in ls]
    tot = int(np.argmin(te))
    ax.plot(range(1, 201), te, color=mau, lw=2, label=ten)
    ax.plot(tot + 1, te[tot], "o", color=mau, ms=8, mec=NEN, mew=1.5)
ax.set_xlabel("Epoch")
ax.set_ylim(0.15, 0.45)
ax.set_ylabel("Cross-entropy trên 360 ảnh test")
ax.yaxis.set_major_formatter(PHAY)
ax.legend(frameon=False, loc="upper right")
fig.savefig(OUT / "h2_loss_test.svg", metadata=META)
plt.close(fig)
print("OK")
