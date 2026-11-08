"""Chương 33 Bài toán RL: chạy lại bàn thử bandit (trang 2) và tính giá trị chính sách ngẫu nhiên (trang 4), vẽ hình 33.1 và 33.2.

Chạy:  .venv/bin/python scripts/hinh/ch33_bai_toan_rl.py      (vài giây)
Kết quả: public/hinh/ch33/h1_bandit.svg, h2_gia_tri.svg.
Con số nào trong bài sai thì một câu assert báo lỗi.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import gymnasium as gym
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager

GOC = Path(__file__).resolve().parents[2]
OUT = GOC / "public" / "hinh" / "ch33"
OUT.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------- bandit, y hệt trang 2
def bandit(eps, n_lan=2000, n_buoc=1000, k=10, seed=0):
    rng = np.random.default_rng(seed)
    q_that = rng.normal(0, 1, (n_lan, k))
    tot_nhat = q_that.argmax(1)
    Q = np.zeros((n_lan, k))
    N = np.zeros((n_lan, k))
    hang = np.arange(n_lan)
    thuong, dung = np.zeros(n_buoc), np.zeros(n_buoc)
    for t in range(n_buoc):
        a = np.where(rng.random(n_lan) < eps, rng.integers(k, size=n_lan), Q.argmax(1))
        r = rng.normal(q_that[hang, a], 1)
        N[hang, a] += 1
        Q[hang, a] += (r - Q[hang, a]) / N[hang, a]
        thuong[t], dung[t] = r.mean(), (a == tot_nhat).mean()
    return thuong, dung, q_that.max(1).mean()


ket_qua = {eps: bandit(eps) for eps in (0, 0.01, 0.1)}
bang = {eps: (round(th[:100].mean(), 3), round(th[-100:].mean(), 3), round(d[-100:].mean(), 3)) for eps, (th, d, _) in ket_qua.items()}
assert bang == {0: (0.963, 1.039, 0.355), 0.01: (0.975, 1.318, 0.587), 0.1: (1.005, 1.37, 0.797)}, bang
assert round(ket_qua[0][2], 3) == 1.535

# ---------------------------------------------------------------- giá trị chính sách ngẫu nhiên, y hệt trang 3 và 4
env = gym.make("FrozenLake-v1")
P = env.unwrapped.P
T = np.zeros((16, 4, 16))
R = np.zeros((16, 4))
for s in range(16):
    for a in range(4):
        for p, s2, r, xong in P[s][a]:
            T[s, a, s2] += p
            R[s, a] += p * r
CUOI = [5, 7, 11, 12, 15]
ngau = np.full((16, 4), 0.25)
P_pi = np.einsum("sa,sat->st", ngau, T)
R_pi = (ngau * R).sum(1)
P_pi[CUOI] = 0
R_pi[CUOI] = 0
V = np.linalg.solve(np.eye(16) - P_pi, R_pi)
assert [round(V[s], 4) for s in (0, 6, 9, 10, 13, 14)] == [0.0139, 0.0408, 0.0882, 0.1421, 0.1758, 0.4393], V
assert V[:4].max().round(4) == 0.021

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
    "savefig.bbox": "tight", "svg.hashsalt": "ch33",
})


def phay(x, pos=None):
    return f"{x:g}".replace(".", ",")


# Hình 33.1: hai đường theo lượt kéo
fig, axs = plt.subplots(2, 1, figsize=(9, 7.6), sharex=True)
mau = {0: XAM, 0.01: CAM, 0.1: XANH}
ten = {0: "tham lam (ε = 0)", 0.01: "ε = 0,01", 0.1: "ε = 0,1"}
luot = np.arange(1, 1001)
for eps, (th, d, tran) in ket_qua.items():
    axs[0].plot(luot, th, color=mau[eps], lw=1.4, label=ten[eps])
    axs[1].plot(luot, d * 100, color=mau[eps], lw=1.4, label=ten[eps])
axs[0].axhline(tran, color=CHU, lw=1, ls="--")
axs[0].text(1000, tran + 0.04, "trần: luôn kéo tay tốt nhất, 1,535", ha="right", va="bottom", fontsize=11)
axs[0].set_ylabel("phần thưởng trung bình")
axs[0].yaxis.set_major_formatter(phay)
axs[0].legend(loc="lower right", frameon=False)
axs[1].set_ylabel("chọn đúng tay tốt nhất (%)")
axs[1].set_xlabel("lượt kéo")
axs[1].set_ylim(0, 100)
fig.tight_layout()
fig.savefig(OUT / "h1_bandit.svg", metadata={"Date": None})
plt.close(fig)
# số kiểm cho mô tả hình: các đường ở cuối
print({eps: (round(th[-50:].mean(), 2), round(d[-50:].mean(), 2)) for eps, (th, d, _) in ket_qua.items()})

# Hình 33.2: bản đồ và giá trị
desc = env.unwrapped.desc.astype(str)
fig, axs = plt.subplots(1, 2, figsize=(10, 5))
mau_o = {"S": "#DCEBF5", "F": "#EEF4F8", "H": "#33414F", "G": "#F4D9B8"}
nhan_o = {"S": "xuất phát", "F": "", "H": "hố", "G": "đích"}
for i in range(4):
    for j in range(4):
        c = desc[i, j]
        axs[0].add_patch(plt.Rectangle((j, i), 1, 1, facecolor=mau_o[c], edgecolor=NEN, lw=3))
        mau_chu = "#FFFFFF" if c == "H" else CHU
        axs[0].text(j + 0.5, i + 0.42, c, ha="center", va="center", fontsize=20, fontweight="bold", color=mau_chu)
        axs[0].text(j + 0.5, i + 0.75, f"{4 * i + j}" + (f" · {nhan_o[c]}" if nhan_o[c] else ""), ha="center", va="center", fontsize=10.5, color=mau_chu)
im = axs[1].imshow(V.reshape(4, 4), cmap="Blues", vmin=0, vmax=0.5, extent=(0, 4, 4, 0))
for i in range(4):
    for j in range(4):
        s = 4 * i + j
        if desc[i, j] == "H":
            axs[1].add_patch(plt.Rectangle((j, i), 1, 1, facecolor="#33414F", edgecolor=NEN, lw=3))
            axs[1].text(j + 0.5, i + 0.5, "hố", ha="center", va="center", fontsize=11, color="#FFFFFF")
        else:
            axs[1].add_patch(plt.Rectangle((j, i), 1, 1, facecolor="none", edgecolor=NEN, lw=3))
            axs[1].text(j + 0.5, i + 0.5, f"{V[s]:.3f}".replace(".", ","), ha="center", va="center", fontsize=12,
                        color="#FFFFFF" if V[s] > 0.3 else CHU)
for ax, tieu_de in zip(axs, ["bản đồ và số thứ tự trạng thái", "giá trị của chính sách ngẫu nhiên"]):
    ax.set_xlim(0, 4)
    ax.set_ylim(4, 0)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.grid(False)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.set_title(tieu_de, fontsize=12.5)
fig.tight_layout()
fig.savefig(OUT / "h2_gia_tri.svg", metadata={"Date": None})
plt.close(fig)
print("xong", sorted(p.name for p in OUT.iterdir()))
