"""Dựng notebooks/ch01_python_tu_dau.ipynb: python3 scripts/notebook/ch01.py notebooks/ch01_python_tu_dau.ipynb"""
import json, sys

WEB = "https://ai-and-robotics.vercel.app/ai-engineer/ch01-python-tu-dau"
P = '<p style="margin:8px 0 0;color:#2b2b2b;line-height:1.6;">{}</p>'
MAU = {
    "truc-giac": ("#1F5F8B", "#E9F1F8", "#1F5F8B", "TRỰC GIÁC"),
    "doc": ("#2E8B57", "#EAF6EF", "#1E6B42", "ĐỌC KẾT QUẢ"),
    "loi": ("#C0392B", "#FBECEA", "#962D22", "LỖI HAY GẶP"),
    "vi-sao": ("#E07A1F", "#FDF1E6", "#9A4F0E", None),
    "thu": ("#7A6A58", "#F4F1EC", "#5C4E3F", "THỬ SỬA"),
}


def khung(loai, doan, nhan=None):
    vien, nen, chu, mac_dinh = MAU[loai]
    the = [f'<div style="border-left:6px solid {vien};background-color:{nen};color:#2b2b2b;padding:12px 18px 14px;border-radius:8px;margin:10px 0;">',
           f'<div style="color:{chu};font-weight:700;font-size:0.85em;letter-spacing:0.08em;">{nhan or mac_dinh}</div>']
    the += [P.format(d) for d in doan]
    return "\n".join(the + ["</div>"])


def md(s):
    return {"cell_type": "markdown", "metadata": {}, "source": s.strip("\n").splitlines(True)}


def code(s):
    return {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [], "source": s.strip("\n").splitlines(True)}


def mong_doi(out, them=""):
    return f"Output mong đợi{them}:\n\n```text\n{out.strip()}\n```"


def trang(so, ten, slug, gioi_thieu):
    return md(f'<a name="trang-{so}" id="trang-{so}"></a>\n\n## Trang {so} · {ten}\n\n{gioi_thieu}\n\n*Đọc kèm trên web: [Trang {so} · {ten}]({WEB}/{slug}/)*')


TEN = ["Biến, kiểu dữ liệu và phép tính", "Điều kiện và vòng lặp", "Hàm", "List và dict", "Bài tập"]
SLUG = ["01-bien-va-kieu", "02-dieu-kien-va-vong-lap", "03-ham", "04-list-va-dict", "05-bai-tap"]
VIEN = '<span style="display:inline-block;margin:4px 6px 0 0;padding:4px 12px;border-radius:99px;background-color:#FDF1E6;color:#2b2b2b;border:1px solid #E07A1F;font-size:0.9em;">{}</span>'

cells = [md(f'''<div style="background-color:#0e2233;background-image:linear-gradient(135deg,#0b1a29,#123049);color:#ffffff;padding:26px 28px 24px;border-radius:12px;border:1px solid #2a4a66;">
<div style="color:#a0d2ff;font-size:0.78em;font-weight:600;letter-spacing:0.18em;">AI &amp; ROBOTICS · NHÁNH AI ENGINEER · NOTEBOOK THỰC HÀNH</div>
<div style="width:56px;height:4px;background-color:#E07A1F;margin:14px 0 12px;"></div>
<h1 style="color:#ffffff;font-size:2.3em;line-height:1.15;margin:0;border:0;">Chương 1 · Python từ đầu</h1>
<p style="color:#cfe6ff;font-size:1.12em;line-height:1.5;margin:10px 0 0;">Biến, điều kiện, vòng lặp, hàm, list và dict: đủ Python để tự viết hàm tính MSE, con số mà Chương 10 sẽ dùng để huấn luyện mô hình đầu tiên.</p>
</div>

### Sau notebook này bạn sẽ

- Chạy được code Python trên Colab và đọc được output.
- Dùng đúng biến, bốn kiểu dữ liệu cơ bản và bảy phép tính số học.
- Viết được điều kiện if, vòng lặp for và while.
- Tự viết hàm có tham số mặc định, phân biệt return với print.
- Giữ dữ liệu trong list và dict, viết gọn bằng list comprehension.

<div>
{VIEN.format("<b>Thời gian chạy:</b> dưới 1 phút")}
{VIEN.format("<b>Runtime:</b> CPU là đủ, không cần GPU")}
{VIEN.format(f'<b>Trang web của chương:</b> <a href="{WEB}/01-bien-va-kieu/" style="color:#1F5F8B;">mở bài đọc</a>')}
</div>

### Mục lục

''' + "\n".join(f"{i}. [Trang {i} · {t}](#trang-{i})" for i, t in enumerate(TEN, 1)) + '''

### Cách chạy

Bấm vào một ô code rồi nhấn **Shift + Enter** để chạy ô đó và nhảy sang ô kế tiếp. Muốn chạy hết một lượt thì chọn menu **Runtime > Run all**. Các ô nên chạy theo thứ tự từ trên xuống, vì ô sau dùng biến của ô trước.''')]

# Trang 1
cells += [
    trang(1, TEN[0], SLUG[0], "Dòng code đầu tiên, biến là cái nhãn dán lên giá trị, bốn kiểu dữ liệu và các phép tính."),
    code('''
print("Xin chào, AI!")  # print in ra màn hình thứ nằm trong ngoặc
print(2 + 3)            # Python tính 2 + 3 trước, rồi in kết quả
'''),
    md(mong_doi("Xin chào, AI!\n5")),
    md(khung("truc-giac", ["Mỗi giá trị là một chiếc hộp. <b>Biến</b> (variable) là cái nhãn dán lên hộp.",
                           "Viết <code>gio = 3</code> là dán nhãn <code>gio</code> lên hộp chứa số 3. Dấu <code>=</code> là lệnh gán, không phải dấu bằng trong toán."])),
    code('''
gio = 3          # số giờ tự học của bạn An, một số nguyên
diem = 5.5       # điểm thi, một số có phần thập phân
ten = "An"       # tên, một chuỗi chữ đặt trong dấu nháy
da_thi = True    # đã thi hay chưa, chỉ có hai giá trị True hoặc False
print(type(gio), type(diem), type(ten), type(da_thi))  # type cho biết kiểu của giá trị
'''),
    md(mong_doi("<class 'int'> <class 'float'> <class 'str'> <class 'bool'>")),
    code('''
print(7 + 2, 7 - 2, 7 * 2, 7 / 2, 7 // 2, 7 % 2, 7 ** 2)  # cộng, trừ, nhân, chia, chia nguyên, chia dư, lũy thừa
print(f"Bạn {ten} học {gio} giờ, được {diem} điểm")      # f-string: thay {ten} bằng giá trị của biến ten
print(0.1 + 0.2)                                          # đoán trước: có ra đúng 0.3 không?
'''),
    md(mong_doi("9 5 14 3.5 3 1 49\nBạn An học 3 giờ, được 5.5 điểm\n0.30000000000000004") + "\n\n" +
       khung("doc", ["Phép <code>/</code> luôn ra số thực (3.5). Phép <code>//</code> bỏ phần lẻ (3), phép <code>%</code> lấy phần dư (1).",
                     "0.1 + 0.2 lệch ở chữ số thứ 17 vì máy lưu số thực ở hệ nhị phân. Đừng so số thực bằng <code>==</code>, hãy dùng <code>math.isclose(a, b)</code>."]) + "\n\n" +
       khung("loi", ["<b>Viết dấu phẩy thay dấu chấm.</b> <code>diem = 5,5</code> không báo lỗi, nhưng Python hiểu đó là cặp hai số 5 và 5.",
                     "<b>Nhầm = với ==.</b> Một dấu bằng là gán, hai dấu bằng là hỏi có bằng nhau không."])),
]

# Trang 2
cells += [
    trang(2, TEN[1], SLUG[1], "Cho chương trình tự chọn đường đi bằng if, và lặp lại công việc bằng for, while."),
    code('''
diem = 7.5                  # điểm của một bạn
if diem >= 8:               # điều kiện thứ nhất: từ 8 trở lên
    xep_loai = "Giỏi"       # khối thụt lề 4 dấu cách chạy khi điều kiện đúng
elif diem >= 6.5:           # elif = else if: chỉ xét khi điều kiện trên sai
    xep_loai = "Khá"        # 7.5 rơi vào đây
else:                       # không điều kiện nào ở trên đúng
    xep_loai = "Trung bình" # các điểm dưới 6.5
print(xep_loai)             # in kết quả xếp loại
'''),
    md(mong_doi("Khá")),
    code('''
for i in range(4):  # range(4) sinh ra 0, 1, 2, 3: bốn số, bắt đầu từ 0
    print(i)        # khối thụt lề chạy một lần cho mỗi giá trị của i
print(list(range(1, 5)), list(range(0, 10, 3)))  # có điểm đầu, có bước nhảy; luôn dừng TRƯỚC số cuối
'''),
    md(mong_doi("0\n1\n2\n3\n[1, 2, 3, 4] [0, 3, 6, 9]")),
    code('''
tong = 0                     # bắt đầu từ 0, chưa cộng gì
for gio in [1, 2, 3, 4]:     # lặp thẳng qua giờ học của bốn bạn A, B, C, D
    tong = tong + gio        # tổng cũ cộng thêm giờ của bạn này, gán lại vào tong
print(tong)                  # in tổng số giờ

w = 0.0                # giá trị bắt đầu
buoc = 0               # đếm số bước đã đi
while w < 1.6:         # còn nhỏ hơn 1.6 thì còn lặp
    w = w + 0.5        # mỗi bước nhích w thêm 0.5
    buoc = buoc + 1    # đếm thêm một bước
print(buoc, w)         # số bước và giá trị cuối của w
'''),
    md(mong_doi("10\n4 2.0") + "\n\n" +
       khung("doc", ["w đi 0,5; 1,0; 1,5; 2,0. Sau bước 3, w = 1,5 vẫn nhỏ hơn 1,6 nên lặp tiếp. Sau bước 4, w = 2,0 thì dừng.",
                     "Vòng dừng ở 2,0 chứ không phải 1,6, vì bước nhảy quá dài. Chương 10 sẽ gặp lại hiện tượng này với learning rate."]) + "\n\n" +
       khung("thu", ["<b>1.</b> Đổi <code>w + 0.5</code> thành <code>w + 0.1</code>. Vòng lặp cần bao nhiêu bước, và dừng ở w bằng bao nhiêu?",
                     "<b>2.</b> Đổi <code>range(4)</code> thành <code>range(2, 8, 2)</code> và đoán output trước khi chạy."])),
]

# Trang 3
cells += [
    trang(3, TEN[2], SLUG[2], "Đóng gói công thức dự đoán của hồi quy tuyến tính thành một hàm."),
    code('''
def du_doan(x, w=1.6, b=0.5):   # định nghĩa hàm; w và b có giá trị mặc định
    return w * x + b            # return: trả kết quả về cho chỗ gọi hàm

print(du_doan(3))               # dùng cả hai mặc định: 1.6 * 3 + 0.5
print(du_doan(5), du_doan(5, b=0))  # lần sau đổi riêng b bằng cách gọi theo tên
'''),
    md(mong_doi("5.300000000000001\n8.5 8.0")),
    code('''
def in_ra(x):        # hàm chỉ in, không có return
    print(x * 2)    # chỉ IN ra màn hình, không trả gì về

kq = in_ra(3)       # màn hình hiện 6, nhưng kq nhận được gì?
print(kq)           # hàm không có return thì trả về None
'''),
    md(mong_doi("6\nNone") + "\n\n" +
       khung("loi", ["<b>Dùng print thay cho return.</b> Bạn thấy số trên màn hình, nhưng biến nhận về <code>None</code>. Lỗi lộ ra muộn khi đem <code>None</code> đi cộng trừ.",
                     "<b>Định nghĩa hàm nhưng quên gọi.</b> Khối <code>def</code> chỉ tạo ra hàm, phải gọi <code>du_doan(3)</code> thì hàm mới chạy."])),
]

# Trang 4
cells += [
    trang(4, TEN[3], SLUG[3], "Giữ cả cột dữ liệu trong list, tra theo tên với dict, và cái bẫy hai nhãn một hộp."),
    code('''
gio = [1, 2, 3, 4]     # giờ tự học của bốn bạn A, B, C, D
diem = [2, 4, 5, 7]    # điểm thi tương ứng
print(gio[0], gio[-1], gio[1:3], len(gio))  # phần tử đầu, phần tử cuối, lát cắt, độ dài
gio.append(5)          # thêm 5 vào cuối list
print(gio)             # list giờ đã có 5 phần tử
'''),
    md(mong_doi("1 4 [2, 3] 4\n[1, 2, 3, 4, 5]")),
    code('''
ban = {"ten": "An", "gio": 3, "diem": 5}  # dict: mỗi cặp khóa: giá trị
print(ban["diem"])                         # tra khóa "diem"
ban["diem"] = 6                            # gán lại giá trị cho khóa đã có
for khoa, gia_tri in ban.items():          # items() cho từng cặp (khóa, giá trị)
    print(khoa, gia_tri)                   # in khóa và giá trị trên cùng một dòng
'''),
    md(mong_doi("5\nten An\ngio 3\ndiem 6")),
    code('''
for g, d in zip(gio, diem):         # zip ghép từng cặp cùng vị trí, dừng ở list ngắn hơn
    print(g, d)                     # gio có 5 phần tử nhưng diem chỉ có 4: in 4 cặp

gio = [1, 2, 3, 4]                  # đặt lại về 4 bạn
du = [1.6 * x + 0.5 for x in gio]   # list comprehension: tính điểm đoán cho từng bạn
print(du)                           # còn sai số dấu phẩy động ở số thứ ba
print([round(v, 1) for v in du])    # làm tròn 1 chữ số sau dấu chấm để dễ đọc
'''),
    md(mong_doi("1 2\n2 4\n3 5\n4 7\n[2.1, 3.7, 5.300000000000001, 6.9]\n[2.1, 3.7, 5.3, 6.9]")),
    code('''
a = [1, 2]       # một list
b = a            # KHÔNG tạo list mới: dán thêm nhãn b lên cùng hộp với a
b.append(3)      # sửa hộp qua nhãn b
print(a)         # a cũng thấy thay đổi
'''),
    md(mong_doi("[1, 2, 3]") + "\n\n" +
       khung("vi-sao", ["Phép gán không sao chép list, chỉ dán thêm một nhãn lên cùng hộp. Sửa qua nhãn nào thì hộp cũng đổi.",
                        "Muốn bản sao độc lập: <code>b = a[:]</code> hoặc <code>b = a.copy()</code>."], nhan="VÌ SAO LẠI LÀ [1, 2, 3]?") + "\n\n" +
       khung("loi", ["<b>IndexError.</b> List 4 phần tử có chỉ số 0 tới 3, gọi <code>gio[4]</code> là ra ngoài list.",
                     "<b>Dùng list cho phép toán.</b> <code>[1, 2] * 2</code> ra <code>[1, 2, 1, 2]</code>, không phải <code>[2, 4]</code>. Muốn tính như toán, cần NumPy ở Chương 3."])),
]

# Trang 5
cells += [
    trang(5, TEN[4], SLUG[4], "Ba bài tập. Tự viết code vào ô trống trước, chạy thử, rồi mới mở đáp án."),
    md(r'''### Bài 1.1 · Tự viết hàm MSE

Viết hàm `mse(gio, diem, w, b)` trả về $\frac{1}{n}\sum (y_i - (w x_i + b))^2$, chỉ dùng `for`, `zip`, `len`. Chạy với $w = 1{,}6,\ b = 0{,}5$ và với $w = 0,\ b = 0$.
<details><summary>Xem đáp án</summary>

Phần dư của đường $w = 1{,}6,\ b = 0{,}5$ là $-0{,}1;\ 0{,}3;\ -0{,}3;\ 0{,}1$. Bình phương cộng lại $0{,}2$, chia 4 được $0{,}05$. Đường $y = 0$ cho $(4 + 16 + 25 + 49)/4 = 23{,}5$. Code đáp án ở ô ngay dưới.
</details>'''),
    code('''
def mse(gio, diem, w, b):
    tong = 0                          # cộng dồn bình phương sai số
    for x, y in zip(gio, diem):       # đi qua từng bạn, lấy cặp (giờ, điểm)
        e = y - (w * x + b)           # phần dư: điểm thật trừ điểm đoán
        tong = tong + e ** 2          # bình phương rồi cộng vào tổng
    return tong / len(gio)            # chia cho số bạn để lấy trung bình

gio = [1, 2, 3, 4]                    # giờ học của A, B, C, D
diem = [2, 4, 5, 7]                   # điểm thi của A, B, C, D
print(mse(gio, diem, 1.6, 0.5))       # đường tốt nhất của Chương 10
print(round(mse(gio, diem, 1.6, 0.5), 6))  # làm tròn để bỏ sai số dấu phẩy động
print(mse(gio, diem, 0, 0))           # đường nằm ngang y = 0
'''),
    md(mong_doi("0.050000000000000065\n0.05\n23.5")),
    md(r'''### Bài 1.2 · Đếm xếp loại

Điểm của lớp là `[9, 7, 5.5, 8, 6.5]`. Viết hàm `xep_loai(d)` (Giỏi nếu $d \ge 8$, Khá nếu $d \ge 6{,}5$, còn lại Trung bình), rồi dùng dict đếm số bạn mỗi loại.
<details><summary>Xem đáp án</summary>

9 và 8 là Giỏi, 7 và 6,5 là Khá, 5,5 là Trung bình. Hai điểm ranh giới thuộc loại trên vì dùng `>=`. Dòng `dem.get(loai, 0) + 1` tránh `KeyError` khi gặp loại lần đầu. Code đáp án ở ô ngay dưới.
</details>'''),
    code('''
def xep_loai(d):
    if d >= 8:                # >= nên 8 điểm vẫn là Giỏi
        return "Giỏi"         # trả về ngay, không xét tiếp
    elif d >= 6.5:            # 6.5 điểm vẫn là Khá
        return "Khá"          # trả về loại Khá
    else:                     # còn lại
        return "Trung bình"   # trả về loại Trung bình

dem = {}                                 # dict rỗng: chưa đếm loại nào
for d in [9, 7, 5.5, 8, 6.5]:            # đi qua điểm của từng bạn
    loai = xep_loai(d)                   # xếp loại bạn này
    dem[loai] = dem.get(loai, 0) + 1     # get(loai, 0): chưa có khóa thì coi như 0
print(dem)                               # in kết quả đếm
'''),
    md(mong_doi("{'Giỏi': 2, 'Khá': 2, 'Trung bình': 1}")),
    md(r'''### Bài 1.3 · Đoán output trước khi chạy

Viết ra giấy ô dưới in gì, rồi mới chạy.
<details><summary>Xem đáp án</summary>

`range(1, 10, 4)` cho 1, 5, 9 (số tiếp theo 13 đã vượt 10). `a[:]` tạo hộp mới, nên thêm 3 vào `b` không đụng tới `a`: in `[1, 2] [1, 2, 3]`.
</details>'''),
    code('''
for i in range(1, 10, 4):   # bắt đầu từ 1, mỗi lần cộng 4, dừng trước 10
    print(i)                # in từng giá trị của i
a = [1, 2]                  # list gốc
b = a[:]                    # lát cắt lấy hết: tạo một bản sao mới
b.append(3)                 # chỉ sửa bản sao
print(a, b)                 # so hai list
'''),
    md(mong_doi("1\n5\n9\n[1, 2] [1, 2, 3]")),
]

nb = {"cells": cells, "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                                   "language_info": {"name": "python"}, "colab": {"provenance": [], "toc_visible": True}},
      "nbformat": 4, "nbformat_minor": 0}
json.dump(nb, open(sys.argv[1], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
