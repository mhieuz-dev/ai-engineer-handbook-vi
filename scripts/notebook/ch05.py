"""Dựng notebooks/ch05_dai_so_tuyen_tinh.ipynb: python3 scripts/notebook/ch05.py"""
from pathlib import Path
from nblib import Chuong, khung

c = Chuong(5, "Đại số tuyến tính cho ML", "ch05-dai-so-tuyen-tinh",
           "Vector, ma trận như phép biến đổi, hệ phương trình và trị riêng, mỗi khái niệm gắn với một chỗ dùng cụ thể trong ML.",
           ["Tính độ dài, tích vô hướng, cosine giữa hai vector.",
            "Đọc ma trận như phép biến đổi, ghép phép biến đổi bằng nhân ma trận.",
            "Giải hệ phương trình và tìm lại nghiệm hồi quy bằng phương trình chuẩn.",
            "Tính trị riêng, vector riêng và thấy hướng trải rộng nhất của dữ liệu."],
           [("Vector và tích vô hướng", "01-vector"), ("Ma trận là một phép biến đổi", "02-ma-tran-la-bien-doi"),
            ("Hệ phương trình và nghịch đảo", "03-he-phuong-trinh"), ("Trị riêng và vector riêng", "04-tri-rieng"), ("Bài tập", "05-bai-tap")])

c.mo_trang(1, "Cộng vector, độ dài, tích vô hướng, cosine.")
c.o('''
import numpy as np                       # thư viện tính toán
u = np.array([3.0, 4.0])                 # vector u
v = np.array([4.0, 3.0])                 # vector v
print(u + v, 2 * u)                      # cộng từng tọa độ; kéo dài gấp đôi
print(np.linalg.norm(u), u @ v)          # độ dài của u; tích vô hướng
print(round(u @ v / (np.linalg.norm(u) * np.linalg.norm(v)), 4))  # cosine giữa u và v
print(np.array([1.0, 0.0]) @ np.array([0.0, 1.0]))                # hai trục vuông góc
''', "[7. 7.] [6. 8.]\n5.0 24.0\n0.96\n0.0",
    khung("truc-giac", ["Cosine bằng 1 là cùng hướng, 0 là vuông góc, -1 là ngược hướng. u và v lệch nhau một chút quanh đường chéo nên cosine 0,96."]))

c.mo_trang(2, "Kéo giãn, quay, ghép hai phép biến đổi, định thức.")
c.o('''
M = np.array([[2.0, 0.0], [0.0, 1.0]])   # kéo giãn ngang gấp đôi
R = np.array([[0.0, -1.0], [1.0, 0.0]])  # quay 90 độ ngược chiều kim đồng hồ
p = np.array([1.0, 1.0])                 # điểm (1, 1)
print(M @ p, R @ p)                      # từng phép riêng lẻ
print(R @ (M @ p))                       # kéo giãn trước, quay sau
print((R @ M) @ p)                       # ghép thành một ma trận: cùng kết quả
print((M @ R) @ p)                       # đổi thứ tự: khác
print(np.linalg.det(M), np.linalg.det(R))                 # định thức
print(np.linalg.det(np.array([[1.0, 2.0], [2.0, 4.0]])))  # hai cột cùng hướng
''', "[2. 1.] [-1.  1.]\n[-1.  2.]\n[-1.  2.]\n[-2.  1.]\n2.0 1.0\n0.0",
    khung("loi", ["<b>Đọc sai thứ tự ghép.</b> R @ M @ p là làm M trước rồi mới làm R. Đọc từ phải sang trái."]))

c.mo_trang(3, "Giải hệ phương trình, nghịch đảo, phương trình chuẩn.")
c.o('''
A = np.array([[2.0, 1.0], [1.0, 3.0]])   # 2x + y = 5; x + 3y = 10
b = np.array([5.0, 10.0])                # vế phải
print(np.linalg.solve(A, b))             # nghiệm (x, y)
print(np.linalg.inv(A))                  # ma trận nghịch đảo
print(np.linalg.inv(A) @ b)              # cùng nghiệm, nhưng nên dùng solve
''', "[1. 3.]\n[[ 0.6 -0.2]\n [-0.2  0.4]]\n[1. 3.]")
c.o('''
x = np.array([1, 2, 3, 4.0])             # giờ học của A, B, C, D
y = np.array([2, 4, 5, 7.0])             # điểm thi
X = np.column_stack([np.ones(4), x])     # cột toàn 1 (cho b) ghép với cột giờ học (cho w)
print(X.T @ X, X.T @ y)                  # hai vế phương trình chuẩn
print(np.linalg.solve(X.T @ X, X.T @ y)) # nghiệm (b, w)
''', "[[ 4. 10.]\n [10. 30.]] [18. 53.]\n[0.5 1.6]",
    khung("doc", ["b = 0,5 và w = 1,6: đúng đường thẳng tốt nhất của Chương 10.",
                  "Trong X.T @ X: 4 là số bạn, 10 là tổng giờ học, 30 là tổng bình phương giờ học."]))

c.mo_trang(4, "Trị riêng, vector riêng, và hướng trải rộng nhất của dữ liệu.")
c.o('''
S = np.array([[2.0, 1.0], [1.0, 2.0]])          # ma trận đối xứng
gia_tri, vec = np.linalg.eigh(S)                # trị riêng xếp tăng dần; mỗi cột là một vector riêng
print(gia_tri)                                  # hai trị riêng
print(vec)                                      # hai vector riêng (theo cột)
print(S @ vec[:, 1], gia_tri[1] * vec[:, 1])    # kiểm tra A v = lambda v
''', "[1. 3.]\n[[-0.70710678  0.70710678]\n [ 0.70710678  0.70710678]]\n[2.12132034 2.12132034] [2.12132034 2.12132034]")
c.o('''
D = np.array([[1, 2], [2, 1], [3, 4], [4, 3]], dtype=float)  # bảng X của Chương 3
Dc = D - D.mean(axis=0)                  # trừ trung bình từng cột
C = Dc.T @ Dc / 4                        # ma trận hiệp phương sai
print(C)                                 # đường chéo là phương sai từng cột
gia_tri, vec = np.linalg.eigh(C)         # trị riêng và vector riêng
print(gia_tri)                           # phương sai theo hai hướng chính
print(vec)                               # hai hướng chính
''', "[[1.25 0.75]\n [0.75 1.25]]\n[0.5 2. ]\n[[-0.70710678  0.70710678]\n [ 0.70710678  0.70710678]]",
    khung("vi-sao", ["Hướng (1, 1) là hướng bốn bạn trải ra xa nhất, phương sai 2. Giữ một con số theo hướng đó là giữ 2 / 2,5 = 80% tổng phương sai: ý tưởng của PCA ở Chương 20."],
          nhan="VÌ SAO LẠI LÀ HƯỚNG ĐƯỜNG CHÉO?"))

c.mo_trang(5, "Ba bài tập. Tự tính tay trước, rồi mới mở đáp án.")
c.bai("5.1", "Ai giống ai?", "Với A $= (1, 7)$, I $= (7, 7)$, C $= (3, 8)$, tính cosine và khoảng cách giữa A với I, A với C.",
      "Cosine A, I $= 56/70 = 0{,}8$; cosine A, C $\\approx 0{,}9766$. Khoảng cách A, I là 6; A, C là $\\sqrt 5 \\approx 2{,}2361$. Cosine chỉ nhìn tỷ lệ, khoảng cách nhìn cả độ lớn. Code đáp án ở ô ngay dưới.")
c.o('''
A_, I_, C_ = np.array([1.0, 7.0]), np.array([7.0, 7.0]), np.array([3.0, 8.0])   # (giờ học, giờ ngủ)
cos = lambda p, q: round(p @ q / np.linalg.norm(p) / np.linalg.norm(q), 4)       # hàm cosine
print(cos(A_, I_), cos(A_, C_))                              # độ giống về hướng
print(np.linalg.norm(A_ - I_), round(np.linalg.norm(A_ - C_), 4))  # khoảng cách
''', "0.8 0.9766\n6.0 2.2361")
c.bai("5.2", "Hệ ba ẩn", "Giải $x + y + z = 6$, $2y + 5z = -4$, $2x + 5y - z = 27$ và tính định thức của ma trận hệ số.",
      "Nghiệm $(5, 3, -2)$, định thức $-21$ khác 0 nên nghiệm duy nhất. Nhớ hệ số 0 của $x$ ở phương trình thứ hai. Code đáp án ở ô ngay dưới.")
c.o('''
A = np.array([[1, 1, 1], [0, 2, 5], [2, 5, -1]], dtype=float)   # hệ số; hàng hai không có x
b = np.array([6, -4, 27], dtype=float)                          # vế phải
print(np.linalg.solve(A, b), round(np.linalg.det(A), 6))        # nghiệm và định thức
''', "[ 5.  3. -2.] -21.0")
c.bai("5.3", "Trị riêng của phép kéo giãn và phép quay", "Đoán trị riêng của $M$ và $R$ ở trang 2 trước khi chạy ô dưới.",
      "$M$: trị riêng 2 theo trục ngang, 1 theo trục dọc. $R$ quay mọi hướng nên không có trị riêng thực; NumPy trả về $i$ và $-i$.")
c.o('''
print(np.linalg.eigh(np.array([[2.0, 0.0], [0.0, 1.0]])).eigenvalues)   # ma trận kéo giãn
print(np.linalg.eig(np.array([[0.0, -1.0], [1.0, 0.0]])).eigenvalues)   # ma trận quay: eig, không phải eigh
''', "[1. 2.]\n[0.+1.j 0.-1.j]")

c.ghi(Path(__file__).resolve().parents[2] / "notebooks/ch05_dai_so_tuyen_tinh.ipynb")
