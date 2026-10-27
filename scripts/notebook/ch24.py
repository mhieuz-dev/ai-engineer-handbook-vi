"""Dựng notebooks/ch24_backpropagation.ipynb: python3 scripts/notebook/ch24.py"""
from pathlib import Path
from nblib import Chuong, khung

c = Chuong(24, "Backpropagation tự cài", "ch24-backpropagation",
           "Lan truyền ngược bằng tay trên một nơ-ron, công thức cho cả một lớp, rồi tự cài mạng hai lớp bằng NumPy, kiểm gradient và huấn luyện trên hai vầng trăng.",
           ["Vẽ đồ thị tính toán và lan truyền ngược bằng tay.",
            "Dẫn dW = Xᵀ·dZ và đạo hàm ReLU dạng mặt nạ.",
            "Tự cài mạng hai lớp và kiểm gradient bằng sai phân.",
            "Huấn luyện mạng tự viết tới 93% trên hai vầng trăng."],
           [("Đồ thị tính toán", "01-do-thi-tinh-toan"), ("Lan truyền ngược qua một lớp", "02-lan-truyen-qua-mot-lop"),
            ("Tự cài mạng hai lớp", "03-tu-cai-mang-hai-lop"), ("Huấn luyện mạng tự cài", "04-huan-luyen"), ("Bài tập", "05-bai-tap")])

c.mo_trang(1, "Một nơ-ron: lượt xuôi, lượt ngược, gradient check.")
c.o('''
import numpy as np                                  # tính toán
x, w, b, y = 2.0, 0.5, 0.1, 1.0                     # đầu vào, tham số, nhãn
z = w * x + b                                       # lượt xuôi
a = 1 / (1 + np.exp(-z))                            # sigmoid
L = (a - y) ** 2                                    # loss bình phương
dL_da = 2 * (a - y)                                 # lượt ngược bắt đầu từ loss
dL_dz = dL_da * a * (1 - a)                         # qua sigmoid
dL_dw, dL_db = dL_dz * x, dL_dz                     # qua phép nhân và phép cộng
print(round(z, 4), round(a, 4), round(L, 4), round(dL_dz, 4), round(dL_dw, 4), round(dL_db, 4))   # giá trị và gradient
h = 1e-5                                            # bước sai phân
f = lambda w_: (1 / (1 + np.exp(-(w_ * x + b))) - y) ** 2     # loss theo w
print(round((f(w + h) - f(w - h)) / (2 * h), 4))    # gradient check
''', "1.1 0.7503 0.0624 -0.0936 -0.1872 -0.0936\n-0.1872")

c.mo_trang(2, "Đạo hàm của ReLU là một mặt nạ.")
c.o('''
Z = np.array([[1.5, -0.3], [-2.0, 0.7]])     # đầu vào của ReLU
dA = np.array([[0.2, 0.4], [0.1, -0.5]])     # gradient từ lớp sau
print((Z > 0).astype(int))                   # mặt nạ 0 và 1
print(dA * (Z > 0))                          # công thức (24.2)
''', "[[1 0]\n [0 1]]\n[[ 0.2  0. ]\n [ 0.  -0.5]]")

c.mo_trang(3, "Mạng 2-32-1 bằng NumPy và gradient check.")
c.o('''
from sklearn.datasets import make_moons                     # dữ liệu
from sklearn.model_selection import train_test_split        # chia
Xm, ym = make_moons(300, noise=0.3, random_state=0)         # hai vầng trăng
Xtr, Xte, ytr, yte = train_test_split(Xm, ym, test_size=0.3, random_state=0)   # 210 train, 90 test
r = np.random.default_rng(0)                                # seed
P = [r.normal(0, 1.0, (2, 32)),                             # W1, khởi tạo He với d = 2
     np.zeros(32),                                          # b1
     r.normal(0, np.sqrt(2 / 32), (32, 1)),                 # W2, khởi tạo He với d = 32
     np.zeros(1)]                                           # b2
print([p.shape for p in P], sum(p.size for p in P))         # shape và số tham số

def truyen_xuoi(P, X):                                      # lượt xuôi
    W1, b1, W2, b2 = P                                      # mở gói tham số
    Z1 = X @ W1 + b1                                        # (n, 32)
    A1 = np.maximum(0, Z1)                                  # ReLU
    p = 1 / (1 + np.exp(-(A1 @ W2 + b2)))                   # sigmoid ở lớp ra
    return Z1, A1, p.ravel()                                # giữ Z1, A1 cho lượt ngược

def mat_mat(P, X, y):                                       # cross-entropy
    p = np.clip(truyen_xuoi(P, X)[2], 1e-12, 1 - 1e-12)     # tránh log(0)
    return float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))   # trung bình

def truyen_nguoc(P, X, y):                                  # lượt ngược
    W1, b1, W2, b2 = P                                      # mở gói
    Z1, A1, p = truyen_xuoi(P, X)                           # cần giá trị lượt xuôi
    dZ2 = (p - y)[:, None] / len(y)                         # (24.3)
    dW2, db2 = A1.T @ dZ2, dZ2.sum(0)                       # (24.1) lớp ra
    dA1 = dZ2 @ W2.T                                        # gửi về lớp ẩn
    dZ1 = dA1 * (Z1 > 0)                                    # (24.2) qua ReLU
    dW1, db1 = X.T @ dZ1, dZ1.sum(0)                        # (24.1) lớp ẩn
    return [dW1, db1, dW2, db2]                             # cùng thứ tự với P
''', "[(2, 32), (32,), (32, 1), (1,)] 129")
c.o('''
G = truyen_nguoc(P, Xtr, ytr)                            # gradient bằng công thức
for k, i in [(0, (0, 0)), (2, (5, 0)), (1, (3,))]:       # ba tham số bất kỳ
    cu = P[k][i]                                         # giữ giá trị cũ
    P[k][i] = cu + h; lp = mat_mat(P, Xtr, ytr)          # nhích lên
    P[k][i] = cu - h; lm = mat_mat(P, Xtr, ytr)          # nhích xuống
    P[k][i] = cu                                         # trả lại
    print(k, i, round(float(G[k][i]), 8), round((lp - lm) / (2 * h), 8))   # công thức và sai phân
''', "0 (0, 0) -0.01272586 -0.01272586\n2 (5, 0) -0.05968156 -0.05968156\n1 (3,) 0.09515478 0.09515478",
    khung("vi-sao", ["Gradient sai không làm chương trình báo lỗi: loss vẫn có thể giảm, chỉ chậm hoặc dừng sai chỗ. Kiểm trước khi huấn luyện."],
          nhan="VÌ SAO LẠI KIỂM TRƯỚC KHI HUẤN LUYỆN?"))

c.mo_trang(4, "3000 bước gradient descent.")
c.o('''
dung = lambda X, y: float(np.mean((truyen_xuoi(P, X)[2] > 0.5) == y))   # độ chính xác
for buoc in range(3001):                                                # 3000 bước
    if buoc in (0, 100, 1000, 3000):                                    # in vài mốc
        print(buoc, round(mat_mat(P, Xtr, ytr), 4), round(dung(Xtr, ytr), 4), round(dung(Xte, yte), 4))   # loss, train, test
    G = truyen_nguoc(P, Xtr, ytr)                                       # gradient
    P = [p - 0.5 * g for p, g in zip(P, G)]                             # cập nhật, learning rate 0,5
''', "0 1.1723 0.2095 0.3111\n100 0.312 0.8476 0.8667\n1000 0.1673 0.9381 0.9444\n3000 0.1474 0.9429 0.9333",
    khung("thu", ["<b>1.</b> Đổi learning rate thành 5. Loss có thành nan không?",
                  "<b>2.</b> Đổi 32 nơ-ron thành 4. Test còn được bao nhiêu?"]))

c.mo_trang(5, "Ba bài tập. Tính tay trước, rồi mới mở đáp án.")
c.bai("24.1", "Nhãn đổi thành 0", "Với nhãn $y = 0$, tính $\\partial L/\\partial a$, $\\partial L/\\partial z$, $\\partial L/\\partial w$.",
      "$1{,}5005$; $0{,}2812$; $0{,}5623$. Gradient đổi dấu và lớn gấp ba vì đầu ra 0,75 giờ quá cao. Code ở ô ngay dưới.")
c.o('''
y0 = 0.0                                     # nhãn mới
dz0 = 2 * (a - y0) * a * (1 - a)             # qua loss và sigmoid
print(round(2 * (a - y0), 4), round(dz0, 4), round(dz0 * x, 4))   # dL/da, dL/dz, dL/dw
''', "1.5005 0.2812 0.5623")
c.bai("24.2", "Shape của mọi gradient", "Với mạng 784-128-10 và lô 64 ảnh, viết shape của mọi đại lượng ở lượt xuôi và lượt ngược.",
      "$dW_1$ là (784, 128), $dW_2$ là (128, 10), $Z_1$ và $dA_1$ là (64, 128), $dZ_2$ là (64, 10). Gradient của tham số không phụ thuộc cỡ lô.")
c.bai("24.3", "Khởi tạo đối xứng", "Khởi tạo mọi trọng số bằng 0,1, huấn luyện 3000 bước, đếm số giá trị khác nhau trong mỗi hàng của $W_1$.",
      "Mỗi hàng chỉ một giá trị: 32 nơ-ron vẫn giống hệt nhau, test chỉ 83%. Code ở ô ngay dưới.")
c.o('''
Pd = [np.full((2, 32), 0.1), np.zeros(32), np.full((32, 1), 0.1), np.zeros(1)]   # mọi trọng số bằng nhau
for _ in range(3000):                                                           # huấn luyện như trang 4
    Pd = [p - 0.5 * g for p, g in zip(Pd, truyen_nguoc(Pd, Xtr, ytr))]          # gradient descent
print(np.unique(Pd[0][0].round(6)).size, np.unique(Pd[0][1].round(6)).size, round(float(np.mean((truyen_xuoi(Pd, Xte)[2] > 0.5) == yte)), 4))   # số giá trị khác nhau, test
''', "1 1 0.8333")

c.ghi(Path(__file__).resolve().parents[2] / "notebooks/ch24_backpropagation.ipynb")
