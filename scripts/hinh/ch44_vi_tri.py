"""Chương 44 Transformer: vẽ hình 44.1 (mã hóa vị trí sin, cos cho 64 vị trí, 128 chiều), đúng hàm vi_tri của trang 2.

Chạy:  .venv/bin/python scripts/hinh/ch44_vi_tri.py      (dưới một giây)
Kết quả: public/hinh/ch44/h1_vi_tri.svg. Con số nào trong bài sai thì một câu assert báo lỗi.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import torch
from matplotlib import font_manager

GOC = Path(__file__).resolve().parents[2]
OUT = GOC / "public" / "hinh" / "ch44"
OUT.mkdir(parents=True, exist_ok=True)


def vi_tri(n, d):
    p = torch.arange(n).unsqueeze(1)
    goc = p / 10000 ** (torch.arange(0, d, 2) / d)
    P = torch.zeros(n, d)
    P[:, 0::2], P[:, 1::2] = torch.sin(goc), torch.cos(goc)
    return P


P = vi_tri(64, 128)
tich = P @ P.T
assert [round(tich[i, i + 5].item(), 3) for i in (0, 10, 30)] == [47.185] * 3

NEN, CHU = "#FBF8F1", "#2B2B2B"
co_sans = {f.name for f in font_manager.fontManager.ttflist}
FONT = "Be Vietnam Pro" if "Be Vietnam Pro" in co_sans else "DejaVu Sans"
plt.rcParams.update({"font.family": FONT, "font.size": 12.5, "text.color": CHU, "axes.labelcolor": CHU,
                     "xtick.color": CHU, "ytick.color": CHU, "figure.facecolor": NEN, "axes.facecolor": NEN,
                     "savefig.facecolor": NEN, "savefig.bbox": "tight", "svg.hashsalt": "ch44"})
fig, ax = plt.subplots(figsize=(10, 5))
anh = ax.imshow(P.numpy(), cmap="RdBu_r", vmin=-1, vmax=1, aspect="auto")
ax.set_xlabel("chiều")
ax.set_ylabel("vị trí")
fig.colorbar(anh, ax=ax, fraction=0.03)
fig.tight_layout()
fig.savefig(OUT / "h1_vi_tri.svg", metadata={"Date": None})
print("xong", sorted(p.name for p in OUT.iterdir()))
