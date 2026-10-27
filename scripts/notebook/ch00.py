"""Dựng notebooks/ch00_lo_trinh_va_colab.ipynb: python3 scripts/notebook/ch00.py"""
from pathlib import Path
from nblib import Chuong, khung

c = Chuong(0, "Lộ trình AI Engineer và cách dùng Colab", "ch00-lo-trinh-va-colab",
           "Notebook đầu tiên: kiểm tra môi trường, chạy ô code, và làm quen với cách các ô của notebook dùng chung biến.",
           ["Chạy được ô code và đọc output.",
            "Biết phiên bản thư viện đang dùng.",
            "Hiểu vì sao phải chạy các ô theo thứ tự."],
           [("Lộ trình AI Engineer", "01-lo-trinh"), ("Dùng Google Colab", "02-dung-colab"), ("Bài tập", "03-bai-tap")])

c.mo_trang(1, "Không có code ở phần này. Đọc trang web để biết giáo trình gồm những phần nào.")
c.mo_trang(2, "Kiểm tra môi trường.")
c.o('''
import sys, numpy, pandas, sklearn, matplotlib      # các thư viện dùng trong Phần I và II
print(sys.version.split()[0], numpy.__version__, pandas.__version__, sklearn.__version__, matplotlib.__version__)  # phiên bản đang cài
''', "3.12.14 2.5.4 3.1.0 1.9.1 3.11.2",
    khung("doc", ["Đây là phiên bản giáo trình dùng để chạy output trong bài. Colab của bạn có thể khác; phần lớn code vẫn chạy y hệt."]))

c.mo_trang(3, "Ba bài tập khởi động.")
c.bai("0.1", "Ô code đầu tiên", "Đoán từng dòng output của ô dưới trước khi chạy.",
      "5050 là tổng 1 tới 100. $2^{10} = 1024$, $7 // 2 = 3$, $22/7 \\approx 3{,}1429$.")
c.o('''
print(sum(range(1, 101)))                  # tổng các số từ 1 tới 100
print(2 ** 10, 7 // 2, round(22 / 7, 4))   # lũy thừa, chia lấy phần nguyên, làm tròn
''', "5050\n1024 3 3.1429")
c.bai("0.2", "Gây lỗi rồi sửa", "Restart session, rồi chạy riêng ô cuối cùng (bỏ qua ô tạo biến `ten`). Đọc lỗi và sửa.",
      "Python báo `NameError: name 'ten' is not defined` vì ô tạo `ten` chưa chạy. Sửa: chạy ô đó trước, hoặc Run all.")
c.bai("0.3", "Thứ tự ô", "Chạy hai ô dưới. Rồi sửa ô thứ nhất thành `ten = \"Bình\"`, không chạy lại nó, và chạy lại ô thứ hai.",
      "Vẫn in \"Chào An\": sửa chữ trong ô không đổi gì cho tới khi ô được chạy.")
c.o('''
ten = "An"          # ô thứ nhất: tạo biến
print(ten)          # in ra để xác nhận
''', "An")
c.o('''
print(f"Chào {ten}")   # ô thứ hai: dùng biến của ô thứ nhất
''', "Chào An")

c.ghi(Path(__file__).resolve().parents[2] / "notebooks/ch00_lo_trinh_va_colab.ipynb")
