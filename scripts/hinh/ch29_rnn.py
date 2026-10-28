"""Chương 29 RNN, LSTM, GRU: đo lại gradient theo bước (trang 2) và huấn luyện bài nhớ ký hiệu đầu (trang 3).

Chạy:  .venv/bin/python scripts/hinh/ch29_rnn.py      (khoảng 1 phút trên CPU 16 nhân)
Kết quả: public/hinh/ch29/h1_gradient_theo_buoc.svg, h2_kep_gradient.svg.
Con số nào trong bài sai thì một câu assert báo lỗi.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import torch
import torch.nn as nn
from matplotlib import font_manager
from matplotlib.ticker import FuncFormatter

GOC = Path(__file__).resolve().parents[2]
OUT = GOC / "public" / "hinh" / "ch29"
OUT.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------- hình 1: gradient theo bước, y hệt trang 2 và 3
def do_grad(mang, T, seed=0):
    torch.manual_seed(seed)
    x = torch.randn(1, T, 8, requires_grad=True)
    ra, _ = mang(x)
    ra[0, -1].sum().backward()
    return x.grad[0].norm(dim=1)


def mang(loai, nhan_wh=1.0, bias_quen=0.0):
    torch.manual_seed(0)
    m = loai(8, 32, batch_first=True)
    with torch.no_grad():
        m.weight_hh_l0 *= nhan_wh
        if bias_quen:
            m.bias_ih_l0[32:64] += bias_quen
    return m


g_rnn = do_grad(mang(nn.RNN), 100)
g_rnn3 = do_grad(mang(nn.RNN, nhan_wh=3.0), 100)
g_lstm = do_grad(mang(nn.LSTM), 100)
g_lstm3 = do_grad(mang(nn.LSTM, bias_quen=3.0), 100)
so = [f"{g[0].item():.1e}" for g in (g_rnn, g_rnn3, g_lstm, g_lstm3)]
print(so)
assert so == ["0.0e+00", "6.1e+01", "7.1e-22", "4.4e-02"]
assert f"{g_rnn[99].item():.1e}" == "2.0e+00" and f"{g_rnn[50].item():.1e}" == "3.0e-14"


# ---------------------------------------------------------------- hình 2: bài nhớ ký hiệu đầu, y hệt trang 3
def tao_lo(n, T, g):
    X = torch.randint(0, 10, (n, T), generator=g)
    return X, X[:, 0].clone()


class Nho(nn.Module):
    def __init__(self, loai, bias_cong=0.0):
        super().__init__()
        self.nhung = nn.Embedding(10, 16)
        self.loi = loai(16, 64, batch_first=True)
        self.ra = nn.Linear(64, 10)
        if bias_cong:
            with torch.no_grad():
                self.loi.bias_ih_l0[64:128] += bias_cong

    def forward(self, x):
        ra, _ = self.loi(self.nhung(x))
        return self.ra(ra[:, -1])


ce = nn.CrossEntropyLoss()


def huan_luyen(kep, T=50, so_buoc=1500):
    torch.manual_seed(0)
    m = Nho(nn.LSTM, 3.0)
    opt = torch.optim.Adam(m.parameters(), lr=1e-3)
    g = torch.Generator().manual_seed(1)
    Xte, yte = tao_lo(2000, T, torch.Generator().manual_seed(2))
    do_dai, acc = [], {}
    for b in range(1, so_buoc + 1):
        x, y = tao_lo(64, T, g)
        opt.zero_grad()
        ce(m(x), y).backward()
        do_dai.append(nn.utils.clip_grad_norm_(m.parameters(), kep or float("inf")).item())
        opt.step()
        if b % 50 == 0:                                 # đo dày hơn trang 3, không đổi quá trình huấn luyện
            with torch.no_grad():
                acc[b] = round((m(Xte).argmax(1) == yte).float().mean().item(), 3)
    return do_dai, acc


dd0, acc0 = huan_luyen(None)
dd1, acc1 = huan_luyen(1.0)
moc0, moc1 = [acc0[b] for b in range(250, 1501, 250)], [acc1[b] for b in range(250, 1501, 250)]
print(moc0, round(max(dd0), 1), moc1, round(max(dd1), 1))
assert acc0[1150] == 1.0 and acc0[1200] == 0.878 and dd0.index(max(dd0)) + 1 == 1194   # cú vọt và cú rơi ở trang 3
assert f"{g_rnn[19].item():.1e}" == "2.7e-22" and g_rnn[9].item() == 0
assert moc0 == [0.746, 0.867, 0.988, 1.0, 0.899, 1.0] and round(max(dd0), 1) == 140.0
assert moc1 == [0.697, 0.983, 0.999, 1.0, 0.994, 0.994] and round(max(dd1), 1) == 723.6

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
    "savefig.bbox": "tight", "svg.hashsalt": "ch29",
})
PHAY = FuncFormatter(lambda v, _: f"{v:g}".replace(".", ","))

fig, ax = plt.subplots(figsize=(8, 4.8))
t = torch.arange(1, 101)
for g, ten, mau in [(g_rnn3, "RNN, $W_h$ nhân 3", DO), (g_lstm3, "LSTM, bias cổng quên 3", CAM),
                    (g_lstm, "LSTM mặc định", XAM), (g_rnn, "RNN mặc định", XANH)]:
    g = g.clone()
    g[g == 0] = float("nan")                            # 0 trong float32 không vẽ được trên thang log
    ax.plot(t, g, color=mau, lw=2, label=ten)
ax.set_yscale("log")
ax.set_ylim(1e-22, 1e3)
ax.set_xlim(1, 100)
ax.set_xlabel("Bước $t$ của đầu vào $x_t$ (chuỗi 100 bước, loss ở bước 100)")
ax.set_ylabel("Độ lớn gradient")
ax.legend(frameon=False, loc="lower right", fontsize=11)
fig.savefig(OUT / "h1_gradient_theo_buoc.svg", metadata={"Date": None})

fig, (a1, a2) = plt.subplots(2, 1, figsize=(8, 6.4), sharex=True, gridspec_kw={"height_ratios": [1, 1.2]})
b = range(1, 1501)
a1.plot(b, dd0, color=XANH, lw=1, label="không kẹp")
a1.plot(b, dd1, color=CAM, lw=1, alpha=0.8, label="kẹp ở 1,0")
a1.axhline(1.0, color=XAM, lw=1.2, ls=":")
a1.set_yscale("log")
a1.set_ylabel("Độ dài gradient\ntrước khi kẹp")
a1.legend(frameon=False, loc="upper left", fontsize=11, ncol=2)
for acc, mau, ten in [(acc0, XANH, "không kẹp"), (acc1, CAM, "kẹp ở 1,0")]:
    a2.plot(list(acc), list(acc.values()), "o-", color=mau, lw=2, ms=3.5, label=ten)
a2.set_ylim(0, 1.03)
a2.set_xlabel("Bước huấn luyện")
a2.set_ylabel("Độ chính xác test")
a2.yaxis.set_major_formatter(PHAY)
a2.legend(frameon=False, loc="lower right", fontsize=11)
fig.savefig(OUT / "h2_kep_gradient.svg", metadata={"Date": None})
print("OK")
