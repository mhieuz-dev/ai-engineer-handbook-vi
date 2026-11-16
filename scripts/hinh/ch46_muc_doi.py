"""Chương 46 Fine-tune PhoBERT: vẽ hình 46.1 (độ thay đổi tương đối của trọng số sau tinh chỉnh, theo từng phần).

Tinh chỉnh mất khoảng 40 phút trên CPU, nên script không huấn luyện lại: nó đọc thẳng danh sách muc_doi
trong khối Output của trang 4 (khối đó được scripts/kiem_chuong.sh ch46 chạy lại và đối chiếu từng ký tự).
Chạy:  .venv/bin/python scripts/hinh/ch46_muc_doi.py      (dưới một giây)
Kết quả: public/hinh/ch46/h1_muc_doi.svg. Con số nào trong bài sai thì một câu assert báo lỗi.
"""
import ast
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

GOC = Path(__file__).resolve().parents[2]
OUT = GOC / "public" / "hinh" / "ch46"
OUT.mkdir(parents=True, exist_ok=True)
trang = (GOC / "src/content/docs/ai-engineer/ch46-fine-tune-phobert/04-ben-trong-mo-hinh.mdx").read_text(encoding="utf-8")
khoi = re.search(r"muc_doi = \[doi\(t\) for t in phan\]\nprint\(muc_doi\)\n```\n\n```text title=\"Output\"\n(.*?)\n```", trang, re.S)
muc_doi = ast.literal_eval(khoi.group(1))
assert len(muc_doi) == 14 and muc_doi[0] == 0.127 and muc_doi[1] == 0.664 and muc_doi[12] == 1.02 and muc_doi[13] == 4.525, muc_doi

nhan = ["vector từ"] + [f"khối {i}" for i in range(12)] + ["đầu phân loại"]
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
    "savefig.bbox": "tight", "svg.hashsalt": "ch46",
})
fig, ax = plt.subplots(figsize=(10, 4.8))
mau = [XAM] + [XANH] * 12 + [CAM]
ax.bar(range(14), muc_doi, color=mau, width=0.7)
for i, v in enumerate(muc_doi):
    ax.text(i, v + 0.06, f"{v:.2f}".replace(".", ","), ha="center", va="bottom", fontsize=10)
ax.set_xticks(range(14), nhan, rotation=45, ha="right")
ax.set_ylabel("thay đổi tương đối (%)")
ax.set_ylim(0, 5.1)
ax.grid(axis="x", visible=False)
fig.tight_layout()
fig.savefig(OUT / "h1_muc_doi.svg", metadata={"Date": None})
print("xong", muc_doi)
