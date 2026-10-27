"""Dựng notebooks/ch09_quy_trinh_du_an_ml.ipynb: python3 scripts/notebook/ch09.py"""
from pathlib import Path
from nblib import Chuong, khung

c = Chuong(9, "Quy trình một dự án ML", "ch09-quy-trinh-du-an-ml",
           "Một vòng dự án hoàn chỉnh trên 442 bệnh nhân tiểu đường: đặt bài toán, chia dữ liệu, baseline, mô hình, Pipeline, và đo test đúng một lần.",
           ["Gọi đúng tên đặc trưng, nhãn, mô hình, tham số, siêu tham số.",
            "Chia train, validation, test và dùng cross-validation.",
            "Dựng baseline và so mô hình trên validation.",
            "Dùng Pipeline để chuẩn hóa không rò rỉ, và nhận ra ba kiểu rò rỉ dữ liệu."],
           [("Đặt bài toán và nhìn dữ liệu", "01-dat-bai-toan"), ("Chia train, validation, test", "02-chia-du-lieu"),
            ("Baseline và mô hình đầu tiên", "03-baseline-va-mo-hinh"), ("Pipeline và rò rỉ dữ liệu", "04-pipeline-va-ro-ri"), ("Bài tập", "05-bai-tap")],
           runtime="CPU là đủ. Bộ dữ liệu có sẵn trong scikit-learn, không cần tải")

c.mo_trang(1, "Nạp và nhìn bộ dữ liệu 442 bệnh nhân.")
c.o('''
from sklearn.datasets import load_diabetes                 # bộ dữ liệu có sẵn
X, y = load_diabetes(return_X_y=True, as_frame=True, scaled=False)   # DataFrame, giữ đơn vị gốc
print(X.shape)                                              # 442 bệnh nhân, 10 đặc trưng
print(X.head(3))                                            # 3 hàng đầu
''', "(442, 10)\n    age  sex   bmi     bp     s1     s2    s3   s4      s5    s6\n0  59.0  2.0  32.1  101.0  157.0   93.2  38.0  4.0  4.8598  87.0\n1  48.0  1.0  21.6   87.0  183.0  103.2  70.0  3.0  3.8918  69.0\n2  72.0  2.0  30.5   93.0  156.0   93.6  41.0  4.0  4.6728  85.0")
c.o('''
print(y.describe().round(1))                         # nhãn: mức tiến triển sau một năm
print(X[["age", "bmi", "bp"]].describe().round(2))   # ba đặc trưng dễ hiểu nhất
''', "count    442.0\nmean     152.1\nstd       77.1\nmin       25.0\n25%       87.0\n50%      140.5\n75%      211.5\nmax      346.0\nName: target, dtype: float64\n          age     bmi      bp\ncount  442.00  442.00  442.00\nmean    48.52   26.38   94.65\nstd     13.11    4.42   13.83\nmin     19.00   18.00   62.00\n25%     38.25   23.20   84.00\n50%     50.00   25.70   93.00\n75%     59.00   29.28  105.00\nmax     79.00   42.20  133.00",
    khung("doc", ["Không có ô thiếu. Nhãn có độ lệch chuẩn 77: mốc để so. Các đặc trưng có thang đo rất khác nhau, trang 4 sẽ thấy hậu quả."]))

c.mo_trang(2, "Chia ba tập và cross-validation.")
c.o('''
from sklearn.model_selection import train_test_split, cross_val_score   # chia dữ liệu và cross-validation
from sklearn.linear_model import LinearRegression                       # hồi quy tuyến tính
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42)        # 20% làm test
Xtr2, Xva, ytr2, yva = train_test_split(Xtr, ytr, test_size=0.25, random_state=42) # 25% phần còn lại làm validation
print(len(Xtr2), len(Xva), len(Xte))                                    # khoảng 60/20/20
diem = cross_val_score(LinearRegression(), Xtr, ytr, cv=5, scoring="r2")  # 5 lần chia, 5 điểm R²
print(diem.round(4), round(diem.mean(), 4), round(diem.std(), 4))       # dao động giữa các lần chia
''', "264 89 89\n[0.5476 0.3612 0.5048 0.6177 0.2149] 0.4493 0.1441",
    khung("vi-sao", ["Cùng mô hình, chỉ khác cách chia mà R² từ 0,21 tới 0,62. Một lần đo trên khoảng 70 người rất bấp bênh, nên báo cáo trung bình kèm độ lệch."],
          nhan="VÌ SAO LẠI DAO ĐỘNG NHIỀU VẬY?"))

c.mo_trang(3, "Baseline, thêm dần đặc trưng, đo test một lần.")
c.o('''
from sklearn.dummy import DummyRegressor                       # baseline
from sklearn.metrics import mean_squared_error, r2_score       # hai thước đo

def danh_gia(mo_hinh, cot=None):                               # huấn luyện trên train, chấm trên validation
    a = Xtr2 if cot is None else Xtr2[cot]                     # chọn cột cho train
    b = Xva if cot is None else Xva[cot]                       # cùng các cột cho validation
    mo_hinh.fit(a, ytr2)                                       # học
    p = mo_hinh.predict(b)                                     # đoán validation
    return round(mean_squared_error(yva, p), 1), round(r2_score(yva, p), 4)   # MSE và R²

print(danh_gia(DummyRegressor()))                              # luôn đoán trung bình
print(danh_gia(LinearRegression(), ["bmi"]))                   # một đặc trưng
print(danh_gia(LinearRegression(), ["bmi", "bp"]))             # hai đặc trưng
print(danh_gia(LinearRegression(), ["bmi", "bp", "s5"]))       # ba đặc trưng
print(danh_gia(LinearRegression()))                            # cả 10
''', "(5721.3, -0.0443)\n(3430.1, 0.3739)\n(2997.2, 0.4529)\n(2713.8, 0.5047)\n(2620.8, 0.5216)")
c.o('''
m = LinearRegression().fit(Xtr2[["bmi"]], ytr2)          # mô hình một đặc trưng
print(round(m.coef_[0], 4), round(m.intercept_, 4))      # độ dốc và hệ số chặn
mo_hinh = LinearRegression().fit(Xtr, ytr)               # chọn xong: học lại trên train + validation
p = mo_hinh.predict(Xte)                                 # đo test, đúng một lần
print(round(mean_squared_error(yte, p), 1), round(r2_score(yte, p), 4), round(mean_squared_error(yte, p) ** 0.5, 1))  # MSE, R², RMSE
''', "10.7331 -134.5023\n2900.2 0.4526 53.9",
    khung("loi", ["<b>Quay lại chỉnh mô hình sau khi thấy điểm test.</b> Từ lúc này, test đã thành validation. Điểm test chỉ được đo một lần."]))

c.mo_trang(4, "SGD không chuẩn hóa, Pipeline, và một đặc trưng rò rỉ.")
c.o('''
from sklearn.linear_model import SGDRegressor            # hồi quy học bằng SGD
from sklearn.pipeline import make_pipeline               # ghép các bước
from sklearn.preprocessing import StandardScaler         # chuẩn hóa
s = SGDRegressor(random_state=0).fit(Xtr2, ytr2)         # học thẳng trên đơn vị gốc
print(r2_score(yva, s.predict(Xva)))                     # phân kỳ
p = make_pipeline(StandardScaler(), SGDRegressor(random_state=0))   # chuẩn hóa rồi mới hồi quy
p.fit(Xtr2, ytr2)                                        # scaler học mu, sigma chỉ từ train
print(round(r2_score(yva, p.predict(Xva)), 4))           # ngang nghiệm đóng
''', "-5.0340614999537655e+22\n0.5198")
c.o('''
import numpy as np                                         # sinh nhiễu
rng = np.random.default_rng(0)                             # seed
Xl = X.copy()                                              # bản sao để thêm cột
Xl["xet_nghiem_sau"] = y + rng.normal(0, 10, len(y))       # cột "bí mật" chứa gần như đáp án
a, b, c_, d = train_test_split(Xl, y, test_size=0.2, random_state=42)   # chia như trước
print(round(r2_score(d, LinearRegression().fit(a, c_).predict(b)), 4))  # đẹp giả tạo
''', "0.9826",
    khung("truc-giac", ["Hỏi: ngày mô hình được dùng thật, nó có được thấy thông tin này không? Kết quả 6 tháng sau thì không. R² 0,98 ở đây là ảo."]))

c.mo_trang(5, "Ba bài tập. Đoán trước, rồi mới mở đáp án.")
c.bai("9.1", "Baseline trung vị", "Đoán MSE của `DummyRegressor(strategy=\"median\")` trên validation so với baseline trung bình 5721,3.",
      "Tệ hơn: 6342,1. Trung bình là hằng số tốt nhất cho MSE; trung vị tốt nhất cho MAE. Nhãn lại lệch phải. Code ở ô ngay dưới.")
c.o('''
print(danh_gia(DummyRegressor(strategy="median")))          # baseline trung vị
print(round(ytr2.mean(), 2), ytr2.median(), round(yva.mean(), 2))   # trung bình train, trung vị train, trung bình validation
''', "(6342.1, -0.1576)\n149.81 136.0 165.38")
c.bai("9.2", "Tự tính R²", "Tính $1 - \\text{MSE}/\\text{phương sai của yva}$ cho mô hình 10 đặc trưng và baseline.",
      "Phương sai 5478,8. Ra 0,5216 và $-0{,}0443$, khớp Bảng 9.2. Baseline âm vì đoán trung bình của train chứ không phải của validation. Code ở ô ngay dưới.")
c.o('''
v = ((yva - yva.mean()) ** 2).mean()                          # MSE nếu đoán đúng trung bình validation
print(round(v, 1), round(1 - 2620.8 / v, 4), round(1 - 5721.3 / v, 4))   # R² của mô hình và baseline
''', "5478.8 0.5216 -0.0443")
c.bai("9.3", "Tìm rò rỉ", "Mô hình dự đoán khách hủy gói cước đạt 97%. Đặc trưng có \"ngày hủy gói\"; chuẩn hóa trên cả bộ rồi mới chia; thử 40 cấu hình rồi báo điểm test tốt nhất. Chỉ ra từng chỗ rò rỉ.",
      "Ngày hủy gói là nhãn viết dạng khác (kiểu 1). Chuẩn hóa trước khi chia (kiểu 2). Chọn bằng test (kiểu 3). Thêm nữa: nếu chỉ 3% khách hủy, luôn đoán \"không hủy\" đã được 97%.")

c.ghi(Path(__file__).resolve().parents[2] / "notebooks/ch09_quy_trinh_du_an_ml.ipynb")
