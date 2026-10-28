"""Khuôn chung dựng notebook Colab cho mỗi chương, cùng phong cách notebook Ch10."""
import json

P = '<p style="margin:8px 0 0;color:#2b2b2b;line-height:1.6;">{}</p>'
MAU = {
    "truc-giac": ("#1F5F8B", "#E9F1F8", "#1F5F8B", "TRỰC GIÁC"),
    "doc": ("#2E8B57", "#EAF6EF", "#1E6B42", "ĐỌC KẾT QUẢ"),
    "loi": ("#C0392B", "#FBECEA", "#962D22", "LỖI HAY GẶP"),
    "vi-sao": ("#E07A1F", "#FDF1E6", "#9A4F0E", None),
    "thu": ("#7A6A58", "#F4F1EC", "#5C4E3F", "THỬ SỬA"),
}
VIEN = '<span style="display:inline-block;margin:4px 6px 0 0;padding:4px 12px;border-radius:99px;background-color:#FDF1E6;color:#2b2b2b;border:1px solid #E07A1F;font-size:0.9em;">{}</span>'


def khung(loai, doan, nhan=None):
    vien, nen, chu, mac_dinh = MAU[loai]
    the = [f'<div style="border-left:6px solid {vien};background-color:{nen};color:#2b2b2b;padding:12px 18px 14px;border-radius:8px;margin:10px 0;">',
           f'<div style="color:{chu};font-weight:700;font-size:0.85em;letter-spacing:0.08em;">{nhan or mac_dinh}</div>']
    return "\n".join(the + [P.format(d) for d in doan] + ["</div>"])


def md(s):
    return {"cell_type": "markdown", "metadata": {}, "source": s.strip("\n").splitlines(True)}


def code(s):
    return {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [], "source": s.strip("\n").splitlines(True)}


def mong_doi(out, them=""):
    return f"Output mong đợi{them}:\n\n```text\n{out.strip()}\n```"


class Chuong:
    def __init__(self, so, ten, slug_chuong, mo_ta, sau, trang, thoi_gian="dưới 1 phút", runtime="CPU là đủ, không cần GPU"):
        self.so, self.trang = so, trang  # trang: list (tên, slug)
        self.web = f"https://ai-and-robotics-handbook.vercel.app/ai-engineer/{slug_chuong}"
        muc = "\n".join(f"{i}. [Trang {i} · {t}](#trang-{i})" for i, (t, _) in enumerate(trang, 1))
        sau_md = "\n".join(f"- {s}" for s in sau)
        self.cells = [md(f'''<div style="background-color:#0e2233;background-image:linear-gradient(135deg,#0b1a29,#123049);color:#ffffff;padding:26px 28px 24px;border-radius:12px;border:1px solid #2a4a66;">
<div style="color:#a0d2ff;font-size:0.78em;font-weight:600;letter-spacing:0.18em;">AI &amp; ROBOTICS · NHÁNH AI ENGINEER · NOTEBOOK THỰC HÀNH</div>
<div style="width:56px;height:4px;background-color:#E07A1F;margin:14px 0 12px;"></div>
<h1 style="color:#ffffff;font-size:2.3em;line-height:1.15;margin:0;border:0;">Chương {so} · {ten}</h1>
<p style="color:#cfe6ff;font-size:1.12em;line-height:1.5;margin:10px 0 0;">{mo_ta}</p>
</div>

### Sau notebook này bạn sẽ

{sau_md}

<div>
{VIEN.format(f"<b>Thời gian chạy:</b> {thoi_gian}")}
{VIEN.format(f"<b>Runtime:</b> {runtime}")}
{VIEN.format(f'<b>Trang web của chương:</b> <a href="{self.web}/{trang[0][1]}/" style="color:#1F5F8B;">mở bài đọc</a>')}
</div>

### Mục lục

{muc}

### Cách chạy

Bấm vào một ô code rồi nhấn **Shift + Enter** để chạy ô đó và nhảy sang ô kế tiếp. Muốn chạy hết một lượt thì chọn menu **Runtime > Run all**. Các ô nên chạy theo thứ tự từ trên xuống, vì ô sau dùng biến của ô trước.''')]

    def mo_trang(self, so, gioi_thieu):
        ten, slug = self.trang[so - 1]
        self.cells.append(md(f'<a name="trang-{so}" id="trang-{so}"></a>\n\n## Trang {so} · {ten}\n\n{gioi_thieu}\n\n*Đọc kèm trên web: [Trang {so} · {ten}]({self.web}/{slug}/)*'))

    def o(self, src, out, sau=""):
        """Một ô code kèm khối Output mong đợi (và khung tùy chọn) ngay sau."""
        self.cells.append(code(src))
        self.cells.append(md(mong_doi(out) + (("\n\n" + sau) if sau else "")))

    def bai(self, so, ten, de, dap_an):
        self.cells.append(md(f"### Bài {so} · {ten}\n\n{de}\n<details><summary>Xem đáp án</summary>\n\n{dap_an}\n</details>"))

    def ghi(self, duong_dan):
        nb = {"cells": self.cells, "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                                                "language_info": {"name": "python"}, "colab": {"provenance": [], "toc_visible": True}},
              "nbformat": 4, "nbformat_minor": 0}
        json.dump(nb, open(duong_dan, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
