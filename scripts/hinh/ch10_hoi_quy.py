"""Chương 10 Hồi quy tuyến tính: tính lại mọi con số dùng trong bài và vẽ hình.

Chạy:  .venv/bin/python scripts/hinh/ch10_hoi_quy.py
Kết quả: các file SVG trong public/hinh/ch10/. Nếu một con số trong bài sai,
một câu assert bên dưới sẽ báo lỗi, vì vậy mỗi lần sửa bài thì chạy lại script này.
"""
import warnings
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
from matplotlib.ticker import FuncFormatter

GOC = Path(__file__).resolve().parents[2]
OUT = GOC / "public" / "hinh" / "ch10"
OUT.mkdir(parents=True, exist_ok=True)


def gan(a, b, tol=1e-9):
    """So sánh hai số thực với sai số tuyệt đối tol."""
    return abs(a - b) <= tol


# ---------------------------------------------------------------- số liệu
x = np.array([1.0, 2.0, 3.0, 4.0])  # giờ tự học mỗi tuần (bảng 10.1)
y = np.array([2.0, 4.0, 5.0, 7.0])  # điểm thi
n = len(x)

# Nghiệm đóng (trang 03)
assert x.mean() == 2.5 and y.mean() == 4.5
tich = (x - x.mean()) * (y - y.mean())
assert np.allclose(x - x.mean(), [-1.5, -0.5, 0.5, 1.5]) and np.allclose(y - y.mean(), [-2.5, -0.5, 0.5, 2.5])
assert gan((x - x.mean()).sum(), 0) and gan((y - y.mean()).sum(), 0)  # cột độ lệch cộng lại bằng 0
assert np.allclose(tich, [3.75, 0.25, 0.25, 3.75]) and gan(tich.sum(), 8)
assert np.allclose((x - x.mean()) ** 2, [2.25, 0.25, 0.25, 2.25]) and gan(((x - x.mean()) ** 2).sum(), 5)
w_ols = tich.sum() / ((x - x.mean()) ** 2).sum()
b_ols = y.mean() - w_ols * x.mean()
assert gan(w_ols, 1.6) and gan(b_ols, 0.5)
yhat = w_ols * x + b_ols
assert np.allclose(yhat, [2.1, 3.7, 5.3, 6.9])
e_ols = y - yhat
assert np.allclose(e_ols, [-0.1, 0.3, -0.3, 0.1]) and gan(e_ols.sum(), 0)
mse_ols = (e_ols ** 2).mean()
assert gan(mse_ols, 0.05)
ss_res, ss_tot = (e_ols ** 2).sum(), ((y - y.mean()) ** 2).sum()
assert gan(ss_res, 0.2) and gan(ss_tot, 13)
r2 = 1 - ss_res / ss_tot
assert gan(r2, 0.98462, 1e-5)  # "khoảng 0,985", tức 98,5%
print(f"OLS w={w_ols} b={b_ols} MSE={mse_ols} R2={r2:.5f}")

# Một outlier: bạn D gõ nhầm 4 giờ thành 40 giờ (khung vì sao bình phương, trang 02)
x_nham = np.array([1.0, 2.0, 3.0, 40.0])
w_nham = ((x_nham - x_nham.mean()) * (y - y.mean())).sum() / ((x_nham - x_nham.mean()) ** 2).sum()
assert gan(w_nham, 0.0903, 1e-4)  # độ dốc tụt từ 1,6 xuống còn khoảng 0,09
print(f"outlier 40 gio: w={w_nham:.4f}")

# Một bước gradient descent từ w = b = 0, η = 0,05 (trang 03)
LR = 0.05
w, b = 0.0, 0.0
e = y - (w * x + b)
assert np.allclose(e, [2, 4, 5, 7]) and gan((e ** 2).mean(), 23.5)
assert gan((x * e).sum(), 53) and gan(e.sum(), 18)
gw, gb = -2 / n * (x * e).sum(), -2 / n * e.sum()
assert gan(gw, -26.5) and gan(gb, -9)
w, b = w - LR * gw, b - LR * gb
assert gan(w, 1.325) and gan(b, 0.45)
y1 = w * x + b
assert np.allclose(y1, [1.775, 3.1, 4.425, 5.75])
mse1 = ((y - y1) ** 2).mean()
assert gan(mse1, 0.6884375)
assert gan(1 - mse1 / 23.5, 0.9707, 1e-4)  # "giảm hơn 97%"

# Bài 10.2: bước thứ hai.
# Bản PDF mẫu ghi Σ x·e = 9,05 và w = 1,55125: đó là lỗi cộng tay.
# Đúng là 0,225 + 1,8 + 1,725 + 5 = 8,75, nên w = 1,54375 (code GD cũng ra đúng số này).
e2 = y - y1
assert np.allclose(e2, [0.225, 0.9, 0.575, 1.25])
assert np.allclose(x * e2, [0.225, 1.8, 1.725, 5.0])
assert gan((x * e2).sum(), 8.75) and gan(e2.sum(), 2.95)
gw2, gb2 = -2 / n * (x * e2).sum(), -2 / n * e2.sum()
assert gan(gw2, -4.375) and gan(gb2, -1.475)
w2, b2 = w - LR * gw2, b - LR * gb2
assert gan(w2, 1.54375) and gan(b2, 0.52375)
mse2 = ((y - (w2 * x + b2)) ** 2).mean()
assert gan(mse2, 0.0676, 1e-4)
assert gan(mse2, 0.06761484375)  # trùng MSE ở bước 2 của code GD
assert np.allclose(w2 * x + b2, [2.0675, 3.61125, 5.155, 6.69875])
assert np.allclose(y - (w2 * x + b2), [-0.0675, 0.38875, -0.155, 0.30125])
assert gan(1 - mse2 / mse1, 0.9018, 1e-4)  # bước 2 giảm thêm khoảng 90%
print(f"buoc 2: w={w2} b={b2} MSE={mse2}")

# Bài 10.1: thêm sinh viên E (x = 5, y = 6)
x5, y5 = np.append(x, 5.0), np.append(y, 6.0)
assert gan(x5.mean(), 3) and gan(y5.mean(), 4.8)
s_xy = ((x5 - x5.mean()) * (y5 - y5.mean())).sum()
s_xx = ((x5 - x5.mean()) ** 2).sum()
assert np.allclose(x5 - x5.mean(), [-2, -1, 0, 1, 2]) and np.allclose(y5 - y5.mean(), [-2.8, -0.8, 0.2, 2.2, 1.2])
assert np.allclose((x5 - x5.mean()) * (y5 - y5.mean()), [5.6, 0.8, 0, 2.2, 2.4])
assert np.allclose((x5 - x5.mean()) ** 2, [4, 1, 0, 1, 4])
assert gan(s_xy, 11) and gan(s_xx, 10)
assert gan((x5 - x5.mean()).sum(), 0) and gan((y5 - y5.mean()).sum(), 0)
assert gan(s_xy / s_xx, 1.1) and gan(y5.mean() - s_xy / s_xx * x5.mean(), 1.5)


def chay_gd(xx, lr, so_buoc, bo_chia_n=False):
    """GD từ w = b = 0. Trả về MSE trước mỗi lần cập nhật và quỹ đạo (w, b)."""
    w = b = 0.0
    mse, duong = [], [(w, b)]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")  # khi phát nổ numpy báo tràn số, đó là điều ta muốn quan sát
        for _ in range(so_buoc):
            e = y - (w * xx + b)
            mse.append((e ** 2).mean())
            chia = 1 if bo_chia_n else n
            w -= lr * (-2 / chia * (xx * e).sum())
            b -= lr * (-2 / chia * e.sum())
            duong.append((w, b))
    return np.array(mse), np.array(duong)


# Code trang 04: 201 vòng, in mỗi 50 bước
mse200, duong200 = chay_gd(x, LR, 201)
moc = {k: (duong200[k][0], duong200[k][1], mse200[k]) for k in (0, 50, 100, 150, 200)}
dong_in = [f"Bước {k:3d} | w = {wv:.4f} | b = {bv:.4f} | MSE = {m:.6f}" for k, (wv, bv, m) in moc.items()]
assert dong_in == [
    "Bước   0 | w = 0.0000 | b = 0.0000 | MSE = 23.500000",
    "Bước  50 | w = 1.5937 | b = 0.5186 | MSE = 0.050058",
    "Bước 100 | w = 1.5970 | b = 0.5088 | MSE = 0.050013",
    "Bước 150 | w = 1.5986 | b = 0.5041 | MSE = 0.050003",
    "Bước 200 | w = 1.5993 | b = 0.5019 | MSE = 0.050001",
], dong_in

# Lỗi hay gặp "quên chia n": với 4 điểm, bước chân thật thành 0,05 × 4 = 0,2 > 0,12 nên nổ
mse_quen, _ = chay_gd(x, LR, 40, bo_chia_n=True)
assert mse_quen[-1] > mse_quen[0] * 1e6

# Hình 10.2: ba learning rate, 40 bước (bước 0 đến 39)
CAC_LR = [(0.005, "η = 0,005 (quá nhỏ)"), (0.05, "η = 0,05 (vừa)"), (0.135, "η = 0,135 (quá lớn)")]
mse_lr = {lr: chay_gd(x, lr, 40)[0] for lr, _ in CAC_LR}
xanh = mse_lr[0.05]
assert gan(xanh[1], 0.6884375) and gan(xanh[3], 0.0507, 1e-4)  # 0,69 ở bước 1; 0,051 ở bước 3
xam = mse_lr[0.005]
assert gan(xam[39], 0.0763, 1e-4) and 1.5 < xam[39] / 0.05 < 1.55  # cuối hình vẫn cao hơn đáy khoảng 50%
do = mse_lr[0.135]
assert [round(v) for v in do[1:4]] == [37, 58, 91] and do[39] > 1e9
assert gan(do[2] / do[1], 1.574, 1e-3)  # mỗi bước MSE nhân khoảng 1,57 lần
print("mse lr:", {k: v[[1, 3, 39]] for k, v in mse_lr.items()})

# Sát ngưỡng, η = 0,11: vẫn hội tụ nhưng mấy bước đầu dội qua lại nên giảm chậm
mse_011, duong_011 = chay_gd(x, 0.11, 201)
assert gan(mse_011[1], 16.48, 1e-2) and mse_011[200] < 0.0501
# Khung Đào sâu: trị riêng của H = (2/n) XᵀX, X có thêm cột 1 cho b
X = np.c_[x, np.ones(n)]
assert np.allclose(X.T @ X, [[30, 10], [10, 4]]) and np.allclose(2 / n * X.T @ X, [[15, 5], [5, 2]])
assert gan((17 + np.sqrt(269)) / 2, np.linalg.eigvalsh(2 / n * X.T @ X)[1])  # công thức nghiệm bậc hai
lam = np.linalg.eigvalsh(2 / n * X.T @ X)  # tăng dần
lam_min, lam_max = lam
assert gan(lam_max, 16.7, 1e-2) and gan(lam_min, 0.299, 1e-3)
assert gan(2 / lam_max, 0.11976, 1e-5)
assert gan(1 - LR * lam_max, 0.165, 1e-3)  # hướng dốc: mỗi bước còn 16,5% khoảng cách
assert gan(1 - LR * lam_min, 0.985, 1e-3)  # hướng thoải: mỗi bước chỉ bớt 1,5%
assert gan(1 - 0.135 * lam_max, -1.2546, 1e-4) and gan((1 - 0.135 * lam_max) ** 2, 1.574, 1e-3)
assert gan(lam_max / lam_min, 55.8, 0.1)  # thung lũng hẹp: một hướng dốc hơn hướng kia khoảng 56 lần
# Đổi giờ sang phút
Xp = np.c_[60 * x, np.ones(n)]
lam_p = np.linalg.eigvalsh(2 / n * Xp.T @ Xp)
assert gan(lam_p[1], 54001.7, 0.05)
assert gan(2 / lam_p[1], 3.7e-5, 1e-6)
assert LR / (2 / lam_p[1]) > 1000  # 0,05 lớn gấp hơn 1000 lần ngưỡng
assert np.allclose(Xp.T @ Xp, [[30 * 3600, 600], [600, 4]])  # ô Σx² phình 60² = 3 600 lần
assert gan(abs(1 - LR * lam_p[1]), 2699, 1)  # mỗi bước khoảng cách nhân khoảng 2 700 lần
assert gan((1 - LR * lam_p[1]) ** 2, 7.29e6, 0.01e6)  # nên MSE nhân khoảng 7,3 triệu lần mỗi bước
print(f"lambda gio={lam} phut={lam_p} nguong={2 / lam_max:.5f} / {2 / lam_p[1]:.3e}")

# Bài 10.3: chạy đúng code trang 04 với x tính bằng phút
mse_p, duong_p = chay_gd(60 * x, LR, 201)
assert gan(mse_p[1], 1.705e8, 1e5) and gan(mse_p[2], 1.242e15, 1e12)
dau_inf = int(np.argmax(np.isinf(mse_p)))
dau_nan = int(np.argmax(np.isnan(mse_p)))
assert dau_inf == 45 and dau_nan == 91 and np.isinf(mse_p[50]) and np.all(np.isnan(mse_p[[100, 150, 200]]))
assert gan(mse_p[2] / mse_p[1], 7.285e6, 0.01e6)
print(f"phut: buoc1={mse_p[1]:.4e} buoc2={mse_p[2]:.4e} inf tu buoc {dau_inf}, nan tu buoc {dau_nan}")

# Vì sao GD: nghịch đảo ma trận d×d tốn khoảng d³ phép tính
assert 10_000 ** 3 == 10 ** 12

# Hình 10.3: 60 bước GD
duong60 = duong200[:61]
assert gan(duong60[1][0], 1.325) and gan(duong60[1][1], 0.45)
print("sau 60 buoc:", duong60[-1])

# Hình 10.4: hai bộ 120 điểm giả lập
rng = np.random.default_rng(42)
xa = rng.uniform(0, 10, 120)
ya_thang = 1.5 * xa + 2 + rng.normal(0, 1.5, 120)
ya_cong = 0.25 * xa ** 2 + rng.normal(0, 1.5, 120)
phan_du_4 = []
for yy in (ya_thang, ya_cong):
    A = np.c_[xa, np.ones_like(xa)]
    he_so, *_ = np.linalg.lstsq(A, yy, rcond=None)
    du_doan = A @ he_so
    r = yy - du_doan
    phan_du_4.append((du_doan, r, 1 - (r ** 2).sum() / ((yy - yy.mean()) ** 2).sum()))
r2a, r2b = phan_du_4[0][2], phan_du_4[1][2]
assert gan(r2a, 0.8795, 1e-4) and gan(r2b, 0.9046, 1e-4) and r2b > r2a
assert (f"{r2a:.3f}", f"{r2b:.3f}") == ("0.879", "0.905")  # số in trên hình và trong bài
print(f"R2 hinh 4: a={r2a:.4f} b={r2b:.4f}")

# Các số phụ trong bài
assert (2 ** 2 + 4 ** 2 + 5 ** 2 + 7 ** 2) == 94 and gan(94 / 4, 23.5)  # trang 03, MSE ở w = b = 0
assert np.allclose((y - y1) ** 2, [0.050625, 0.81, 0.330625, 1.5625]) and gan(((y - y1) ** 2).sum(), 2.75375)
assert np.allclose(y - y.mean(), [-2.5, -0.5, 0.5, 2.5])  # trang 05: 2,5² + 0,5² + 0,5² + 2,5² = 13
assert gan(1.6 * 5 + 0.5, 8.5)  # bài 10.1: đường cũ đoán E được 8,5 điểm
assert gan(LR * 4.375, 0.21875) and gan(LR * 1.475, 0.07375)  # bài 10.2
assert 6 < 26.5 / 4.375 < 6.1  # gradient bước 2 nhỏ hơn bước 1 khoảng 6 lần
assert (y - (w2 * x + b2))[0] < 0 and (y - (w2 * x + b2))[2] < 0  # A và C lần đầu có phần dư âm
assert 1.79e308 < np.finfo(float).max < np.inf  # số thực lớn nhất khoảng 1,8 × 10^308
w50, b50 = duong_p[50]
assert len(f"{abs(w50):.0f}") > 160 and len(f"{abs(b50):.0f}") > 160 and w50 < 0 and b50 < 0  # bài 10.3: "dài hơn 160 chữ số"

# Trang 04: biến thể in 3 bước đầu, và lỗi quên dấu trừ (đi lên dốc)
ba_dong = [f"Bước {k:3d} | w = {duong200[k][0]:.4f} | b = {duong200[k][1]:.4f} | MSE = {mse200[k]:.6f}" for k in range(3)]
assert ba_dong == [
    "Bước   0 | w = 0.0000 | b = 0.0000 | MSE = 23.500000",
    "Bước   1 | w = 1.3250 | b = 0.4500 | MSE = 0.688437",
    "Bước   2 | w = 1.5437 | b = 0.5237 | MSE = 0.067615",
], ba_dong
wn = bn = 0.0
for buoc in range(51):
    e = y - (wn * x + bn)
    mse_nguoc = (e ** 2).mean()
    wn, bn = wn + LR * (-2 / n * (x * e).sum()), bn + LR * (-2 / n * e.sum())  # cố tình sai: cộng thay vì trừ
assert mse_nguoc > 1e27  # đến bước 50 MSE đã vượt 10^27

# ---------------------------------------------------------------- vẽ hình
NEN = "#FBF8F1"
XANH, CAM, DO, XAM, CHU, LUOI = "#1F5F8B", "#E07A1F", "#C0392B", "#8A8170", "#2B2B2B", "#E6DECD"
co_sans = {f.name for f in font_manager.fontManager.ttflist}
FONT = "Be Vietnam Pro" if "Be Vietnam Pro" in co_sans else "DejaVu Sans"
plt.rcParams.update({
    "font.family": FONT, "font.size": 12.5, "mathtext.fontset": "dejavusans",
    "text.color": CHU, "axes.labelcolor": CHU, "xtick.color": CHU, "ytick.color": CHU,
    "axes.edgecolor": XAM, "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": LUOI, "grid.alpha": 0.8,
    "figure.facecolor": NEN, "axes.facecolor": NEN, "savefig.facecolor": NEN,
    "savefig.bbox": "tight", "svg.hashsalt": "ch10",
})
PHAY = FuncFormatter(lambda v, _: f"{v:g}".replace(".", ","))


def luu(fig, ten):
    fig.savefig(OUT / ten, metadata={"Date": None})  # bỏ ngày giờ để file không đổi giữa các lần chạy
    plt.close(fig)


# Sơ đồ vòng lặp huấn luyện (trang 01, không đánh số). Xếp 2 cột cho vừa màn hình điện thoại.
fig, ax = plt.subplots(figsize=(5.2, 5.2))
ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.axis("off")
RONG, CAO = 4.2, 2.3  # kích thước mỗi ô, theo đơn vị trục
o = {
    "tham": (2.5, 8.6, "Tham số\n$w,\\ b$", XANH),
    "doan": (7.5, 8.6, "Dự đoán\n$\\hat y = wx + b$", XANH),
    "sai": (7.5, 5.0, "Đo sai số\n(hàm mất mát)", XANH),
    "grad": (7.5, 1.4, "Tính gradient\n$\\partial L/\\partial w,\\ \\partial L/\\partial b$", CAM),
    "cap": (2.5, 1.4, "Cập nhật\n$w \\leftarrow w - \\eta\\,\\partial L/\\partial w$", CAM),
}
for cx, cy, chu, mau in o.values():
    ax.add_patch(FancyBboxPatch((cx - RONG / 2, cy - CAO / 2), RONG, CAO, boxstyle="round,pad=0.02,rounding_size=0.25",
                                fc=mau + "1A", ec=mau, lw=1.5))
    ax.text(cx, cy, chu, ha="center", va="center", fontsize=12, linespacing=1.6)
for a, bb in [("tham", "doan"), ("doan", "sai"), ("sai", "grad"), ("grad", "cap"), ("cap", "tham")]:
    (x0, y0, *_), (x1, y1_, *_) = o[a], o[bb]
    if y0 == y1_:  # mũi tên ngang
        p, q = (x0 + (RONG / 2 + 0.1) * np.sign(x1 - x0), y0), (x1 - (RONG / 2 + 0.1) * np.sign(x1 - x0), y1_)
    else:  # mũi tên dọc
        p, q = (x0, y0 - (CAO / 2 + 0.1) * np.sign(y0 - y1_)), (x1, y1_ + (CAO / 2 + 0.1) * np.sign(y0 - y1_))
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=16, color=XAM, lw=1.5))
ax.text(2.85, 5.0, "lặp lại\nhàng trăm\nlần", ha="left", va="center", fontsize=11, color=XAM, style="italic", linespacing=1.5)
luu(fig, "h0_vong_lap.svg")

# Hình 10.1: dữ liệu, đường hồi quy, phần dư
fig, ax = plt.subplots(figsize=(5.6, 3.9))
xs = np.linspace(0.5, 4.5, 50)
ax.plot(xs, w_ols * xs + b_ols, color=XANH, lw=2.2, label=r"Đường hồi quy $\hat y = 1{,}6x + 0{,}5$")
for xi, yi, hi in zip(x, y, yhat):
    ax.plot([xi, xi], [yi, hi], color=DO, ls="--", lw=1.4)
ax.scatter(x, y, s=70, color=CAM, zorder=3, label="Dữ liệu thật (4 bạn)")
for xi, yi, hi, ten in zip(x, y, yhat, "ABCD"):
    ax.annotate(f"e = {yi - hi:+.1f}".replace(".", ","), (xi, (yi + hi) / 2), xytext=(12, 0),
                textcoords="offset points", fontsize=11.5, color=DO, va="center")
    ax.annotate(ten, (xi, yi), xytext=(-14, 6), textcoords="offset points", fontsize=11.5, color=CHU)
ax.set_xlabel("Số giờ tự học mỗi tuần (x)"); ax.set_ylabel("Điểm thi (y)")
ax.set_xlim(0.5, 4.7); ax.set_ylim(0, 8); ax.legend(loc="upper left", frameon=False)
ax.xaxis.set_major_formatter(PHAY); ax.yaxis.set_major_formatter(PHAY)
luu(fig, "h1_duong_hoi_quy.svg")

# Hình 10.2: MSE theo bước lặp với ba learning rate
fig, ax = plt.subplots(figsize=(5.6, 3.9))
for (lr, ten), mau in zip(CAC_LR, (XAM, XANH, DO)):
    ax.plot(mse_lr[lr], color=mau, lw=2.2, label=ten)
ax.axhline(0.05, color=XANH, lw=0.8, ls=":")
ax.text(12, 0.06, "đáy 0,05", ha="left", va="bottom", fontsize=11, color=XANH)
ax.set_yscale("log"); ax.set_xlabel("Bước lặp"); ax.set_ylabel("MSE (thang log)")
ax.set_xlim(0, 39); ax.legend(frameon=False, loc="upper left")
ax.xaxis.set_major_formatter(PHAY)
luu(fig, "h2_loss_lr.svg")

# Hình 10.3: đường đồng mức của L(w, b) và 60 bước GD
W, B = np.meshgrid(np.linspace(-0.5, 3.2, 300), np.linspace(-3, 4, 300))
L = ((y[None, None, :] - (W[..., None] * x + B[..., None])) ** 2).mean(-1)
fig, ax = plt.subplots(figsize=(5.6, 4.3))
ax.contour(W, B, L, levels=np.geomspace(0.15, 40, 14), cmap="Blues_r", linewidths=1)
ax.plot(duong60[:, 0], duong60[:, 1], "-o", color=CAM, ms=3.5, lw=1.3, label="60 bước gradient descent (η = 0,05)")
ax.annotate("bước 1", duong60[1], xytext=(-14, -22), textcoords="offset points", fontsize=11, color=CAM)
ax.annotate("xuất phát (0; 0)", duong60[0], xytext=(8, -14), textcoords="offset points", fontsize=11, color=CAM)
ax.scatter([w_ols], [b_ols], marker="*", s=160, color=DO, zorder=4, label="Đáy (1,6; 0,5)")
ax.set_xlabel("w (độ dốc)"); ax.set_ylabel("b (hệ số chặn)")
ax.legend(loc="upper right", fontsize=11, facecolor=NEN, edgecolor=LUOI, framealpha=1)
ax.xaxis.set_major_formatter(PHAY); ax.yaxis.set_major_formatter(PHAY)
# Ô phóng to quanh đáy: từ bước 2 trở đi các bước quá ngắn, nhìn ở cỡ hình lớn sẽ bị ngôi sao che mất
WZ, BZ = np.meshgrid(np.linspace(1.53, 1.61, 200), np.linspace(0.49, 0.55, 200))
LZ = ((y[None, None, :] - (WZ[..., None] * x + BZ[..., None])) ** 2).mean(-1)
oz = ax.inset_axes([0.58, 0.04, 0.4, 0.42], xlim=(1.53, 1.61), ylim=(0.49, 0.55))
oz.set_facecolor(NEN)
oz.contour(WZ, BZ, LZ, levels=np.geomspace(0.0501, 0.06, 7), cmap="Blues_r", linewidths=0.8)
oz.plot(duong60[:, 0], duong60[:, 1], "-o", color=CAM, ms=2.5, lw=1)
oz.scatter([w_ols], [b_ols], marker="*", s=120, color=DO, zorder=4)
oz.annotate("bước 2", duong60[2], xytext=(-8, 8), textcoords="offset points", fontsize=10, color=CAM)
oz.annotate("bước 60", duong60[60], xytext=(-34, -22), textcoords="offset points", fontsize=10, color=CAM)
oz.set_xticks([]); oz.set_yticks([]); oz.grid(False)
for canh in oz.spines.values():
    canh.set_visible(True); canh.set_color(XAM)
ax.indicate_inset_zoom(oz, edgecolor=XAM)
luu(fig, "h3_mat_loss.svg")

# Hình 10.4: đồ thị phần dư
fig, axs = plt.subplots(2, 1, figsize=(5.6, 7.2))
for ax, (du_doan, r, r2_), tieu_de in zip(axs, phan_du_4, ("(a) Quan hệ thật là đường thẳng", "(b) Quan hệ thật là đường cong")):
    ax.scatter(du_doan, r, s=14, color=XANH, alpha=0.75)
    ax.axhline(0, color=DO, lw=1.2)
    ax.set_title(f"{tieu_de}\nR² = {r2_:.3f}".replace(".", ","), fontsize=12.5)
    ax.set_xlabel("Giá trị dự đoán ŷ"); ax.set_ylabel("Phần dư y − ŷ")
    ax.xaxis.set_major_formatter(PHAY); ax.yaxis.set_major_formatter(PHAY)
fig.tight_layout()
luu(fig, "h4_phan_du.svg")

print("Font:", FONT, "| Đã ghi:", sorted(p.name for p in OUT.glob("*.svg")))
