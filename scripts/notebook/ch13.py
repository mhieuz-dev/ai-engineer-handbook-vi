"""Dựng notebooks/ch13_overfitting_regularization.ipynb: python3 scripts/notebook/ch13.py"""
from pathlib import Path
from nblib import Chuong, khung

c = Chuong(13, "Overfitting, bias-variance và regularization", "ch13-overfitting-regularization",
           "Đa thức bậc 1 tới 12 trên 15 điểm nhiễu, tách lỗi thành bias và variance, rồi kìm mô hình bằng ridge, lasso và thêm dữ liệu.",
           ["Nhận ra overfitting và underfitting từ lỗi train và validation.",
            "Đo bias và variance bằng mô phỏng.",
            "Dùng ridge và lasso, đọc đường hệ số lasso.",
            "Chọn alpha bằng cross-validation và đọc đường cong học."],
           [("Overfitting và underfitting", "01-overfitting"), ("Bias và variance", "02-bias-variance"),
            ("Ridge và lasso", "03-ridge-va-lasso"), ("Thêm dữ liệu và chọn độ mạnh", "04-them-du-lieu-va-chon-alpha"), ("Bài tập", "05-bai-tap")])

c.mo_trang(1, "Đa thức bậc 1, 3, 9 trên 15 điểm.")
c.o('''
import numpy as np                                               # tính toán
from sklearn.preprocessing import PolynomialFeatures, StandardScaler   # sinh cột x^k, chuẩn hóa
from sklearn.linear_model import LinearRegression                # hồi quy tuyến tính
from sklearn.pipeline import make_pipeline                       # ghép các bước
from sklearn.metrics import mean_squared_error as mse            # MSE

f = lambda t: np.sin(2 * np.pi * t)                              # quy luật thật
rng = np.random.default_rng(0)                                   # seed
x = rng.uniform(0, 1, 15); y = f(x) + rng.normal(0, 0.3, 15)     # 15 điểm train
xv = rng.uniform(0, 1, 200); yv = f(xv) + rng.normal(0, 0.3, 200)    # 200 điểm validation
khop = lambda d: make_pipeline(PolynomialFeatures(d), LinearRegression()).fit(x[:, None], y)   # đa thức bậc d
for d in [1, 3, 9]:                                              # ba độ phức tạp
    m = khop(d)                                                  # khớp
    print(d, round(mse(y, m.predict(x[:, None])), 4), round(mse(yv, m.predict(xv[:, None])), 4))   # lỗi train, validation
''', "1 0.1682 0.4381\n3 0.038 0.1047\n9 0.0273 0.7235",
    khung("doc", ["Bậc 1 sai cả hai: underfitting. Bậc 3 gần mức nhiễu 0,09. Bậc 9 train thấp hơn cả nhiễu nhưng validation tệ hơn đường thẳng: overfitting."]))

c.mo_trang(2, "Bias và variance trên 200 bộ dữ liệu.")
c.o('''
xg = np.linspace(0.05, 0.95, 50)                          # 50 điểm đo
for d in [1, 3, 6]:                                       # ba bậc
    rng = np.random.default_rng(1)                        # cùng seed cho mỗi bậc
    P = []                                                # lưu dự đoán của từng bộ dữ liệu
    for _ in range(200):                                  # 200 bộ dữ liệu
        xs = rng.uniform(0, 1, 15); ys = f(xs) + rng.normal(0, 0.3, 15)   # một bộ 15 điểm mới
        P.append(make_pipeline(PolynomialFeatures(d), LinearRegression()).fit(xs[:, None], ys).predict(xg[:, None]))  # dự đoán tại 50 điểm
    P = np.array(P)                                       # shape (200, 50)
    bias2 = np.mean((P.mean(axis=0) - f(xg)) ** 2)        # bias bình phương
    var = np.mean(P.var(axis=0))                          # variance
    print(d, round(bias2, 4), round(var, 4))              # in hai phần
''', "1 0.1501 0.044\n3 0.0023 0.098\n6 0.2257 30.5294",
    khung("vi-sao", ["Thường thì đa thức bậc 6 khớp ổn, nhưng vài bộ dữ liệu để lại khoảng trống gần mép và nó vọt lên hàng chục đơn vị. Vài lần như vậy kéo variance lên 30."],
          nhan="VÌ SAO LẠI LÀ VARIANCE 30?"))

c.mo_trang(3, "Ridge trên đa thức bậc 9, lasso trên bộ tiểu đường.")
c.o('''
from sklearn.linear_model import Ridge                                              # ridge
m0 = make_pipeline(PolynomialFeatures(9), StandardScaler(), LinearRegression()).fit(x[:, None], y)   # không phạt
print(round(mse(yv, m0.predict(xv[:, None])), 4), round(float(np.abs(m0[-1].coef_).max()), 1))       # lỗi và trọng số lớn nhất
for a in [1e-6, 1e-3, 1e-1, 10]:                                                    # bốn mức phạt
    m = make_pipeline(PolynomialFeatures(9), StandardScaler(), Ridge(alpha=a)).fit(x[:, None], y)    # ridge
    print(a, round(mse(y, m.predict(x[:, None])), 4), round(mse(yv, m.predict(xv[:, None])), 4), round(float(np.abs(m[-1].coef_).max()), 2))  # train, validation, trọng số lớn nhất
''', "0.7403 2356.8\n1e-06 0.0331 0.15 66.55\n0.001 0.0352 0.1167 3.47\n0.1 0.0593 0.2417 0.81\n10 0.1493 0.4134 0.13")
c.o('''
from sklearn.linear_model import Lasso                                       # lasso
from sklearn.datasets import load_diabetes                                   # bộ của Chương 9
from sklearn.model_selection import train_test_split                         # chia dữ liệu
from sklearn.metrics import r2_score                                         # R²
X, yd = load_diabetes(return_X_y=True, as_frame=True, scaled=False)          # đơn vị gốc
Xtr, Xte, ytr, yte = train_test_split(X, yd, test_size=0.2, random_state=42)             # test 20%
Xtr2, Xva, ytr2, yva = train_test_split(Xtr, ytr, test_size=0.25, random_state=42)       # validation
for a in [0.01, 1, 5, 10, 20]:                                               # năm mức phạt
    ml = make_pipeline(StandardScaler(), Lasso(alpha=a)).fit(Xtr2, ytr2)     # chuẩn hóa rồi lasso
    c_ = ml[-1].coef_                                                        # hệ số
    print(a, int((c_ == 0).sum()), round(r2_score(yva, ml.predict(Xva)), 4), [n for n, v in zip(X.columns, c_) if v != 0])   # số hệ số bằng 0, R², đặc trưng còn lại
''', "0.01 0 0.5219 ['age', 'sex', 'bmi', 'bp', 's1', 's2', 's3', 's4', 's5', 's6']\n1 1 0.5241 ['age', 'sex', 'bmi', 'bp', 's1', 's3', 's4', 's5', 's6']\n5 4 0.5183 ['sex', 'bmi', 'bp', 's2', 's3', 's5']\n10 6 0.4844 ['bmi', 'bp', 's3', 's5']\n20 7 0.3774 ['bmi', 'bp', 's5']",
    khung("loi", ["<b>Dùng regularization mà không chuẩn hóa.</b> Khoản phạt so trọng số của các đặc trưng với nhau; thang đo lệch nhau là phạt không công bằng."]))

c.mo_trang(4, "Đường cong học và chọn alpha bằng cross-validation.")
c.o('''
for n in [15, 30, 100, 1000]:                                                   # lượng dữ liệu tăng dần
    rng = np.random.default_rng(2)                                              # seed
    xs = rng.uniform(0, 1, n); ys = f(xs) + rng.normal(0, 0.3, n)              # n điểm train
    xt = rng.uniform(0, 1, 2000); yt = f(xt) + rng.normal(0, 0.3, 2000)         # 2000 điểm đo
    m6 = make_pipeline(PolynomialFeatures(6), LinearRegression()).fit(xs[:, None], ys)   # đa thức bậc 6
    print(n, round(mse(ys, m6.predict(xs[:, None])), 4), round(mse(yt, m6.predict(xt[:, None])), 4))   # train tăng, mới giảm
''', "15 0.056 0.1865\n30 0.075 0.1077\n100 0.0766 0.0966\n1000 0.086 0.0899")
c.o('''
from sklearn.linear_model import RidgeCV, LassoCV                              # chọn alpha bằng cross-validation
cv = make_pipeline(PolynomialFeatures(9), StandardScaler(), RidgeCV(alphas=np.logspace(-6, 2, 50))).fit(x[:, None], y)   # 50 mức alpha
print(round(float(cv[-1].alpha_), 5), round(mse(yv, cv.predict(xv[:, None])), 4))          # alpha chọn được, lỗi validation
lc = make_pipeline(StandardScaler(), LassoCV(cv=5, random_state=0)).fit(Xtr, ytr)          # 5 phần, trên 353 người
print(round(float(lc[-1].alpha_), 4), int((lc[-1].coef_ == 0).sum()), round(r2_score(yte, lc.predict(Xte)), 4))   # alpha, số đặc trưng bị loại, R² test
print(round(r2_score(yte, LinearRegression().fit(Xtr, ytr).predict(Xte)), 4))               # so sánh: không regularization
''', "0.00126 0.1177\n1.6552 3 0.4714\n0.4526",
    khung("thu", ["<b>1.</b> Đổi bậc đa thức trong đường cong học từ 6 thành 1. Lỗi có giảm về 0,09 khi n = 1000 không?",
                  "<b>2.</b> Đổi seed 2 thành 3, 4, 5. Dòng n = 15 thay đổi nhiều không?"]))

c.mo_trang(5, "Ba bài tập. Làm ra giấy trước, rồi mới mở đáp án.")
c.bai("13.1", "Hai khoản phạt", "Với $\\alpha = 0{,}1$, tính khoản phạt ridge và lasso cho $(3, -4)$ và $(5, 0)$.",
      "Ridge: 2,5 và 2,5, như nhau vì cùng độ dài 5. Lasso: 0,7 và 0,5, ưa vector có một trọng số bằng 0. Code ở ô ngay dưới.")
c.o('''
w1, w2, a = np.array([3, -4.0]), np.array([5, 0.0]), 0.1     # hai vector và alpha
print(a * (w1 ** 2).sum(), round(a * np.abs(w1).sum(), 4))   # ridge và lasso cho w1
print(a * (w2 ** 2).sum(), a * np.abs(w2).sum())             # ridge và lasso cho w2
''', "2.5 0.7\n2.5 0.5")
c.bai("13.2", "Chẩn đoán", "Ba mô hình có (train, validation) là A (0,48; 0,51), B (0,02; 0,64), C (0,11; 0,13), nhiễu khoảng 0,10. Chẩn đoán từng mô hình.",
      "A underfitting: thêm dữ liệu vô ích, cần mô hình mạnh hơn. B overfitting: train dưới mức nhiễu; thêm dữ liệu hoặc regularization giúp được. C ổn: dừng và đo test.")
c.bai("13.3", "Cứu đa thức bậc 12", "Đo MSE validation của đa thức bậc 12, rồi dùng `RidgeCV` để cứu nó.",
      "Không phạt: 1,3054. RidgeCV chọn $\\alpha \\approx 0{,}00087$, còn 0,1211. Code ở ô ngay dưới.")
c.o('''
m12 = make_pipeline(PolynomialFeatures(12), StandardScaler(), LinearRegression()).fit(x[:, None], y)   # không phạt
print(round(mse(yv, m12.predict(xv[:, None])), 4))                                                   # lỗi validation
cv12 = make_pipeline(PolynomialFeatures(12), StandardScaler(), RidgeCV(alphas=np.logspace(-6, 2, 50))).fit(x[:, None], y)   # ridge chọn alpha
print(round(float(cv12[-1].alpha_), 5), round(mse(yv, cv12.predict(xv[:, None])), 4))                # alpha và lỗi
''', "1.3054\n0.00087 0.1211")

c.ghi(Path(__file__).resolve().parents[2] / "notebooks/ch13_overfitting_regularization.ipynb")
