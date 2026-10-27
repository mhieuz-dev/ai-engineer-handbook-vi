"""Dựng notebooks/ch23_no_ron_mang_nhieu_lop.ipynb: python3 scripts/notebook/ch23.py"""
from pathlib import Path
from nblib import Chuong, khung

c = Chuong(23, "Nơ-ron và mạng nhiều lớp", "ch23-no-ron-mang-nhieu-lop",
           "Một nơ-ron là w · x + b qua hàm kích hoạt. Xếp nhiều nơ-ron thành lớp, nhiều lớp thành mạng, tự đặt trọng số giải XOR, rồi để MLPClassifier tự học trên hai vầng trăng.",
           ["Tính tay một nơ-ron và một mạng hai lớp.",
            "Thấy vì sao không có hàm kích hoạt thì mạng sâu chỉ là hồi quy.",
            "Giải XOR bằng trọng số đặt tay, viết truyền xuôi cho cả lô.",
            "Dùng MLPClassifier và đếm số tham số."],
           [("Một nơ-ron", "01-mot-no-ron"), ("Vì sao cần phi tuyến", "02-vi-sao-can-phi-tuyen"),
            ("Giải XOR và lượt truyền xuôi", "03-xor-va-truyen-xuoi"), ("MLP trong scikit-learn", "04-mlp-scikit-learn"), ("Bài tập", "05-bai-tap")])

c.mo_trang(1, "Một nơ-ron với sigmoid và ReLU.")
c.o('''
import numpy as np                           # tính toán
sig = lambda z: 1 / (1 + np.exp(-z))         # sigmoid
relu = lambda z: np.maximum(0, z)            # ReLU
x = np.array([2.0, 3.0])                     # đầu vào
w = np.array([0.5, -0.4])                    # trọng số
b = 0.1                                      # hệ số chặn
z = w @ x + b                                # tổng có trọng số (23.1)
print(round(float(z), 4), round(float(sig(z)), 4), float(relu(z)))   # z, sigmoid, ReLU
''', "-0.1 0.475 0.0")

c.mo_trang(2, "Hai lớp tuyến tính gộp thành một.")
c.o('''
A = np.array([[1.0, 2.0], [3.0, 4.0]])    # lớp thứ nhất
B = np.array([[0.5, 0.0], [1.0, 1.0]])    # lớp thứ hai
v = np.array([1.0, -1.0])                 # một đầu vào
print(v @ A @ B, v @ (A @ B))             # qua hai lớp, và qua một lớp gộp AB
''', "[-3. -2.] [-3. -2.]",
    khung("vi-sao", ["Ghép hai phép biến đổi tuyến tính là nhân hai ma trận (Chương 5). Không có hàm kích hoạt, mạng 100 lớp cũng chỉ là một phép tuyến tính."],
          nhan="VÌ SAO LẠI BẰNG NHAU?"))

c.mo_trang(3, "Mạng XOR với trọng số đặt tay.")
c.o('''
X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]], dtype=float)   # 4 mẫu, 2 đặc trưng
W1 = np.array([[1, 1], [1, 1]], dtype=float)                   # 2 đầu vào, 2 nơ-ron ẩn
b1 = np.array([0, -1.0])                                       # hệ số chặn lớp ẩn
w2 = np.array([1, -2.0])                                       # lớp ra
b2 = 0.0                                                       # hệ số chặn lớp ra
H = relu(X @ W1 + b1)                                          # (4, 2) @ (2, 2) + (2,) -> (4, 2)
print(H)                                                       # đặc trưng mà lớp ẩn tạo ra
print(H @ w2 + b2)                                             # đầu ra: đúng bảng XOR
''', "[[0. 0.]\n [1. 0.]\n [1. 0.]\n [2. 1.]]\n[0. 1. 1. 0.]",
    khung("truc-giac", ["Cột h₂ bằng 1 đúng ở (1, 1): lớp ẩn tự tạo ra đặc trưng x₁x₂ mà Chương 21 phải thêm bằng tay."]))

c.mo_trang(4, "MLPClassifier trên hai vầng trăng.")
c.o('''
from sklearn.datasets import make_moons                        # dữ liệu
from sklearn.model_selection import train_test_split           # chia
from sklearn.neural_network import MLPClassifier               # mạng nhiều lớp
from sklearn.linear_model import LogisticRegression            # để so sánh
Xm, ym = make_moons(300, noise=0.3, random_state=0)            # như các chương trước
a, b_, c_, e = train_test_split(Xm, ym, test_size=0.3, random_state=0)   # 210 train, 90 test
print(round(LogisticRegression().fit(a, c_).score(b_, e), 4))  # hồi quy logistic
for h in [(2,), (8,), (32,), (32, 32)]:                        # bốn kiến trúc
    m = MLPClassifier(h, max_iter=3000, random_state=0).fit(a, c_)   # huấn luyện bằng Adam
    so_tham_so = sum(W.size for W in m.coefs_) + sum(v_.size for v_ in m.intercepts_)   # đếm tham số
    print(h, round(m.score(a, c_), 4), round(m.score(b_, e), 4), so_tham_so)        # train, test, số tham số
''', "0.8444\n(2,) 0.8381 0.8222 9\n(8,) 0.819 0.8444 33\n(32,) 0.8429 0.8333 129\n(32, 32) 0.9333 0.9444 1185",
    khung("loi", ["<b>Gặp ConvergenceWarning rồi bỏ qua.</b> max_iter mặc định 200 thường chưa đủ; ở đây đặt 3000."]))

c.mo_trang(5, "Ba bài tập. Tính tay trước, rồi mới mở đáp án.")
c.bai("23.1", "Một nơ-ron ba đầu vào", "Tính $z$, ReLU và sigmoid với $\\mathbf w = (0{,}3;\\ 0{,}8;\\ -0{,}5)$, $b = 0{,}4$, $\\mathbf x = (1;\\ 0;\\ 2)$.",
      "$z = -0{,}3$, ReLU 0, sigmoid $\\approx 0{,}4256$. Code ở ô ngay dưới.")
c.o('''
x3 = np.array([1.0, 0.0, 2.0])                 # đầu vào
w3 = np.array([0.3, 0.8, -0.5])                # trọng số
z3 = w3 @ x3 + 0.4                             # tổng có trọng số
print(round(float(z3), 4), float(relu(z3)), round(float(sig(z3)), 4))   # z, ReLU, sigmoid
''', "-0.3 0.0 0.4256")
c.bai("23.2", "Đếm tham số", "Mạng 784-128-64-10 có bao nhiêu tham số?",
      "100 480 + 8 256 + 650 = 109 386; lớp đầu chiếm 92%. Code ở ô ngay dưới.")
c.o('''
print(784 * 128 + 128 + 128 * 64 + 64 + 64 * 10 + 10)    # ba lớp, mỗi lớp trọng số cộng hệ số chặn
''', "109386")
c.bai("23.3", "Bỏ ReLU", "Thay ReLU trong mạng XOR bằng hàm đồng nhất, tính bốn đầu ra.",
      "$2, 1, 1, 0$: điểm $(0, 0)$ sai. Mạng gộp thành $2 - x_1 - x_2$, một hàm tuyến tính. Code ở ô ngay dưới.")
c.o('''
print((X @ W1 + b1) @ w2 + b2)          # không có ReLU ở lớp ẩn
''', "[2. 1. 1. 0.]")

c.ghi(Path(__file__).resolve().parents[2] / "notebooks/ch23_no_ron_mang_nhieu_lop.ipynb")
