"""Chương 34 Quy hoạch động và Q-learning: chạy lại policy iteration, value iteration (trang 1, 2),
Q-learning 20 lần chạy cho ba mức epsilon (trang 3) và SARSA với Q-learning trên bài vách đá (trang 4), vẽ hình 34.1 tới 34.4.

Chạy:  .venv/bin/python scripts/hinh/ch34_q_learning.py      (khoảng 5 phút, gần hết là 60 lần chạy Q-learning)
Kết quả: public/hinh/ch34/h1_toi_uu.svg, h2_lan_gia_tri.svg, h3_q_learning.svg, h4_vach_da.svg.
Con số nào trong bài sai thì một câu assert báo lỗi.
"""
from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import gymnasium as gym
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager

GOC = Path(__file__).resolve().parents[2]
OUT = GOC / "public" / "hinh" / "ch34"
OUT.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- trang 1: MDP, policy iteration
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
GAMMA = 0.99


def danh_gia(pi, gamma=GAMMA):
    P_pi = np.einsum("sa,sat->st", pi, T)
    R_pi = (pi * R).sum(1)
    P_pi[CUOI] = 0
    R_pi[CUOI] = 0
    return np.linalg.solve(np.eye(16) - gamma * P_pi, R_pi)


def q_tu_v(V, gamma=GAMMA):
    Q = R + gamma * np.einsum("sat,t->sa", T, V)
    Q[CUOI] = 0
    return Q


pi = np.full((16, 4), 0.25)
vong_pi = []
for vong in range(10):
    V = danh_gia(pi)
    tham = q_tu_v(V).round(10).argmax(1)
    pi_moi = np.eye(4)[tham]
    vong_pi.append((round(V[0], 4), round(danh_gia(pi, 1.0)[0], 4), int((pi_moi != pi).any(1).sum())))
    if (pi_moi == pi).all():
        break
    pi = pi_moi
assert vong_pi == [(0.0124, 0.0139, 16), (0.5325, 0.7805, 1), (0.542, 0.8235, 0)], vong_pi
V_sao = V.copy()
assert tham.tolist() == [0, 3, 3, 3, 0, 0, 0, 0, 3, 1, 0, 0, 0, 2, 1, 0]
assert [round(V_sao[s], 3) for s in (0, 1, 2, 3, 4, 8, 9, 10, 13, 14)] == [0.542, 0.499, 0.471, 0.457, 0.558, 0.592, 0.643, 0.615, 0.742, 0.863]

# ---------------------------------------------------------------- trang 2: value iteration
V = np.zeros(16)
anh = {}
for k in range(1, 2001):
    V_moi = q_tu_v(V).max(1)
    chenh = np.abs(V_moi - V).max()
    V = V_moi
    if k in (1, 3, 6, 20):
        anh[k] = V.copy()
    if chenh < 1e-10:
        break
assert k == 571 and round(V[0], 4) == 0.542
anh[571] = V.copy()
assert [s for s in range(16) if anh[1][s] > 0] == [14]
assert [s for s in range(16) if anh[3][s] > 0] == [6, 9, 10, 13, 14]
assert anh[6][0] > 0 and round(anh[6][0], 4) == 0.0039
V_vi = V.copy()


# ---------------------------------------------------------------- trang 3: Q-learning, y hệt trang 3 (chỉ ghi lại thay vì in)
def ti_le_toi_dich(Q, so_buoc=10_000):
    pi = Q.argmax(1)
    P_pi, R_pi = T[np.arange(16), pi], R[np.arange(16), pi].copy()
    P_pi[CUOI] = 0
    R_pi[CUOI] = 0
    V = np.zeros(16)
    for _ in range(so_buoc):
        V = R_pi + P_pi @ V
    return round(V[0], 4)


def q_learning(n_tap, eps, alpha=0.1, gamma=GAMMA, seed=0, moi=2000, dem=None):
    rng = np.random.default_rng(seed)
    Q = np.zeros((16, 4))
    env.reset(seed=seed)
    ghi = []
    for tap in range(1, n_tap + 1):
        s, _ = env.reset()
        while True:
            a = int(rng.integers(4)) if rng.random() < eps else int(Q[s].argmax())
            s2, r, ket_thuc, cat_ngang, _ = env.step(a)
            muc_tieu = r if ket_thuc else r + gamma * Q[s2].max()
            Q[s, a] += alpha * (muc_tieu - Q[s, a])
            s = s2
            if ket_thuc or cat_ngang:
                break
        if dem is not None and tap <= 10_000:
            dem.append((s, r))
        if tap % moi == 0:
            ghi.append(ti_le_toi_dich(Q))
    return Q, ghi


dem = []
_, ghi = q_learning(20_000, 0.1, dem=dem)
assert ghi == [0.0] * 5 + [0.7805, 0.7805, 0.7568, 0.7805, 0.7805], ghi
cuoi_tap = Counter(s for s, _ in dem)
lan_thang = [i + 1 for i, (_, r) in enumerate(dem) if r == 1]
assert cuoi_tap[12] == 7563 and cuoi_tap[5] == 2435 and lan_thang == [9313], (cuoi_tap, lan_thang)
Q_05, ghi = q_learning(20_000, 0.5)
assert ghi == [0.625, 0.7368, 0.7368] + [0.8235] * 7, ghi
assert round(np.abs(Q_05 - q_tu_v(V_vi)).max(), 3) == 0.207

duong_cong = {eps: np.array([q_learning(20_000, eps, seed=k, moi=500)[1] for k in range(20)]) for eps in (0.1, 0.5, 1.0)}
tb = {eps: duong_cong[eps].mean(0) for eps in duong_cong}
assert [round(tb[0.5][i], 3) for i in (1, 3)] == [0.591, 0.776], tb[0.5][:4]
assert [round(tb[1.0][i], 3) for i in (1, 7, 39)] == [0.265, 0.666, 0.769], tb[1.0]
assert [round(tb[0.1][i], 3) for i in (1, 3, 19, 39)] == [0.0, 0.077, 0.36, 0.594], tb[0.1]
assert (duong_cong[0.5][:, -1] > 0.82).sum() == 14

# ---------------------------------------------------------------- trang 4: vách đá, y hệt trang 4 (thêm đếm số lần ghé ô)
vd = gym.make("CliffWalking-v1")


def hoc_vach(cach, n_tap=500, alpha=0.5, eps=0.1, seed=0, ghe=None):
    rng = np.random.default_rng(seed)
    Q = np.zeros((48, 4))
    vd.reset(seed=seed)

    def chon(s):
        return int(rng.integers(4)) if rng.random() < eps else int(Q[s].argmax())
    tong = []
    for tap in range(n_tap):
        s, _ = vd.reset()
        a = chon(s)
        G = 0
        while True:
            if ghe is not None and tap >= n_tap - 100:
                ghe[s] += 1
            s2, r, ket_thuc, cat_ngang, _ = vd.step(a)
            G += r
            a2 = chon(s2)
            if ket_thuc:
                muc_tieu = r
            elif cach == "sarsa":
                muc_tieu = r + Q[s2, a2]
            else:
                muc_tieu = r + Q[s2].max()
            Q[s, a] += alpha * (muc_tieu - Q[s, a])
            s, a = s2, a2
            if ket_thuc or cat_ngang:
                break
        tong.append(G)
    return Q, np.array(tong)


ghe = {c: np.zeros(48) for c in ("sarsa", "q")}
tong_vach = {}
for cach in ("sarsa", "q"):
    tong_vach[cach] = np.array([hoc_vach(cach, seed=k, ghe=ghe[cach])[1] for k in range(50)])
assert round(tong_vach["sarsa"][:, -100:].mean(), 1) == -25.7 and round(tong_vach["q"][:, -100:].mean(), 1) == -48.5

# ---------------------------------------------------------------- vẽ hình
NEN = "#FBF8F1"
XANH, CAM, DO, XAM, CHU, LUOI = "#1F5F8B", "#E07A1F", "#C0392B", "#8A8170", "#2B2B2B", "#E6DECD"
HO = "#33414F"
co_sans = {f.name for f in font_manager.fontManager.ttflist}
FONT = "Be Vietnam Pro" if "Be Vietnam Pro" in co_sans else "DejaVu Sans"
plt.rcParams.update({
    "font.family": FONT, "font.size": 12.5, "text.color": CHU, "axes.labelcolor": CHU,
    "xtick.color": CHU, "ytick.color": CHU, "axes.edgecolor": XAM,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": LUOI, "grid.alpha": 0.8, "axes.axisbelow": True,
    "figure.facecolor": NEN, "axes.facecolor": NEN, "savefig.facecolor": NEN,
    "savefig.bbox": "tight", "svg.hashsalt": "ch34",
})
desc = env.unwrapped.desc.astype(str)


def phay(x, pos=None):
    return f"{x:g}".replace(".", ",")


def bo_truc(ax, rong, cao):
    ax.set_xlim(0, rong)
    ax.set_ylim(cao, 0)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.grid(False)
    for sp in ax.spines.values():
        sp.set_visible(False)


def luoi_ho(ax, V, vmax, so=True):
    ax.imshow(V.reshape(4, 4), cmap="Blues", vmin=0, vmax=vmax, extent=(0, 4, 4, 0))
    for i in range(4):
        for j in range(4):
            s = 4 * i + j
            if desc[i, j] == "H":
                ax.add_patch(plt.Rectangle((j, i), 1, 1, facecolor=HO, edgecolor=NEN, lw=3))
            elif desc[i, j] == "G":
                ax.add_patch(plt.Rectangle((j, i), 1, 1, facecolor="#F4D9B8", edgecolor=NEN, lw=3))
                ax.text(j + 0.5, i + 0.5, "G", ha="center", va="center", fontsize=14, fontweight="bold")
            else:
                ax.add_patch(plt.Rectangle((j, i), 1, 1, facecolor="none", edgecolor=NEN, lw=3))
                if so:
                    ax.text(j + 0.5, i + 0.5, f"{V[s]:.3f}".replace(".", ","), ha="center", va="center", fontsize=11,
                            color="#FFFFFF" if V[s] > 0.6 * vmax else CHU)
    bo_truc(ax, 4, 4)


# Hình 34.1: chính sách tối ưu và giá trị tối ưu
fig, ax = plt.subplots(figsize=(5.6, 5.6))
luoi_ho(ax, V_sao, 1.0, so=False)
huong = {0: (-1, 0), 1: (0, 1), 2: (1, 0), 3: (0, -1)}
for s in range(16):
    i, j = divmod(s, 4)
    if desc[i, j] in "HG":
        continue
    dx, dy = huong[tham[s]]
    ax.annotate("", xy=(j + 0.5 + 0.3 * dx, i + 0.4 + 0.3 * dy), xytext=(j + 0.5 - 0.3 * dx, i + 0.4 - 0.3 * dy),
                arrowprops=dict(arrowstyle="-|>", color=CAM, lw=2.6, mutation_scale=20))
    ax.text(j + 0.5, i + 0.83, f"{V_sao[s]:.3f}".replace(".", ","), ha="center", va="center", fontsize=11,
            color="#FFFFFF" if V_sao[s] > 0.6 else CHU)
ax.set_title("chính sách tối ưu, gamma = 0,99", fontsize=12.5)
fig.savefig(OUT / "h1_toi_uu.svg", metadata={"Date": None})
plt.close(fig)

# Hình 34.2: giá trị lan dần
fig, axs = plt.subplots(1, 5, figsize=(15, 3.6))
for ax, k in zip(axs, (1, 3, 6, 20, 571)):
    luoi_ho(ax, anh[k], 0.9, so=False)
    ax.set_title(f"sau {k} vòng", fontsize=12.5)
fig.tight_layout()
fig.savefig(OUT / "h2_lan_gia_tri.svg", metadata={"Date": None})
plt.close(fig)

# Hình 34.3: Q-learning theo số tập
fig, ax = plt.subplots(figsize=(9, 5))
x = np.arange(500, 20_001, 500)
for eps, mau in ((0.5, XANH), (1.0, CAM), (0.1, XAM)):
    ax.plot(x, tb[eps], color=mau, lw=2, label=f"ε = {phay(eps)}")
ax.axhline(0.8235, color=CHU, lw=1, ls="--")
ax.text(20_000, 0.84, "chính sách tối ưu, 0,8235", ha="right", va="bottom", fontsize=11)
ax.set_xlabel("số tập đã học")
ax.set_ylabel("xác suất tới đích của chính sách tham lam")
ax.set_ylim(0, 0.92)
ax.yaxis.set_major_formatter(phay)
ax.xaxis.set_major_formatter(lambda v, p: f"{int(v):,}".replace(",", " "))
ax.legend(loc="lower right", frameon=False)
fig.tight_layout()
fig.savefig(OUT / "h3_q_learning.svg", metadata={"Date": None})
plt.close(fig)

# Hình 34.4: vách đá
fig = plt.figure(figsize=(11, 8.2))
gs = fig.add_gridspec(3, 1, height_ratios=[1, 1, 1.6], hspace=0.35)
vmax = max(ghe["sarsa"].max(), ghe["q"].max())
for hang, (cach, ten) in enumerate((("q", "Q-learning"), ("sarsa", "SARSA"))):
    ax = fig.add_subplot(gs[hang])
    ax.imshow(np.log1p(ghe[cach]).reshape(4, 12), cmap="Blues", vmin=0, vmax=np.log1p(vmax), extent=(0, 12, 4, 0))
    for j in range(1, 11):
        ax.add_patch(plt.Rectangle((j, 3), 1, 1, facecolor=HO, edgecolor=NEN, lw=2))
    ax.text(6, 3.5, "vực", ha="center", va="center", color="#FFFFFF", fontsize=12)
    ax.text(0.5, 3.5, "S", ha="center", va="center", fontsize=13, fontweight="bold", color="#FFFFFF")
    ax.add_patch(plt.Rectangle((11, 3), 1, 1, facecolor="#F4D9B8", edgecolor=NEN, lw=2))
    ax.text(11.5, 3.5, "G", ha="center", va="center", fontsize=13, fontweight="bold")
    for i in range(5):
        ax.axhline(i, color=NEN, lw=2)
    for j in range(13):
        ax.axvline(j, color=NEN, lw=2)
    bo_truc(ax, 12, 4)
    ax.set_title(f"{ten}: số lần ghé mỗi ô trong 100 tập cuối (thang log)", fontsize=12)
ax = fig.add_subplot(gs[2])
for cach, ten, mau in (("sarsa", "SARSA", XANH), ("q", "Q-learning", CAM)):
    y = tong_vach[cach].mean(0)
    y = np.convolve(y, np.ones(10) / 10, mode="valid")
    ax.plot(np.arange(10, 501), y, color=mau, lw=2, label=ten)
ax.set_ylim(-150, 0)
ax.set_xlabel("tập")
ax.set_ylabel("lợi nhuận mỗi tập")
ax.legend(loc="lower right", frameon=False)
fig.savefig(OUT / "h4_vach_da.svg", metadata={"Date": None})
plt.close(fig)

# số để đối chiếu mô tả hình
print("q hàng 2:", ghe["q"].reshape(4, 12)[2].astype(int).tolist())
print("sarsa hàng 0:", ghe["sarsa"].reshape(4, 12)[0].astype(int).tolist())
for cach in ("sarsa", "q"):
    y = np.convolve(tong_vach[cach].mean(0), np.ones(10) / 10, mode="valid")
    print(cach, y[[0, 40, 90, 200, 490]].round(1))
print("xong", sorted(p.name for p in OUT.iterdir()))
