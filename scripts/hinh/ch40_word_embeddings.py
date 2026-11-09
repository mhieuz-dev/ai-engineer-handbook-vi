"""Chương 40 Word embeddings: chạy code của trang 1 và 2 (đọc thẳng từ trang) để có vector Word2Vec, vẽ hình 40.1.

Chạy:  .venv/bin/python scripts/hinh/ch40_word_embeddings.py      (khoảng 20 giây; dữ liệu ở ~/.cache/vsfc)
Kết quả: public/hinh/ch40/h1_vector_tu.svg. Con số nào trong bài sai thì một câu assert báo lỗi.
"""
import contextlib
import io
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager

GOC = Path(__file__).resolve().parents[2]
OUT = GOC / "public" / "hinh" / "ch40"
OUT.mkdir(parents=True, exist_ok=True)
TRANG = GOC / "src/content/docs/ai-engineer/ch40-word-embeddings"
g = {}
for ten in ("01-tu-thua-toi-day.mdx", "02-word2vec.mdx"):
    for khoi in re.findall(r"```python\n(.*?)```", (TRANG / ten).read_text(encoding="utf-8"), re.S):
        if not khoi.startswith("!"):
            with contextlib.redirect_stdout(io.StringIO()):
                exec(khoi, g)
E, id_ = g["E_w2v"], g["id_"]
assert round(float(E[id_["tốt"]] @ E[id_["tệ"]]), 3) == 0.588

NHOM = {"người": ["thầy", "cô", "giảng_viên", "giáo_viên", "sinh_viên"],
        "tính cách": ["nhiệt_tình", "tận_tâm", "thân_thiện", "vui_tính"],
        "cơ sở vật chất": ["phòng", "máy_chiếu", "wifi", "thiết_bị"],
        "đánh giá": ["tốt", "tệ", "hay", "nhanh", "chậm", "khó", "dễ"]}
tu = [w for ds in NHOM.values() for w in ds]
LECH = {"vui_tính": (6, -14), "thân_thiện": (6, 6), "tốt": (-26, 6), "nhanh": (6, -14), "chậm": (6, 6)}   # tránh nhãn đè nhau
X = E[[id_[w] for w in tu]]
Xc = X - X.mean(0)
_, _, Vt = np.linalg.svd(Xc, full_matrices=False)
P = Xc @ Vt[:2].T
for w, (a, b) in zip(tu, P):
    print(w, round(float(a), 2), round(float(b), 2))

NEN = "#FBF8F1"
MAU = ["#1F5F8B", "#E07A1F", "#2E8B57", "#C0392B"]
CHU, XAM, LUOI = "#2B2B2B", "#8A8170", "#E6DECD"
co_sans = {f.name for f in font_manager.fontManager.ttflist}
FONT = "Be Vietnam Pro" if "Be Vietnam Pro" in co_sans else "DejaVu Sans"
plt.rcParams.update({
    "font.family": FONT, "font.size": 12.5, "text.color": CHU, "axes.labelcolor": CHU,
    "xtick.color": CHU, "ytick.color": CHU, "axes.edgecolor": XAM,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": LUOI, "grid.alpha": 0.8, "axes.axisbelow": True,
    "figure.facecolor": NEN, "axes.facecolor": NEN, "savefig.facecolor": NEN,
    "savefig.bbox": "tight", "svg.hashsalt": "ch40",
})
fig, ax = plt.subplots(figsize=(9, 6.5))
k = 0
for (nhom, ds), mau in zip(NHOM.items(), MAU):
    pts = P[k:k + len(ds)]
    ax.scatter(pts[:, 0], pts[:, 1], color=mau, s=55, label=nhom, zorder=3)
    for w, (a, b) in zip(ds, pts):
        ax.annotate(w.replace("_", " "), (a, b), xytext=LECH.get(w, (6, 4)), textcoords="offset points", fontsize=12, color=mau)
    k += len(ds)
ax.set_xlabel("thành phần chính 1")
ax.set_ylabel("thành phần chính 2")
ax.set_xticklabels([])
ax.set_yticklabels([])
ax.legend(loc="best", frameon=False)
fig.tight_layout()
fig.savefig(OUT / "h1_vector_tu.svg", metadata={"Date": None})
print("xong", sorted(p.name for p in OUT.iterdir()))
