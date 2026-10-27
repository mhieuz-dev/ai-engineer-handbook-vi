"""Dựng notebooks/ch06_giai_tich.ipynb: python3 scripts/notebook/ch06.py"""
from pathlib import Path
from nblib import Chuong, khung

c = Chuong(6, "Giải tích cho ML", "ch06-giai-tich",
           "Đạo hàm, quy tắc chuỗi, gradient và cách tự kiểm tra một công thức gradient: đủ giải tích để hiểu gradient descent và backpropagation.",
           ["Tính đạo hàm bằng sai phân và hiểu nó là độ dốc.",
            "Dùng quy tắc chuỗi, tính đạo hàm của sigmoid.",
            "Tính gradient của MSE theo w và b, khớp các con số của Chương 10.",
            "Bắt lỗi công thức gradient bằng gradient check."],
           [("Đạo hàm là độ dốc", "01-dao-ham"), ("Quy tắc đạo hàm và quy tắc chuỗi", "02-quy-tac-chuoi"),
            ("Đạo hàm riêng và gradient", "03-dao-ham-rieng-va-gradient"), ("Kiểm tra gradient bằng sai phân", "04-kiem-tra-gradient"), ("Bài tập", "05-bai-tap")])

c.mo_trang(1, "Từ cát tuyến tới tiếp tuyến, sai phân một phía và trung tâm.")
c.o('''
import numpy as np                         # thư viện tính toán
f = lambda x: x ** 2                       # hàm f(x) = x bình phương
for h in [0.1, 0.01, 0.001]:               # thu ngắn dần đoạn h
    print(h, (f(3 + h) - f(3)) / h)        # sai phân một phía: tiến về 6
for h in [0.1, 0.01, 0.001]:               # cùng các h
    print(h, (f(3 + h) - f(3 - h)) / (2 * h))   # sai phân trung tâm: gần 6 ngay từ đầu
''', "0.1 6.100000000000012\n0.01 6.009999999999849\n0.001 6.000999999999479\n0.1 6.000000000000005\n0.01 5.999999999999872\n0.001 5.999999999999339",
    khung("doc", ["Một phía: phần thừa đúng bằng h (6,1; 6,01; 6,001). Trung tâm: khử hết phần thừa, chỉ còn sai số dấu phẩy động.",
                  "h = 0,001 lại kém chính xác hơn h = 0,1 ở sai phân trung tâm: h quá nhỏ thì trừ hai số gần bằng nhau, mất chữ số có nghĩa."]))

c.mo_trang(2, "Quy tắc chuỗi và hàm sigmoid.")
c.o('''
g = lambda x: (2 * x + 1) ** 2              # hàm lồng nhau
h = 1e-5                                    # bước sai phân
print((g(1 + h) - g(1 - h)) / (2 * h))      # quy tắc chuỗi cho 4(2x + 1) = 12 tại x = 1
sig = lambda z: 1 / (1 + np.exp(-z))        # hàm sigmoid
print(sig(0.0), sig(0.0) * (1 - sig(0.0)))  # giá trị và đạo hàm theo công thức (6.4)
print((sig(h) - sig(-h)) / (2 * h))         # kiểm tra bằng sai phân
print(round(sig(2.0), 4), round(sig(2.0) * (1 - sig(2.0)), 4))  # xa 0 thì đạo hàm nhỏ đi
''', "12.000000000078613\n0.5 0.25\n0.2499999999933111\n0.8808 0.105",
    khung("loi", ["<b>Quên nhân đạo hàm lớp trong.</b> (2x + 1)² có đạo hàm 2(2x + 1) × 2, không phải 2(2x + 1)."]))

c.mo_trang(3, "Gradient của MSE theo w và b.")
c.o('''
x = np.array([1, 2, 3, 4.0])                # giờ học của A, B, C, D
y = np.array([2, 4, 5, 7.0])                # điểm thi

def grad(w, b):                             # gradient của MSE theo (w, b)
    e = y - (w * x + b)                     # phần dư
    return float(-2 * np.mean(x * e)), float(-2 * np.mean(e))   # công thức (6.5)

print(grad(0, 0))          # điểm xuất phát của Chương 10
print(grad(1.6, 0.5))      # tại đáy: gần 0
''', "(-26.5, -9.0)\n(1.9984014443252818e-15, 6.661338147750939e-16)",
    khung("truc-giac", ["Gradient chỉ hướng dốc lên. Tại (0, 0) cả hai thành phần âm, nên đi ngược hướng là tăng cả w lẫn b: đường y = 0 cần dốc hơn và nhấc lên."]))

c.mo_trang(4, "So công thức với sai phân, bắt một lỗi quên hệ số 2.")
c.o('''
def L(w, b):                                          # MSE của bốn bạn
    return float(np.mean((y - (w * x + b)) ** 2))     # float để in gọn

def grad_so(w, b, h=1e-5):                            # gradient bằng sai phân trung tâm
    dw = (L(w + h, b) - L(w - h, b)) / (2 * h)        # nhích riêng w
    db = (L(w, b + h) - L(w, b - h)) / (2 * h)        # nhích riêng b
    return dw, db                                     # trả về cả hai

def grad_sai(w, b):                                   # công thức viết nhầm
    e = y - (w * x + b)                               # phần dư
    return float(-np.mean(x * e)), float(-2 * np.mean(e))   # QUÊN số 2 ở thành phần đầu

def lech(a, b):                                       # sai lệch tương đối
    return abs(a - b) / max(abs(a), abs(b))           # chia cho số lớn hơn

print(grad_so(0, 0))                                  # khớp (-26.5, -9.0)
so = grad_so(0.3, 0.2)                                # kiểm tra ở một điểm bất kỳ
print([round(lech(a, b), 8) for a, b in zip(grad(0.3, 0.2), so)])      # công thức đúng
print([round(lech(a, b), 8) for a, b in zip(grad_sai(0.3, 0.2), so)])  # công thức sai
''', "(-26.499999999884945, -8.99999999965928)\n[0.0, 0.0]\n[0.5, 0.0]",
    khung("thu", ["<b>1.</b> Đổi dấu trừ trong <code>grad_sai</code> thành dấu cộng ở thành phần b. Sai lệch thành bao nhiêu?",
                  "<b>2.</b> Chạy kiểm tra tại (1.6, 0.5). Vì sao kết quả ở đáy khó tin hơn?"]))

c.mo_trang(5, "Ba bài tập. Tính tay trước, rồi mới mở đáp án.")
c.bai("6.1", "Chỗ mặt đất bằng phẳng", "Cho $k(x) = x^3 - 3x$. Tính $k'(2)$, tìm mọi $x$ có $k'(x) = 0$.",
      "$k'(x) = 3x^2 - 3$, $k'(2) = 9$. $k'(x) = 0$ tại $x = \\pm 1$: một đỉnh đồi và một thung lũng nhỏ, không phải đáy thấp nhất. Code kiểm tra ở ô ngay dưới.")
c.o('''
k = lambda x: x ** 3 - 3 * x              # hàm bậc ba
print((k(2 + h) - k(2 - h)) / (2 * h))    # phải gần 9
''', "9.000000000147779")
c.bai("6.2", "Chuỗi qua sigmoid", "Với $p = \\sigma(2w)$ và loss $(p - 1)^2$, tính đạo hàm theo $w$ tại $w = 0$.",
      "Ba lớp: $2(p - 1) = -1$, $\\sigma(1 - \\sigma) = 0{,}25$, $dz/dw = 2$. Nhân lại $-0{,}5$. Code kiểm tra ở ô ngay dưới.")
c.o('''
q = lambda w: (sig(w * 2) - 1) ** 2       # loss theo w, với x = 2 và nhãn 1
print((q(h) - q(-h)) / (2 * h))           # phải gần -0.5
''', "-0.4999999999810711")
c.bai("6.3", "Bước hai của Chương 10", "Từ $w = 1{,}325$, $b = 0{,}45$, tính gradient và $w$, $b$ sau một bước với $\\eta = 0{,}05$.",
      "$\\sum x_i e_i = 8{,}75$, $\\sum e_i = 2{,}95$. Gradient $(-4{,}375;\\ -1{,}475)$. Sau bước: $w = 1{,}54375$, $b = 0{,}52375$. Code kiểm tra ở ô ngay dưới.")
c.o('''
gw, gb = grad(1.325, 0.45)                 # gradient tại sau bước 1
print(gw, gb)                              # hai thành phần
print(1.325 - 0.05 * gw, 0.45 - 0.05 * gb) # bước cập nhật thứ hai
''', "-4.375 -1.475\n1.54375 0.52375")

c.ghi(Path(__file__).resolve().parents[2] / "notebooks/ch06_giai_tich.ipynb")
