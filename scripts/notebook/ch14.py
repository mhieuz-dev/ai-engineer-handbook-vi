"""Dựng notebooks/ch14_knn.ipynb: python3 scripts/notebook/ch14.py"""
from pathlib import Path
from nblib import Chuong, khung

c = Chuong(14, "KNN và khoảng cách", "ch14-knn",
           "Mô hình không học tham số: hỏi k láng giềng gần nhất. Chọn k, chuẩn hóa, lời nguyền số chiều, và KNN cho hồi quy.",
           ["Tính tay KNN cho một điểm mới.",
            "Chọn k bằng cross-validation như một núm vặn bias-variance.",
            "Thấy vì sao KNN bắt buộc phải chuẩn hóa và hỏng dần khi nhiều chiều.",
            "Dùng KNN cho hồi quy và hiểu chi phí của nó."],
           [("Hỏi hàng xóm", "01-y-tuong"), ("Chọn k", "02-chon-k"),
            ("Chuẩn hóa và lời nguyền số chiều", "03-chuan-hoa-va-so-chieu"), ("KNN hồi quy và chi phí", "04-hoi-quy-va-chi-phi"), ("Bài tập", "05-bai-tap")])

c.mo_trang(1, "Khoảng cách tới 10 bạn và bỏ phiếu.")
c.o('''
import numpy as np                                                   # tính toán
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor   # KNN
ten = list("ABCDEFGHIK")                                             # tên 10 bạn
X = np.array([[1, 7], [2, 6], [3, 8], [4, 7], [5, 6], [2, 7], [6, 8], [3, 5], [7, 7], [4, 6]], dtype=float)   # (giờ học, giờ ngủ)
y = (np.array([2, 4, 5, 7, 6, 3.5, 8.5, 4, 9, 6.5]) >= 5).astype(int)    # 1 là đạt
q = np.array([3.4, 6.3])                                             # bạn mới
d = np.sqrt(((X - q) ** 2).sum(axis=1))                              # khoảng cách Euclid
thu_tu = np.argsort(d)                                               # xếp theo khoảng cách
print([(ten[i], float(round(d[i], 4)), int(y[i])) for i in thu_tu[:5]])     # 5 người gần nhất
for k in [1, 3, 5]:                                                  # ba giá trị k
    phieu = y[thu_tu[:k]]                                            # nhãn của k người gần nhất
    print(k, phieu, "đạt" if phieu.mean() > 0.5 else "không đạt")    # bỏ phiếu
''', "[('K', 0.6708, 1), ('D', 0.922, 1), ('H', 1.3601, 0), ('B', 1.4318, 0), ('F', 1.5652, 0)]\n1 [1] đạt\n3 [1 1 0] đạt\n5 [1 1 0 0 0] không đạt",
    khung("doc", ["Cùng bạn mới, k = 3 đoán đạt, k = 5 đoán không đạt: vòng 5 người bắt thêm B và F, cả hai không đạt."]))
c.o('''
for k in [1, 3, 5]:                                         # cùng việc với scikit-learn
    knn = KNeighborsClassifier(n_neighbors=k).fit(X, y)     # fit chỉ là cất dữ liệu
    print(k, knn.predict([q]), knn.predict_proba([q]).round(2))   # nhãn và tỷ lệ phiếu
''', "1 [1] [[0. 1.]]\n3 [1] [[0.33 0.67]]\n5 [0] [[0.6 0.4]]")

c.mo_trang(2, "Ba giá trị k trên hai vầng trăng, chọn k bằng cross-validation.")
c.o('''
from sklearn.datasets import make_moons, load_breast_cancer           # hai bộ dữ liệu
from sklearn.model_selection import train_test_split, cross_val_score  # chia và cross-validation
from sklearn.pipeline import make_pipeline                            # ghép bước
from sklearn.preprocessing import StandardScaler                      # chuẩn hóa
Xm, ym = make_moons(n_samples=300, noise=0.3, random_state=0)         # hai nửa vầng trăng
a, b, c_, e = train_test_split(Xm, ym, test_size=0.3, random_state=0) # chia
for k in [1, 15, 100]:                                                # linh hoạt, vừa, cứng
    m = KNeighborsClassifier(k).fit(a, c_)                            # huấn luyện
    print(k, round(m.score(a, c_), 4), round(m.score(b, e), 4))       # train, test
''', "1 1.0 0.8889\n15 0.9429 0.9222\n100 0.819 0.8222")
c.o('''
dd = load_breast_cancer()                                       # ung thư vú, như Chương 12
Xb, yb = dd.data, 1 - dd.target                                 # 1 là ác tính
Xtr, Xte, ytr, yte = train_test_split(Xb, yb, test_size=0.25, random_state=0, stratify=yb)   # cùng cách chia
for k in [1, 3, 5, 11, 21, 51, 151]:                            # nhiều giá trị k
    pl = make_pipeline(StandardScaler(), KNeighborsClassifier(k))   # chuẩn hóa rồi KNN
    s = cross_val_score(pl, Xtr, ytr, cv=5)                     # 5 phần
    print(k, round(pl.fit(Xtr, ytr).score(Xtr, ytr), 4), round(s.mean(), 4))   # train và cross-validation
''', "1 1.0 0.9578\n3 0.9859 0.9695\n5 0.9765 0.9672\n11 0.9742 0.9554\n21 0.9554 0.9507\n51 0.9413 0.9343\n151 0.9038 0.8803",
    khung("loi", ["<b>Chọn k bằng độ chính xác train.</b> k = 1 luôn được 100% trên train vì mỗi điểm tự tìm thấy chính nó."]))

c.mo_trang(3, "Thang đo, chuẩn hóa và lời nguyền số chiều.")
c.o('''
print(Xb[:, [0, 3, 9]].std(axis=0).round(3))                                  # ba đặc trưng, ba thang đo
print(round(KNeighborsClassifier(5).fit(Xtr, ytr).score(Xte, yte), 4))        # không chuẩn hóa
print(round(make_pipeline(StandardScaler(), KNeighborsClassifier(5)).fit(Xtr, ytr).score(Xte, yte), 4))   # có chuẩn hóa
''', "[3.52100e+00 3.51605e+02 7.00000e-03]\n0.9231\n0.9371")
c.o('''
rng = np.random.default_rng(0)                         # seed
for dim in [2, 10, 100, 1000]:                         # số chiều tăng dần
    P = rng.uniform(0, 1, (1000, dim))                 # 1000 điểm trong hình lập phương
    qq = rng.uniform(0, 1, dim)                        # một điểm mới
    dd_ = np.sqrt(((P - qq) ** 2).sum(axis=1))         # khoảng cách tới cả 1000 điểm
    print(dim, round(dd_.min(), 3), round(dd_.max(), 3), round(dd_.min() / dd_.max(), 3))   # gần nhất, xa nhất, tỷ lệ
''', "2 0.01 1.334 0.007\n10 0.471 2.111 0.223\n100 3.349 4.653 0.72\n1000 12.166 13.553 0.898",
    khung("truc-giac", ["Ở 1000 chiều, láng giềng gần nhất chỉ gần hơn điểm xa nhất khoảng 10%. Mọi điểm đều xa gần bằng nhau, hỏi hàng xóm mất ý nghĩa."]))

c.mo_trang(4, "KNN hồi quy trên bộ tiểu đường.")
c.o('''
from sklearn.datasets import load_diabetes                     # bộ của Chương 9
from sklearn.metrics import r2_score                           # R²
Xd, yd = load_diabetes(return_X_y=True, as_frame=True, scaled=False)   # đơn vị gốc
Xdtr, Xdte, ydtr, ydte = train_test_split(Xd, yd, test_size=0.2, random_state=42)   # cách chia Chương 9
for k in [1, 5, 20, 50]:                                       # bốn giá trị k
    md = make_pipeline(StandardScaler(), KNeighborsRegressor(k)).fit(Xdtr, ydtr)    # chuẩn hóa rồi KNN hồi quy
    print(k, round(r2_score(ydte, md.predict(Xdte)), 4))       # R² test
''', "1 0.0678\n5 0.4248\n20 0.4246\n50 0.4276",
    khung("thu", ["<b>1.</b> Bỏ StandardScaler trong ô trên. R² thay đổi thế nào?",
                  "<b>2.</b> Đo thời gian predict bằng %timeit với k = 5 và so với LinearRegression."]))

c.mo_trang(5, "Ba bài tập. Tính tay trước, rồi mới mở đáp án.")
c.bai("14.1", "Khoảng cách tay", "Tính tay khoảng cách từ bạn mới tới D (4; 7) và H (3; 5).",
      "D: $\\sqrt{0{,}85} \\approx 0{,}922$. H: $\\sqrt{1{,}85} \\approx 1{,}3601$. Code ở ô ngay dưới.")
c.o('''
print(np.sqrt(0.6 ** 2 + 0.7 ** 2), np.sqrt(0.4 ** 2 + 1.3 ** 2))   # D và H
''', "0.9219544457292886 1.3601470508735443")
c.bai("14.2", "Phiếu có trọng số", "Với $k = 5$, cho mỗi láng giềng phiếu nặng $1/d$. Kết quả có đổi không?",
      "Đạt: $2{,}576$; không đạt: $2{,}072$. Kết quả lật thành đạt, xác suất khoảng 0,554. Code ở ô ngay dưới.")
c.o('''
mw = KNeighborsClassifier(5, weights="distance").fit(X, y)    # phiếu nặng theo nghịch đảo khoảng cách
print(mw.predict([q]), mw.predict_proba([q]).round(4))        # nhãn và xác suất
''', "[1] [[0.4459 0.5541]]")
c.bai("14.3", "k bằng cả lớp", "KNN hồi quy dự đoán điểm của bạn mới với $k = 3$ và $k = 10$.",
      "$k = 3$: $5{,}8333$. $k = 10$: $5{,}55$, trung bình cả lớp, chính là baseline luôn đoán trung bình. Code ở ô ngay dưới.")
c.o('''
diem = np.array([2, 4, 5, 7, 6, 3.5, 8.5, 4, 9, 6.5])            # điểm thi
for k in [3, 10]:                                               # ba láng giềng, cả lớp
    print(k, KNeighborsRegressor(k).fit(X, diem).predict([q]).round(4))   # trung bình điểm của k láng giềng
''', "3 [5.8333]\n10 [5.55]")

c.ghi(Path(__file__).resolve().parents[2] / "notebooks/ch14_knn.ipynb")
