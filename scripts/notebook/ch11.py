"""Dựng notebooks/ch11_hoi_quy_logistic.ipynb: python3 scripts/notebook/ch11.py"""
from pathlib import Path
from nblib import Chuong, khung

c = Chuong(11, "Hồi quy logistic", "ch11-hoi-quy-logistic",
           "Mô hình phân loại đầu tiên: sigmoid, cross-entropy, gradient (p - y)x tự cài bằng tay, rồi softmax cho nhiều lớp.",
           ["Hiểu vì sao phân loại cần sigmoid và cross-entropy.",
            "Tự dẫn và kiểm gradient, tự cài hồi quy logistic.",
            "Đọc xác suất, ranh giới quyết định, tỷ lệ cược.",
            "Dùng softmax và LogisticRegression cho nhiều lớp."],
           [("Bài toán phân loại và hàm sigmoid", "01-bai-toan-phan-loai"), ("Hàm mất mát cross-entropy", "02-cross-entropy"),
            ("Gradient và tự cài", "03-gradient-va-tu-cai"), ("scikit-learn và nhiều lớp", "04-scikit-learn-va-softmax"), ("Bài tập", "05-bai-tap")])

c.mo_trang(1, "Dữ liệu đỗ trượt và hàm sigmoid. Code của trang này nằm chung với trang 2.")
c.mo_trang(2, "Cross-entropy và giá trị lúc bắt đầu.")
c.o('''
import numpy as np                                    # thư viện tính toán
gio = np.array([1, 2, 2, 3, 3, 4, 4, 5, 6, 7.0])      # Bảng 11.1: giờ học
do = np.array([0, 0, 1, 0, 0, 1, 0, 1, 1, 1.0])       # 1 là đỗ, 0 là trượt
sig = lambda z: 1 / (1 + np.exp(-z))                  # hàm sigmoid

def bce(w, b):                                        # cross-entropy nhị phân (11.2)
    p = sig(w * gio + b)                              # xác suất đỗ đoán ra cho từng bạn
    return float(-np.mean(do * np.log(p) + (1 - do) * np.log(1 - p)))   # trung bình mức phạt

print(round(bce(0, 0), 4), np.log(2))                 # lúc bắt đầu: đoán 50-50 cho mọi bạn
''', "0.6931 0.6931471805599453",
    khung("doc", ["Loss đứng yên ở 0,693 nghĩa là mô hình vẫn đang đoán 50-50, chưa học được gì."]))

c.mo_trang(3, "Kiểm gradient bằng sai phân, rồi tự cài.")
c.o('''
def grad(w, b):                                                     # gradient (11.3)
    p = sig(w * gio + b)                                            # xác suất đoán ra
    return float(np.mean((p - do) * gio)), float(np.mean(p - do))   # (đoán trừ thật) nhân đặc trưng

h = 1e-5                                                            # bước sai phân
print(grad(0.3, -1.0))                                              # công thức
print(((bce(0.3 + h, -1) - bce(0.3 - h, -1)) / (2 * h), (bce(0.3, -1 + h) - bce(0.3, -1 - h)) / (2 * h)))  # sai phân
''', "(-0.23101772770510198, 0.024684044519859026)\n(-0.23101772779754445, 0.024684044519496236)")
c.o('''
w = b = 0.0                                           # khởi tạo
for buoc in range(5001):                              # 5000 bước
    if buoc in (0, 1, 100, 1000, 5000):               # in vài bước
        print(f"Bước {buoc:4d} | w = {w:.4f} | b = {b:.4f} | loss = {bce(w, b):.4f}")  # trạng thái
    gw, gb = grad(w, b)                               # gradient
    w -= 0.1 * gw                                     # learning rate 0,1
    b -= 0.1 * gb                                     # cùng bước cho b
print(round(-b / w, 4))                               # ranh giới quyết định
''', "Bước    0 | w = 0.0000 | b = 0.0000 | loss = 0.6931\nBước    1 | w = 0.0550 | b = 0.0000 | loss = 0.6693\nBước  100 | w = 0.3426 | b = -0.9249 | loss = 0.5633\nBước 1000 | w = 0.9144 | b = -3.2546 | loss = 0.4696\nBước 5000 | w = 1.0204 | b = -3.6696 | loss = 0.4680\n3.5962",
    khung("thu", ["<b>1.</b> Đổi learning rate thành 1.0. Loss có xuống nhanh hơn không?",
                  "<b>2.</b> Đổi nhãn bạn học 4 giờ đang trượt thành đỗ, chạy lại. Ranh giới dịch về đâu?"]))

c.mo_trang(4, "scikit-learn, softmax và bộ hoa iris.")
c.o('''
from sklearn.linear_model import LogisticRegression     # mô hình có sẵn
X1 = gio.reshape(-1, 1)                                 # bảng một cột
m = LogisticRegression(C=np.inf).fit(X1, do)            # tắt regularization để so với bản tự cài
print(m.coef_.round(4), m.intercept_.round(4))          # w và b
print(m.predict_proba(np.array([[2.0], [3.5], [5.0]]))[:, 1].round(4))   # xác suất đỗ
print(m.predict(X1), m.score(X1, do))                   # nhãn đoán ra, độ chính xác
''', "[[1.0216]] [-3.6745]\n[0.1637 0.4753 0.8075]\n[0. 0. 0. 0. 0. 1. 1. 1. 1. 1.] 0.8")
c.o('''
z = np.array([2.0, 1.0, 0.1])                 # điểm số ba lớp
e = np.exp(z)                                 # lấy mũ
print(e.round(4), round(e.sum(), 4), (e / e.sum()).round(4))   # softmax (11.4)
big = np.array([1000.0, 999.0])               # điểm số rất lớn
with np.errstate(all="ignore"):               # tắt cảnh báo tràn số để in gọn
    print(np.exp(big) / np.exp(big).sum())    # tràn: ra nan
b2 = big - big.max()                          # trừ số lớn nhất trước
print((np.exp(b2) / np.exp(b2).sum()).round(4))   # không tràn
''', "[7.3891 2.7183 1.1052] 11.2125 [0.659  0.2424 0.0986]\n[nan nan]\n[0.7311 0.2689]")
c.o('''
from sklearn.datasets import load_iris                       # 150 bông hoa, 3 loài
from sklearn.model_selection import train_test_split         # chia dữ liệu
X, y = load_iris(return_X_y=True)                            # 4 đặc trưng
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=0, stratify=y)   # giữ tỷ lệ 3 loài
m3 = LogisticRegression(max_iter=1000).fit(Xtr, ytr)         # softmax tự động khi có 3 lớp
print(m3.coef_.shape, round(m3.score(Xte, yte), 4))          # 3 x 4 trọng số; độ chính xác test
print(m3.predict_proba(Xte[:3]).round(4), m3.predict(Xte[:3]), yte[:3])   # 3 bông đầu
''', "(3, 4) 1.0\n[[0.000e+00 3.480e-02 9.651e-01]\n [5.000e-04 2.333e-01 7.662e-01]\n [9.660e-01 3.400e-02 0.000e+00]] [2 2 0] [2 2 0]")

c.mo_trang(5, "Ba bài tập. Tính tay trước, rồi mới mở đáp án.")
c.bai("11.1", "Bước đầu tiên, tính tay", "Từ $w = b = 0$, tính gradient và $w$, $b$ sau một bước với learning rate 0,1.",
      "Gradient $(-0{,}55;\\ 0)$: năm đỗ năm trượt nên theo $b$ triệt tiêu. Sau bước: $w = 0{,}055$, $b = 0$. Code ở ô ngay dưới.")
c.o('''
print(grad(0.0, 0.0))          # gradient tại điểm xuất phát
''', "(-0.55, 0.0)")
c.bai("11.2", "Hạ ngưỡng", "Đoán đỗ khi $p > 0{,}3$ thay vì 0,5. Bạn nào đổi kết quả, độ chính xác thành bao nhiêu?",
      "Hai bạn học 3 giờ (xác suất 0,352) chuyển sang đoán đỗ, nhưng cả hai thật ra trượt: độ chính xác giảm từ 0,8 xuống 0,6. Code ở ô ngay dưới.")
c.o('''
p = sig(1.0216 * gio - 3.6745)                              # xác suất của mô hình trang 4
print((p > 0.3).astype(int), float(((p > 0.3) == do).mean()))   # nhãn với ngưỡng 0,3 và độ chính xác
''', "[0 0 0 1 1 1 1 1 1 1] 0.6")
c.bai("11.3", "Softmax tính tay", "Tính softmax của $(1, 2, 3)$, của $(101, 102, 103)$ và của $(2, 4, 6)$.",
      "$(0{,}090;\\ 0{,}245;\\ 0{,}665)$. Cộng cùng một số: không đổi. Nhân 2: nhọn hơn, $(0{,}016;\\ 0{,}117;\\ 0{,}867)$. Code ở ô ngay dưới.")
c.o('''
sm = lambda v: np.exp(v - v.max()) / np.exp(v - v.max()).sum()   # softmax ổn định số
z = np.array([1.0, 2.0, 3.0])                                    # điểm số
print(sm(z).round(3), sm(z + 100).round(3), sm(2 * z).round(3))  # gốc, cộng 100, nhân 2
''', "[0.09  0.245 0.665] [0.09  0.245 0.665] [0.016 0.117 0.867]")

c.ghi(Path(__file__).resolve().parents[2] / "notebooks/ch11_hoi_quy_logistic.ipynb")
