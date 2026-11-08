"""Chương 36 Policy gradient: chạy hàm hoc của trang 2 với 3 cách x 5 seed, vẽ hình 36.1.

Chạy:  .venv/bin/python scripts/hinh/ch36_policy_gradient.py      (khoảng 4 phút: 15 lần chạy, 5 tiến trình song song, mỗi tiến trình 1 luồng)
Kết quả: public/hinh/ch36/h1_ba_cach.svg. Con số nào trong bài sai thì một câu assert báo lỗi.
"""
import contextlib
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
OUT = GOC / "public" / "hinh" / "ch36"
OUT.mkdir(parents=True, exist_ok=True)
torch.set_num_threads(1)


# ---------------------------------------------------------------- y hệt trang 1 và 2
def mlp(so_ra):
    return nn.Sequential(nn.Linear(4, 128), nn.ReLU(), nn.Linear(128, so_ra))


env = gym.make("CartPole-v1")

def danh_gia(pi, n=20, seed=10_000):                 # như Chương 35: chính sách tham lam, 20 tập cố định
    e = gym.make("CartPole-v1")
    tong = []
    for i in range(n):
        s, _ = e.reset(seed=seed + i)
        G = 0
        while True:
            with torch.no_grad():
                a = int(pi(torch.as_tensor(s)).argmax())
            s, r, ket_thuc, cat_ngang, _ = e.step(a)
            G += r
            if ket_thuc or cat_ngang:
                break
        tong.append(G)
    return float(np.mean(tong))

def hoc(cach="reinforce", n_tap=1000, seed=0, lr=1e-3, lr_v=1e-3, gamma=0.99, in_moi=100):
    torch.manual_seed(seed)
    pi = mlp(2)                                      # mạng chính sách
    opt = torch.optim.Adam(pi.parameters(), lr=lr, fused=True)
    v = mlp(1)                                       # mạng giá trị, dùng ở trang 3 và 4
    opt_v = torch.optim.Adam(v.parameters(), lr=lr_v, fused=True)
    env.reset(seed=seed)
    diem = []
    for tap in range(1, n_tap + 1):
        s, _ = env.reset()                           # 1. chơi một tập theo chính sách hiện tại
        log_p, R, S, S2, D = [], [], [], [], []
        while True:
            S.append(torch.as_tensor(s))
            phan_phoi = torch.distributions.Categorical(logits=pi(S[-1]))
            a = phan_phoi.sample()                   # lấy mẫu, không argmax
            log_p.append(phan_phoi.log_prob(a))
            s, r, ket_thuc, cat_ngang, _ = env.step(int(a))
            R.append(r)
            S2.append(torch.as_tensor(s))
            D.append(float(ket_thuc))
            if ket_thuc or cat_ngang:
                break
        G, loi_nhuan = 0.0, []                       # 2. lợi nhuận từ mỗi bước về sau
        for r in reversed(R):
            G = r + gamma * G
            loi_nhuan.append(G)
        G_t = torch.tensor(loi_nhuan[::-1], dtype=torch.float32)
        S, S2, R, D = torch.stack(S), torch.stack(S2), torch.tensor(R), torch.tensor(D)
        if cach == "reinforce":
            loi_the = G_t                            # trọng số của mỗi hành động
        elif cach == "chuan_hoa":                    # bài tập 36.3: chuẩn hóa trong tập
            loi_the = (G_t - G_t.mean()) / (G_t.std() + 1e-8)
        else:                                        # trang 3 và 4: học V, trừ nó đi
            V = v(S).squeeze(1)
            if cach == "baseline":
                muc_tieu = G_t                       # V học theo lợi nhuận thật của tập
            else:
                with torch.no_grad():
                    muc_tieu = R + gamma * (1 - D) * v(S2).squeeze(1)   # actor-critic: mục tiêu TD
            loss_v = F.mse_loss(V, muc_tieu)
            opt_v.zero_grad()
            loss_v.backward()
            opt_v.step()
            loi_the = muc_tieu - V.detach()          # lợi thế: tốt hơn mong đợi bao nhiêu
        loss = -(torch.stack(log_p) * loi_the).sum() # 3. một bước gradient, dấu trừ để đi lên
        opt.zero_grad()
        loss.backward()
        opt.step()
        diem.append(len(R))                          # thưởng 1 mỗi bước: điểm bằng số bước
        if tap % in_moi == 0:
            print(tap, round(np.mean(diem[-in_moi:]), 1), danh_gia(pi))
    return pi


CACH = {"reinforce": {}, "baseline": {}, "actor_critic": {"lr_v": 1e-2}}


def mot_lan(viec):
    cach, seed = viec
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        hoc(cach, seed=seed, **CACH[cach])
    dong = [d.split() for d in buf.getvalue().strip().splitlines()]
    return cach, seed, [float(d[1]) for d in dong], [float(d[2]) for d in dong]


if __name__ == "__main__":
    with Pool(5) as p:
        kq = p.map(mot_lan, [(c, sd) for c in CACH for sd in range(5)])
    hoc_ = {c: np.array([k[2] for k in kq if k[0] == c]) for c in CACH}
    dg = {c: np.array([k[3] for k in kq if k[0] == c]) for c in CACH}
    for c in CACH:
        print(c, "trung bình lúc học", hoc_[c].mean(0).round(1).tolist())
        print("   min", hoc_[c].min(0).round(1).tolist(), "max", hoc_[c].max(0).round(1).tolist())
        print("   đánh giá cuối", dg[c][:, -1].tolist(), "số seed từng chạm 500", int((dg[c].max(1) == 500).sum()))
    # seed 0 khớp trang 2, 3, 4
    assert hoc_["reinforce"][0].tolist() == [28.0, 69.5, 205.0, 202.1, 275.5, 404.2, 401.9, 362.6, 455.4, 433.9]
    assert hoc_["baseline"][0].tolist() == [27.7, 85.1, 230.5, 342.0, 431.2, 453.8, 465.2, 487.4, 484.0, 458.2]
    assert [round(hoc_[c].mean(0)[i], 1) for c in CACH for i in (4, 9)] == [291.4, 419.9, 408.8, 477.2, 163.9, 221.3]
    assert (hoc_["actor_critic"].max(0) < hoc_["baseline"].min(0)).all()
    assert hoc_["baseline"][:, -1].min() == 458.2 and hoc_["reinforce"][:, -1].min() == 317.1
    assert hoc_["actor_critic"][0].tolist() == [16.8, 45.4, 126.2, 51.0, 157.5, 253.2, 140.3, 223.2, 397.1, 322.4]

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
        "savefig.bbox": "tight", "svg.hashsalt": "ch36",
    })
    x = np.arange(100, 1001, 100)
    fig, ax = plt.subplots(figsize=(9, 5))
    for c, ten, mau in (("baseline", "REINFORCE có baseline", XANH), ("reinforce", "REINFORCE trơn", CAM), ("actor_critic", "actor-critic một bước", XAM)):
        ax.fill_between(x, hoc_[c].min(0), hoc_[c].max(0), color=mau, alpha=0.15, lw=0)
        ax.plot(x, hoc_[c].mean(0), color=mau, lw=2.5, marker="o", ms=4, label=ten)
    ax.set_xlabel("số tập")
    ax.set_ylabel("điểm trung bình 100 tập lúc học")
    ax.set_ylim(0, 510)
    ax.legend(loc="upper left", frameon=False)
    fig.tight_layout()
    fig.savefig(OUT / "h1_ba_cach.svg", metadata={"Date": None})
    plt.close(fig)
    print("xong", sorted(p.name for p in OUT.iterdir()))
