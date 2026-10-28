"""Chương 28 Kiến trúc CNN: chạy lại bốn cách huấn luyện ở trang 4 và vẽ hình 28.1.

Chạy:  .venv/bin/python scripts/hinh/ch28_transfer.py      (khoảng 4 phút trên CPU 16 nhân)
Kết quả: public/hinh/ch28/h1_transfer.svg. Con số nào trong bài sai thì một câu assert báo lỗi.
Ảnh kiến, ong và trọng số ResNet-18 tải về ~/.cache (lần đầu), không nằm trong repo.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import torch
import torch.nn as nn
from matplotlib import font_manager
from matplotlib.ticker import FuncFormatter
from torch.utils.data import DataLoader
from torchvision import datasets, models, transforms
from torchvision.datasets.utils import download_and_extract_archive

GOC = Path(__file__).resolve().parents[2]
OUT = GOC / "public" / "hinh" / "ch28"
OUT.mkdir(parents=True, exist_ok=True)
DATA = Path.home() / ".cache" / "hymenoptera"

# ---------------------------------------------------------------- dữ liệu và vòng huấn luyện, y hệt trang 3 và 4
download_and_extract_archive("https://download.pytorch.org/tutorial/hymenoptera_data.zip", DATA)
goc = DATA / "hymenoptera_data"
TB, DL = [0.485, 0.456, 0.406], [0.229, 0.224, 0.225]
bd_train = transforms.Compose([transforms.RandomResizedCrop(224), transforms.RandomHorizontalFlip(),
                               transforms.ToTensor(), transforms.Normalize(TB, DL)])
bd_test = transforms.Compose([transforms.Resize(256), transforms.CenterCrop(224),
                              transforms.ToTensor(), transforms.Normalize(TB, DL)])
ds_tr = datasets.ImageFolder(goc / "train", transform=bd_train)
ds_te = datasets.ImageFolder(goc / "val", transform=bd_test)
torch.manual_seed(0)
dl_tr = DataLoader(ds_tr, batch_size=32, shuffle=True, num_workers=2)
dl_te = DataLoader(ds_te, batch_size=64, num_workers=2)
next(iter(dl_tr))                                       # trang 3 lấy một lô, giữ nguyên trạng thái ngẫu nhiên
ce = nn.CrossEntropyLoss()


def danh_gia(m):
    m.eval()
    dung = 0
    with torch.no_grad():
        for xb, yb in dl_te:
            dung += (m(xb).argmax(1) == yb).sum().item()
    return round(dung / len(ds_te), 4)


def huan_luyen(m, tham_so, so_epoch, lr):
    torch.manual_seed(1)
    opt = torch.optim.Adam(tham_so, lr=lr)
    kq = []
    for ep in range(so_epoch):
        m.train()
        for xb, yb in dl_tr:
            opt.zero_grad()
            ce(m(xb), yb).backward()
            opt.step()
        kq.append(danh_gia(m))
    return kq


def khoi(vao, ra):
    return nn.Sequential(nn.Conv2d(vao, ra, 3, padding=1), nn.BatchNorm2d(ra), nn.ReLU(), nn.MaxPool2d(2))


torch.manual_seed(0)
tu_dau = nn.Sequential(khoi(3, 16), khoi(16, 32), khoi(32, 64), khoi(64, 128),
                       nn.AdaptiveAvgPool2d(1), nn.Flatten(), nn.Linear(128, 2))
kq_tu_dau = huan_luyen(tu_dau, tu_dau.parameters(), 10, 1e-3)
w = models.ResNet18_Weights.IMAGENET1K_V1
torch.manual_seed(0)
net = models.resnet18(weights=w)
for p in net.parameters():
    p.requires_grad = False
net.fc = nn.Linear(512, 2)
kq_dong_bang = huan_luyen(net, net.fc.parameters(), 5, 1e-3)
torch.manual_seed(0)
net2 = models.resnet18(weights=w)
net2.fc = nn.Linear(512, 2)
kq_tinh_chinh = huan_luyen(net2, net2.parameters(), 5, 1e-4)
torch.manual_seed(0)
net3 = models.resnet18(weights=None)
net3.fc = nn.Linear(512, 2)
kq_ngau_nhien = huan_luyen(net3, net3.parameters(), 5, 1e-3)
print(kq_tu_dau, kq_dong_bang, kq_tinh_chinh, kq_ngau_nhien)
assert kq_tu_dau[-1] == 0.7059 and kq_dong_bang[-1] == 0.9281
assert kq_tinh_chinh[-1] == 0.9281 and kq_ngau_nhien[-1] == 0.6928

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
    "savefig.bbox": "tight", "svg.hashsalt": "ch28",
})
PHAY = FuncFormatter(lambda v, _: f"{v:g}".replace(".", ","))
fig, ax = plt.subplots(figsize=(8, 4.8))
for kq, ten, mau in [(kq_dong_bang, "ResNet-18 ImageNet, đóng băng", XANH),
                     (kq_tinh_chinh, "ResNet-18 ImageNet, tinh chỉnh toàn bộ", CAM),
                     (kq_tu_dau, "CNN nhỏ học từ đầu", XAM),
                     (kq_ngau_nhien, "ResNet-18 trọng số ngẫu nhiên", DO)]:
    ax.plot(range(1, len(kq) + 1), kq, "o-", color=mau, lw=2, ms=5, label=ten)
ax.axhline(83 / 153, color=XAM, lw=1.2, ls=":")
ax.set_ylim(0.5, 1)
ax.set_xticks(range(1, 11))
ax.set_xlabel("Epoch")
ax.set_ylabel("Độ chính xác trên 153 ảnh val")
ax.yaxis.set_major_formatter(PHAY)
ax.legend(frameon=False, loc="lower right", fontsize=11)
fig.savefig(OUT / "h1_transfer.svg", metadata={"Date": None})
print("OK")
