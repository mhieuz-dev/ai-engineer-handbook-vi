"""Dựng notebooks/ch40_word_embeddings.ipynb: python3 scripts/notebook/ch40.py"""
from pathlib import Path
from nblib import Chuong, code, khung

c = Chuong(40, "Word embeddings", "ch40-word-embeddings",
           "Học vector từ trên UIT-VSFC bằng hai cách: đếm đồng xuất hiện rồi nén bằng SVD, và Word2Vec skip-gram tự cài bằng nn.Embedding. Đọc hàng xóm gần nhất, phép tương tự, và đo vector từ làm đặc trưng phân loại cảm xúc.",
           ["Thấy giới hạn của one-hot và giả thuyết phân bố.",
            "Dựng vector PPMI và SVD từ ma trận đồng xuất hiện.",
            "Cài Word2Vec skip-gram với negative sampling bằng PyTorch.",
            "Đọc vector từ, thấy vì sao từ trái nghĩa gần nhau, và so với TF-IDF khi phân loại."],
           [("Từ vector thưa tới vector dày", "01-tu-thua-toi-day"), ("Word2Vec", "02-word2vec"), ("Đọc vector từ", "03-doc-vector-tu"),
            ("Vector từ làm đặc trưng", "04-vector-tu-lam-dac-trung"), ("Bài tập", "05-bai-tap")],
           thoi_gian="khoảng 1 phút")

c.mo_trang(1, "Ma trận đồng xuất hiện, PPMI, SVD.")
c.cells.append(code('''
!pip install -q underthesea                                 # thư viện xử lý tiếng Việt
'''))
c.o('''
import os                                                   # đường dẫn
import re                                                   # biểu thức chính quy
import time                                                 # đo thời gian
import urllib.request                                       # tải tệp
from collections import Counter                             # đếm
import numpy as np                                          # mảng
import pandas as pd                                         # bảng
from underthesea import word_tokenize                       # tách từ
URL = "https://huggingface.co/api/datasets/uitnlp/vietnamese_students_feedback/parquet/default/{}/0.parquet"   # UIT-VSFC
THU_MUC = os.path.expanduser("~/.cache/vsfc")               # lưu tạm
def tai(phan):                                              # tải một lần
    os.makedirs(THU_MUC, exist_ok=True)                     # tạo thư mục
    tep = os.path.join(THU_MUC, phan + ".parquet")          # đường dẫn
    if not os.path.exists(tep):                             # chưa có thì tải
        urllib.request.urlretrieve(URL.format(phan), tep)   # tải về
    return pd.read_parquet(tep)                             # đọc
tr, va, te = tai("train"), tai("validation"), tai("test")   # ba phần
tach = lambda s: [w.replace(" ", "_") for w in word_tokenize(s) if re.search(r"\\w", w)]   # tách từ, bỏ dấu câu
C_tr, C_va = [tach(s) for s in tr.sentence], [tach(s) for s in va.sentence]   # train và val đã tách
dem = Counter(w for c in C_tr for w in c)                   # tần suất trên train
tu = [w for w, n in dem.most_common() if n >= 5]            # từ gặp ít nhất 5 lần
id_ = {w: i for i, w in enumerate(tu)}                      # từ sang chỉ số
V = len(tu)                                                 # cỡ từ điển
M = np.zeros((V, V))                                        # ma trận đồng xuất hiện
for c in C_tr:                                              # mỗi câu
    ids = [id_[w] for w in c if w in id_]                   # chỉ số các từ có trong từ điển
    for i, a in enumerate(ids):                             # mỗi từ trung tâm
        for j in range(max(0, i - 2), min(len(ids), i + 3)):   # cửa sổ 2 từ mỗi bên
            if j != i:                                      # bỏ chính nó
                M[a, ids[j]] += 1                           # đếm ngữ cảnh
print(V, int(M.sum()), round((M > 0).mean(), 4))            # cỡ từ điển, số cặp, tỷ lệ ô khác 0
''', "1208 349962 0.0646")
c.o('''
tong = M.sum()                                              # tổng số cặp
p_w, p_c = M.sum(1) / tong, M.sum(0) / tong                 # xác suất từ, xác suất ngữ cảnh
with np.errstate(divide="ignore"):                          # log 0 cho -vô cùng, không cảnh báo
    pmi = np.log(M / tong / np.outer(p_w, p_c))             # PMI
ppmi = np.maximum(pmi, 0)                                   # cắt giá trị âm
U, S, Vt = np.linalg.svd(ppmi)                              # phân tích SVD
E_svd = U[:, :50] * S[:50]                                  # 50 chiều đầu
E_svd /= np.linalg.norm(E_svd, axis=1, keepdims=True)       # độ dài 1: tích vô hướng là cosine
def gan(w, E, k=6):                                         # k từ gần w nhất
    s = E @ E[id_[w]]                                       # cosine với mọi từ
    return [(tu[i], round(float(s[i]), 2)) for i in s.argsort()[::-1][1:k + 1]]   # bỏ chính nó
for w in ("thầy", "nhiệt_tình", "phòng", "điểm"):           # bốn từ
    print(w, gan(w, E_svd))                                 # hàng xóm
''', "thầy [('cô', 0.91), ('rất', 0.81), ('dạy', 0.8), ('giảng_viên', 0.76), ('giáo_viên', 0.75), ('hay', 0.73)]\nnhiệt_tình [('tận_tâm', 0.97), ('dễ_thương', 0.95), ('tận_tình', 0.95), ('thân_thiện', 0.94), ('vui_tính', 0.93), ('chu_đáo', 0.91)]\nphòng [('chất_lượng', 0.84), ('máy', 0.8), ('trang_thiết_bị', 0.78), ('thiết_bị', 0.78), ('nâng_cấp', 0.77), ('máy_chiếu', 0.77)]\nđiểm [('chấm', 0.77), ('quá_trình', 0.65), ('lấy', 0.63), ('công_bằng', 0.63), ('chuẩn_xác', 0.58), ('cộng', 0.56)]")

c.mo_trang(2, "Word2Vec skip-gram với negative sampling (khoảng 5 giây).")
c.o('''
import torch                                                # PyTorch
import torch.nn as nn                                       # các lớp mạng
import torch.nn.functional as F                             # hàm loss
torch.set_num_threads(1)                                    # một luồng, kết quả lặp lại được
bang = nn.Embedding(5, 3)                                   # 5 từ, mỗi từ 3 số
print(bang.weight.shape, bang(torch.tensor([0, 3, 3])).shape)   # tra bảng 3 lần
''', "torch.Size([5, 3]) torch.Size([3, 3])")
c.o('''
cap = []                                                    # mọi cặp (từ, ngữ cảnh)
for c in C_tr:                                              # mỗi câu
    ids = [id_[w] for w in c if w in id_]                   # chỉ số
    for i, a in enumerate(ids):                             # mỗi từ trung tâm
        for j in range(max(0, i - 2), min(len(ids), i + 3)):   # cửa sổ 2
            if j != i:                                      # bỏ chính nó
                cap.append((a, ids[j]))                     # một cặp thật
cap = torch.tensor(cap)                                     # sang tensor
p_gia = torch.tensor([dem[w] for w in tu], dtype=torch.float) ** 0.75   # rút ngữ cảnh giả theo tần suất mũ 0,75
p_gia /= p_gia.sum()                                        # chuẩn hóa thành xác suất
torch.manual_seed(0)                                        # khởi tạo cố định
vao, ra = nn.Embedding(V, 50), nn.Embedding(V, 50)          # vector trung tâm, vector ngữ cảnh
nn.init.uniform_(vao.weight, -0.5 / 50, 0.5 / 50)           # nhỏ, ngẫu nhiên
nn.init.zeros_(ra.weight)                                   # bằng 0
opt = torch.optim.Adam(list(vao.parameters()) + list(ra.parameters()), lr=0.01, fused=True)   # Adam
t0 = time.time()                                            # đo thời gian
for ep in range(5):                                         # 5 epoch
    thu_tu, tong, n = torch.randperm(len(cap)), 0.0, 0      # xáo trộn
    for k in range(0, len(cap), 1024):                      # lô 1024 cặp
        lo = cap[thu_tu[k:k + 1024]]                        # một lô
        w, c = lo[:, 0], lo[:, 1]                           # từ, ngữ cảnh thật
        gia = torch.multinomial(p_gia, len(lo) * 5, replacement=True).view(len(lo), 5)   # 5 ngữ cảnh giả mỗi cặp
        v = vao(w)                                          # vector từ trung tâm
        diem_that = (v * ra(c)).sum(1)                      # điểm cặp thật
        diem_gia = torch.bmm(ra(gia), v.unsqueeze(2)).squeeze(2)   # điểm 5 cặp giả
        loss = -(F.logsigmoid(diem_that).mean() + F.logsigmoid(-diem_gia).sum(1).mean())   # BCE: thật là 1, giả là 0
        opt.zero_grad()                                     # xóa gradient
        loss.backward()                                     # lượt ngược
        opt.step()                                          # cập nhật
        tong, n = tong + loss.item() * len(lo), n + len(lo) # cộng loss
    print(ep + 1, round(tong / n, 4))                       # loss trung bình mỗi epoch
print(len(cap), time.time() - t0 < 60)                      # số cặp, có dưới một phút không
E_w2v = vao.weight.detach().numpy()                         # giữ vector trung tâm
E_w2v = E_w2v / np.linalg.norm(E_w2v, axis=1, keepdims=True)   # độ dài 1
''', "1 2.578\n2 2.2832\n3 2.2176\n4 2.185\n5 2.1657\n349962 True")

c.mo_trang(3, "Hàng xóm, từ trái nghĩa, phép tương tự.")
c.o('''
for w in ("thầy", "nhiệt_tình", "slide", "phòng", "điểm", "nhanh", "tốt"):   # bảy từ chọn trước
    print(w, "| SVD:", [x for x, _ in gan(w, E_svd, 5)], "| W2V:", [x for x, _ in gan(w, E_w2v, 5)])   # hai bộ vector
''', "thầy | SVD: ['cô', 'rất', 'dạy', 'giảng_viên', 'giáo_viên'] | W2V: ['cô', 'giảng_viên', 'giáo_viên', 'thầy_giáo', 'cô_giáo']\nnhiệt_tình | SVD: ['tận_tâm', 'dễ_thương', 'tận_tình', 'thân_thiện', 'vui_tính'] | W2V: ['tận_tình', 'nhiệt_huyết', 'chuyên_tâm', 'dễ_tính', 'tận_tâm']\nslide | SVD: ['bài', 'đọc', 'chép', 'đẹp', 'tài_liệu'] | W2V: ['sách', 'song_ngữ', 'việt', 'chữ', 'tài_liệu']\nphòng | SVD: ['chất_lượng', 'máy', 'trang_thiết_bị', 'thiết_bị', 'nâng_cấp'] | W2V: ['nóng', 'âm_thanh', 'máy', 'trang_thiết_bị', 'thiết_bị']\nđiểm | SVD: ['chấm', 'quá_trình', 'lấy', 'công_bằng', 'chuẩn_xác'] | W2V: ['đánh_giá', 'chấm', 'trung_bình', 'điểm_số', 'công_bằng']\nnhanh | SVD: ['khó', 'hơi', 'giảng_hơi', 'đôi_lúc', 'giảng'] | W2V: ['chậm', 'đôi_khi', 'to', 'khó', 'đôi_lúc']\ntốt | SVD: ['truyền_đạt', 'khả_năng', 'cao', 'được', 'giảng_dạy'] | W2V: ['tệ', 'thuyết_phục', 'tận_tâm', 'hết_mình', 'cao']",
    khung("loi", ["Theo Word2Vec, từ gần \"tốt\" nhất là \"tệ\" và gần \"nhanh\" nhất là \"chậm\": từ trái nghĩa đứng trong cùng ngữ cảnh."], "TỪ TRÁI NGHĨA"))
c.o('''
cos_cap = lambda E, a, b: round(float(E[id_[a]] @ E[id_[b]]), 3)   # cosine của hai từ
for a, b in (("tốt", "tệ"), ("tốt", "hay"), ("nhanh", "chậm"), ("nhiệt_tình", "tận_tâm")):   # bốn cặp
    print(a, b, cos_cap(E_svd, a, b), cos_cap(E_w2v, a, b)) # SVD, Word2Vec
''', "tốt tệ 0.39 0.588\ntốt hay 0.491 0.477\nnhanh chậm 0.686 0.74\nnhiệt_tình tận_tâm 0.97 0.701")
c.o('''
def tuong_tu(a, b, c, E, k=3):                              # a : b = c : ?
    v = E[id_[b]] - E[id_[a]] + E[id_[c]]                   # b - a + c
    s = E @ (v / np.linalg.norm(v))                         # cosine với mọi từ
    return [tu[i] for i in s.argsort()[::-1] if tu[i] not in (a, b, c)][:k]   # bỏ ba từ đầu vào
print(tuong_tu("thầy", "thầy_giáo", "cô", E_svd), tuong_tu("thầy", "thầy_giáo", "cô", E_w2v))   # SVD, Word2Vec
''', "['thân_thiện', 'dễ_thương', 'trẻ_trung'] ['cô_giáo', 'giảng_viên', 'giáo_viên']")

c.mo_trang(4, "Vector trung bình làm đặc trưng, so với TF-IDF.")
c.o('''
from sklearn.feature_extraction.text import TfidfVectorizer # TF-IDF
from sklearn.linear_model import LogisticRegression         # hồi quy logistic
from sklearn.metrics import accuracy_score, f1_score        # thước đo
y_tr, y_va = tr.sentiment.values, va.sentiment.values       # nhãn cảm xúc
def vector_cau(C, E):                                       # trung bình vector các từ có trong từ điển
    X = np.zeros((len(C), E.shape[1]))                      # mặc định 0
    for i, c in enumerate(C):                               # mỗi câu
        ids = [id_[w] for w in c if w in id_]               # từ có vector
        if ids:                                             # có ít nhất một từ
            X[i] = E[ids].mean(0)                           # trung bình
    return X                                                # ma trận câu
def cham(X_tr, X_va):                                       # học trên train, chấm trên val
    p = LogisticRegression(max_iter=2000).fit(X_tr, y_tr).predict(X_va)   # ba lớp
    return round(accuracy_score(y_va, p), 4), round(f1_score(y_va, p, average="macro"), 4)   # độ chính xác, macro-F1
print("SVD     ", cham(vector_cau(C_tr, E_svd), vector_cau(C_va, E_svd)))   # vector SVD
print("Word2Vec", cham(vector_cau(C_tr, E_w2v), vector_cau(C_va, E_w2v)))   # vector Word2Vec
tv = TfidfVectorizer(analyzer=lambda c: c)                  # C_tr đã là danh sách từ
print("TF-IDF  ", cham(tv.fit_transform(C_tr), tv.transform(C_va)))   # TF-IDF
print("lớp đông nhất", round((y_va == 2).mean(), 4))        # đoán toàn tích cực
''', "SVD      (0.868, 0.6256)\nWord2Vec (0.8756, 0.6146)\nTF-IDF   (0.9059, 0.6857)\nlớp đông nhất 0.5085",
    khung("doc", ["TF-IDF thắng: trung bình vector làm mất thứ tự và phủ định, và vector học trên chính 11 nghìn câu train không thêm thông tin mới."]))
c.o('''
n = sum(len(c) for c in C_va)                               # số token của val
print(round(sum(w not in id_ for c in C_va for w in c) / n, 4), sum(1 for c in C_va if not any(w in id_ for w in c)))   # tỷ lệ không có vector, số câu không có từ nào
''', "0.0399 6")

c.mo_trang(5, "Ba bài tập. Đoán trước, rồi mới mở đáp án.")
c.bai("40.1", "Cửa sổ rộng hơn", "PPMI và SVD với cửa sổ 5 từ mỗi bên.",
      "Hàng xóm nghiêng về cùng chủ đề (thầy gần hay, giảng_bài; nhanh gần kịp) thay vì thay được cho nhau. Code ở ô ngay dưới.")
c.o('''
def svd_cua_so(r, d=50):                                    # vector PPMI và SVD với cửa sổ r
    M = np.zeros((V, V))                                    # đồng xuất hiện
    for c in C_tr:                                          # mỗi câu
        ids = [id_[w] for w in c if w in id_]               # chỉ số
        for i, a in enumerate(ids):                         # mỗi từ trung tâm
            for j in range(max(0, i - r), min(len(ids), i + r + 1)):   # cửa sổ r
                if j != i:                                  # bỏ chính nó
                    M[a, ids[j]] += 1                       # đếm
    tong = M.sum()                                          # tổng
    with np.errstate(divide="ignore"):                      # log 0
        pmi = np.log(M / tong / np.outer(M.sum(1) / tong, M.sum(0) / tong))   # PMI
    U, S, _ = np.linalg.svd(np.maximum(pmi, 0))             # SVD của PPMI
    E = U[:, :d] * S[:d]                                    # d chiều đầu
    return E / np.linalg.norm(E, axis=1, keepdims=True)     # độ dài 1
E5 = svd_cua_so(5)                                          # cửa sổ 5
for w in ("thầy", "phòng", "nhanh"):                        # ba từ
    print(w, [x for x, _ in gan(w, E5, 5)])                 # hàng xóm mới
''', "thầy ['cô', 'rất', 'dạy', 'hay', 'giảng_bài']\nphòng ['máy', 'chất_lượng', 'trang_thiết_bị', 'nâng_cấp', 'quạt']\nnhanh ['kịp', 'khó', 'hơi', 'giảng_hơi', 'chậm']")
c.bai("40.2", "Cộng hai bảng", "Vector từ là vao + ra; so hàng xóm của tốt và phân loại.",
      "tệ rời khỏi hàng xóm của tốt (cosine 0,588 xuống 0,369), nhưng phân loại không tốt hơn (86,8%). Code ở ô ngay dưới.")
c.o('''
E_tong = (vao.weight + ra.weight).detach().numpy()          # tổng hai bảng
E_tong /= np.linalg.norm(E_tong, axis=1, keepdims=True)     # độ dài 1
print([x for x, _ in gan("tốt", E_tong, 5)], round(float(E_tong[id_["tốt"]] @ E_tong[id_["tệ"]]), 3))   # hàng xóm của tốt, cosine tốt và tệ
print(cham(vector_cau(C_tr, E_tong), vector_cau(C_va, E_tong)))   # phân loại cảm xúc
''', "['truyền_đạt', 'càng', 'phát_huy', 'chất_lượng', 'thuyết_phục'] 0.369\n(0.868, 0.6256)")
c.bai("40.3", "Ghép hai loại đặc trưng", "Ghép TF-IDF với vector trung bình Word2Vec.",
      "90,52% so với 90,59%: không thêm gì, vì vector học trên chính dữ liệu TF-IDF đã thấy. Code ở ô ngay dưới.")
c.o('''
from scipy.sparse import hstack, csr_matrix                 # ghép ma trận thưa
X_tr = hstack([tv.transform(C_tr), csr_matrix(vector_cau(C_tr, E_w2v))]).tocsr()   # 4009 + 50 cột
X_va = hstack([tv.transform(C_va), csr_matrix(vector_cau(C_va, E_w2v))]).tocsr()   # val
print(cham(X_tr, X_va))                                     # độ chính xác, macro-F1
''', "(0.9052, 0.6853)")

c.ghi(Path(__file__).resolve().parents[2] / "notebooks/ch40_word_embeddings.ipynb")
