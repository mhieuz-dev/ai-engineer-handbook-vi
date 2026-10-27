"""Dựng notebooks/ch22_du_an_phan_2.ipynb: python3 scripts/notebook/ch22.py"""
from pathlib import Path
from nblib import Chuong, khung

c = Chuong(22, "Dự án Phần II", "ch22-du-an-phan-2",
           "Một dự án trọn vẹn trên 20 640 khu dân cư California: nhìn dữ liệu, baseline, mô hình tuyến tính, boosting, chọn siêu tham số, đo test và phân tích lỗi.",
           ["Đi trọn quy trình dự án trên dữ liệu hai mươi nghìn dòng.",
            "Tạo đặc trưng từ quan sát về dữ liệu.",
            "Chọn mô hình và siêu tham số chỉ bằng cross-validation.",
            "Phân tích lỗi theo nhóm và nói rõ giới hạn của mô hình."],
           [("Bài toán và dữ liệu", "01-bai-toan-va-du-lieu"), ("Baseline và mô hình tuyến tính", "02-baseline-va-tuyen-tinh"),
            ("Mô hình cây và chọn siêu tham số", "03-mo-hinh-cay"), ("Đo test và phân tích lỗi", "04-do-test-va-phan-tich-loi"), ("Bài tập", "05-bai-tap")],
           thoi_gian="khoảng 3 tới 5 phút (GridSearchCV huấn luyện 40 lần)", runtime="CPU là đủ. Lần đầu cần mạng để tải dữ liệu")

c.mo_trang(1, "Tải và nhìn dữ liệu.")
c.o('''
import numpy as np                                                 # tính toán
import pandas as pd                                                # bảng dữ liệu
pd.set_option("display.width", 120, "display.max_columns", 20)     # in đủ 8 cột trên một dòng
from sklearn.datasets import fetch_california_housing              # bộ dữ liệu
d = fetch_california_housing(as_frame=True)                        # tải lần đầu cần mạng
X, y = d.frame.drop(columns="MedHouseVal"), d.frame["MedHouseVal"] # 8 đặc trưng và nhãn
print(X.shape, list(X.columns))                                    # kích thước, tên cột
print(X.describe().round(2).loc[["mean", "50%", "max"]])           # ba dòng thống kê
print(int((y >= 5.0).sum()), round(float((y >= 5.0).mean()), 4), y.max())   # các khu bị chặn giá
''', "(20640, 8) ['MedInc', 'HouseAge', 'AveRooms', 'AveBedrms', 'Population', 'AveOccup', 'Latitude', 'Longitude']\n      MedInc  HouseAge  AveRooms  AveBedrms  Population  AveOccup  Latitude  Longitude\nmean    3.87     28.64      5.43       1.10     1425.48      3.07     35.63    -119.57\n50%     3.53     29.00      5.23       1.05     1166.00      2.82     34.26    -118.49\nmax    15.00     52.00    141.91      34.07    35682.00   1243.33     41.95    -114.31\n992 0.0481 5.00001",
    khung("doc", ["AveOccup lớn nhất 1243 người mỗi hộ (trung vị 2,82): cột lệch cực mạnh. 992 khu (4,8%) bị chặn giá ở 5,00001: chỉ biết giá ít nhất 500 000 USD."]))

c.mo_trang(2, "Baseline, hồi quy tuyến tính, bốn đặc trưng mới.")
c.o('''
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV   # chia, CV, lưới
from sklearn.dummy import DummyRegressor                                # baseline
from sklearn.pipeline import make_pipeline                              # ghép bước
from sklearn.preprocessing import StandardScaler, FunctionTransformer   # chuẩn hóa, bọc hàm
from sklearn.linear_model import LinearRegression                       # hồi quy tuyến tính
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42)   # 80/20
print(len(Xtr), len(Xte))                                               # số khu

def mae_cv(m, XX=Xtr):                                                  # MAE cross-validation trên train
    return round(-cross_val_score(m, XX, ytr, cv=5, scoring="neg_mean_absolute_error").mean(), 4)   # đổi dấu cho dễ đọc

def them_cot(D):                                                        # bốn đặc trưng mới
    D = D.copy()                                                        # không sửa bảng gốc
    D["RoomsPerPerson"] = D["AveRooms"] / D["AveOccup"]                 # phòng mỗi người
    D["BedrmRatio"] = D["AveBedrms"] / D["AveRooms"]                    # tỷ lệ phòng ngủ
    D["LogPop"] = np.log(D["Population"])                               # log dân số
    D["LogOccup"] = np.log(D["AveOccup"])                               # log số người mỗi hộ
    return D                                                            # bảng đã thêm cột

fe = FunctionTransformer(them_cot)                                      # bước Pipeline
print(mae_cv(DummyRegressor()))                                         # baseline
print(mae_cv(make_pipeline(StandardScaler(), LinearRegression())))      # tuyến tính
print(mae_cv(make_pipeline(fe, StandardScaler(), LinearRegression())))  # tuyến tính + 4 cột
''', "16512 4128\n0.9139\n0.5291\n0.4815")

c.mo_trang(3, "Random forest, boosting, GridSearchCV.")
c.o('''
from sklearn.ensemble import RandomForestRegressor, HistGradientBoostingRegressor   # hai ensemble
print(mae_cv(RandomForestRegressor(100, random_state=0, n_jobs=-1)))                # rừng
print(mae_cv(HistGradientBoostingRegressor(random_state=0)))                        # boosting mặc định
print(mae_cv(make_pipeline(fe, HistGradientBoostingRegressor(random_state=0))))     # boosting + 4 cột
luoi = {"learning_rate": [0.05, 0.1], "max_iter": [300, 600], "max_leaf_nodes": [31, 63]}   # 8 tổ hợp
gs = GridSearchCV(HistGradientBoostingRegressor(random_state=0), luoi, cv=5,       # 40 lần huấn luyện
                  scoring="neg_mean_absolute_error", n_jobs=-1).fit(Xtr, ytr)      # chọn theo MAE
print(gs.best_params_, round(-gs.best_score_, 4))                                   # tổ hợp tốt nhất
''', "0.3349\n0.3154\n0.3128\n{'learning_rate': 0.05, 'max_iter': 600, 'max_leaf_nodes': 63} 0.3024",
    khung("vi-sao", ["Giá phụ thuộc vị trí theo cách phi tuyến (gần bờ biển và gần thành phố mới đắt). Cây chia mặt phẳng kinh độ, vĩ độ thành từng vùng nhỏ."],
          nhan="VÌ SAO LẠI LÀ CÂY THẮNG XA?"))

c.mo_trang(4, "Đo test một lần, lỗi theo nhóm, permutation importance.")
c.o('''
from sklearn.metrics import mean_absolute_error, r2_score, mean_squared_error   # thước đo
from sklearn.inspection import permutation_importance                          # độ quan trọng
p = gs.predict(Xte)                                                            # đo test, đúng một lần
print(round(mean_absolute_error(yte, p), 4), round(r2_score(yte, p), 4), round(mean_squared_error(yte, p) ** 0.5, 4))   # MAE, R², RMSE
loi = (yte - p).abs()                                                          # lỗi từng khu
chan = yte >= 5.0                                                              # khu bị chặn giá
print(int(chan.sum()), round(float(loi[chan].mean()), 4), round(float(loi[~chan].mean()), 4))   # số khu, MAE hai nhóm
pi = permutation_importance(gs.best_estimator_, Xte, yte, n_repeats=5, random_state=0, scoring="neg_mean_absolute_error")   # xáo mỗi cột 5 lần
o = np.argsort(pi.importances_mean)[::-1]                                      # xếp giảm dần
print([(c_, round(float(v), 4)) for c_, v in zip(X.columns[o], pi.importances_mean[o])])   # tên và độ quan trọng
''', "0.2887 0.8494 0.4443\n184 0.592 0.2745\n[('Latitude', 0.6319), ('Longitude', 0.5714), ('MedInc', 0.31), ('AveOccup', 0.1449), ('AveRooms', 0.0863), ('HouseAge', 0.0434), ('AveBedrms', 0.0107), ('Population', 0.0085)]",
    khung("loi", ["<b>Chỉ báo cáo MAE tổng.</b> Các khu bị chặn giá có lỗi gấp đôi phần còn lại. Luôn chia lỗi theo nhóm có ý nghĩa."]))

c.mo_trang(5, "Ba bài tập. Đoán trước, rồi mới mở đáp án.")
c.bai("22.1", "Báo cáo bằng đô la", "Đổi MAE của baseline và mô hình cuối ra đô la.",
      "Khoảng 91 400 USD so với 28 900 USD: giảm 68%. Code ở ô ngay dưới.")
c.o('''
print(round(0.2887 * 100000), round(0.9139 * 100000))     # nhãn tính bằng 100 000 USD
''', "28870 91390")
c.bai("22.2", "Bỏ các khu bị chặn", "Huấn luyện lại chỉ trên khu có giá dưới 5,0, đo trên khu test dưới 5,0.",
      "0,269 so với 0,2745: tốt hơn một chút, nhưng mô hình mới không biết gì về nhà trên 500 000 USD. Code ở ô ngay dưới.")
c.o('''
tot = dict(learning_rate=0.05, max_iter=600, max_leaf_nodes=63, random_state=0)   # siêu tham số tốt nhất
k, kt = ytr < 5, yte < 5                                                         # bỏ khu bị chặn
m2 = HistGradientBoostingRegressor(**tot).fit(Xtr[k], ytr[k])                    # huấn luyện lại
print(round(mean_absolute_error(yte[kt], p[kt]), 4), round(mean_absolute_error(yte[kt], m2.predict(Xte[kt])), 4))   # mô hình gốc, mô hình mới
''', "0.2745 0.269")
c.bai("22.3", "Lỗi theo thu nhập", "Chia test thành 4 nhóm thu nhập, tính MAE và giá trung bình từng nhóm.",
      "Lỗi tuyệt đối tăng theo thu nhập (0,236 lên 0,342) nhưng lỗi tương đối giảm (19% xuống 11%). Code ở ô ngay dưới.")
c.o('''
q = pd.qcut(Xte["MedInc"], 4, labels=["thấp", "vừa thấp", "vừa cao", "cao"])         # 4 nhóm bằng nhau
print(pd.Series(np.abs(yte - p)).groupby(q, observed=True).mean().round(4).to_dict())  # MAE từng nhóm
print(pd.Series(yte).groupby(q, observed=True).mean().round(4).to_dict())              # giá trung bình từng nhóm
''', "{'thấp': 0.2364, 'vừa thấp': 0.2765, 'vừa cao': 0.3006, 'cao': 0.3415}\n{'thấp': 1.2147, 'vừa thấp': 1.7267, 'vừa cao': 2.161, 'cao': 3.1205}")

c.ghi(Path(__file__).resolve().parents[2] / "notebooks/ch22_du_an_phan_2.ipynb")
