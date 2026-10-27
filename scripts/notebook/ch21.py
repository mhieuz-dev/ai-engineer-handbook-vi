"""Dựng notebooks/ch21_feature_engineering.ipynb: python3 scripts/notebook/ch21.py"""
from pathlib import Path
from nblib import Chuong, khung

c = Chuong(21, "Feature engineering", "ch21-feature-engineering",
           "Biến dữ liệu thô thành đặc trưng tốt: mã hóa one-hot, ColumnTransformer, log cho cột lệch, đặc trưng tương tác, và đo độ quan trọng bằng permutation.",
           ["Mã hóa cột phân loại đúng cách.",
            "Gom mọi bước xử lý cột vào ColumnTransformer trong Pipeline.",
            "Tạo đặc trưng tương tác khi mô hình tuyến tính cần.",
            "Đo độ quan trọng bằng permutation importance."],
           [("Mã hóa đặc trưng phân loại", "01-ma-hoa-phan-loai"), ("ColumnTransformer và biến đổi cột số", "02-column-transformer"),
            ("Tạo đặc trưng mới", "03-tao-dac-trung-moi"), ("Đo độ quan trọng đúng cách", "04-do-quan-trong"), ("Bài tập", "05-bai-tap")])

c.mo_trang(1, "One-hot trên Bảng 4.1.")
c.o('''
import io                                                    # đọc chuỗi như file
import numpy as np                                           # tính toán
import pandas as pd                                          # bảng dữ liệu
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, StandardScaler   # mã hóa và chuẩn hóa
hang = ["ten,lop,gio,ngu,diem",                              # dòng tiêu đề
        "A,L1,1,7,2", "B,L1,2,6,4", "C,L1,3,8,5",            # Bảng 4.1
        "D,L1,4,7,7", "E,L2,5,6,6", "F,L2,2,,3.5",           # F thiếu giờ ngủ
        "G,L2,6,8,8.5", "H,L2,3,5,4", "I,L1,7,7,9",          # tiếp
        "K,L2,4,6,6.5"]                                      # bạn cuối
csv = "\\n".join(hang)                                       # nối thành một chuỗi CSV
df = pd.read_csv(io.StringIO(csv))                           # đọc thành DataFrame
oh = OneHotEncoder(sparse_output=False).fit(df[["lop"]])     # one-hot cột lớp
print(oh.get_feature_names_out(), oh.transform(df[["lop"]])[:3])   # tên cột mới, 3 hàng đầu
''', "['lop_L1' 'lop_L2'] [[1. 0.]\n [1. 0.]\n [1. 0.]]")

c.mo_trang(2, "ColumnTransformer, Pipeline, và log cho cột lệch.")
c.o('''
from sklearn.compose import ColumnTransformer               # xử lý từng nhóm cột
from sklearn.impute import SimpleImputer                    # điền giá trị thiếu
from sklearn.pipeline import make_pipeline                  # ghép bước
from sklearn.linear_model import LinearRegression, LogisticRegression   # mô hình
ct = ColumnTransformer([                                    # hai đường xử lý
    ("so", make_pipeline(SimpleImputer(strategy="median"), StandardScaler()), ["gio", "ngu"]),   # cột số
    ("chu", OneHotEncoder(), ["lop"]),                      # cột chữ
])                                                          # cột không liệt kê bị bỏ
Z = ct.fit_transform(df)                                    # học và biến đổi
print(Z.shape, Z[5].round(4), ct.get_feature_names_out())   # hàng của bạn F
m = make_pipeline(ct, LinearRegression()).fit(df, df["diem"])   # Pipeline nhận DataFrame thô
print(m[-1].coef_.round(4), round(m[-1].intercept_, 4))     # hệ số và hệ số chặn
''', "(10, 4) [-0.9488  0.3333  0.      1.    ] ['so__gio' 'so__ngu' 'chu__lop_L1' 'chu__lop_L2']\n[ 2.0287  0.1964  0.1242 -0.1242] 5.55",
    khung("doc", ["Khi đã biết giờ học, lớp L1 hay L2 chỉ chênh khoảng 0,25 điểm. Chênh lệch 0,3 điểm trung bình ở Chương 4 phần lớn là do L2 học nhiều giờ hơn."]))
c.o('''
rng = np.random.default_rng(0)                                         # seed
x = rng.lognormal(3, 1, 1000)                                          # 1000 giá trị lệch phải
lech = lambda v: float(((v - v.mean()) ** 3).mean() / v.std() ** 3)    # độ lệch (skewness)
print(round(float(np.mean(x)), 2), round(float(np.median(x)), 2), round(lech(x), 3), round(lech(np.log(x)), 3))   # trung bình, trung vị, độ lệch trước và sau log
''', "30.63 18.64 3.875 -0.073")

c.mo_trang(3, "Đặc trưng tương tác: XOR và bộ tiểu đường.")
c.o('''
from sklearn.model_selection import cross_val_score, train_test_split   # cross-validation, chia
rng = np.random.default_rng(0)                          # seed
X = rng.uniform(-1, 1, (400, 2))                        # 400 điểm trong hình vuông
y = ((X[:, 0] * X[:, 1]) > 0).astype(int)               # cùng dấu thì 1
print(round(cross_val_score(LogisticRegression(), X, y, cv=5).mean(), 4))   # chỉ hai đặc trưng gốc
X2 = np.c_[X, X[:, 0] * X[:, 1]]                        # thêm cột tích
print(round(cross_val_score(LogisticRegression(), X2, y, cv=5).mean(), 4))  # có cột tích
''', "0.4825\n0.955")
c.o('''
from sklearn.datasets import load_diabetes                                   # bộ của Chương 9
Xd, yd = load_diabetes(return_X_y=True, as_frame=True, scaled=False)          # đơn vị gốc
Xdtr, Xdte, ydtr, ydte = train_test_split(Xd, yd, test_size=0.2, random_state=42)   # cách chia Chương 9
goc = cross_val_score(make_pipeline(StandardScaler(), LinearRegression()), Xdtr, ydtr, cv=5, scoring="r2").mean()   # trước
Xm = Xdtr.copy()                                                              # bản sao để thêm cột
Xm["bmi_x_bp"] = Xm["bmi"] * Xm["bp"]                                         # tương tác
Xm["bmi2"] = Xm["bmi"] ** 2                                                   # bình phương
moi = cross_val_score(make_pipeline(StandardScaler(), LinearRegression()), Xm, ydtr, cv=5, scoring="r2").mean()   # sau
print(round(goc, 4), round(moi, 4))                                           # không giúp gì
''', "0.4493 0.4475",
    khung("vi-sao", ["Hai giả thuyết (BMI và huyết áp cộng hưởng, BMI tăng nhanh dần) không đúng trên dữ liệu này. Hai cột mới chỉ thêm hai hệ số phải ước lượng."],
          nhan="VÌ SAO LẠI KHÔNG TỐT HƠN?"))

c.mo_trang(4, "Impurity importance và permutation importance, với một cột nhiễu.")
c.o('''
from sklearn.ensemble import RandomForestRegressor                 # rừng
from sklearn.inspection import permutation_importance              # permutation importance
rf = RandomForestRegressor(300, random_state=0).fit(Xdtr, ydtr)    # 300 cây
pi = permutation_importance(rf, Xdte, ydte, n_repeats=20, random_state=0)   # xáo mỗi cột 20 lần
o = np.argsort(pi.importances_mean)[::-1][:4]                      # 4 cột quan trọng nhất
print([(c_, round(float(v), 4)) for c_, v in zip(Xd.columns[o], pi.importances_mean[o])])   # permutation
o2 = np.argsort(rf.feature_importances_)[::-1][:4]                 # theo impurity
print([(c_, round(float(v), 4)) for c_, v in zip(Xd.columns[o2], rf.feature_importances_[o2])])   # impurity
''', "[('s5', 0.2323), ('bmi', 0.2127), ('bp', 0.0229), ('s6', 0.0177)]\n[('bmi', 0.348), ('s5', 0.237), ('bp', 0.0929), ('s6', 0.0678)]")
c.o('''
rng = np.random.default_rng(0)                                     # seed
Xn, Xnt = Xdtr.copy(), Xdte.copy()                                 # bản sao train, test
Xn["nhieu"] = rng.normal(size=len(Xn))                             # cột ngẫu nhiên cho train
Xnt["nhieu"] = rng.normal(size=len(Xnt))                           # và cho test
rfn = RandomForestRegressor(300, random_state=0).fit(Xn, ydtr)     # rừng có cột nhiễu
pin = permutation_importance(rfn, Xnt, ydte, n_repeats=20, random_state=0)   # permutation
print(round(float(rfn.feature_importances_[-1]), 4), round(float(pin.importances_mean[-1]), 4))   # impurity và permutation của cột nhiễu
print(list(Xn.columns[np.argsort(rfn.feature_importances_)[::-1][:5]]))   # 5 cột đứng đầu theo impurity
''', "0.0742 -0.0044\n['bmi', 's5', 'bp', 'nhieu', 's6']",
    khung("loi", ["<b>Tin độ quan trọng impurity.</b> Cột nhiễu đứng hạng tư vì cây sâu luôn tìm được ngưỡng may mắn trên cột có nhiều giá trị. Permutation importance trên test cho nó gần 0."]))

c.mo_trang(5, "Ba bài tập. Làm ra giấy trước, rồi mới mở đáp án.")
c.bai("21.1", "One-hot cho ba tỉnh", "Viết tay ma trận one-hot cho HN, HCM, DN, HCM, HN.",
      "Ba cột xếp theo chữ cái: DN, HCM, HN. Hàng đầu (HN) là $(0, 0, 1)$. Code ở ô ngay dưới.")
c.o('''
t = pd.DataFrame({"tinh": ["HN", "HCM", "DN", "HCM", "HN"]})          # năm hàng
oh3 = OneHotEncoder(sparse_output=False).fit(t)                      # one-hot
print(oh3.get_feature_names_out(), oh3.transform(t).astype(int).tolist())   # tên cột và ma trận
''', "['tinh_DN' 'tinh_HCM' 'tinh_HN'] [[0, 0, 1], [0, 1, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]]")
c.bai("21.2", "Gán số thứ tự sai", "Ba lớp có điểm trung bình 5, 8, 4. So dự đoán của hồi quy với mã hóa thứ tự và one-hot.",
      "Thứ tự: 6,17; 5,67; 5,17, sai cả ba, lớp giỏi nhất bị đoán gần kém nhất. One-hot: đúng 5, 8, 4. Code ở ô ngay dưới.")
c.o('''
lop = pd.DataFrame({"lop": ["L1"] * 4 + ["L2"] * 4 + ["L3"] * 4})       # ba lớp
yl = np.array([5] * 4 + [8] * 4 + [4] * 4, dtype=float)                  # điểm
r1 = LinearRegression().fit(OrdinalEncoder().fit_transform(lop), yl)     # mã hóa thứ tự
print(r1.predict([[0], [1], [2]]).round(4))                              # dự đoán ba lớp
r2 = LinearRegression().fit(OneHotEncoder(sparse_output=False).fit_transform(lop), yl)   # one-hot
print(r2.predict(np.eye(3)).round(4))                                    # dự đoán ba lớp
''', "[6.1667 5.6667 5.1667]\n[5. 8. 4.]")
c.bai("21.3", "Permutation importance bằng tay", "Xáo một lần cột `bmi` của tập test, so $R^2$ của hồi quy tuyến tính trước và sau.",
      "Từ 0,4526 xuống 0,1842: giảm 0,27. Code ở ô ngay dưới.")
c.o('''
from sklearn.metrics import r2_score                                     # R²
ml = LinearRegression().fit(Xdtr, ydtr)                                  # hồi quy tuyến tính
g = r2_score(ydte, ml.predict(Xdte))                                     # R² gốc
Xx = Xdte.copy()                                                         # bản sao test
Xx["bmi"] = np.random.default_rng(0).permutation(Xx["bmi"].values)       # xáo riêng cột bmi
print(round(g, 4), round(r2_score(ydte, ml.predict(Xx)), 4), round(g - r2_score(ydte, ml.predict(Xx)), 4))   # trước, sau, độ tụt
''', "0.4526 0.1842 0.2684")

c.ghi(Path(__file__).resolve().parents[2] / "notebooks/ch21_feature_engineering.ipynb")
