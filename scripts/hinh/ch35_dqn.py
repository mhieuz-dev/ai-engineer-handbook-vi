"""Chương 35 Deep Q-Network: chạy DQN của trang 2 với 6 cấu hình x 5 seed, vẽ hình 35.1 và in số cho bảng 35.1 và các bài tập.

Chạy:  .venv/bin/python scripts/hinh/ch35_dqn.py      (khoảng 5 phút: 30 lần chạy, 5 tiến trình song song, mỗi tiến trình 1 luồng)
Kết quả: public/hinh/ch35/h1_duong_hoc.svg, và bảng số in ra màn hình.
Con số nào trong bài sai thì một câu assert báo lỗi.
"""
import contextlib
import copy
import io
from multiprocessing import Pool
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import gymnasium as gym
import matplotlib.pyplot as plt
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from matplotlib import font_manager

GOC = Path(__file__).resolve().parents[2]
OUT = GOC / "public" / "hinh" / "ch35"
OUT.mkdir(parents=True, exist_ok=True)

torch.set_num_threads(1)
env = gym.make("CartPole-v1")
S0 = torch.as_tensor(env.reset(seed=0)[0])


# ---------------------------------------------------------------- y hệt trang 1 và 2
def tao_mang():
    return nn.Sequential(nn.Linear(4, 128), nn.ReLU(), nn.Linear(128, 128), nn.ReLU(), nn.Linear(128, 2))


def danh_gia(mang, n=20, seed=10_000):
    e = gym.make("CartPole-v1")
    tong = []
    for i in range(n):
        s, _ = e.reset(seed=seed + i)
        G = 0
        while True:
            with torch.no_grad():
                a = int(mang(torch.as_tensor(s)).argmax())
            s, r, ket_thuc, cat_ngang, _ = e.step(a)
            G += r
            if ket_thuc or cat_ngang:
                break
        tong.append(G)
    return float(np.mean(tong))


def dqn(n_buoc=50_000, seed=0, muc_tieu_rieng=True, replay=True, double=False, ket_thuc_khi_cat=False,
        lr=5e-4, cap_nhat_dich=100, bo_nho=50_000, lo=128, gamma=0.99, eps_cuoi=0.05, eps_buoc=10_000,
        bat_dau=1000, danh_gia_moi=5000):
    torch.manual_seed(seed)
    rng = np.random.default_rng(seed)
    q = tao_mang()
    q_dich = copy.deepcopy(q)
    opt = torch.optim.Adam(q.parameters(), lr=lr, fused=True)
    S, S2 = np.zeros((bo_nho, 4), np.float32), np.zeros((bo_nho, 4), np.float32)
    A, Rw, D = np.zeros(bo_nho, np.int64), np.zeros(bo_nho, np.float32), np.zeros(bo_nho, np.float32)
    n, G, diem_tap = 0, 0, []
    tot_nhat, ban_tot = -1, None
    s, _ = env.reset(seed=seed)
    for t in range(1, n_buoc + 1):
        eps = max(eps_cuoi, 1 - (1 - eps_cuoi) * t / eps_buoc)
        if rng.random() < eps:
            a = int(rng.integers(2))
        else:
            with torch.no_grad():
                a = int(q(torch.as_tensor(s)).argmax())
        s2, r, ket_thuc, cat_ngang, _ = env.step(a)
        G += r
        i = n % bo_nho
        S[i], A[i], Rw[i], S2[i] = s, a, r, s2
        D[i] = float(ket_thuc or (ket_thuc_khi_cat and cat_ngang))
        n += 1
        s = s2
        if ket_thuc or cat_ngang:
            diem_tap.append(G)
            G = 0
            s, _ = env.reset()
        if n >= bat_dau:
            idx = rng.integers(min(n, bo_nho), size=lo) if replay else np.array([i])
            sb, ab, rb, s2b, db = map(torch.as_tensor, (S[idx], A[idx], Rw[idx], S2[idx], D[idx]))
            with torch.no_grad():
                mang_dich = q_dich if muc_tieu_rieng else q
                if double:
                    q_sau = mang_dich(s2b).gather(1, q(s2b).argmax(1, keepdim=True)).squeeze(1)
                else:
                    q_sau = mang_dich(s2b).max(1).values
                y = rb + gamma * (1 - db) * q_sau
            q_sa = q(sb).gather(1, ab.unsqueeze(1)).squeeze(1)
            loss = F.smooth_l1_loss(q_sa, y)
            opt.zero_grad()
            loss.backward()
            opt.step()
            if t % cap_nhat_dich == 0:
                q_dich.load_state_dict(q.state_dict())
        if t % danh_gia_moi == 0:
            diem = danh_gia(q)
            print(t, len(diem_tap), round(np.mean(diem_tap[-20:]), 1), diem)
            if diem > tot_nhat:
                tot_nhat, ban_tot = diem, copy.deepcopy(q)
    return ban_tot, q


CAU_HINH = {"day_du": {}, "khong_dich": {"muc_tieu_rieng": False}, "khong_replay": {"replay": False},
            "dich_500": {"cap_nhat_dich": 500}, "double": {"double": True}, "cat_la_ket_thuc": {"ket_thuc_khi_cat": True}}


def mot_lan(viec):
    ten, seed = viec
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        _, cuoi = dqn(seed=seed, **CAU_HINH[ten])
    diem = [float(d.split()[-1]) for d in buf.getvalue().strip().splitlines()]
    with torch.no_grad():
        q0 = cuoi(S0).max().item()
    return ten, seed, diem, danh_gia(cuoi, n=100, seed=20_000), q0


if __name__ == "__main__":
    with Pool(5) as p:
        kq = p.map(mot_lan, [(ten, sd) for ten in CAU_HINH for sd in range(5)])
    bang = {}
    for ten in CAU_HINH:
        dong = [k for k in kq if k[0] == ten]
        diem = np.array([k[2] for k in dong])
        bang[ten] = dict(cuoi=round(diem[:, -1].mean(), 1), cham_500=int((diem.max(1) == 500).sum()),
                         cao_nhat=round(diem.max(1).mean(), 1), test=round(np.mean([k[3] for k in dong]), 1),
                         q0=round(np.mean([k[4] for k in dong]), 1), diem=diem)
        print(ten, {k: v for k, v in bang[ten].items() if k != "diem"})
        print("   ", [k[2] for k in dong])
        print("    test", [round(k[3], 1) for k in dong], "q0", [round(k[4], 1) for k in dong])
    # seed 0 khớp trang 3 và 4
    assert bang["day_du"]["diem"][0].tolist() == [177.35, 95.2, 101.2, 129.95, 90.05, 151.1, 104.2, 500.0, 56.15, 500.0]
    assert bang["khong_dich"]["diem"][0].tolist() == [9.45] * 10
    assert bang["khong_replay"]["diem"][0].max() == 93.5
    so = {t: (float(bang[t]["cuoi"]), bang[t]["cham_500"], float(bang[t]["cao_nhat"]), float(bang[t]["test"]), float(bang[t]["q0"])) for t in bang}
    assert so["day_du"] == (478.1, 4, 484.2, 479.2, 128.1), so["day_du"]
    assert so["khong_dich"][:4] == (9.4, 0, 9.4, 9.3) and so["khong_dich"][4] > 2e8, so["khong_dich"]
    assert so["khong_replay"][:4] == (56.8, 0, 158.4, 56.4), so["khong_replay"]
    assert so["dich_500"][:4] == (284.8, 1, 352.0, 284.8), so["dich_500"]
    assert so["double"][3:] == (389.4, 137.0), so["double"]
    assert so["cat_la_ket_thuc"][1] == 5 and so["cat_la_ket_thuc"][3] == 360.6, so["cat_la_ket_thuc"]

    # Hình 35.1: năm seed của DQN đầy đủ
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
        "savefig.bbox": "tight", "svg.hashsalt": "ch35",
    })
    x = np.arange(5000, 50_001, 5000)
    fig, ax = plt.subplots(figsize=(9, 5))
    diem = bang["day_du"]["diem"]
    for k in range(5):
        ax.plot(x, diem[k], color=XANH, lw=1, alpha=0.45, marker="o", ms=3.5, label="từng seed" if k == 0 else None)
    ax.plot(x, diem.mean(0), color=XANH, lw=3, label="trung bình 5 seed")
    ax.axhline(21.77, color=CAM, lw=1.2, ls="--")
    ax.text(50_000, 30, "chọn bừa, 21,8", ha="right", va="bottom", fontsize=11, color=CAM)
    ax.set_xlabel("số bước môi trường")
    ax.set_ylabel("điểm đánh giá (20 tập)")
    ax.set_ylim(0, 520)
    ax.xaxis.set_major_formatter(lambda v, p: f"{int(v):,}".replace(",", " "))
    ax.legend(loc="upper left", frameon=False)
    fig.tight_layout()
    fig.savefig(OUT / "h1_duong_hoc.svg", metadata={"Date": None})
    plt.close(fig)
    print("trung bình theo bước", diem.mean(0).round(1).tolist())
    print("xong", sorted(p.name for p in OUT.iterdir()))
