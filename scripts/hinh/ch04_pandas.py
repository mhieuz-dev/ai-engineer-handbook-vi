"""Chương 4 Pandas và Matplotlib: tính lại các con số dùng trong bài và vẽ hình.

Chạy:  .venv/bin/python scripts/hinh/ch04_pandas.py
Kết quả: các file SVG trong public/hinh/ch04/. Con số nào trong bài sai thì một câu assert báo lỗi.
"""
import io
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import font_manager
from matplotlib.ticker import FuncFormatter

GOC = Path(__file__).resolve().parents[2]
OUT = GOC / "public" / "hinh" / "ch04"
OUT.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- số liệu (Bảng 4.1)
CSV = """ten,lop,gio,ngu,diem
A,L1,1,7,2
B,L1,2,6,4
C,L1,3,8,5
D,L1,4,7,7
E,L2,5,6,6
F,L2,2,,3.5
G,L2,6,8,8.5
H,L2,3,5,4
I,L1,7,7,9
K,L2,4,6,6.5
"""
df = pd.read_csv(io.StringIO(CSV))
assert df.shape == (10, 5) and df["ngu"].isna().sum() == 1
assert df["diem"].mean() == 5.55 and df["ngu"].median() == 7.0
df["ngu"] = df["ngu"].fillna(df["ngu"].median())
tb_lop = df.groupby("lop")["diem"].mean()
assert np.isclose(tb_lop["L1"], 5.4) and np.isclose(tb_lop["L2"], 5.7)
assert round(df["gio"].corr(df["diem"]), 4) == 0.9566
x, y = df["gio"].to_numpy(float), df["diem"].to_numpy(float)
w = ((x - x.mean()) * (y - y.mean())).sum() / ((x - x.mean()) ** 2).sum()
b = y.mean() - w * x.mean()
assert round(w, 4) == 1.1417 and round(b, 4) == 1.3255

# ---------------------------------------------------------------- vẽ hình (cùng bảng màu Chương 10)
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
    "savefig.bbox": "tight", "svg.hashsalt": "ch04",
})
PHAY = FuncFormatter(lambda v, _: f"{v:g}".replace(".", ","))


def luu(fig, ten):
    fig.savefig(OUT / ten, metadata={"Date": None})  # bỏ ngày giờ để file không đổi giữa các lần chạy
    plt.close(fig)


# Hình 4.1: điểm theo giờ học, tô màu theo lớp, kèm đường hồi quy
fig, ax = plt.subplots(figsize=(6.2, 4.2))
for lop, mau in (("L1", XANH), ("L2", CAM)):
    d = df[df["lop"] == lop]
    ax.scatter(d["gio"], d["diem"], s=70, color=mau, label=f"Lớp {lop}", zorder=3)
    for _, h in d.iterrows():
        ax.annotate(h["ten"], (h["gio"], h["diem"]), xytext=(6, -4), textcoords="offset points", fontsize=11)
xx = np.linspace(0.5, 7.5, 2)
ax.plot(xx, w * xx + b, color=XAM, lw=1.6, ls="--", label="đường hồi quy", zorder=2)
ax.set_xlabel("Giờ tự học mỗi tuần")
ax.set_ylabel("Điểm thi")
ax.yaxis.set_major_formatter(PHAY)
ax.legend(loc="upper left", fontsize=11, facecolor=NEN, edgecolor=LUOI, framealpha=1)
luu(fig, "h1_scatter.svg")

# Hình 4.2: histogram điểm thi
fig, ax = plt.subplots(figsize=(6.2, 3.6))
dem, bien, _ = ax.hist(df["diem"], bins=[2, 4, 6, 8, 10], color=XANH, edgecolor=NEN, linewidth=2)
assert list(dem) == [2, 3, 3, 2]  # [2,4): A F; [4,6): B C H; [6,8): D E K; [8,10]: G I
ax.set_xticks(bien)
ax.set_xlabel("Điểm thi")
ax.set_ylabel("Số bạn")
ax.set_yticks(range(0, 5))
luu(fig, "h2_histogram.svg")

# Hình 4.3: điểm trung bình theo lớp
fig, ax = plt.subplots(figsize=(5.0, 3.4))
cot = ax.bar(tb_lop.index, tb_lop.values, color=[XANH, CAM], width=0.55)
ax.bar_label(cot, labels=[f"{v:.1f}".replace(".", ",") for v in tb_lop.values], padding=4)
ax.set_ylim(0, 7)
ax.set_ylabel("Điểm trung bình")
ax.yaxis.set_major_formatter(PHAY)
ax.grid(axis="x", visible=False)
luu(fig, "h3_trung_binh_lop.svg")
print("Đã vẽ 3 hình vào", OUT)
