"""Dựng notebooks/ch08_toi_uu_hoa.ipynb: python3 scripts/notebook/ch08.py"""
from pathlib import Path
from nblib import Chuong, khung

c = Chuong(8, "Tối ưu hóa", "ch08-toi-uu-hoa",
           "Gradient descent, learning rate, SGD, momentum và Adam: cách mô hình thật sự xuống tới đáy hàm mất mát.",
           ["Tự viết gradient descent và dự đoán hội tụ hay phân kỳ.",
            "Hiểu vì sao bát dẹt làm gradient descent chậm.",
            "So gradient descent đầy đủ, mini-batch và SGD.",
            "Cài momentum và Adam, so ba đường đi trên cùng một bát."],
           [("Gradient descent một chiều", "01-gradient-descent"), ("Chọn learning rate", "02-learning-rate"),
            ("SGD và mini-batch", "03-sgd-va-mini-batch"), ("Momentum và Adam", "04-momentum-va-adam"), ("Bài tập", "05-bai-tap")])

c.mo_trang(1, "Gradient descent trên f(x) = (x - 3)².")
c.o('''
import numpy as np                   # thư viện tính toán

def gd_1d(lr, x=0.0, n=20):          # gradient descent cho f(x) = (x - 3)^2
    xs = [x]                         # lưu vị trí sau mỗi bước
    for _ in range(n):               # n bước
        x = x - lr * 2 * (x - 3)     # công thức (8.1) với f'(x) = 2(x - 3)
        xs.append(x)                 # ghi lại vị trí mới
    return xs                        # trả về cả đường đi

xs = gd_1d(0.05)                                          # learning rate 0,05
print([round(v, 4) for v in xs[:4]], round(xs[20], 4))    # 3 bước đầu và sau 20 bước
''', "[0.0, 0.3, 0.57, 0.813] 2.6353",
    khung("doc", ["Mỗi bước khoảng cách tới đáy nhân 1 - 2η = 0,9. Sau 20 bước còn 0,9²⁰ ≈ 0,12 lần, tức x ≈ 2,64."]))

c.mo_trang(2, "Bốn learning rate, và bát dẹt.")
c.o('''
for lr in [0.05, 0.5, 0.9, 1.1]:     # chậm, một bước tới đích, dao động, phân kỳ
    xs = gd_1d(lr)                   # chạy 20 bước
    print(lr, [round(v, 4) for v in xs[:4]], round(xs[10], 4), round(xs[20], 4))  # đầu, giữa, cuối
''', "0.05 [0.0, 0.3, 0.57, 0.813] 1.954 2.6353\n0.5 [0.0, 3.0, 3.0, 3.0] 3.0 3.0\n0.9 [0.0, 5.4, 1.08, 4.536] 2.6779 2.9654\n1.1 [0.0, 6.6, -1.32, 8.184] -15.5752 -112.0128")
c.o('''
K = 50                                                   # bát dẹt x^2 + 50 y^2
g2 = lambda p: np.array([2 * p[0], 2 * K * p[1]])        # gradient
f2 = lambda p: p[0] ** 2 + K * p[1] ** 2                 # giá trị hàm
for lr in [0.019, 0.021]:                                # ngay dưới và ngay trên ngưỡng 0,02
    p = np.array([-8.0, 1.0])                            # xuất phát, f = 114
    for _ in range(100):                                 # 100 bước
        p = p - lr * g2(p)                               # gradient descent
    print(lr, f2(p))                                     # loss sau 100 bước
''', "0.019 0.027618172398899857\n0.021 9495263823.035332",
    khung("vi-sao", ["Hướng y cong 100 nên η phải dưới 2/100 = 0,02. Vượt một chút là phân kỳ, dù hướng x vẫn ổn."],
          nhan="VÌ SAO LẠI LÀ 0,02?"))

c.mo_trang(3, "Gradient descent đầy đủ, mini-batch và SGD trên 10 sinh viên.")
c.o('''
gio = np.array([1, 2, 3, 4, 5, 2, 6, 3, 7, 4.0])                # Bảng 4.1
diem = np.array([2, 4, 5, 7, 6, 3.5, 8.5, 4, 9, 6.5])            # điểm thi
mse = lambda w, b: float(np.mean((diem - (w * gio + b)) ** 2))   # loss trên cả 10 bạn

def train(bs, lr, ep=100, seed=0):               # huấn luyện với lô kích thước bs
    rng = np.random.default_rng(seed)            # để xáo trộn lặp lại được
    w = b = 0.0                                  # khởi tạo
    L = [mse(w, b)]                              # loss sau mỗi epoch
    for _ in range(ep):                          # mỗi epoch
        idx = rng.permutation(10)                # xáo trộn thứ tự 10 bạn
        for s in range(0, 10, bs):               # chia thành các lô
            j = idx[s:s + bs]                    # chỉ số các bạn trong lô
            e = diem[j] - (w * gio[j] + b)       # phần dư trên lô
            w -= lr * (-2 * np.mean(gio[j] * e)) # bước theo gradient của lô
            b -= lr * (-2 * np.mean(e))          # tương tự cho b
        L.append(mse(w, b))                      # đo trên cả 10 bạn
    return w, b, L                               # tham số cuối và đường loss

for bs, lr in [(10, 0.03), (5, 0.03), (1, 0.01)]:   # GD đầy đủ, mini-batch, SGD
    w, b, L = train(bs, lr)                          # 100 epoch
    print(bs, round(w, 4), round(b, 4), round(L[100], 4), round(min(L), 4))  # cuối và tốt nhất
''', "10 1.2176 0.9827 0.4103 0.4103\n5 1.1274 1.2165 0.415 0.3911\n1 1.0894 1.3378 0.4298 0.3882",
    khung("doc", ["Đáy thật là 0,388. GD đầy đủ mượt nhưng chậm (0,410). SGD có lúc chạm 0,3882 nhưng cuối lại nảy lên 0,430: với learning rate cố định, SGD không nằm yên ở đáy."]))

c.mo_trang(4, "Momentum và Adam trên bát dẹt.")
c.o('''
def duong(kieu, lr, n, beta=0.9):                     # chạy một thuật toán n bước
    p = np.array([-8.0, 1.0])                         # xuất phát
    v, m, s = np.zeros(2), np.zeros(2), np.zeros(2)   # vận tốc, trung bình gradient, trung bình bình phương
    for t in range(1, n + 1):                         # đếm bước từ 1 cho phép hiệu chỉnh của Adam
        gr = g2(p)                                    # gradient tại chỗ đang đứng
        if kieu == "gd":                              # gradient descent thường
            p = p - lr * gr                           # công thức (8.1)
        elif kieu == "momentum":                      # momentum
            v = beta * v + gr                         # cộng dồn vận tốc (8.4)
            p = p - lr * v                            # bước theo vận tốc
        else:                                         # Adam (8.5)
            m = 0.9 * m + 0.1 * gr                    # trung bình động của gradient
            s = 0.999 * s + 0.001 * gr ** 2           # trung bình động của bình phương
            p = p - lr * (m / (1 - 0.9 ** t)) / (np.sqrt(s / (1 - 0.999 ** t)) + 1e-8)  # bước đã chuẩn hóa
    return p                                          # vị trí cuối

for kieu, lr in [("gd", 0.019), ("momentum", 0.01), ("adam", 0.3)]:            # mỗi thuật toán một lr tốt
    print(kieu, [round(float(f2(duong(kieu, lr, n))), 5) for n in (25, 50, 100)])  # loss sau 25, 50, 100 bước
''', "gd [9.48199, 1.33082, 0.02762]\nmomentum [6.97099, 0.47314, 0.00124]\nadam [2.11279, 0.44973, 0.00051]",
    khung("thu", ["<b>1.</b> Chạy momentum với η = 0,019 (bằng GD). Nó còn hội tụ không?",
                  "<b>2.</b> Chạy Adam với η = 0,001, giá trị mặc định của thư viện. Vì sao ở bài này nó chậm?"]))

c.mo_trang(5, "Ba bài tập. Đoán bằng công thức trước, rồi mới mở đáp án.")
c.bai("8.1", "Đếm số bước", "Với $\\eta = 0{,}25$, xuất phát $x_0 = 0$, cần bao nhiêu bước để $|x - 3| < 0{,}01$?",
      "Hệ số co 0,5. Cần $3 \\times 0{,}5^k < 0{,}01$: $k = 9$. Code ở ô ngay dưới.")
c.o('''
x, k = 0.0, 0                          # vị trí và số bước
while abs(x - 3) >= 0.01:              # chưa đủ gần đáy
    x = x - 0.25 * 2 * (x - 3)         # một bước với η = 0,25
    k += 1                             # đếm bước
print(k, x)                            # số bước và vị trí cuối
''', "9 2.994140625")
c.bai("8.2", "Tách bát dẹt thành hai hướng", "Với $\\eta = 0{,}019$ trên $x^2 + 50y^2$, tính hệ số co theo từng hướng và dự đoán $(x, y)$ sau 100 bước.",
      "Hệ số $0{,}962$ theo $x$ và $-0{,}9$ theo $y$. Sau 100 bước $x \\approx -0{,}166$, $y \\approx 2{,}66 \\times 10^{-5}$: hướng $x$ là nút thắt. Code ở ô ngay dưới.")
c.o('''
p = np.array([-8.0, 1.0])                                  # xuất phát
for _ in range(100):                                       # 100 bước
    p = p - 0.019 * np.array([2 * p[0], 100 * p[1]])       # gradient descent
print(p, 8 * 0.962 ** 100, 0.9 ** 100)                     # so với dự đoán từ hệ số co
''', "[-1.66187055e-01  2.65613989e-05] 0.16618705462070174 2.6561398887587544e-05")
c.bai("8.3", "Momentum không có quán tính", "Gọi `duong(\"momentum\", 0.019, 100, beta=0.0)` và so với `duong(\"gd\", 0.019, 100)`.",
      "Với $\\beta = 0$ vận tốc chỉ là gradient hiện tại, nên momentum thu về gradient descent thường. Hai kết quả bằng nhau. Code ở ô ngay dưới.")
c.o('''
print(round(float(f2(duong("momentum", 0.019, 100, beta=0.0))), 5))   # momentum với beta = 0
print(round(float(f2(duong("gd", 0.019, 100))), 5))                   # gradient descent thường
''', "0.02762\n0.02762")

c.ghi(Path(__file__).resolve().parents[2] / "notebooks/ch08_toi_uu_hoa.ipynb")
