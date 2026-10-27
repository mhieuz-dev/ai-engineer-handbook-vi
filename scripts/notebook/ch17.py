"""Dựng notebooks/ch17_cay_quyet_dinh.ipynb: python3 scripts/notebook/ch17.py"""
from pathlib import Path
from nblib import Chuong, khung

c = Chuong(17, "Cây quyết định", "ch17-cay-quyet-dinh",
           "Một chuỗi câu hỏi có hoặc không: Gini tính tay, độ sâu và overfitting, cây hồi quy, độ quan trọng đặc trưng, và vì sao một cây không ổn định.",
           ["Đọc cây và tính tay Gini để chọn câu hỏi.",
            "Hãm cây bằng độ sâu tối đa, chọn bằng cross-validation.",
            "Dùng cây cho hồi quy và đọc độ quan trọng đặc trưng.",
            "Thấy cây đổi cấu trúc khi đổi một ít dữ liệu."],
           [("Một chuỗi câu hỏi", "01-chuoi-cau-hoi"), ("Gini và cách chọn câu hỏi", "02-gini-va-chon-cau-hoi"),
            ("Độ sâu và overfitting", "03-do-sau-va-overfitting"), ("Cây hồi quy, độ quan trọng và tính bất ổn", "04-hoi-quy-va-do-quan-trong"), ("Bài tập", "05-bai-tap")])

c.mo_trang(1, "Cây của 10 bạn, và cây không cần chuẩn hóa.")
c.o('''
import numpy as np                                                  # tính toán
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor, export_text   # cây
X = np.array([[1, 7], [2, 6], [3, 8], [4, 7], [5, 6], [2, 7], [6, 8], [3, 5], [7, 7], [4, 6]], dtype=float)   # (giờ học, giờ ngủ)
y = (np.array([2, 4, 5, 7, 6, 3.5, 8.5, 4, 9, 6.5]) >= 5).astype(int)   # 1 là đạt
cay = DecisionTreeClassifier(random_state=0).fit(X, y)              # để cây mọc tự do
print(export_text(cay, feature_names=["gio", "ngu"]))               # in cây dạng chữ
print(cay.get_depth(), cay.get_n_leaves())                          # độ sâu, số lá
''', "|--- gio <= 3.50\n|   |--- ngu <= 7.50\n|   |   |--- class: 0\n|   |--- ngu >  7.50\n|   |   |--- class: 1\n|--- gio >  3.50\n|   |--- class: 1\n\n2 3")
c.o('''
from sklearn.datasets import load_breast_cancer                    # ung thư vú
from sklearn.model_selection import train_test_split, cross_val_score   # chia và cross-validation
from sklearn.preprocessing import StandardScaler                   # chuẩn hóa
dd = load_breast_cancer()                                          # 569 ca
Xb, yb = dd.data, 1 - dd.target                                    # 1 là ác tính
Xtr, Xte, ytr, yte = train_test_split(Xb, yb, test_size=0.25, random_state=0, stratify=yb)   # cách chia Chương 12
s = StandardScaler().fit(Xtr)                                      # bộ chuẩn hóa
m_goc = DecisionTreeClassifier(max_depth=3, random_state=0).fit(Xtr, ytr)              # dữ liệu gốc
m_chuan = DecisionTreeClassifier(max_depth=3, random_state=0).fit(s.transform(Xtr), ytr)   # dữ liệu đã chuẩn hóa
print((m_goc.predict(Xte) == m_chuan.predict(s.transform(Xte))).all())                 # dự đoán có trùng nhau không
''', "True",
    khung("vi-sao", ["Câu hỏi \"giá trị có nhỏ hơn ngưỡng không\" chỉ phụ thuộc thứ tự các giá trị. Chuẩn hóa giữ nguyên thứ tự, nên cây y hệt."],
          nhan="VÌ SAO LẠI TRÙNG NHAU 100%?"))

c.mo_trang(2, "Thử mọi câu hỏi, chọn câu làm Gini giảm nhiều nhất.")
c.o('''
gini = lambda v: 1 - sum(np.mean(v == k) ** 2 for k in (0, 1)) if len(v) else 0.0   # công thức (17.1)
ung_vien = []                                                  # mọi phép chia thử được
for j, ten in [(0, "gio"), (1, "ngu")]:                        # hai đặc trưng
    gt = np.unique(X[:, j])                                    # giá trị khác nhau, đã sắp xếp
    for t in (gt[:-1] + gt[1:]) / 2:                           # ngưỡng là trung điểm
        L, R = y[X[:, j] <= t], y[X[:, j] > t]                 # hai nhóm con
        g = (len(L) * gini(L) + len(R) * gini(R)) / len(y)     # Gini trung bình có trọng số (17.2)
        ung_vien.append((round(float(g), 4), ten, float(t), len(L), len(R)))   # lưu lại
print(round(gini(y), 4))                                       # Gini của nút gốc
for u in sorted(ung_vien)[:4]:                                 # bốn phép chia tốt nhất
    print(u)                                                   # (Gini, đặc trưng, ngưỡng, trái, phải)
''', "0.48\n(0.16, 'gio', 3.5, 5, 5)\n(0.1714, 'gio', 2.5, 3, 7)\n(0.3429, 'gio', 4.5, 7, 3)\n(0.4, 'gio', 1.5, 1, 9)")

c.mo_trang(3, "Độ sâu tối đa và cross-validation trên ung thư vú.")
c.o('''
for md in [1, 2, 3, 4, 5, None]:                                   # độ sâu tăng dần
    m = DecisionTreeClassifier(max_depth=md, random_state=0).fit(Xtr, ytr)   # huấn luyện
    cv = cross_val_score(DecisionTreeClassifier(max_depth=md, random_state=0), Xtr, ytr, cv=5).mean()   # cross-validation
    print(md, m.get_n_leaves(), round(m.score(Xtr, ytr), 4), round(cv, 4), round(m.score(Xte, yte), 4))   # lá, train, CV, test
''', "1 2 0.9249 0.9014 0.8741\n2 4 0.9507 0.9201 0.9231\n3 8 0.9742 0.9295 0.958\n4 13 0.993 0.9201 0.9441\n5 16 0.9953 0.9201 0.958\nNone 18 1.0 0.9178 0.9441",
    khung("doc", ["Cross-validation chọn độ sâu 3 (0,930). Từ độ sâu 4, train vẫn tăng tới 100% mà cross-validation giảm: overfitting."]))

c.mo_trang(4, "Cây hồi quy, độ quan trọng, tính bất ổn.")
c.o('''
from sklearn.datasets import load_diabetes                          # bộ của Chương 9
from sklearn.metrics import r2_score                                # R²
Xd, yd = load_diabetes(return_X_y=True, as_frame=True, scaled=False)   # đơn vị gốc
Xdtr, Xdte, ydtr, ydte = train_test_split(Xd, yd, test_size=0.2, random_state=42)   # cách chia Chương 9
for md in [2, 3, 5, None]:                                          # bốn độ sâu
    r = DecisionTreeRegressor(max_depth=md, random_state=0).fit(Xdtr, ydtr)   # cây hồi quy
    print(md, round(r2_score(ydte, r.predict(Xdte)), 4))            # R² test
m3 = DecisionTreeClassifier(max_depth=3, random_state=0).fit(Xtr, ytr)   # cây sâu 3 trên ung thư vú
qt = m3.feature_importances_                                       # độ quan trọng
o = np.argsort(qt)[::-1][:4]                                       # bốn đặc trưng quan trọng nhất
print([(str(dd.feature_names[i]), round(float(qt[i]), 4)) for i in o], int((qt > 0).sum()))   # tên, độ quan trọng, số đặc trưng được dùng
''', "2 0.2949\n3 0.3294\n5 0.2602\nNone -0.0063\n[('mean concave points', 0.7731), ('worst concavity', 0.0659), ('worst radius', 0.0653), ('mean texture', 0.037)] 7")
c.o('''
rng = np.random.default_rng(0)                                         # seed
for k in range(5):                                                     # năm lần thử
    idx = rng.choice(len(Xtr), len(Xtr) - 20, replace=False)           # bỏ ngẫu nhiên 20 ca
    t = DecisionTreeClassifier(random_state=0).fit(Xtr[idx], ytr[idx]).tree_   # cây không giới hạn
    goc, trai, phai = t.feature[0], t.feature[1], t.feature[t.children_right[0]]   # đặc trưng ở gốc và hai nút con
    print(k, dd.feature_names[goc], "|", dd.feature_names[trai], "|", dd.feature_names[phai])   # in tên
''', "0 mean concave points | worst radius | worst perimeter\n1 mean concave points | worst area | worst concavity\n2 mean concave points | worst radius | worst concavity\n3 mean concave points | worst radius | worst concavity\n4 mean concave points | worst radius | worst concavity",
    khung("thu", ["<b>1.</b> Bỏ 100 ca thay vì 20. Câu hỏi ở gốc còn giữ nguyên không?",
                  "<b>2.</b> Thêm min_samples_leaf=10 vào cây. Tầng hai có ổn định hơn không?"]))

c.mo_trang(5, "Ba bài tập. Tính tay trước, rồi mới mở đáp án.")
c.bai("17.1", "Câu hỏi về giờ ngủ", "Tính tay Gini của phép chia \"giờ ngủ ≤ 5,5\".",
      "Trái 1 bạn ($G = 0$), phải 9 bạn ($G \\approx 0{,}444$). Trung bình có trọng số 0,4: chỉ cắt riêng một điểm, nhóm còn lại vẫn lẫn lộn.")
c.bai("17.2", "Đi theo cây", "Đi theo cây để đoán bạn mới (3,4 giờ học; 6,3 giờ ngủ), so với KNN $k = 3$.",
      "Giờ học ≤ 3,5 rồi giờ ngủ ≤ 7,5: không đạt, \"chắc chắn\" 100%. KNN $k = 3$ đoán đạt. Code ở ô ngay dưới.")
c.o('''
print(cay.predict([[3.4, 6.3]]), cay.predict_proba([[3.4, 6.3]]))   # nhãn và xác suất của cây
''', "[0] [[1. 0.]]")
c.bai("17.3", "Entropy", "Tính entropy của nút gốc, hai nhóm con của \"giờ học ≤ 3,5\", và information gain.",
      "0,971; 0,722 và 0; information gain $\\approx 0{,}61$ bit. Code ở ô ngay dưới.")
c.o('''
H = lambda p: -sum(q * np.log2(q) for q in p if q > 0)                         # entropy theo bit
print(round(H([0.6, 0.4]), 4), round(H([0.2, 0.8]), 4), round(H([0.6, 0.4]) - 0.5 * H([0.2, 0.8]), 4))   # gốc, nhóm trái, information gain
''', "0.971 0.7219 0.61")

c.ghi(Path(__file__).resolve().parents[2] / "notebooks/ch17_cay_quyet_dinh.ipynb")
