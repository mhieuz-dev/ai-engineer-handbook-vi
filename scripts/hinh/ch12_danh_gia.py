"""Chương 12 Đánh giá mô hình: tính lại các con số dùng trong bài và vẽ hình.

Chạy:  .venv/bin/python scripts/hinh/ch12_danh_gia.py
Kết quả: các file SVG trong public/hinh/ch12/. Con số nào trong bài sai thì một câu assert báo lỗi.
"""
import warnings
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
from matplotlib.ticker import FuncFormatter
from sklearn.datasets import load_breast_cancer, make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (average_precision_score, confusion_matrix, precision_recall_curve,
                             precision_score, recall_score, roc_auc_score, roc_curve)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore")
GOC = Path(__file__).resolve().parents[2]
OUT = GOC / "public" / "hinh" / "ch12"
OUT.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- 1. ung thư vú, 1 là ác tính
d = load_breast_cancer()
X, y = d.data, 1 - d.target
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.25, random_state=0, stratify=y)
m = make_pipeline(StandardScaler(), LogisticRegression()).fit(Xtr, ytr)
pr = m.predict_proba(Xte)[:, 1]
assert len(yte) == 143 and yte.sum() == 53
assert confusion_matrix(yte, m.predict(Xte)).ravel().tolist() == [90, 0, 2, 51]
assert round(roc_auc_score(yte, pr), 4) == 0.9958
assert confusion_matrix(yte, (pr >= 0.1).astype(int)).ravel().tolist() == [79, 11, 0, 53]

# ---------------------------------------------------------------- 2. dữ liệu mất cân bằng 1%
Xm, ym = make_classification(n_samples=10000, n_features=10, weights=[0.99], flip_y=0, random_state=0)
a, b, c, e = train_test_split(Xm, ym, test_size=0.3, random_state=0, stratify=ym)
mm = LogisticRegression(max_iter=1000).fit(a, c)
prm = mm.predict_proba(b)[:, 1]
assert e.sum() == 30 and round(recall_score(e, mm.predict(b)), 4) == 0.1
assert round(roc_auc_score(e, prm), 4) == 0.9075 and round(average_precision_score(e, prm), 4) == 0.2368

# ---------------------------------------------------------------- vẽ hình (bảng màu Chương 10)
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
    "savefig.bbox": "tight", "svg.hashsalt": "ch12",
})
PHAY = FuncFormatter(lambda v, _: f"{v:g}".replace(".", ","))


def luu(fig, ten):
    fig.savefig(OUT / ten, metadata={"Date": None})  # bỏ ngày giờ để file không đổi giữa các lần chạy
    plt.close(fig)


# Hình 12.1: precision và recall theo ngưỡng (ung thư vú)
nguong = np.linspace(0.01, 0.99, 99)
P = [precision_score(yte, (pr >= t).astype(int)) for t in nguong]
R = [recall_score(yte, (pr >= t).astype(int)) for t in nguong]
fig, ax = plt.subplots(figsize=(6.8, 3.9))
ax.plot(nguong, P, color=XANH, lw=2.2, label="precision")
ax.plot(nguong, R, color=CAM, lw=2.2, label="recall")
for t in (0.1, 0.5):
    ax.axvline(t, color=XAM, ls="--", lw=1.2)
    ax.text(t + 0.01, 0.72, f"ngưỡng {t:g}".replace(".", ","), fontsize=10.5, color=XAM)
ax.set_ylim(0.7, 1.02)
ax.set_xlabel("Ngưỡng xác suất để đoán ác tính")
ax.set_ylabel("Giá trị")
ax.xaxis.set_major_formatter(PHAY)
ax.yaxis.set_major_formatter(PHAY)
ax.legend(loc="lower right", fontsize=10.5, facecolor=NEN, edgecolor=LUOI, framealpha=1)
luu(fig, "h1_nguong.svg")

# Hình 12.2: ROC và precision-recall trên dữ liệu mất cân bằng
fig, (trai, phai) = plt.subplots(1, 2, figsize=(9.6, 4.2))
fpr, tpr, _ = roc_curve(e, prm)
trai.plot(fpr, tpr, color=XANH, lw=2.2)
trai.plot([0, 1], [0, 1], color=XAM, ls="--", lw=1.2)
trai.text(0.42, 0.12, "AUC = 0,9075", fontsize=12, color=XANH)
trai.set_xlabel("Tỷ lệ báo động nhầm (FPR)")
trai.set_ylabel("Recall (TPR)")
trai.set_title("Đường ROC", fontsize=12.5)
prec, rec, _ = precision_recall_curve(e, prm)
phai.plot(rec, prec, color=DO, lw=2.2)
phai.axhline(0.01, color=XAM, ls="--", lw=1.2)
phai.text(0.66, 0.14, "đoán bừa: 0,01", fontsize=10.5, color=XAM)
phai.text(0.38, 0.62, "AP = 0,2368", fontsize=12, color=DO)
phai.set_xlabel("Recall")
phai.set_ylabel("Precision")
phai.set_title("Đường precision-recall", fontsize=12.5)
for ax in (trai, phai):
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.02)
    ax.xaxis.set_major_formatter(PHAY)
    ax.yaxis.set_major_formatter(PHAY)
luu(fig, "h2_roc_pr.svg")
print("Đã vẽ 2 hình vào", OUT)
