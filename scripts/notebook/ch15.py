"""Dựng notebooks/ch15_naive_bayes.ipynb: python3 scripts/notebook/ch15.py"""
from pathlib import Path
from nblib import Chuong, khung

c = Chuong(15, "Naive Bayes", "ch15-naive-bayes",
           "Phân loại tin nhắn rác bằng cách đếm từ: định lý Bayes, giả định ngây thơ, làm trơn Laplace, tính bằng log, và cái giá của giả định độc lập.",
           ["Tính tay Naive Bayes từ bảng đếm từ.",
            "Hiểu vì sao cần làm trơn Laplace và tính bằng log.",
            "Dùng CountVectorizer với MultinomialNB, đọc feature_log_prob_.",
            "Dùng GaussianNB và thấy nó quá tự tin khi đặc trưng tương quan."],
           [("Bayes cho phân loại", "01-bayes-cho-phan-loai"), ("Đếm từ và làm trơn Laplace", "02-tinh-tay"),
            ("Tính bằng log và đọc mô hình", "03-log-va-scikit-learn"), ("Gaussian Naive Bayes và cái giá của giả định", "04-gaussian-nb"), ("Bài tập", "05-bai-tap")])

c.mo_trang(1, "Định lý Bayes và giả định độc lập. Phần này chỉ có lý thuyết, code bắt đầu ở trang 2.")
c.mo_trang(2, "Đếm từ, rồi so có và không có làm trơn Laplace.")
c.o('''
import numpy as np                                                   # tính toán
from sklearn.feature_extraction.text import CountVectorizer          # tách từ và đếm
from sklearn.naive_bayes import MultinomialNB, GaussianNB            # hai loại Naive Bayes
tin = ["trúng thưởng iphone miễn phí", "nhận quà miễn phí ngay",     # tin rác
       "khuyến mãi trúng thưởng lớn", "bấm link nhận tiền thưởng",   # tin rác
       "hẹn gặp lúc ba giờ", "gửi tài liệu họp ngày mai",            # tin thường
       "mai đi ăn trưa không", "tài liệu môn học đã gửi"]            # tin thường
nhan = np.array([1, 1, 1, 1, 0, 0, 0, 0])                            # 1 là rác
cv = CountVectorizer()                                               # bộ đếm từ
Xt = cv.fit_transform(tin)                                           # ma trận 8 tin nhân 32 từ
print(Xt.shape, Xt[nhan == 1].sum(), Xt[nhan == 0].sum())            # kích thước, tổng số từ mỗi lớp
for a in [1e-10, 1.0]:                                               # gần như không làm trơn, và Laplace
    m = MultinomialNB(alpha=a, force_alpha=True).fit(Xt, nhan)       # huấn luyện là đếm
    print(a, m.predict_proba(cv.transform(["nhận thưởng họp"])).round(4))   # [P(thường), P(rác)]
''', "(8, 32) 20 22\n1e-10 [[0. 1.]]\n1.0 [[0.1295 0.8705]]",
    khung("doc", ["Không làm trơn: \"nhận\" và \"thưởng\" chưa từng có trong tin thường nên P(thường) = 0, mô hình chắc chắn 100%. Có làm trơn: 87%, khớp tính tay."]))

c.mo_trang(3, "Tràn số, log xác suất, đọc mô hình.")
c.o('''
print((1 / 52) ** 200, 200 * np.log(1 / 52))             # tích 200 xác suất nhỏ tràn về 0; tổng log thì không
m = MultinomialNB(alpha=1.0).fit(Xt, nhan)               # làm trơn Laplace
v = cv.get_feature_names_out()                           # 32 từ
lp = m.feature_log_prob_                                 # log P(từ | lớp), shape (2, 32)
print(np.exp(m.class_log_prior_).round(4), lp[1][list(v).index("thưởng")].round(4), round(float(np.log(4 / 52)), 4))   # tỷ lệ nền, log P(thưởng | rác)
chenh = lp[1] - lp[0]                                    # bằng chứng của từng từ
o = np.argsort(chenh)                                    # xếp tăng dần
print([(v[i], float(chenh[i].round(4))) for i in o[-3:]])     # nghiêng về rác nhất
print([(v[i], float(chenh[i].round(4))) for i in o[:3]])      # nghiêng về thường nhất
print(m.predict_proba(cv.transform(["miễn phí tài liệu"])).round(4))   # số đếm đối xứng mà không 50-50
''', "0.0 -790.2487437162854\n[0.5 0.5] -2.5649 -2.5649\n[('nhận', 1.1364), ('trúng', 1.1364), ('thưởng', 1.424)]\n[('gửi', -1.0609), ('mai', -1.0609), ('liệu', -1.0609)]\n[[0.4623 0.5377]]",
    khung("vi-sao", ["Tin rác có 20 từ, tin thường 22 từ. Làm trơn chia cho 52 và 54, nên mỗi từ của lớp rác được lợi một chút: (54/52)⁴ ≈ 1,163."],
          nhan="VÌ SAO LẠI LÀ 0,5377 MÀ KHÔNG PHẢI 0,5?"))

c.mo_trang(4, "Gaussian Naive Bayes trên giờ học và trên ung thư vú.")
c.o('''
gio = np.array([1, 2, 2, 3, 3, 4, 4, 5, 6, 7.0])         # Bảng 11.1
do = np.array([0, 0, 1, 0, 0, 1, 0, 1, 1, 1])            # 1 là đỗ
g = GaussianNB().fit(gio[:, None], do)                   # mỗi lớp một phân phối chuẩn
print(g.theta_.ravel(), g.var_.ravel().round(4), g.predict_proba([[3.5]]).round(4))   # trung bình, phương sai, xác suất ở 3,5 giờ
''', "[2.6 4.8] [1.04 2.96] [[0.6033 0.3967]]")
c.o('''
from sklearn.datasets import load_breast_cancer                  # ung thư vú
from sklearn.model_selection import train_test_split             # chia dữ liệu
from sklearn.linear_model import LogisticRegression              # để so sánh
from sklearn.pipeline import make_pipeline                       # ghép bước
from sklearn.preprocessing import StandardScaler                 # chuẩn hóa
dd = load_breast_cancer()                                        # 569 ca
Xb, yb = dd.data, 1 - dd.target                                  # 1 là ác tính
a, b, c_, e = train_test_split(Xb, yb, test_size=0.25, random_state=0, stratify=yb)   # cách chia Chương 12
gb = GaussianNB().fit(a, c_)                                     # Gaussian NB
print(round(gb.score(b, e), 4))                                  # độ chính xác test
print(round(np.corrcoef(Xb[:, 0], Xb[:, 2])[0, 1], 4), dd.feature_names[[0, 2]])   # bán kính và chu vi gần như trùng nhau
pg = gb.predict_proba(b)[:, 1]                                   # xác suất của Naive Bayes
pl = make_pipeline(StandardScaler(), LogisticRegression()).fit(a, c_).predict_proba(b)[:, 1]   # xác suất của hồi quy logistic
print(round(float(np.mean((pg > 0.01) & (pg < 0.99))), 4), round(float(np.mean((pl > 0.01) & (pl < 0.99))), 4))   # tỷ lệ ca có xác suất ở vùng giữa
''', "0.9161\n0.9979 ['mean radius' 'mean perimeter']\n0.0629 0.3007",
    khung("loi", ["<b>Tin con số xác suất của Naive Bayes.</b> Chỉ 6% số ca nằm giữa 0,01 và 0,99: mô hình quá tự tin vì đếm cùng một bằng chứng nhiều lần."]))

c.mo_trang(5, "Ba bài tập. Tính tay trước, rồi mới mở đáp án.")
c.bai("15.1", "Một tin rõ ràng", "Tính tay xác suất \"nhận thưởng miễn phí\" là rác.",
      "Tỷ số $108 \\times (54/52)^4 \\approx 125{,}6$, xác suất rác $\\approx 0{,}9921$. Code ở ô ngay dưới.")
c.o('''
print(m.predict_proba(cv.transform(["nhận thưởng miễn phí"])).round(4))   # bốn bằng chứng của rác
''', "[[0.0079 0.9921]]")
c.bai("15.2", "Tỷ lệ nền thật", "Tính lại xác suất \"nhận thưởng họp\" là rác khi chỉ 10% tin nhắn là rác.",
      "$6{,}7195 \\times 0{,}1/0{,}9 \\approx 0{,}7466$, xác suất rác $\\approx 0{,}4275$: kết luận đảo ngược. Code ở ô ngay dưới.")
c.o('''
m10 = MultinomialNB(alpha=1.0, class_prior=[0.9, 0.1]).fit(Xt, nhan)    # thứ tự lớp: thường, rác
print(m10.predict_proba(cv.transform(["nhận thưởng họp"])).round(4))      # cùng bằng chứng, tỷ lệ nền khác
''', "[[0.5725 0.4275]]")
c.bai("15.3", "Gaussian NB tự tính", "Từ trung bình và phương sai của mỗi lớp, tính tay mật độ tại 3,5 giờ.",
      "Lớp trượt 0,265, lớp đỗ 0,174, xác suất đỗ $\\approx 0{,}397$. Code ở ô ngay dưới.")
c.o('''
for cl in [0, 1]:                                         # hai lớp
    xg = gio[do == cl]                                    # giờ học của lớp đó
    mu, var = xg.mean(), xg.var()                         # trung bình, phương sai chia n
    print(cl, mu, round(var, 4), round(np.exp(-(3.5 - mu) ** 2 / (2 * var)) / np.sqrt(2 * np.pi * var), 4))   # mật độ chuẩn tại 3,5
''', "0 2.6 1.04 0.265\n1 4.8 2.96 0.1743")

c.ghi(Path(__file__).resolve().parents[2] / "notebooks/ch15_naive_bayes.ipynb")
