"""Dựng notebooks/ch18_ensemble.ipynb: python3 scripts/notebook/ch18.py"""
from pathlib import Path
from nblib import Chuong, khung

c = Chuong(18, "Ensemble", "ch18-ensemble",
           "Gộp nhiều cây thành một mô hình mạnh: bagging, random forest, OOB score, gradient boosting tính tay, và so sánh trên dữ liệu thật.",
           ["Giải thích vì sao trung bình nhiều mô hình giảm variance.",
            "Dùng bagging và random forest, đọc OOB score.",
            "Tính tay gradient boosting và kiểm bằng thư viện.",
            "So sánh các ensemble trên ung thư vú và tiểu đường."],
           [("Trí tuệ đám đông", "01-tri-tue-dam-dong"), ("Bagging và random forest", "02-bagging-random-forest"),
            ("Gradient boosting", "03-gradient-boosting"), ("So sánh trên dữ liệu thật", "04-so-sanh-tren-du-lieu-that"), ("Bài tập", "05-bai-tap")],
           thoi_gian="khoảng 1 phút")

c.mo_trang(1, "Lý thuyết: variance của trung bình. Code bắt đầu ở trang 2.")
c.mo_trang(2, "Tương quan giữa các cây, thêm cây, OOB score.")
c.o('''
import numpy as np                                                       # tính toán
from sklearn.datasets import load_breast_cancer, make_moons, load_diabetes   # ba bộ dữ liệu
from sklearn.model_selection import train_test_split, cross_val_score    # chia, cross-validation
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor   # cây
from sklearn.ensemble import (BaggingClassifier, RandomForestClassifier, GradientBoostingClassifier,   # ensemble phân loại
                              HistGradientBoostingClassifier, RandomForestRegressor,              # và hồi quy
                              GradientBoostingRegressor, HistGradientBoostingRegressor)
dd = load_breast_cancer()                                                # ung thư vú
Xb, yb = dd.data, 1 - dd.target                                          # 1 là ác tính
Xtr, Xte, ytr, yte = train_test_split(Xb, yb, test_size=0.25, random_state=0, stratify=yb)   # cách chia Chương 12
for ten, m in [("bagging", BaggingClassifier(DecisionTreeClassifier(), n_estimators=100, random_state=0)),   # hai ensemble
               ("random forest", RandomForestClassifier(n_estimators=100, random_state=0))]:
    m.fit(Xtr, ytr)                                                      # huấn luyện 100 cây
    P = np.array([cay.predict_proba(Xte)[:, 1] for cay in m.estimators_])   # xác suất của từng cây
    tq = np.corrcoef(P)[np.triu_indices(len(P), 1)]                      # tương quan mọi cặp cây
    rieng = np.mean([cay.score(Xte, yte) for cay in m.estimators_])      # độ chính xác của một cây
    print(ten, round(float(tq.mean()), 4), round(float(rieng), 4), round(m.score(Xte, yte), 4))   # tương quan, một cây, cả rừng
''', "bagging 0.8242 0.9266 0.958\nrandom forest 0.7955 0.9183 0.958",
    khung("doc", ["Mỗi cây riêng lẻ đúng khoảng 92%, gộp 100 cây được 95,8%. Random forest làm các cây kém đi một chút nhưng bớt tương quan."]))
c.o('''
Xm, ym = make_moons(300, noise=0.3, random_state=0)                    # hai vầng trăng
a, b, c_, e = train_test_split(Xm, ym, test_size=0.3, random_state=0)  # 210 train, 90 test
for n in [1, 10, 100, 500]:                                            # số cây tăng dần
    rf = RandomForestClassifier(n_estimators=n, random_state=0).fit(a, c_)   # rừng n cây
    print(n, round(rf.score(a, c_), 4), round(rf.score(b, e), 4))      # train, test
rf = RandomForestClassifier(n_estimators=300, random_state=0, oob_score=True).fit(Xtr, ytr)   # bật OOB
print(round(rf.oob_score_, 4), round(cross_val_score(RandomForestClassifier(n_estimators=300, random_state=0), Xtr, ytr, cv=5).mean(), 4), round(rf.score(Xte, yte), 4))   # OOB, CV, test
''', "1 0.9667 0.8444\n10 1.0 0.9111\n100 1.0 0.9333\n500 1.0 0.9333\n0.9577 0.9554 0.951",
    khung("vi-sao", ["Thêm cây chỉ làm số hạng (1 - ρ)σ²/n nhỏ đi, không bao giờ làm variance tăng. Test tăng tới 100 cây rồi đứng yên."],
          nhan="VÌ SAO LẠI KHÔNG OVERFIT KHI THÊM CÂY?"))

c.mo_trang(3, "Gradient boosting tính tay trên 10 bạn.")
c.o('''
gio = np.array([1, 2, 3, 4, 5, 2, 6, 3, 7, 4.0])               # Bảng 4.1
diem = np.array([2, 4, 5, 7, 6, 3.5, 8.5, 4, 9, 6.5])           # điểm thi
X1 = gio[:, None]                                              # bảng một cột
f = np.full(10, diem.mean())                                   # f0: trung bình 5,55
print(0, round(float(np.mean((diem - f) ** 2)), 4))            # MSE ban đầu
for k in range(1, 4):                                          # ba vòng
    goc = DecisionTreeRegressor(max_depth=1).fit(X1, diem - f) # gốc cây khớp phần dư
    t = goc.tree_                                              # cấu trúc cây
    f = f + 0.5 * goc.predict(X1)                              # cộng với learning rate 0,5
    print(k, t.threshold[0], t.value[1:, 0, 0].round(4), round(float(np.mean((diem - f) ** 2)), 4))   # ngưỡng, hai lá, MSE
''', "0 4.5725\n1 3.5 [-1.85  1.85] 2.0056\n2 5.5 [-0.5687  2.275 ] 1.0352\n3 1.5 [-2.3406  0.2601] 0.5787",
    khung("truc-giac", ["Mỗi gốc cây chỉ hỏi một câu, nhưng nhắm đúng chỗ còn sai nhiều nhất: vòng 2 tách G và I đang bị đoán thấp, vòng 3 sửa bạn A đang bị đoán cao."]))

c.mo_trang(4, "Năm mô hình cây trên ung thư vú, bốn trên tiểu đường.")
c.o('''
ung_vien = [("cây sâu 3", DecisionTreeClassifier(max_depth=3, random_state=0)),            # cây đơn
            ("bagging", BaggingClassifier(DecisionTreeClassifier(), n_estimators=100, random_state=0)),   # bagging
            ("random forest", RandomForestClassifier(n_estimators=300, random_state=0)),    # rừng
            ("gradient boosting", GradientBoostingClassifier(random_state=0)),             # boosting
            ("hist gradient boosting", HistGradientBoostingClassifier(random_state=0))]    # boosting nhanh
for ten, m in ung_vien:                                                                   # từng mô hình
    cv = cross_val_score(m, Xtr, ytr, cv=5).mean()                                        # cross-validation
    print(ten, round(cv, 4), round(m.fit(Xtr, ytr).score(Xte, yte), 4))                   # CV, test
''', "cây sâu 3 0.9295 0.958\nbagging 0.9483 0.958\nrandom forest 0.9554 0.951\ngradient boosting 0.9507 0.972\nhist gradient boosting 0.9601 0.979")
c.o('''
from sklearn.metrics import r2_score                                       # R²
Xd, yd = load_diabetes(return_X_y=True, as_frame=True, scaled=False)       # bộ của Chương 9
Xdtr, Xdte, ydtr, ydte = train_test_split(Xd, yd, test_size=0.2, random_state=42)   # cách chia Chương 9
for ten, m in [("cây sâu 3", DecisionTreeRegressor(max_depth=3, random_state=0)),   # bốn mô hình
               ("random forest", RandomForestRegressor(n_estimators=300, random_state=0)),    # rừng
               ("gradient boosting", GradientBoostingRegressor(random_state=0)),             # boosting
               ("hist gradient boosting", HistGradientBoostingRegressor(random_state=0))]:   # boosting nhanh
    print(ten, round(r2_score(ydte, m.fit(Xdtr, ydtr).predict(Xdte)), 4))  # R² test
''', "cây sâu 3 0.3294\nrandom forest 0.4251\ngradient boosting 0.451\nhist gradient boosting 0.3866",
    khung("loi", ["<b>Bỏ qua mô hình tuyến tính.</b> Hồi quy tuyến tính đạt R² 0,4526 trên cùng tập test, ngang mô hình cây tốt nhất. Luôn thử mốc đơn giản trước."]))

c.mo_trang(5, "Ba bài tập. Tính tay trước, rồi mới mở đáp án.")
c.bai("18.1", "Mẫu ngoài túi", "Tính $(1 - 1/n)^n$ với $n = 10$, 100, 1000 và so với $e^{-1}$.",
      "0,3487; 0,366; 0,3677, tiến về $e^{-1} \\approx 0{,}3679$. Code ở ô ngay dưới.")
c.o('''
print([round((1 - 1 / n) ** n, 4) for n in [10, 100, 1000]], round(np.exp(-1), 4))   # tỷ lệ ngoài túi và giới hạn
''', "[0.3487, 0.366, 0.3677] 0.3679")
c.bai("18.2", "Sàn của variance", "Với $\\sigma^2 = 1$ và 100 mô hình, tính variance của trung bình khi $\\rho = 0{,}8$ và $\\rho = 0{,}3$.",
      "0,802 và 0,307. Hạ tương quan có tác dụng lớn hơn thêm mô hình. Code ở ô ngay dưới.")
c.o('''
print(0.8 + 0.2 / 100, 0.3 + 0.7 / 100)    # công thức (18.1)
''', "0.802 0.307")
c.bai("18.3", "Kiểm boosting tự viết", "Dùng `GradientBoostingRegressor` với learning rate 0,5, độ sâu 1 để kiểm MSE sau 1, 3, 10 vòng.",
      "2,0056; 0,5787; 0,1174, khớp từng chữ số với vòng lặp tự viết. Code ở ô ngay dưới.")
c.o('''
for n in [1, 3, 10]:                                                          # ba số vòng
    g = GradientBoostingRegressor(n_estimators=n, learning_rate=0.5, max_depth=1, random_state=0).fit(X1, diem)   # boosting thư viện
    print(n, round(float(np.mean((diem - g.predict(X1)) ** 2)), 4))           # MSE trên 10 bạn
''', "1 2.0056\n3 0.5787\n10 0.1174")

c.ghi(Path(__file__).resolve().parents[2] / "notebooks/ch18_ensemble.ipynb")
