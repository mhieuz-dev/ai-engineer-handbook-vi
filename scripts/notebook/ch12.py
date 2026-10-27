"""Dựng notebooks/ch12_danh_gia_mo_hinh.ipynb: python3 scripts/notebook/ch12.py"""
from pathlib import Path
from nblib import Chuong, khung

c = Chuong(12, "Đánh giá mô hình", "ch12-danh-gia-mo-hinh",
           "Ma trận nhầm lẫn, precision, recall, F1, ngưỡng, ROC và precision-recall, rồi khoảng tin cậy bằng bootstrap, trên 569 ca ung thư vú thật.",
           ["Đọc ma trận nhầm lẫn và thấy cái bẫy của độ chính xác.",
            "Tính precision, recall, F1 và chọn ngưỡng theo cái giá của từng kiểu sai.",
            "Đọc ROC AUC, average precision, và biết khi nào AUC đánh lừa.",
            "Báo cáo kết quả kèm khoảng tin cậy bootstrap."],
           [("Ma trận nhầm lẫn và cái bẫy accuracy", "01-ma-tran-nham-lan"), ("Precision, recall và F1", "02-precision-recall-f1"),
            ("Ngưỡng, ROC và AUC", "03-nguong-roc-auc"), ("Thước đo hồi quy và khoảng tin cậy", "04-hoi-quy-va-khoang-tin-cay"), ("Bài tập", "05-bai-tap")])

c.mo_trang(1, "Dữ liệu ung thư vú, baseline và ma trận nhầm lẫn.")
c.o('''
import numpy as np                                         # tính toán
from sklearn.datasets import load_breast_cancer            # 569 khối u
from sklearn.model_selection import train_test_split       # chia dữ liệu
from sklearn.pipeline import make_pipeline                 # ghép chuẩn hóa và mô hình
from sklearn.preprocessing import StandardScaler           # chuẩn hóa
from sklearn.linear_model import LogisticRegression        # mô hình
from sklearn.dummy import DummyClassifier                  # baseline
from sklearn.metrics import (accuracy_score, confusion_matrix, precision_score,   # các thước đo
                             recall_score, f1_score, roc_auc_score, average_precision_score)
d = load_breast_cancer()                                   # nạp dữ liệu
X, y = d.data, 1 - d.target                                # đảo nhãn: 1 là ác tính
print(X.shape, np.bincount(y))                             # 357 lành, 212 ác
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.25, random_state=0, stratify=y)   # giữ tỷ lệ hai lớp
print(len(yte), yte.sum())                                 # số ca test và số ca ác tính
''', "(569, 30) [357 212]\n143 53")
c.o('''
du = DummyClassifier(strategy="most_frequent").fit(Xtr, ytr)   # luôn đoán lành
p0 = du.predict(Xte)                                           # dự đoán của baseline
print(round(accuracy_score(yte, p0), 4), recall_score(yte, p0))   # độ chính xác cao, nhưng bỏ sót hết
m = make_pipeline(StandardScaler(), LogisticRegression()).fit(Xtr, ytr)   # hồi quy logistic
p = m.predict(Xte)                                             # nhãn đoán, ngưỡng 0,5
print(confusion_matrix(yte, p))                                # hàng là thật, cột là đoán
print(round(accuracy_score(yte, p), 4))                        # độ chính xác
''', "0.6294 0.0\n[[90  0]\n [ 2 51]]\n0.986",
    khung("doc", ["Baseline đạt 63% mà không bắt được ca ác tính nào. Mô hình đạt 98,6%, nhưng vẫn bỏ sót 2 ca ác tính (hàng dưới, cột trái)."]))

c.mo_trang(2, "Precision, recall, F1, và dữ liệu chỉ 1% dương tính.")
c.o('''
print(round(precision_score(yte, p), 4), round(recall_score(yte, p), 4), round(f1_score(yte, p), 4))   # ba thước đo
from sklearn.datasets import make_classification                                  # dữ liệu mô phỏng
Xm, ym = make_classification(n_samples=10000, n_features=10, weights=[0.99], flip_y=0, random_state=0)   # đúng 1% dương tính
a, b, c_, e = train_test_split(Xm, ym, test_size=0.3, random_state=0, stratify=ym)   # chia giữ tỷ lệ
mm = LogisticRegression(max_iter=1000).fit(a, c_)                                   # huấn luyện
pm = mm.predict(b)                                                                  # nhãn đoán
print(e.sum(), len(e))                                                              # 30 ca dương trong 3000
print(round(accuracy_score(e, pm), 4), round(precision_score(e, pm), 4), round(recall_score(e, pm), 4), round(f1_score(e, pm), 4))  # độ chính xác cao, recall thấp
''', "1.0 0.9623 0.9808\n30 3000\n0.9903 0.6 0.1 0.1714",
    khung("loi", ["<b>Báo cáo độ chính xác cho dữ liệu mất cân bằng.</b> 99,03% nghe tuyệt vời, nhưng mô hình chỉ bắt được 3 trên 30 ca dương."]))

c.mo_trang(3, "Đổi ngưỡng, ROC AUC và average precision.")
c.o('''
pr = m.predict_proba(Xte)[:, 1]                       # xác suất ác tính
for t in [0.5, 0.3, 0.1, 0.05]:                       # bốn ngưỡng
    q = (pr >= t).astype(int)                         # nhãn với ngưỡng t
    print(t, confusion_matrix(yte, q).ravel(), round(precision_score(yte, q), 4), round(recall_score(yte, q), 4))  # TN FP FN TP, precision, recall
print(round(roc_auc_score(yte, pr), 4))               # AUC của ung thư vú
prm = mm.predict_proba(b)[:, 1]                       # xác suất trên dữ liệu 1%
print(round(roc_auc_score(e, prm), 4), round(average_precision_score(e, prm), 4))   # AUC đẹp, AP thấp
''', "0.5 [90  0  2 51] 1.0 0.9623\n0.3 [84  6  2 51] 0.8947 0.9623\n0.1 [79 11  0 53] 0.8281 1.0\n0.05 [75 15  0 53] 0.7794 1.0\n0.9958\n0.9075 0.2368",
    khung("vi-sao", ["FPR chia cho 2970 ca âm, nên 100 báo động nhầm gần như không đổi đường ROC. Precision chia cho số lần báo động, nên 100 báo động nhầm so với 30 ca dương đè bẹp nó."],
          nhan="VÌ SAO LẠI LÀ AUC 0,91 MÀ AP CHỈ 0,24?"))

c.mo_trang(4, "MAE, RMSE và khoảng tin cậy bootstrap.")
c.o('''
from sklearn.datasets import load_diabetes                         # bộ dữ liệu của Chương 9
from sklearn.linear_model import LinearRegression                  # hồi quy tuyến tính
from sklearn.metrics import mean_absolute_error, mean_squared_error   # thước đo hồi quy
Xd, yd = load_diabetes(return_X_y=True, as_frame=True, scaled=False)  # đơn vị gốc
Xdtr, Xdte, ydtr, ydte = train_test_split(Xd, yd, test_size=0.2, random_state=42)   # cách chia của Chương 9
pd_ = LinearRegression().fit(Xdtr, ydtr).predict(Xdte)             # dự đoán trên test
loi = np.abs(ydte - pd_)                                           # sai số tuyệt đối từng ca
print(round(mean_absolute_error(ydte, pd_), 2), round(mean_squared_error(ydte, pd_) ** 0.5, 2))   # MAE và RMSE
print(round(np.median(loi), 2), round(loi.max(), 2))               # sai số điển hình và lớn nhất
''', "42.79 53.85\n37.99 154.49")
c.o('''
dung = (m.predict(Xte) == yte).astype(float)                      # 1 nếu đoán đúng ca đó
rng = np.random.default_rng(0)                                    # seed
bs = [rng.choice(dung, len(dung)).mean() for _ in range(10000)]   # 10 000 lần lấy mẫu có hoàn lại
print(round(dung.mean(), 4), np.percentile(bs, [2.5, 97.5]).round(4))   # độ chính xác và khoảng tin cậy 95%
''', "0.986 [0.965 1.   ]",
    khung("truc-giac", ["143 ca test như 143 lần tung đồng xu. Bootstrap giả lập việc lấy một bộ test khác để biết con số 98,6% chắc chắn tới đâu."]))

c.mo_trang(5, "Ba bài tập. Tính tay trước, rồi mới mở đáp án.")
c.bai("12.1", "Tính tay ở ngưỡng 0,1", "Từ TN 79, FP 11, FN 0, TP 53, tính độ chính xác, precision, recall, F1.",
      "Độ chính xác $132/143 \\approx 0{,}923$, precision $53/64 \\approx 0{,}828$, recall 1, F1 $\\approx 0{,}906$. Code ở ô ngay dưới.")
c.o('''
q = (pr >= 0.1).astype(int)          # ngưỡng 0,1
print(round(f1_score(yte, q), 4))    # F1
''', "0.906")
c.bai("12.2", "Chọn ngưỡng đúng cách", "Tách validation từ `Xtr`, chọn ngưỡng lớn nhất đạt recall ít nhất 0,97 trên validation, rồi đo trên test.",
      "Ngưỡng 0,57: recall 0,975 trên validation nhưng 0,9434 trên test. Một ca ác tính trong validation bị chấm 0,0019, không ngưỡng hợp lý nào bắt được. Code ở ô ngay dưới.")
c.o('''
a2, v2, ya2, yv2 = train_test_split(Xtr, ytr, test_size=0.25, random_state=0, stratify=ytr)   # tách validation
pv = make_pipeline(StandardScaler(), LogisticRegression()).fit(a2, ya2).predict_proba(v2)[:, 1]   # xác suất trên validation
ts = np.round(np.arange(0.01, 1.0, 0.01), 2)                                              # các ngưỡng thử
t = max(t for t in ts if recall_score(yv2, (pv >= t).astype(int)) >= 0.97)                # ngưỡng lớn nhất đạt recall 0,97
qt = (m.predict_proba(Xte)[:, 1] >= t).astype(int)                                        # áp lên test
print(len(yv2), yv2.sum(), t)                                                             # cỡ validation và ngưỡng chọn
print(confusion_matrix(yte, qt).ravel(), round(precision_score(yte, qt), 4), round(recall_score(yte, qt), 4))   # kết quả test
''', "107 40 0.57\n[90  0  3 50] 1.0 0.9434")
c.bai("12.3", "AUC bằng cách đếm cặp", "Hai mẫu dương có điểm 0,9 và 0,4; hai mẫu âm có điểm 0,6 và 0,2. Tính AUC bằng cách đếm cặp.",
      "3 trên 4 cặp (dương, âm) xếp đúng: AUC 0,75. Code ở ô ngay dưới.")
c.o('''
print(roc_auc_score([1, 1, 0, 0], [0.9, 0.4, 0.6, 0.2]))   # nhãn thật, điểm số
''', "0.75")

c.ghi(Path(__file__).resolve().parents[2] / "notebooks/ch12_danh_gia_mo_hinh.ipynb")
