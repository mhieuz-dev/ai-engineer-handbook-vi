"""Dựng notebooks/ch03_numpy.ipynb: python3 scripts/notebook/ch03.py"""
from pathlib import Path
from nblib import Chuong, khung

c = Chuong(3, "NumPy", "ch03-numpy",
           "Mảng, broadcasting, lọc, trục và nhân ma trận: bộ công cụ tính toán mà mọi thư viện ML đều xây lên trên.",
           ["Tạo mảng và đọc được shape, số chiều.",
            "Tính cho cả mảng không vòng lặp, đoán được shape khi broadcasting.",
            "Lấy hàng, cột, lọc bằng điều kiện; biết khi nào lát cắt là view.",
            "Tính theo trục, nhân ma trận bằng @, sinh số ngẫu nhiên có seed."],
           [("Mảng và shape", "01-mang-va-shape"), ("Phép tính và broadcasting", "02-phep-tinh-va-broadcasting"),
            ("Chỉ số, lát cắt và lọc", "03-chi-so-va-loc"), ("Trục, ma trận và số ngẫu nhiên", "04-truc-va-ma-tran"), ("Bài tập", "05-bai-tap")])

c.mo_trang(1, "Mảng NumPy đầu tiên, shape và các cách tạo mảng nhanh.")
c.o('''
import numpy as np                        # quy ước của cả cộng đồng: đặt tên ngắn là np
x = np.array([1, 2, 3, 4])                # đổi list thành mảng: giờ học của bốn bạn
print(x, x.dtype, x.shape, x.ndim)        # giá trị, kiểu, hình dạng, số chiều
X = np.array([[1, 2],                     # bạn A: giờ học, giờ ngủ
              [2, 1],                     # bạn B
              [3, 4],                     # bạn C
              [4, 3]])                    # bạn D
print(X.shape, X.ndim)                    # 4 hàng, 2 cột; hai chiều
''', "[1 2 3 4] int64 (4,) 1\n(4, 2) 2")
c.o('''
print(np.zeros(3))                 # 3 số 0
print(np.ones((2, 2)))             # bảng 2 x 2 toàn số 1; shape là một tuple
print(np.arange(0, 1, 0.25))       # như range, bước thực, dừng TRƯỚC 1
print(np.linspace(0, 1, 5))        # 5 số cách đều từ 0 tới 1, lấy cả 1
''', "[0. 0. 0.]\n[[1. 1.]\n [1. 1.]]\n[0.   0.25 0.5  0.75]\n[0.   0.25 0.5  0.75 1.  ]",
    khung("loi", ["<b>Nhầm (4,) với (4, 1).</b> (4,) là một dãy 4 số, (4, 1) là bảng 4 hàng 1 cột. scikit-learn đòi X hai chiều, nên Chương 10 phải <code>reshape(-1, 1)</code>."]))

c.mo_trang(2, "Phép tính từng phần tử và luật broadcasting.")
c.o('''
y = np.array([2, 4, 5, 7])          # điểm thi
print(x * 2, x + y, x * y, x ** 2)  # nhân số, cộng hai mảng, nhân từng cặp, bình phương
print(1.6 * x + 0.5)                # dự đoán của đường thẳng cho cả bốn bạn
print([1, 2, 3, 4] * 2)             # so sánh: với list, * 2 là lặp lại list
''', "[2 4 6 8] [ 3  6  8 11] [ 2  8 15 28] [ 1  4  9 16]\n[2.1 3.7 5.3 6.9]\n[1, 2, 3, 4, 1, 2, 3, 4]")
c.o('''
A = np.array([[1, 2, 3],
              [4, 5, 6]])          # shape (2, 3)
v = np.array([10, 20, 30])          # shape (3,): một hàng
print(A + v)                        # v cộng vào từng hàng
col = np.array([[100], [200]])      # shape (2, 1): một cột
print(A + col)                      # col cộng vào từng cột
try:                                # thử một phép không khớp shape
    A + np.array([1, 2])            # (2, 3) với (2,)
except ValueError as e:             # NumPy báo lỗi broadcasting
    print("ValueError:", e)         # in thông báo lỗi
''', "[[11 22 33]\n [14 25 36]]\n[[101 102 103]\n [204 205 206]]\nValueError: operands could not be broadcast together with shapes (2,3) (2,)",
    khung("vi-sao", ["So shape từ phải sang trái. Hai chiều khớp khi bằng nhau hoặc một bên bằng 1. (2, 3) với (2,): chiều phải 3 và 2 khác nhau, không bên nào bằng 1."],
          nhan="VÌ SAO LẠI LÀ LỖI Ở PHÉP CUỐI?"))

c.mo_trang(3, "Lấy phần tử, hàng, cột; lọc bằng điều kiện; view và copy.")
c.o('''
print(x[0], x[-1], x[1:3])          # phần tử đầu, cuối, lát cắt
print(A[1, 2], A[:, 0], A[0])       # hàng 1 cột 2; cả cột 0; cả hàng 0
print(x > 2)                        # mảng đúng sai
print(x[x > 2])                     # chỉ giữ phần tử > 2
print(y[x % 2 == 0])                # điểm của bạn có số giờ học chẵn
''', "1 4 [2 3]\n6 [1 4] [1 2 3]\n[False False  True  True]\n[3 4]\n[4 7]")
c.o('''
a = np.array([1, 2, 3])   # mảng gốc
c2 = a[:2]                # lát cắt là VIEW: cửa sổ nhìn vào a
c2[0] = 99                # sửa qua cửa sổ
print(a)                  # a cũng đổi
d = a.copy()              # bản sao thật
d[1] = -1                 # sửa bản sao
print(a, d)               # a không đổi thêm
''', "[99  2  3]\n[99  2  3] [99 -1  3]",
    khung("loi", ["<b>Dùng and để ghép điều kiện.</b> Phải dùng <code>&amp;</code> và bọc ngoặc: <code>x[(x &gt; 1) &amp; (x &lt; 4)]</code>."]))

c.mo_trang(4, "Tổng theo trục, nhân ma trận, đổi hình, số ngẫu nhiên.")
c.o('''
print(A.sum())             # tổng mọi phần tử
print(A.sum(axis=0))       # trục 0 bị gộp: tổng từng CỘT
print(A.sum(axis=1))       # trục 1 bị gộp: tổng từng HÀNG
print(A.mean(axis=0))      # trung bình từng cột
print(y.mean(), y.std(), y.std(ddof=1))   # trung bình; độ lệch chuẩn chia n; chia n - 1
''', "21\n[5 7 9]\n[ 6 15]\n[2.5 3.5 4.5]\n4.5 1.8027756377319946 2.0816659994661326",
    khung("truc-giac", ["Trục ghi vào là trục bị gộp lại và biến mất. A có shape (2, 3): sum(axis=0) còn shape (3,), sum(axis=1) còn shape (2,)."]))
c.o('''
W = np.array([[1, 0],         # ma trận trọng số
              [0, 2],         # 3 hàng
              [1, 1]])        # 2 cột: shape (3, 2)
print(A @ W)                  # (2, 3) @ (3, 2) ra (2, 2)
print((A @ W).shape)          # hai số giữa khớp và biến mất
print(A.T.shape)              # chuyển vị
print(A.reshape(3, 2))        # xếp lại 6 số thành 3 hàng 2 cột
print(x.reshape(-1, 1).shape) # -1: tự tính
''', "[[ 4  7]\n [10 16]]\n(2, 2)\n(3, 2)\n[[1 2]\n [3 4]\n [5 6]]\n(4, 1)")
c.o('''
rng = np.random.default_rng(42)     # bộ sinh số ngẫu nhiên riêng, seed 42
print(rng.random(3))                # 3 số thực trong [0, 1)
print(rng.integers(1, 7, size=5))   # 5 lần tung xúc xắc
print(rng.normal(0, 1, size=2))     # 2 số theo phân phối chuẩn
''', "[0.77395605 0.43887844 0.85859792]\n[1 5 2 1 4]\n[ 0.1278404  -0.31624259]",
    khung("doc", ["Output này chạy với NumPy 2.5. NumPy không cam kết giữ nguyên dãy số giữa mọi phiên bản, nên nếu Colab cài bản khác mà số lệch thì không phải lỗi của bạn."]))

c.mo_trang(5, "Ba bài tập. Tự viết code trước, rồi mới mở đáp án.")
c.bai("3.1", "MSE không vòng lặp", "Viết lại hàm MSE của Bài 1.1 bằng NumPy trong một dòng tính toán, với $w = 1{,}6,\\ b = 0{,}5$.",
      "Phần dư là $-0{,}1;\\ 0{,}3;\\ -0{,}3;\\ 0{,}1$, MSE $= 0{,}05$, khớp Bài 1.1. Code đáp án ở ô ngay dưới.")
c.o('''
x = np.array([1, 2, 3, 4], dtype=float)   # giờ học
y = np.array([2, 4, 5, 7], dtype=float)   # điểm thi
w, b = 1.6, 0.5                           # đường thẳng tốt nhất
e = y - (w * x + b)                       # phần dư của cả bốn bạn cùng lúc
print(e, np.mean(e ** 2))                 # MSE trong một dòng
''', "[-0.1  0.3 -0.3  0.1] 0.050000000000000065")
c.bai("3.2", "Chuẩn hóa một bảng", "Chuẩn hóa từng cột của `X`: trừ trung bình cột, chia độ lệch chuẩn cột. Kiểm tra mỗi cột sau chuẩn hóa có trung bình 0, độ lệch chuẩn 1.",
      "Mỗi cột có trung bình 2,5 và độ lệch chuẩn $\\sqrt{1{,}25} \\approx 1{,}118$. `X - mu` là broadcasting `(4, 2)` với `(2,)`. Code đáp án ở ô ngay dưới.")
c.o('''
X = np.array([[1, 2], [2, 1], [3, 4], [4, 3]], dtype=float)  # bảng 4 mẫu, 2 đặc trưng
mu = X.mean(axis=0)            # trung bình từng cột
sd = X.std(axis=0)             # độ lệch chuẩn từng cột
Z = (X - mu) / sd              # broadcasting vào từng hàng
print(mu, sd)                  # thống kê trước chuẩn hóa
print(np.round(Z, 4))          # bảng đã chuẩn hóa
print(np.round(Z.mean(axis=0), 10), Z.std(axis=0))  # kiểm tra: trung bình 0, độ lệch chuẩn 1
''', "[2.5 2.5] [1.11803399 1.11803399]\n[[-1.3416 -0.4472]\n [-0.4472 -1.3416]\n [ 0.4472  1.3416]\n [ 1.3416  0.4472]]\n[0. 0.] [1. 1.]")
c.bai("3.3", "Đoán shape trước khi chạy", "Viết ra giấy shape kết quả (hoặc \"lỗi\") của ba phép tính trong ô dưới, rồi mới chạy.",
      "(4, 3) @ (3, 2) ra (4, 2). (4, 1) cộng (3,) ra (4, 3). (2, 3) cộng (3, 2) báo lỗi vì 3 và 2 khác nhau, không bên nào bằng 1.")
c.o('''
print((np.ones((4, 3)) @ np.ones((3, 2))).shape)   # nhân ma trận
print((np.ones((4, 1)) + np.ones((3,))).shape)     # broadcasting hai phía
try:                                               # phép thứ ba có chạy được không?
    np.ones((2, 3)) + np.ones((3, 2))              # so từ phải: 3 và 2
except ValueError as e:                            # không khớp
    print("ValueError:", e)                        # in thông báo lỗi
''', "(4, 2)\n(4, 3)\nValueError: operands could not be broadcast together with shapes (2,3) (3,2)")

c.ghi(Path(__file__).resolve().parents[2] / "notebooks/ch03_numpy.ipynb")
