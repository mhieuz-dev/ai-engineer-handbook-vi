"""Chương 37 PPO và Gymnasium: vẽ hình 37.1 (mục tiêu cắt) và 37.2 (chính sách đặt hàng của PPO so với (s, S)).

Chạy:  .venv/bin/python scripts/hinh/ch37_ppo.py      (khoảng 40 giây: huấn luyện lại PPO trên môi trường kho như trang 4)
Kết quả: public/hinh/ch37/h1_cat.svg, h2_kho.svg. Con số nào trong bài sai thì một câu assert báo lỗi.
"""
import re
import warnings
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager

GOC = Path(__file__).resolve().parents[2]
OUT = GOC / "public" / "hinh" / "ch37"
OUT.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- chạy y hệt code của trang 1, 2, 4 (đọc thẳng từ trang)
TRANG = GOC / "src/content/docs/ai-engineer/ch37-ppo-gymnasium"
g = {}
for ten in ("01-buoc-an-toan.mdx", "02-ppo-tren-cartpole.mdx", "04-tu-viet-moi-truong.mdx"):
    for khoi in re.findall(r"```python\n(.*?)```", (TRANG / ten).read_text(encoding="utf-8"), re.S):
        khoi = khoi.split("luoi = sorted")[0]          # khối lưới (s, S): chỉ lấy phần định nghĩa hàm
        if khoi.startswith("!") or "ppo(CP" in khoi or "tt_kho = ppo" in khoi or "check_env" in khoi:
            continue
        exec(khoi, g)
torch, ppo, danh_gia, Kho, chinh_sach_sS = g["torch"], g["ppo"], g["danh_gia"], g["Kho"], g["chinh_sach_sS"]
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    tt_kho = ppo(Kho, 300_000, n_buoc=512, epoch=10, n_lo=8, lr=1e-3, in_moi=10**9)
assert danh_gia(tt_kho, Kho, n=2000, seed=20_000) == -377.6
assert chinh_sach_sS(2, 7, 2000, 20_000) == -374.9
with torch.no_grad():
    ppo_dat = [int(tt_kho.tham_lam(torch.tensor([t / 20, 0.5]))) for t in range(13)]
assert ppo_dat == [7, 7] + [0] * 11, ppo_dat
sS_dat = [min(10, 7 - t) if t <= 2 else 0 for t in range(13)]

# ---------------------------------------------------------------- vẽ hình
NEN = "#FBF8F1"
XANH, CAM, XAM, CHU, LUOI = "#1F5F8B", "#E07A1F", "#8A8170", "#2B2B2B", "#E6DECD"
co_sans = {f.name for f in font_manager.fontManager.ttflist}
FONT = "Be Vietnam Pro" if "Be Vietnam Pro" in co_sans else "DejaVu Sans"
plt.rcParams.update({
    "font.family": FONT, "font.size": 12.5, "text.color": CHU, "axes.labelcolor": CHU,
    "xtick.color": CHU, "ytick.color": CHU, "axes.edgecolor": XAM,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": LUOI, "grid.alpha": 0.8, "axes.axisbelow": True,
    "figure.facecolor": NEN, "axes.facecolor": NEN, "savefig.facecolor": NEN,
    "savefig.bbox": "tight", "svg.hashsalt": "ch37",
})


def phay(x, pos=None):
    return f"{x:g}".replace(".", ",").replace("-", "−")


# Hình 37.1: mục tiêu cắt
rho = np.linspace(0, 2, 401)
fig, axs = plt.subplots(1, 2, figsize=(11, 4.4))
for ax, A, tieu_de in ((axs[0], 1.0, "lợi thế dương, A = 1"), (axs[1], -1.0, "lợi thế âm, A = −1")):
    L = np.minimum(rho * A, np.clip(rho, 0.8, 1.2) * A)
    ax.axvspan(0.8, 1.2, color=XANH, alpha=0.1, lw=0)
    ax.plot(rho, rho * A, color=XAM, lw=1.3, ls="--", label="không cắt, ρA")
    ax.plot(rho, L, color=CAM, lw=2.8, label="mục tiêu cắt của PPO")
    ax.set_xlabel("tỷ số ρ = π mới / π cũ")
    ax.set_title(tieu_de, fontsize=12.5)
    ax.xaxis.set_major_formatter(phay)
    ax.yaxis.set_major_formatter(phay)
axs[0].legend(loc="upper left", frameon=False)
axs[0].set_ylabel("đóng góp vào mục tiêu")
fig.tight_layout()
fig.savefig(OUT / "h1_cat.svg", metadata={"Date": None})
plt.close(fig)

# Hình 37.2: chính sách đặt hàng
fig, ax = plt.subplots(figsize=(9, 4.6))
x = np.arange(13)
ax.step(x, sS_dat, where="mid", color=CAM, lw=2.6, label="(s, S) = (2, 7), tìm bằng lưới")
ax.step(x, ppo_dat, where="mid", color=XANH, lw=2.6, ls="--", label="PPO, ngày 30")
ax.set_xticks(x)
ax.set_xlabel("tồn kho đầu ngày (thùng)")
ax.set_ylabel("số thùng đặt")
ax.set_ylim(-0.3, 8)
ax.legend(loc="upper right", frameon=False)
fig.tight_layout()
fig.savefig(OUT / "h2_kho.svg", metadata={"Date": None})
plt.close(fig)
print("xong", sorted(p.name for p in OUT.iterdir()))
