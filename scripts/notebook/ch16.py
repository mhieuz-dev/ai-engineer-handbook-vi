"""Dựng notebooks/ch16_svm_kernel.ipynb: python3 scripts/notebook/ch16.py"""
from pathlib import Path
from nblib import Chuong, khung

c = Chuong(16, "SVM và kernel", "ch16-svm-kernel",
           "Lề cực đại, vector hỗ trợ, lề mềm với C, kernel trick tính tay được, và SVM RBF trên dữ liệu thật.",
           ["Tính tay độ rộng lề và nhận ra vector hỗ trợ.",
            "Đọc C như núm vặn regularization.",
            "Kiểm kernel trick bằng tay và chỉnh gamma của RBF.",
            "Chuẩn hóa, chọn C và gamma bằng GridSearchCV."],
           [("Lề cực đại", "01-le-cuc-dai"), ("Lề mềm và tham số C", "02-le-mem-va-c"),
            ("Kernel trick", "03-kernel-trick"), ("SVM trên dữ liệu thật", "04-svm-thuc-te"), ("Bài tập", "05-bai-tap")])

c.mo_trang(1, "SVM lề cứng trên tám điểm.")
c.o('''
import numpy as np                                     # tính toán
from sklearn.svm import SVC                            # SVM
X = np.array([[1, 1], [2, 1], [1, 2], [2, 3], [4, 4], [5, 4], [4, 5], [5, 6]], dtype=float)   # Bảng 16.1
y = np.array([0, 0, 0, 0, 1, 1, 1, 1])                 # nhãn
m = SVC(kernel="linear", C=1e6).fit(X, y)              # C rất lớn: lề cứng
w, b = m.coef_[0], m.intercept_[0]                     # trọng số, hệ số chặn
print(w.round(4), round(b, 4), m.support_)             # và chỉ số vector hỗ trợ
print(round(2 / np.linalg.norm(w), 4))                 # độ rộng lề (16.1)
print(m.decision_function(X).round(4))                 # w·x + b từng điểm
''', "[0.8 0.4] -3.8 [3 4]\n2.2361\n[-2.6 -1.8 -2.2 -1.   1.   1.8  1.4  2.6]",
    khung("doc", ["Hai điểm cho đúng -1 và +1: (2; 3) và (4; 4), hai vector hỗ trợ. Lề rộng √5, đúng khoảng cách giữa hai điểm đó."]))

c.mo_trang(2, "Một điểm lạc và ba mức C.")
c.o('''
X2 = np.vstack([X, [[3.2, 3.6]]])                    # thêm điểm lạc nhãn 0 sát nhóm xanh
y2 = np.append(y, 0)                                 # nhãn của điểm lạc
for C in [1000, 1, 0.1]:                             # ba mức phạt
    mc = SVC(kernel="linear", C=C).fit(X2, y2)       # lề mềm
    wc = mc.coef_[0]                                 # trọng số
    print(C, wc.round(4), round(mc.intercept_[0], 4), round(2 / np.linalg.norm(wc), 4), round(mc.score(X2, y2), 4))   # w, b, lề, độ chính xác
''', "1000 [2. 1.] -11.0 0.8944 1.0\n1 [0.8 0.4] -4.0 2.2361 0.8889\n0.1 [0.3533 0.3133] -2.02 4.235 0.8889",
    khung("truc-giac", ["C lớn: tin từng điểm, lề co lại còn 0,89 để chia đúng điểm lạc. C nhỏ: tin vào lề rộng, chấp nhận hy sinh điểm lạc."]))

c.mo_trang(3, "Thêm cột x², kernel tính tay, kernel RBF.")
c.o('''
x = np.array([-3, -2, -1, 0, 1, 2, 3.0])                                       # bảy điểm trên trục số
y7 = (np.abs(x) <= 1.5).astype(int)                                            # lớp 1 ở giữa
print(SVC(kernel="linear", C=1e6).fit(x[:, None], y7).score(x[:, None], y7))   # chỉ có x: không chia được
P = np.c_[x, x ** 2]                                                            # thêm cột x²
m2 = SVC(kernel="linear", C=1e6).fit(P, y7)                                    # tuyến tính trên (x, x²)
print(m2.score(P, y7), m2.coef_.round(4), m2.intercept_.round(4))              # chia đúng cả 7
a2, b2 = np.array([1.0, 2.0]), np.array([3.0, 1.0])                            # hai điểm
phi = lambda v: np.array([v[0] ** 2, np.sqrt(2) * v[0] * v[1], v[1] ** 2])     # ánh xạ lên 3 chiều
print((a2 @ b2) ** 2, phi(a2) @ phi(b2))                                       # kernel và tích vô hướng tường minh
''', "0.5714285714285714\n1.0 [[-0.     -0.6668]] [1.667]\n25.0 25.0")
c.o('''
from sklearn.datasets import make_moons                                  # hai vầng trăng
from sklearn.model_selection import train_test_split                     # chia
Xm, ym = make_moons(300, noise=0.3, random_state=0)                      # như Chương 14
a, b, c_, e = train_test_split(Xm, ym, test_size=0.3, random_state=0)    # 210 train, 90 test
for g in [0.1, 1, 100]:                                                  # ba giá trị gamma
    mr = SVC(kernel="rbf", gamma=g).fit(a, c_)                           # kernel RBF
    print(g, round(mr.score(a, c_), 4), round(mr.score(b, e), 4))        # train, test
''', "0.1 0.8238 0.8556\n1 0.9429 0.9444\n100 0.9857 0.8667",
    khung("vi-sao", ["γ là nghịch đảo bán kính ảnh hưởng của mỗi điểm. γ = 100 thì mỗi điểm chỉ ảnh hưởng chính nó: train 99%, test 87%, giống KNN với k = 1."],
          nhan="VÌ SAO LẠI LÀ γ = 1 TỐT NHẤT?"))

c.mo_trang(4, "Chuẩn hóa, GridSearchCV, xác suất.")
c.o('''
from sklearn.datasets import load_breast_cancer                    # ung thư vú
from sklearn.model_selection import GridSearchCV                   # tìm trên lưới
from sklearn.pipeline import make_pipeline                         # ghép bước
from sklearn.preprocessing import StandardScaler                   # chuẩn hóa
dd = load_breast_cancer()                                          # 569 ca
Xb, yb = dd.data, 1 - dd.target                                    # 1 là ác tính
Xtr, Xte, ytr, yte = train_test_split(Xb, yb, test_size=0.25, random_state=0, stratify=yb)   # cách chia Chương 12
print(round(SVC().fit(Xtr, ytr).score(Xte, yte), 4), round(make_pipeline(StandardScaler(), SVC()).fit(Xtr, ytr).score(Xte, yte), 4))   # không và có chuẩn hóa
luoi = {"svc__C": [0.1, 1, 10, 100], "svc__gamma": [0.001, 0.01, 0.1, 1]}                     # 16 tổ hợp
gs = GridSearchCV(make_pipeline(StandardScaler(), SVC()), luoi, cv=5).fit(Xtr, ytr)          # 80 lần huấn luyện
print(gs.best_params_, round(gs.best_score_, 4), round(gs.score(Xte, yte), 4))               # tốt nhất, CV, test
mp = make_pipeline(StandardScaler(), SVC(probability=True, random_state=0)).fit(Xtr, ytr)    # bật xác suất
print(mp.predict_proba(Xte[:2]).round(4), mp.decision_function(Xte[:2]).round(4))           # xác suất và khoảng cách có dấu
''', "0.9301 0.951\n{'svc__C': 10, 'svc__gamma': 0.01} 0.9836 0.965\n[[0.0712 0.9288]\n [0.9955 0.0045]] [ 0.6447 -1.5203]",
    khung("loi", ["<b>Tổ hợp tốt nhất nằm ở mép lưới.</b> Khi đó giá trị thật sự tốt có thể nằm ngoài lưới; mở rộng lưới rồi chạy lại."]))

c.mo_trang(5, "Ba bài tập. Tính tay trước, rồi mới mở đáp án.")
c.bai("16.1", "Điểm mới trong lề", "Tính $\\mathbf w \\cdot \\mathbf x + b$ cho điểm $(3; 3)$.",
      "$-0{,}2$: đoán lớp 0 nhưng nằm trong lề, rất gần ranh giới. Code ở ô ngay dưới.")
c.o('''
print(round(0.8 * 3 + 0.4 * 3 - 3.8, 4))     # w·x + b của điểm (3; 3)
''', "-0.2")
c.bai("16.2", "Điểm xa nhất", "Điểm $(5; 6)$ cách ranh giới bao xa? Xóa nó thì ranh giới đổi không?",
      "$2{,}6/\\sqrt{0{,}8} \\approx 2{,}907$. Không phải vector hỗ trợ, xóa đi ranh giới không đổi. Code ở ô ngay dưới.")
c.o('''
print(round(2.6 / np.sqrt(0.8), 4))           # |w·x + b| / ||w||
''', "2.9069")
c.bai("16.3", "Kernel RBF theo gamma", "Tính kernel RBF giữa $(1; 2)$ và $(3; 1)$ với $\\gamma = 0{,}1$; 1; 10.",
      "0,607; 0,0067; $1{,}9 \\times 10^{-22}$. Cùng một cặp điểm, $\\gamma$ quyết định \"gần\" là bao xa. Code ở ô ngay dưới.")
c.o('''
print([float(np.exp(-g * np.sum((a2 - b2) ** 2))) for g in [0.1, 1, 10]])   # ba giá trị gamma
''', "[0.6065306597126334, 0.006737946999085467, 1.9287498479639178e-22]")

c.ghi(Path(__file__).resolve().parents[2] / "notebooks/ch16_svm_kernel.ipynb")
