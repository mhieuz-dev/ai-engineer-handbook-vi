"""Dựng notebooks/ch02_python_cho_du_lieu.ipynb: python3 scripts/notebook/ch02.py"""
from pathlib import Path
from nblib import Chuong, khung, md

c = Chuong(2, "Python cho dữ liệu", "ch02-python-cho-du-lieu",
           "Từ dòng chữ thô trong file tới list số dùng được: chuỗi, thư viện chuẩn, đọc CSV, bắt lỗi, và lớp mô hình đầu tiên.",
           ["Làm sạch và tách một dòng dữ liệu bằng strip, split, float.",
            "Dùng math, random với seed, statistics.",
            "Đọc file CSV thành list số, bỏ qua ô hỏng bằng try và except.",
            "Viết một lớp mô hình có __init__ và du_doan, đúng khuôn scikit-learn."],
           [("Chuỗi, tuple và set", "01-chuoi-tuple-set"), ("Thư viện chuẩn", "02-thu-vien-chuan"),
            ("Đọc file CSV và xử lý lỗi", "03-doc-file-csv"), ("Lớp và đối tượng", "04-lop-va-doi-tuong"), ("Bài tập", "05-bai-tap")])

c.mo_trang(1, "Biến một dòng chữ thô thành các giá trị dùng được.")
c.o('''
dong = "  An,3,5.5  "          # một dòng dữ liệu thô: tên, giờ học, điểm
sach = dong.strip()            # strip bỏ khoảng trắng ở hai đầu chuỗi
print(repr(sach))              # repr in kèm dấu nháy để thấy rõ đã hết dấu cách
cot = sach.split(",")          # split cắt chuỗi tại mỗi dấu phẩy, trả về list
print(cot)                     # các phần tử vẫn là chuỗi
print(cot[0].upper(), float(cot[2]) + 1)  # upper viết hoa; float đổi chuỗi "5.5" thành số
print(", ".join(["A", "B", "C"]))         # join làm ngược split: nối list thành chuỗi
''', "'An,3,5.5'\n['An', '3', '5.5']\nAN 6.5\nA, B, C",
    khung("loi", ["<b>Quên đổi chuỗi thành số.</b> Số đọc từ file luôn là chuỗi, và <code>\"7\" + \"8\"</code> ra <code>\"78\"</code> mà không báo lỗi."]))
c.o('''
diem_A = (1, 2)       # tuple: tọa độ của bạn A (giờ học, điểm), không sửa được
x, y = diem_A         # mở gói: gán từng phần tử cho từng biến
print(x, y, len(diem_A))  # in hai giá trị và độ dài tuple
nhan = ["meo", "cho", "meo", "ga", "cho", "meo"]  # nhãn của 6 bức ảnh
print(sorted(set(nhan)), len(set(nhan)))            # set bỏ trùng; sorted xếp lại cho output cố định
''', "1 2 2\n['cho', 'ga', 'meo'] 3")

c.mo_trang(2, "Mượn code có sẵn của Python: math, random, statistics.")
c.o('''
import math                       # các hàm toán học
import random                     # sinh số ngẫu nhiên
import statistics                 # thống kê mô tả
print(math.sqrt(16), math.log(math.e), round(math.pi, 4))  # căn bậc hai, logarit tự nhiên, số pi
random.seed(42)                   # đặt hạt giống
print(random.random())            # một số ngẫu nhiên trong [0, 1)
random.seed(42)                   # đặt lại đúng hạt giống cũ
print(random.random())            # ra lại đúng số vừa rồi
''', "4.0 1.0 3.1416\n0.6394267984578837\n0.6394267984578837",
    khung("truc-giac", ["Cùng seed thì cùng dãy số, như cùng một bộ bài đã xáo sẵn theo cùng một cách. Vì thế output trên máy bạn khớp với output in trong bài."]))
c.o('''
diem = [2, 4, 5, 7]                           # điểm của bốn bạn A, B, C, D
print(statistics.mean(diem))                  # trung bình
print(statistics.median(diem))                # trung vị
print(round(statistics.stdev(diem), 4))       # độ lệch chuẩn mẫu: chia cho n - 1
print(round(statistics.pstdev(diem), 4))      # độ lệch chuẩn tổng thể: chia cho n
''', "4.5\n4.5\n2.0817\n1.8028",
    khung("vi-sao", ["Tổng bình phương độ lệch là 13. Chia 4 rồi lấy căn được 1,8028; chia 3 rồi lấy căn được 2,0817.",
                     "statistics.stdev và pandas chia n - 1, còn NumPy np.std mặc định chia n. Hai thư viện ra hai số thì kiểm tra mẫu số trước."],
          nhan="VÌ SAO LẠI LÀ HAI CON SỐ KHÁC NHAU?"))

c.mo_trang(3, "Ghi file CSV, đọc lại thành list số, và bắt lỗi khi gặp ô hỏng.")
c.o('''
import csv                                          # module đọc ghi CSV
noi_dung = "ten,gio,diem\\nA,1,2\\nB,2,4\\nC,3,5\\nD,4,7\\n"  # \\n là ký tự xuống dòng
with open("lop.csv", "w", encoding="utf-8") as f:   # "w": mở để ghi
    f.write(noi_dung)                                 # ghi cả chuỗi vào file
gio, diem = [], []                                  # hai list rỗng để gom dữ liệu
with open("lop.csv", encoding="utf-8") as f:        # mở lại để đọc
    for hang in csv.DictReader(f):                  # mỗi hàng là một dict theo tên cột
        gio.append(float(hang["gio"]))              # đổi chuỗi thành số rồi thêm vào list
        diem.append(float(hang["diem"]))            # tương tự cho cột điểm
print(gio)                                          # cột giờ học
print(diem)                                         # cột điểm
''', "[1.0, 2.0, 3.0, 4.0]\n[2.0, 4.0, 5.0, 7.0]")
c.o('''
for s in ["5.5", "abc", "7"]:    # ba chuỗi, một chuỗi không phải số
    try:                         # thử chạy khối này
        print(float(s))          # float("abc") sẽ báo ValueError
    except ValueError:           # bắt đúng loại lỗi đó
        print("Bỏ qua:", s)      # xử lý rồi đi tiếp
''', "5.5\nBỏ qua: abc\n7.0",
    khung("loi", ["<b>Bắt mọi lỗi bằng except trơn.</b> <code>except:</code> không ghi tên lỗi sẽ nuốt cả lỗi gõ sai tên biến. Luôn ghi rõ, ví dụ <code>except ValueError:</code>."]))

c.mo_trang(4, "Gói tham số và hàm dự đoán vào một lớp.")
c.o('''
class MoHinhTuyenTinh:                     # định nghĩa một lớp
    def __init__(self, w=0.0, b=0.0):      # chạy tự động khi tạo đối tượng
        self.w = w                          # cất tham số w vào chính đối tượng
        self.b = b                          # cất tham số b

    def du_doan(self, x):                   # phương thức dự đoán
        return [self.w * xi + self.b for xi in x]  # dùng w, b đã cất

mh = MoHinhTuyenTinh(w=1.6, b=0.5)          # đối tượng thứ nhất
print(mh.w, mh.b)                           # đọc tham số bên trong
print([round(v, 2) for v in mh.du_doan([1, 2, 3, 4])])  # dự đoán cho bốn bạn
mh2 = MoHinhTuyenTinh()                      # đối tượng thứ hai, tham số mặc định
print(mh2.du_doan([1, 2]))                  # w = b = 0 nên đoán toàn 0
''', "1.6 0.5\n[2.1, 3.7, 5.3, 6.9]\n[0.0, 0.0]",
    khung("thu", ["<b>1.</b> Xóa chữ <code>self</code> trong dòng <code>def du_doan(self, x):</code> rồi chạy lại. Đọc kỹ thông báo lỗi.",
                  "<b>2.</b> Đổi <code>mh.w = 2</code> rồi gọi lại <code>mh.du_doan([1])</code>. <code>mh2</code> có bị ảnh hưởng không?"]))

c.mo_trang(5, "Ba bài tập. Tự viết code trước, rồi mới mở đáp án.")
c.bai("2.1", "Đọc file có ô hỏng", "Đọc cột `diem` của file có ô rỗng và ô `abc`, bỏ qua ô hỏng nhưng ghi lại tên bạn bị bỏ, rồi in trung bình.",
      "Ô rỗng và `abc` đều báo `ValueError`. Hợp lệ còn 8; 6,5; 9, trung bình $23{,}5/3 \\approx 7{,}8333$. Thay ô hỏng bằng 0 thì trung bình tụt sai xuống 4,7. Code đáp án ở ô ngay dưới.")
c.o('''
noi_dung = "ten,diem\\nA,8\\nB,\\nC,6.5\\nD,abc\\nE,9\\n"   # B rỗng, D không phải số
with open("diem_lop.csv", "w", encoding="utf-8") as f:   # ghi file thử
    f.write(noi_dung)                                     # nội dung năm dòng dữ liệu
hop_le, bo_qua = [], []                                   # điểm dùng được và tên bị bỏ
with open("diem_lop.csv", encoding="utf-8") as f:         # đọc lại
    for hang in csv.DictReader(f):                        # từng hàng là một dict
        try:                                              # thử đổi điểm thành số
            hop_le.append(float(hang["diem"]))            # ô rỗng và "abc" đều báo ValueError
        except ValueError:                                # gặp ô hỏng
            bo_qua.append(hang["ten"])                    # ghi lại ai bị bỏ
print(hop_le, bo_qua)                                     # kết quả lọc
print(round(sum(hop_le) / len(hop_le), 4))                # trung bình điểm hợp lệ
''', "[8.0, 6.5, 9.0] ['B', 'D']\n7.8333")
c.bai("2.2", "Lớp đếm từ", "Viết lớp `DemTu` có `dem`, `them(cau)` và `pho_bien(k)`. Gọi `them` với hai câu rồi in kết quả.",
      "Nhờ `lower()`, \"Học\" và \"học\" là một từ nên \"học\" có 3 lần. `sorted` giữ thứ tự gặp trước khi bằng nhau, nên \"máy\" đứng thứ hai. Code đáp án ở ô ngay dưới.")
c.o('''
class DemTu:                                                   # lớp đếm tần suất từ
    def __init__(self):                                        # tạo đối tượng mới
        self.dem = {}                                          # mỗi đối tượng một dict riêng

    def them(self, cau):                                       # thêm một câu
        for tu in cau.lower().split():                         # chữ thường rồi tách theo khoảng trắng
            self.dem[tu] = self.dem.get(tu, 0) + 1             # mẫu đếm quen thuộc

    def pho_bien(self, k):                                     # k từ nhiều nhất
        cap = sorted(self.dem.items(), key=lambda t: t[1], reverse=True)  # xếp theo số lần, giảm dần
        return cap[:k]                                         # lấy k cặp đầu

d = DemTu()                                                    # tạo bộ đếm
d.them("Học máy học sâu")                                      # câu thứ nhất
d.them("học tăng cường")                                       # câu thứ hai
print(d.dem)                                                   # toàn bộ bảng đếm
print(d.pho_bien(2))                                           # hai từ phổ biến nhất
''', "{'học': 3, 'máy': 1, 'sâu': 1, 'tăng': 1, 'cường': 1}\n[('học', 3), ('máy', 1)]")
c.bai("2.3", "Độ lệch chuẩn tự tính", "Không dùng `statistics`, tính độ lệch chuẩn của `[2, 4, 5, 7]` theo cách chia $n$ và chia $n - 1$.",
      "Tổng bình phương độ lệch là 13. Chia 4 rồi lấy căn được 1,8028 (khớp `pstdev`), chia 3 rồi lấy căn được 2,0817 (khớp `stdev`). Code đáp án ở ô ngay dưới.")
c.o('''
diem = [2, 4, 5, 7]                                # điểm bốn bạn
tb = sum(diem) / len(diem)                         # trung bình 4.5
tong = sum((v - tb) ** 2 for v in diem)            # tổng bình phương độ lệch
print(tb, tong)                                    # 4.5 và 13.0
print(round(math.sqrt(tong / len(diem)), 4))       # chia n: khớp pstdev
print(round(math.sqrt(tong / (len(diem) - 1)), 4)) # chia n - 1: khớp stdev
''', "4.5 13.0\n1.8028\n2.0817")

c.ghi(Path(__file__).resolve().parents[2] / "notebooks/ch02_python_cho_du_lieu.ipynb")
