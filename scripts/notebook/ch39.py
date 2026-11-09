"""Dựng notebooks/ch39_bow_tfidf_ngram.ipynb: python3 scripts/notebook/ch39.py"""
from pathlib import Path
from nblib import Chuong, code, khung

c = Chuong(39, "BoW, TF-IDF và mô hình n-gram", "ch39-bow-tfidf-ngram",
           "Biến câu thành vector bằng đếm từ và TF-IDF, đo độ giống nhau bằng cosine, dựng máy tìm câu tương tự trên UIT-VSFC. Rồi xây mô hình ngôn ngữ n-gram, làm trơn và đánh giá bằng perplexity.",
           ["Tự cài Bag-of-Words và TF-IDF bằng NumPy, khớp lại công thức của scikit-learn.",
            "Tìm câu tương tự bằng cosine trên ma trận thưa.",
            "Đếm bigram, trigram, sinh câu, thấy vấn đề xác suất 0.",
            "Làm trơn add-k, nội suy, chọn trên val bằng perplexity."],
           [("Bag-of-Words", "01-bag-of-words"), ("TF-IDF", "02-tf-idf"), ("Mô hình ngôn ngữ n-gram", "03-mo-hinh-n-gram"),
            ("Làm trơn và perplexity", "04-lam-tron-va-perplexity"), ("Bài tập", "05-bai-tap")],
           thoi_gian="khoảng 30 giây")

c.mo_trang(1, "BoW trên ba câu, rồi trên UIT-VSFC.")
c.cells.append(code('''
!pip install -q underthesea                                 # thư viện xử lý tiếng Việt
'''))
c.o('''
import math                                                 # log, exp
import os                                                   # đường dẫn
import re                                                   # biểu thức chính quy
import urllib.request                                       # tải tệp
from collections import Counter                             # đếm
import numpy as np                                          # mảng
import pandas as pd                                         # bảng
from underthesea import word_tokenize                       # tách từ
def tach(s):                                                # chữ thường, tách từ, bỏ dấu câu
    return [w.replace(" ", "_") for w in word_tokenize(s.lower()) if re.search(r"\\w", w)]   # "bài tập" thành "bài_tập"
cau = ["Thầy giảng bài rất hay.", "Thầy giảng bài khó hiểu.", "Bài tập rất hay và bổ ích."]   # ba câu ví dụ
T = [tach(c) for c in cau]                                  # token của mỗi câu
tu_dien = sorted({w for t in T for w in t})                 # từ điển theo bảng chữ cái
X = np.array([[t.count(w) for w in tu_dien] for t in T])    # ma trận đếm
print(T)                                                    # token
print(tu_dien)                                              # từ điển
print(X)                                                    # mỗi hàng một câu
''', "[['thầy', 'giảng', 'bài', 'rất', 'hay'], ['thầy', 'giảng', 'bài', 'khó', 'hiểu'], ['bài_tập', 'rất', 'hay', 'và', 'bổ_ích']]\n['bài', 'bài_tập', 'bổ_ích', 'giảng', 'hay', 'hiểu', 'khó', 'rất', 'thầy', 'và']\n[[1 0 0 1 1 0 0 1 1 0]\n [1 0 0 1 0 1 1 0 1 0]\n [0 1 1 0 1 0 0 1 0 1]]")
c.o('''
def cos(a, b):                                              # độ tương tự cosine
    return a @ b / np.linalg.norm(a) / np.linalg.norm(b)    # tích vô hướng chia hai độ dài
print(round(cos(X[0], X[1]), 4), round(cos(X[0], X[2]), 4)) # câu 1 với câu 2, câu 1 với câu 3
''', "0.6 0.4")
c.o('''
URL = "https://huggingface.co/api/datasets/uitnlp/vietnamese_students_feedback/parquet/default/{}/0.parquet"   # UIT-VSFC
THU_MUC = os.path.expanduser("~/.cache/vsfc")               # lưu tạm
def tai(phan):                                              # tải một lần
    os.makedirs(THU_MUC, exist_ok=True)                     # tạo thư mục
    tep = os.path.join(THU_MUC, phan + ".parquet")          # đường dẫn
    if not os.path.exists(tep):                             # chưa có thì tải
        urllib.request.urlretrieve(URL.format(phan), tep)   # tải về
    return pd.read_parquet(tep)                             # đọc
tr, va, te = tai("train"), tai("validation"), tai("test")   # ba phần chia sẵn
noi = lambda ds: [" ".join(w.replace(" ", "_") for w in word_tokenize(c)) for c in ds]   # tách từ, nối bằng dấu cách
S_tr, S_va, S_te = noi(tr.sentence), noi(va.sentence), noi(te.sentence)   # khoảng 5 giây
print(S_tr[1])                                              # một câu đã tách
''', "nhiệt_tình giảng_dạy , gần_gũi với sinh_viên .")
c.o('''
from sklearn.feature_extraction.text import CountVectorizer # BoW của scikit-learn
cv = CountVectorizer(analyzer=str.split)                    # cắt theo dấu cách vì đã tách từ sẵn
B = cv.fit_transform(S_tr)                                  # học từ điển trên train rồi đếm
print(B.shape, B.nnz, round(B.nnz / (B.shape[0] * B.shape[1]), 4), type(B).__name__)   # cỡ, số ô khác 0, tỷ lệ, kiểu
print(round(B.shape[0] * B.shape[1] * 8 / 1e6), "MB nếu lưu dạng đặc")   # nếu lưu đủ mọi ô
''', "(11426, 4009) 118930 0.0026 csr_matrix\n366 MB nếu lưu dạng đặc")

c.mo_trang(2, "TF-IDF tự tính, khớp với scikit-learn, và máy tìm câu tương tự.")
c.o('''
N = len(T)                                                  # số câu
df = (X > 0).sum(0)                                         # số câu chứa mỗi từ
idf = np.log(N / df)                                        # ln(N / df)
tf = X / X.sum(1, keepdims=True)                            # đếm chia số token của câu
W = tf * idf                                                # TF-IDF
print(df, idf.round(4))                                     # df và idf
print(W.round(4))                                           # ma trận TF-IDF
''', "[2 1 1 2 2 1 1 2 2 1] [0.4055 1.0986 1.0986 0.4055 0.4055 1.0986 1.0986 0.4055 0.4055 1.0986]\n[[0.0811 0.     0.     0.0811 0.0811 0.     0.     0.0811 0.0811 0.    ]\n [0.0811 0.     0.     0.0811 0.     0.2197 0.2197 0.     0.0811 0.    ]\n [0.     0.2197 0.2197 0.     0.0811 0.     0.     0.0811 0.     0.2197]]")
c.o('''
print(round(cos(W[0], W[1]), 4), round(cos(W[0], W[2]), 4)) # cosine trên TF-IDF
''', "0.3191 0.1825")
c.o('''
from sklearn.feature_extraction.text import TfidfVectorizer # TF-IDF của scikit-learn
tv3 = TfidfVectorizer(analyzer=str.split)                   # mặc định: đếm thô, idf làm trơn, chuẩn hóa L2
M = tv3.fit_transform([" ".join(t) for t in T]).toarray()   # ba câu
idf_sk = np.log((1 + N) / (1 + df)) + 1                     # idf của scikit-learn
tu_lam = X * idf_sk                                         # đếm thô nhân idf
tu_lam = tu_lam / np.linalg.norm(tu_lam, axis=1, keepdims=True)   # chuẩn hóa L2
print(tv3.idf_.round(4), np.allclose(M, tu_lam))            # khớp từng số
print(M[1].round(4))                                        # câu 2
''', "[1.2877 1.6931 1.6931 1.2877 1.2877 1.6931 1.6931 1.2877 1.2877 1.6931] True\n[0.3935 0.     0.     0.3935 0.     0.5174 0.5174 0.     0.3935 0.    ]")
c.o('''
tv = TfidfVectorizer(analyzer=str.split)                    # TF-IDF trên UIT-VSFC
A = tv.fit_transform(S_tr)                                  # các hàng đã có độ dài 1
truy_van = tv.transform(noi(["thầy dạy nhanh quá không theo kịp"]))   # truy vấn
diem = (A @ truy_van.T).toarray().ravel()                   # cosine với mọi câu train
for i in diem.argsort()[::-1][:5]:                          # năm câu gần nhất
    print(round(diem[i], 3), tr.sentiment[i], tr.sentence[i])   # cosine, nhãn cảm xúc, câu
''', "0.904 0 giáo viên dạy nhanh quá theo không kịp .\n0.82 0 thầy dạy nhanh , nhiều khi theo không kịp .\n0.711 0 dạy nhanh , không thể theo kịp .\n0.706 0 dạy hơi nhanh , sinh viên khó theo kịp .\n0.699 0 bài tập trên lớp làm quá nhanh , có thể không theo kịp .")

c.mo_trang(3, "Đếm n-gram, sinh câu, và vấn đề xác suất 0.")
c.o('''
def them_dau(s, n):                                         # thêm ký hiệu đầu và cuối câu
    return ["<s>"] * (n - 1) + s.split() + ["</s>"]         # n - 1 cái <s>, một cái </s>
def dem(ds, n):                                             # đếm n-gram và lịch sử
    c, h = Counter(), Counter()                             # n-gram, lịch sử
    for s in ds:                                            # mỗi câu
        t = them_dau(s, n)                                  # có ký hiệu
        for i in range(n - 1, len(t)):                      # mỗi vị trí
            g = tuple(t[i - n + 1:i + 1])                   # n-gram kết thúc ở i
            c[g] += 1                                       # đếm n-gram
            h[g[:-1]] += 1                                  # đếm lịch sử
    return c, h                                             # hai bảng đếm
c1, h1 = dem(S_tr, 1)                                       # unigram
c2, h2 = dem(S_tr, 2)                                       # bigram
c3, h3 = dem(S_tr, 3)                                       # trigram
V = len(c1)                                                 # cỡ từ vựng kể cả </s>
print(V, len(c2), len(c3))                                  # số unigram, bigram, trigram khác nhau
sau_thay = [(w, round(n / h2[("thầy",)], 3)) for (a, w), n in c2.most_common() if a == "thầy"]   # P(w | thầy)
print(h2[("thầy",)], sau_thay[:5])                          # năm từ hay đi sau "thầy"
''', "4010 36403 77710\n3039 [('dạy', 0.211), ('rất', 0.082), ('giảng', 0.059), ('nên', 0.037), ('.', 0.027)]")
c.o('''
rng = np.random.default_rng(0)                              # ngẫu nhiên
tiep = {}                                                   # từ, danh sách từ theo sau kèm số lần
for (a, b), n in c2.items():                                # mọi bigram
    tiep.setdefault(a, []).append((b, n))                   # gom theo từ trước
def sinh(toi_da=25):                                        # sinh một câu
    w, ra = "<s>", []                                       # bắt đầu từ <s>
    for _ in range(toi_da):                                 # tối đa 25 từ
        tu, so = zip(*tiep[w])                              # các từ có thể theo sau
        p = np.array(so, dtype=float) / sum(so)             # xác suất
        w = tu[rng.choice(len(tu), p=p)]                    # lấy mẫu
        if w == "</s>":                                     # hết câu
            break                                           # dừng
        ra.append(w)                                        # thêm từ
    return " ".join(ra)                                     # câu sinh ra
for _ in range(4):                                          # bốn câu
    print(sinh())                                           # in
''', "bài giảng bài hay liên_hệ kiến_thức chuyên_môn tốt , lôi_cuốn vào slide nhiều bài_tập đầy_đủ .\nnhững điều gì .\ncách thi cho sinh_viên khó_khăn nhưng với thực_tiễn cho sinh_viên .\ncô rất hay gặp thầy dạy hay và nhiều hơn .")
c.o('''
def log_p(s, n, c, h, k=0.0):                               # log xác suất của câu, None nếu bằng 0
    t = them_dau(s, n)                                      # có ký hiệu
    L = 0.0                                                 # cộng log
    for i in range(n - 1, len(t)):                          # mỗi từ cần đoán
        g = tuple(t[i - n + 1:i + 1])                       # n-gram
        tu_so, mau_so = c[g] + k, h[g[:-1]] + k * V         # add-k (k = 0 là không làm trơn)
        if tu_so == 0:                                      # chưa từng gặp
            return None                                     # xác suất 0
        L += math.log(tu_so / mau_so)                       # cộng log xác suất
    return L                                                # log xác suất cả câu
so_0 = sum(log_p(s, 2, c2, h2) is None for s in S_te)       # số câu test xác suất 0
print(so_0, len(S_te), round(so_0 / len(S_te), 3))          # bao nhiêu phần trăm
''', "1860 3166 0.587",
    khung("loi", ["58,7% câu test có xác suất 0 vì chứa ít nhất một cặp từ chưa từng gặp trong train."], "XÁC SUẤT 0"))

c.mo_trang(4, "Perplexity theo k cho unigram, bigram, trigram.")
c.o('''
def perplexity(ds, n, c, h, k):                             # exp của cross-entropy trung bình
    L, N = 0.0, 0                                           # tổng log, số token
    for s in ds:                                            # mỗi câu
        l = log_p(s, n, c, h, k)                            # log xác suất
        if l is None:                                       # có câu xác suất 0
            return float("inf")                             # perplexity vô cùng
        L += l                                              # cộng
        N += len(s.split()) + 1                             # các từ cộng </s>
    return round(math.exp(-L / N), 2)                       # perplexity
for k in (1, 0.1, 0.01, 0.001):                             # bốn giá trị k
    print(k, perplexity(S_va, 1, c1, h1, k), perplexity(S_va, 2, c2, h2, k), perplexity(S_va, 3, c3, h3, k))   # unigram, bigram, trigram trên val
''', "1 218.18 213.53 896.02\n0.1 222.07 90.46 377.04\n0.01 228.47 70.61 209.43\n0.001 235.26 81.95 197.03")
c.o('''
print(perplexity(S_te, 2, c2, h2, 0.01), perplexity(S_te, 1, c1, h1, 1))   # mô hình chọn trên val, đo test một lần
''', "81.6 234.97")

c.mo_trang(5, "Ba bài tập. Đoán trước, rồi mới mở đáp án.")
c.bai("39.1", "Tính tay khi thêm một câu", "Thêm 'Thầy rất nhiệt tình.'; TF-IDF của 'thầy' trong câu 1 và 'khó' trong câu 2.",
      "thầy: 0,2 x ln(4/3) = 0,0575 (giảm từ 0,0811); khó: 0,2 x ln 4 = 0,2773 (tăng từ 0,2197). Code ở ô ngay dưới.")
c.o('''
T4 = T + [tach("Thầy rất nhiệt tình.")]                     # thêm câu thứ tư
tu4 = sorted({w for t in T4 for w in t})                    # từ điển mới
X4 = np.array([[t.count(w) for w in tu4] for t in T4])      # ma trận đếm mới
W4 = X4 / X4.sum(1, keepdims=True) * np.log(len(T4) / (X4 > 0).sum(0))   # TF-IDF với N = 4
print(T4[3], round(W4[0, tu4.index("thầy")], 4), round(W4[1, tu4.index("khó")], 4))   # hai ô cần tính
''', "['thầy', 'rất', 'nhiệt_tình'] 0.0575 0.2773")
c.bai("39.2", "Đếm hay TF-IDF", "Cùng truy vấn, tìm 3 câu gần nhất bằng cosine trên vector đếm.",
      "Hai câu đầu giống TF-IDF, câu thứ ba khác: BoW thưởng các từ phổ biến như 'thầy', 'không'. Code ở ô ngay dưới.")
c.o('''
from sklearn.preprocessing import normalize                 # chuẩn hóa từng hàng
B = normalize(cv.fit_transform(S_tr).astype(float))         # chia độ dài: tích vô hướng thành cosine
q = normalize(cv.transform(noi(["thầy dạy nhanh quá không theo kịp"])).astype(float))   # truy vấn
d = (B @ q.T).toarray().ravel()                             # cosine
for i in d.argsort()[::-1][:3]:                             # ba câu gần nhất
    print(round(d[i], 3), tr.sentence[i])                   # cosine, câu
''', "0.802 giáo viên dạy nhanh quá theo không kịp .\n0.717 thầy dạy nhanh , nhiều khi theo không kịp .\n0.684 thầy dạy hơi nhanh , đa số sinh viên không theo kịp .")
c.bai("39.3", "Nội suy", "Trộn unigram add-one với bigram, trigram chưa làm trơn; chọn lambda trên val.",
      "(0,2; 0,5; 0,3) cho val 57,16, test 65,71 so với 81,6 của bigram add-k. Code ở ô ngay dưới.")
c.o('''
N1 = sum(c1.values())                                       # tổng số token
def p_tron(t, i, lam):                                      # xác suất nội suy của từ thứ i
    w = t[i]                                                # từ cần đoán
    p1 = (c1[(w,)] + 1) / (N1 + V)                          # unigram add-one
    p2 = c2[(t[i - 1], w)] / h2[(t[i - 1],)] if h2[(t[i - 1],)] else 0   # bigram
    p3 = c3[(t[i - 2], t[i - 1], w)] / h3[(t[i - 2], t[i - 1])] if h3[(t[i - 2], t[i - 1])] else 0   # trigram
    return lam[0] * p1 + lam[1] * p2 + lam[2] * p3          # trộn
def pp_tron(ds, lam):                                       # perplexity của mô hình trộn
    L, N = 0.0, 0                                           # tổng log, số token
    for s in ds:                                            # mỗi câu
        t = them_dau(s, 3)                                  # hai <s> ở đầu
        for i in range(2, len(t)):                          # mỗi từ cần đoán
            L += math.log(p_tron(t, i, lam))                # cộng log
            N += 1                                          # đếm token
    return round(math.exp(-L / N), 2)                       # perplexity
bo = [(0.1, 0.9, 0.0), (0.1, 0.6, 0.3), (0.2, 0.5, 0.3), (0.1, 0.4, 0.5), (0.3, 0.4, 0.3)]   # các bộ lambda
ket_qua = [(pp_tron(S_va, lam), lam) for lam in bo]         # đo trên val
print(ket_qua)                                              # so các bộ
tot = min(ket_qua)[1]                                       # bộ tốt nhất
print(tot, pp_tron(S_te, tot))                              # đo test một lần
''', "[(64.41, (0.1, 0.9, 0.0)), (59.81, (0.1, 0.6, 0.3)), (57.16, (0.2, 0.5, 0.3)), (62.62, (0.1, 0.4, 0.5)), (57.83, (0.3, 0.4, 0.3))]\n(0.2, 0.5, 0.3) 65.71")

c.ghi(Path(__file__).resolve().parents[2] / "notebooks/ch39_bow_tfidf_ngram.ipynb")
