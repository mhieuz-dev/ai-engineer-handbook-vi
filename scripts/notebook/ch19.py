"""Dựng notebooks/ch19_phan_cum.ipynb: python3 scripts/notebook/ch19.py"""
from pathlib import Path
from nblib import Chuong, khung

c = Chuong(19, "Phân cụm", "ch19-phan-cum",
           "Tìm nhóm trong dữ liệu không nhãn: k-means tính tay, khởi tạo, chọn số cụm bằng khuỷu tay và silhouette, rồi DBSCAN cho cụm hình dạng bất kỳ.",
           ["Tính tay k-means và hiểu vì sao nó luôn dừng.",
            "Thấy k-means kẹt ở đáy cục bộ và cách k-means++ chữa.",
            "Chọn số cụm bằng inertia và silhouette.",
            "Dùng DBSCAN và phân cụm phân cấp cho cụm không tròn."],
           [("K-means tính tay", "01-kmeans-tinh-tay"), ("Khởi tạo và scikit-learn", "02-khoi-tao-va-scikit-learn"),
            ("Chọn số cụm", "03-chon-so-cum"), ("DBSCAN và phân cụm phân cấp", "04-dbscan-va-phan-cap"), ("Bài tập", "05-bai-tap")])

c.mo_trang(1, "K-means trên bảy điểm.")
c.o('''
import numpy as np                                                 # tính toán
P = np.array([[1, 1], [1.5, 2], [3, 4], [5, 7], [3.5, 5], [4.5, 5], [3.5, 4.5]])   # Bảng 19.1
tam = P[[0, 3]].copy()                                             # tâm khởi đầu: P1 và P4
for vong in range(1, 4):                                           # ba vòng
    d2 = ((P[:, None, :] - tam[None]) ** 2).sum(axis=2)            # bình phương khoảng cách, shape (7, 2)
    nhan = d2.argmin(axis=1)                                       # gán vào tâm gần nhất
    tam = np.array([P[nhan == k].mean(axis=0) for k in range(2)])  # dời tâm về trung bình
    qt = sum(((P[nhan == k] - tam[k]) ** 2).sum() for k in range(2))   # inertia với tâm mới
    print(vong, nhan, tam.round(4).tolist(), round(float(qt), 4))  # nhãn, tâm, inertia
''', "1 [0 0 0 1 1 1 1] [[1.8333, 2.3333], [4.125, 5.375]] 12.2083\n2 [0 0 1 1 1 1 1] [[1.25, 1.5], [3.9, 5.1]] 8.525\n3 [0 0 1 1 1 1 1] [[1.25, 1.5], [3.9, 5.1]] 8.525",
    khung("doc", ["P3 hòa khoảng cách ở vòng 1 nên vào cụm 0, rồi đổi sang cụm 1 ở vòng 2 khi tâm cam trôi lại gần. Vòng 3 không ai đổi: hội tụ."]))

c.mo_trang(2, "Bốn đám điểm, khởi tạo ngẫu nhiên kẹt ở đáy cục bộ.")
c.o('''
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering   # ba thuật toán
from sklearn.datasets import make_blobs, make_moons, load_iris       # ba bộ dữ liệu
from sklearn.metrics import adjusted_rand_score, silhouette_score, silhouette_samples   # thước đo
Xb, yb = make_blobs(n_samples=300, centers=4, cluster_std=0.8, random_state=0)   # 4 đám, giữ nhãn thật để chấm
km = KMeans(n_clusters=4, n_init=10, random_state=0).fit(Xb)          # k-means++ với 10 lần chạy
print(round(km.inertia_, 1), round(adjusted_rand_score(yb, km.labels_), 4))   # inertia và ARI
qt = [KMeans(4, n_init=1, init="random", random_state=s).fit(Xb).inertia_ for s in range(10)]   # 10 lần khởi tạo ngẫu nhiên
print([round(v, 1) for v in qt])                                     # có lần kẹt
''', "369.5 0.9463\n[369.5, 369.5, 369.5, 369.5, 369.5, 669.3, 369.5, 369.5, 369.5, 669.3]",
    khung("vi-sao", ["Ở hai lần kẹt, hai tâm chia nhau một đám, một tâm gộp hai đám khác. Bước gán và dời tâm không thoát ra được: một đáy cục bộ."],
          nhan="VÌ SAO LẠI LÀ 669,3?"))

c.mo_trang(3, "Khuỷu tay, silhouette, và hoa iris.")
c.o('''
for k in range(1, 9):                                                  # k từ 1 tới 8
    kmk = KMeans(k, n_init=10, random_state=0).fit(Xb)                 # k-means
    print(k, round(kmk.inertia_, 1), round(silhouette_score(Xb, kmk.labels_), 4) if k > 1 else "-")   # inertia, silhouette
''', "1 2978.6 -\n2 1348.9 0.4964\n3 708.8 0.5151\n4 369.5 0.5801\n5 326.3 0.5032\n6 292.4 0.4305\n7 260.2 0.3955\n8 225.2 0.3444")
c.o('''
from sklearn.preprocessing import StandardScaler                    # chuẩn hóa
Xi, yi = load_iris(return_X_y=True)                                 # 150 hoa, 3 loài
Zi = StandardScaler().fit_transform(Xi)                             # chuẩn hóa trước khi đo khoảng cách
for k in [2, 3, 4]:                                                 # ba giá trị k
    li = KMeans(k, n_init=10, random_state=0).fit_predict(Zi)       # phân cụm
    print(k, round(silhouette_score(Zi, li), 4), round(adjusted_rand_score(yi, li), 4))   # silhouette và ARI so với loài thật
''', "2 0.5818 0.5681\n3 0.4599 0.6201\n4 0.3869 0.4728",
    khung("loi", ["<b>Tin silhouette là sự thật.</b> Nó thích k = 2 vì setosa tách hẳn, hai loài kia chồng lấn. Số cụm đúng phụ thuộc câu hỏi bạn đặt ra."]))

c.mo_trang(4, "Hai vầng trăng: k-means, DBSCAN, phân cấp.")
c.o('''
Xm, ym = make_moons(300, noise=0.06, random_state=0)                       # hai vầng trăng ít nhiễu
km2 = KMeans(2, n_init=10, random_state=0).fit_predict(Xm)                 # k-means
db = DBSCAN(eps=0.2, min_samples=5).fit_predict(Xm)                        # DBSCAN
ag = AgglomerativeClustering(2, linkage="single").fit_predict(Xm)          # phân cấp, single linkage
print(round(adjusted_rand_score(ym, km2), 4), round(adjusted_rand_score(ym, db), 4), int((db == -1).sum()), round(adjusted_rand_score(ym, ag), 4))   # ARI ba cách, số điểm nhiễu
''', "0.2343 1.0 0 1.0",
    khung("thu", ["<b>1.</b> Đổi linkage=\"single\" thành \"ward\". ARI còn bằng 1 không?",
                  "<b>2.</b> Tăng noise của make_moons lên 0,15. DBSCAN với eps = 0,2 còn tìm đúng hai vầng trăng không?"]))

c.mo_trang(5, "Ba bài tập. Tính tay trước, rồi mới mở đáp án.")
c.bai("19.1", "Silhouette của P3", "Tính tay $a$, $b$ và silhouette của P3 với cách chia cuối cùng.",
      "$a \\approx 1{,}808$, $b \\approx 3{,}053$, $s \\approx 0{,}408$, thấp nhất trong 7 điểm. Code ở ô ngay dưới.")
c.o('''
print(silhouette_samples(P, np.array([0, 0, 1, 1, 1, 1, 1])).round(4))   # silhouette từng điểm
''', "[0.7777 0.7156 0.4076 0.5838 0.6925 0.687  0.6508]")
c.bai("19.2", "k-means++ chọn tâm thứ hai", "Với tâm đầu là P1, tính xác suất mỗi điểm được chọn làm tâm thứ hai.",
      "Tỷ lệ với bình phương khoảng cách: P4 được 38%, P2 chỉ 0,9%. Code ở ô ngay dưới.")
c.o('''
d2 = ((P - P[0]) ** 2).sum(axis=1)       # bình phương khoảng cách tới P1
print(d2, (d2 / d2.sum()).round(4))      # và xác suất được chọn
''', "[ 0.    1.25 13.   52.   22.25 28.25 18.5 ] [0.     0.0092 0.0961 0.3845 0.1645 0.2089 0.1368]")
c.bai("19.3", "Chọn eps", "Chạy DBSCAN với eps 0,05; 0,2; 1,0 trên hai vầng trăng, đếm số cụm và số điểm nhiễu.",
      "0,05: 10 cụm vụn, 243 nhiễu. 0,2: đúng 2 cụm. 1,0: gộp thành 1 cụm. Code ở ô ngay dưới.")
c.o('''
for e in [0.05, 0.2, 1.0]:                                  # ba bán kính
    l = DBSCAN(eps=e, min_samples=5).fit_predict(Xm)        # DBSCAN
    print(e, len(set(l) - {-1}), int((l == -1).sum()))      # số cụm, số điểm nhiễu
''', "0.05 10 243\n0.2 2 0\n1.0 1 0")

c.ghi(Path(__file__).resolve().parents[2] / "notebooks/ch19_phan_cum.ipynb")
