"""Dựng notebooks/ch20_giam_chieu.ipynb: python3 scripts/notebook/ch20.py"""
from pathlib import Path
from nblib import Chuong, khung

c = Chuong(20, "Giảm chiều", "ch20-giam-chieu",
           "PCA tính tay trên bốn điểm, chọn số chiều bằng phương sai giải thích, PCA trong Pipeline, và t-SNE để nhìn 64 chiều trên mặt phẳng.",
           ["Tính tay PCA: thành phần chính, hình chiếu, tái tạo.",
            "Chọn số chiều bằng phương sai tích lũy.",
            "Dùng PCA trong Pipeline mà không mất độ chính xác.",
            "Dùng t-SNE để nhìn dữ liệu và biết giới hạn của nó."],
           [("Vì sao giảm chiều", "01-vi-sao-giam-chieu"), ("PCA tính tay", "02-pca-tinh-tay"),
            ("Chọn số chiều và PCA trong Pipeline", "03-chon-so-chieu"), ("t-SNE để nhìn dữ liệu", "04-tsne"), ("Bài tập", "05-bai-tap")],
           runtime="CPU là đủ. t-SNE có thể cho hình hơi khác giữa các phiên bản scikit-learn")

c.mo_trang(1, "Lý thuyết. Code bắt đầu ở trang 2.")
c.mo_trang(2, "PCA trên bốn điểm.")
c.o('''
import numpy as np                                   # tính toán
from sklearn.decomposition import PCA                # PCA
D = np.array([[1, 2], [2, 1], [3, 4], [4, 3]], dtype=float)   # bốn bạn A, B, C, D
p2 = PCA(2).fit(D)                                   # giữ cả hai thành phần
print(p2.mean_, p2.explained_variance_.round(4), p2.explained_variance_ratio_.round(4))   # trung bình, phương sai (chia n - 1), tỷ lệ
p1 = PCA(1).fit(D)                                   # chỉ giữ thành phần thứ nhất
z = p1.transform(D)                                  # chiếu xuống 1 chiều
print(np.abs(z.ravel()).round(4))                    # độ lớn tọa độ mới
print(p1.inverse_transform(z).round(4))              # tái tạo lại 2 chiều
''', "[2.5 2.5] [2.6667 0.6667] [0.8 0.2]\n[1.4142 1.4142 1.4142 1.4142]\n[[1.5 1.5]\n [1.5 1.5]\n [3.5 3.5]\n [3.5 3.5]]",
    khung("vi-sao", ["Chương 5 chia n = 4 nên ra trị riêng 2 và 0,5. scikit-learn chia n - 1 = 3 nên ra 2,67 và 0,67. Tỷ lệ 0,8 và 0,2 thì như nhau."],
          nhan="VÌ SAO LẠI LÀ 2,67 MÀ KHÔNG PHẢI 2?"))

c.mo_trang(3, "Phương sai tích lũy và PCA trong Pipeline.")
c.o('''
from sklearn.datasets import load_breast_cancer, load_digits     # hai bộ dữ liệu
from sklearn.preprocessing import StandardScaler                 # chuẩn hóa
dd = load_breast_cancer()                                        # 30 đặc trưng
Xb, yb = dd.data, 1 - dd.target                                  # 1 là ác tính
pc = PCA().fit(StandardScaler().fit_transform(Xb))               # đủ 30 thành phần
tich_luy = np.cumsum(pc.explained_variance_ratio_)               # phương sai tích lũy
print(pc.explained_variance_ratio_[:3].round(4), tich_luy[[0, 1, 2, 4, 9]].round(4), int(np.argmax(tich_luy >= 0.95)) + 1)   # 3 thành phần đầu, tích lũy, số thành phần cho 95%
dg = load_digits()                                               # 1797 ảnh 8 x 8
cd = np.cumsum(PCA().fit(dg.data).explained_variance_ratio_)     # tích lũy trên 64 điểm ảnh
print(dg.data.shape, cd[[1, 9, 19, 39]].round(4), int(np.argmax(cd >= 0.9)) + 1)   # kích thước, tích lũy, số thành phần cho 90%
''', "[0.4427 0.1897 0.0939] [0.4427 0.6324 0.7264 0.8473 0.9516] 10\n(1797, 64) [0.2851 0.7382 0.8943 0.9882] 21")
c.o('''
from sklearn.pipeline import make_pipeline                           # ghép bước
from sklearn.linear_model import LogisticRegression                  # mô hình
from sklearn.model_selection import train_test_split, cross_val_score   # chia, cross-validation
Xtr, Xte, ytr, yte = train_test_split(Xb, yb, test_size=0.25, random_state=0, stratify=yb)   # cách chia Chương 12
for k in [1, 2, 5, 10, 30]:                                          # số thành phần giữ lại
    pl = make_pipeline(StandardScaler(), PCA(k), LogisticRegression(max_iter=1000))   # chuẩn hóa, PCA, hồi quy logistic
    print(k, round(cross_val_score(pl, Xtr, ytr, cv=5).mean(), 4), round(pl.fit(Xtr, ytr).score(Xte, yte), 4))   # CV, test
''', "1 0.9249 0.8951\n2 0.9531 0.9371\n5 0.9718 0.9441\n10 0.9812 0.965\n30 0.9812 0.986",
    khung("doc", ["10 thành phần cho cross-validation 0,981, đúng bằng 30 thành phần. Giảm một phần ba số chiều mà không mất gì trên cross-validation."]))

c.mo_trang(4, "PCA và t-SNE trên chữ số viết tay.")
c.o('''
from sklearn.manifold import TSNE                         # t-SNE
from sklearn.neighbors import KNeighborsClassifier        # dùng KNN để đo độ tách
P2 = PCA(2).fit_transform(dg.data)                        # PCA xuống 2 chiều
E2 = TSNE(2, random_state=0, init="pca", perplexity=30).fit_transform(dg.data)   # t-SNE xuống 2 chiều
for ten, Z in [("PCA", P2), ("t-SNE", E2)]:               # hai cách
    print(ten, round(cross_val_score(KNeighborsClassifier(5), Z, dg.target, cv=5).mean(), 4))   # KNN trên 2 chiều
''', "PCA 0.6032\nt-SNE 0.9755",
    khung("loi", ["<b>Huấn luyện mô hình trên đầu ra t-SNE.</b> t-SNE không có transform cho điểm mới và đổi theo seed. Con số 97,6% chỉ để đo độ tách, không phải mô hình dùng được."]))

c.mo_trang(5, "Ba bài tập. Tính tay trước, rồi mới mở đáp án.")
c.bai("20.1", "Tọa độ mới", "Tính tay tọa độ của A trên hai thành phần chính.",
      "$(-1{,}414;\\ 0{,}707)$ (dấu tùy thư viện). Bốn điểm là bốn đỉnh một hình chữ nhật, PCA chỉ xoay hệ trục. Code ở ô ngay dưới.")
c.o('''
print(np.abs(PCA(2).fit(D).transform(D)).round(4))     # độ lớn tọa độ trên hai thành phần
''', "[[1.4142 0.7071]\n [1.4142 0.7071]\n [1.4142 0.7071]\n [1.4142 0.7071]]")
c.bai("20.2", "Sai số tái tạo", "Giữ 1 thành phần rồi tái tạo, tính bình phương sai số của mỗi điểm.",
      "Mỗi điểm mất đúng 0,5, bằng trị riêng bị bỏ (chia $n$). Code ở ô ngay dưới.")
c.o('''
R = p1.inverse_transform(p1.transform(D))                                  # tái tạo từ 1 thành phần
print(((D - R) ** 2).sum(axis=1), float(((D - R) ** 2).sum(axis=1).mean()))   # sai số từng điểm và trung bình
''', "[0.5 0.5 0.5 0.5] 0.5")
c.bai("20.3", "99% phương sai", "Cần bao nhiêu thành phần để giữ 99% phương sai của ung thư vú?",
      "17 thành phần, giữ 99,1%. Từ 95% lên 99% cần thêm 7 thành phần. Code ở ô ngay dưới.")
c.o('''
print(int(np.argmax(tich_luy >= 0.99)) + 1, round(float(tich_luy[16]), 4))   # số thành phần và tỷ lệ
''', "17 0.9911")

c.ghi(Path(__file__).resolve().parents[2] / "notebooks/ch20_giam_chieu.ipynb")
