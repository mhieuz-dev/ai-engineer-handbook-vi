"""Dựng notebooks/ch41_phan_loai_van_ban.ipynb: python3 scripts/notebook/ch41.py"""
from pathlib import Path
from nblib import Chuong, code, khung

c = Chuong(41, "Phân loại văn bản", "ch41-phan-loai-van-ban",
           "Phân loại cảm xúc ba lớp trên UIT-VSFC: baseline, Naive Bayes, hồi quy logistic, SVM; âm tiết hay từ, unigram hay bigram; đọc lỗi và xử lý lớp hiếm; BiLSTM với pack_padded_sequence; chọn trên val và đo test một lần.",
           ["Chọn thước đo hợp với lớp hiếm (macro-F1) trước khi thử mô hình.",
            "Đo xem tách từ và bigram giúp bao nhiêu, và biết khi nào chênh lệch chỉ là nhiễu.",
            "Đọc ma trận nhầm lẫn, trọng số mô hình, những câu sai; dùng trọng số lớp.",
            "Huấn luyện BiLSTM trên chuỗi dài ngắn khác nhau, so công bằng với mô hình tuyến tính."],
           [("Bài toán và baseline", "01-bai-toan-va-baseline"), ("Âm tiết, từ và n-gram", "02-am-tiet-tu-va-n-gram"),
            ("Đọc lỗi và lớp hiếm", "03-doc-loi-va-lop-hiem"), ("BiLSTM và đo test", "04-bilstm-va-do-test"), ("Bài tập", "05-bai-tap")],
           thoi_gian="khoảng 5 phút")

c.mo_trang(1, "Nhãn, thước đo, baseline và ba mô hình tuyến tính.")
c.cells.append(code('''
!pip install -q underthesea                                 # thư viện xử lý tiếng Việt
'''))
c.o('''
import os                                                   # đường dẫn
import time                                                 # đo thời gian
import urllib.request                                       # tải tệp
import numpy as np                                          # mảng
import pandas as pd                                         # bảng
from underthesea import word_tokenize                       # tách từ
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer   # BoW, TF-IDF
from sklearn.linear_model import LogisticRegression         # hồi quy logistic
from sklearn.naive_bayes import MultinomialNB               # Naive Bayes đa thức
from sklearn.svm import LinearSVC                           # SVM tuyến tính
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix, classification_report   # thước đo
URL = "https://huggingface.co/api/datasets/uitnlp/vietnamese_students_feedback/parquet/default/{}/0.parquet"   # UIT-VSFC
THU_MUC = os.path.expanduser("~/.cache/vsfc")               # lưu tạm
def tai(phan):                                              # tải một lần
    os.makedirs(THU_MUC, exist_ok=True)                     # tạo thư mục
    tep = os.path.join(THU_MUC, phan + ".parquet")          # đường dẫn
    if not os.path.exists(tep):                             # chưa có thì tải
        urllib.request.urlretrieve(URL.format(phan), tep)   # tải về
    return pd.read_parquet(tep)                             # đọc
tr, va, te = tai("train"), tai("validation"), tai("test")   # ba phần chia sẵn
y_tr, y_va, y_te = tr.sentiment.values, va.sentiment.values, te.sentiment.values   # nhãn cảm xúc
print(np.bincount(y_tr), np.bincount(y_va), np.round(np.bincount(y_va) / len(y_va), 3))   # số câu mỗi lớp
''', "[5325  458 5643] [705  73 805] [0.445 0.046 0.509]")
c.o('''
def cham(p):                                                # độ chính xác và macro-F1 trên val
    return round(accuracy_score(y_va, p), 4), round(f1_score(y_va, p, average="macro"), 4)   # hai thước đo đã chốt
print("đoán toàn tích cực", cham(np.full(len(y_va), 2)))    # baseline lớp đông nhất
''', "đoán toàn tích cực (0.5085, 0.2247)")
c.o('''
noi = lambda ds: [" ".join(w.replace(" ", "_") for w in word_tokenize(c)) for c in ds]   # tách từ, nối bằng dấu cách
W_tr, W_va, W_te = noi(tr.sentence), noi(va.sentence), noi(te.sentence)   # khoảng 5 giây
cv = CountVectorizer(analyzer=str.split)                    # số đếm cho Naive Bayes
tv = TfidfVectorizer(analyzer=str.split)                    # TF-IDF cho hai mô hình kia
B_tr, B_va = cv.fit_transform(W_tr), cv.transform(W_va)     # đếm
T_tr, T_va = tv.fit_transform(W_tr), tv.transform(W_va)     # TF-IDF
print("Naive Bayes ", cham(MultinomialNB().fit(B_tr, y_tr).predict(B_va)))   # Naive Bayes
print("Logistic    ", cham(LogisticRegression(max_iter=2000).fit(T_tr, y_tr).predict(T_va)))   # hồi quy logistic
print("SVM tuyến tính", cham(LinearSVC().fit(T_tr, y_tr).predict(T_va)))   # SVM
''', "Naive Bayes  (0.8756, 0.6296)\nLogistic     (0.9065, 0.7123)\nSVM tuyến tính (0.9071, 0.7464)")

c.mo_trang(2, "Âm tiết hay từ, unigram hay bigram, và mức nhiễu của val.")
c.o('''
def thu(X_tr, X_va, ngram, mo_hinh):                        # một cấu hình đặc trưng và mô hình
    tv = TfidfVectorizer(token_pattern=r"\\S+", ngram_range=(1, ngram))   # mọi chuỗi không khoảng trắng là một token
    return cham(mo_hinh.fit(tv.fit_transform(X_tr), y_tr).predict(tv.transform(X_va)))   # học trên train, chấm trên val
ket_qua = {}                                                # lưu kết quả
for don_vi, (X_tr, X_va) in (("âm tiết", (tr.sentence, va.sentence)), ("từ", (W_tr, W_va))):   # hai đơn vị
    for ngram in (1, 2):                                    # unigram, unigram cộng bigram
        for ten, mh in (("Logistic", LogisticRegression(max_iter=2000)), ("SVM", LinearSVC())):   # hai mô hình
            ket_qua[(don_vi, ngram, ten)] = thu(X_tr, X_va, ngram, mh)   # chạy
            print(don_vi, ngram, ten, ket_qua[(don_vi, ngram, ten)])   # in
''', "âm tiết 1 Logistic (0.9078, 0.7071)\nâm tiết 1 SVM (0.9141, 0.7695)\nâm tiết 2 Logistic (0.9122, 0.6926)\nâm tiết 2 SVM (0.9191, 0.778)\ntừ 1 Logistic (0.9065, 0.7123)\ntừ 1 SVM (0.9071, 0.7464)\ntừ 2 Logistic (0.9109, 0.6775)\ntừ 2 SVM (0.9191, 0.7827)",
    khung("doc", ["Tách từ không giúp: với bigram, SVM đạt đúng 91,91% ở cả hai mức, vì bigram âm tiết đã chứa sẵn từ ghép."]))
c.o('''
p, n = 0.91, len(y_va)                                      # độ chính xác quanh 91%, 1583 câu
print(round(np.sqrt(p * (1 - p) / n), 4))                   # độ lệch chuẩn của độ chính xác đo được
''', "0.0072")
c.o('''
tv_am = TfidfVectorizer(token_pattern=r"\\S+", ngram_range=(1, 2))   # mô hình được chọn: bigram âm tiết
A_tr, A_va = tv_am.fit_transform(tr.sentence), tv_am.transform(va.sentence)   # đặc trưng
svm = LinearSVC().fit(A_tr, y_tr)                           # SVM
p_svm = svm.predict(A_va)                                   # dự đoán val
print(A_tr.shape, cham(p_svm))                              # số đặc trưng, kết quả
''', "(11426, 34113) (0.9191, 0.778)")

c.mo_trang(3, "Báo cáo từng lớp, trọng số lớp, trọng số đặc trưng, câu sai.")
c.o('''
TEN = ["tiêu cực", "trung tính", "tích cực"]                # tên ba lớp
print(classification_report(y_va, p_svm, target_names=TEN, digits=3))   # precision, recall, F1 từng lớp
print(confusion_matrix(y_va, p_svm))                        # hàng thật, cột đoán
''', "precision    recall  f1-score   support\n\n    tiêu cực      0.912     0.946     0.929       705\n  trung tính      0.800     0.329     0.466        73\n    tích cực      0.929     0.949     0.939       805\n\n    accuracy                          0.919      1583\n   macro avg      0.881     0.741     0.778      1583\nweighted avg      0.916     0.919     0.913      1583\n\n[[667   2  36]\n [ 27  24  22]\n [ 37   4 764]]",
    khung("doc", ["Lớp trung tính chỉ có recall 0,329: mô hình bắt được 24 trên 73 câu. Độ chính xác 91,9% che hoàn toàn chuyện đó."]))
c.o('''
svm_cb = LinearSVC(class_weight="balanced").fit(A_tr, y_tr) # phạt lỗi lớp hiếm nặng hơn
p_cb = svm_cb.predict(A_va)                                 # dự đoán val
print(cham(p_cb))                                           # độ chính xác, macro-F1
print(confusion_matrix(y_va, p_cb))                         # ma trận nhầm lẫn mới
''', "(0.9185, 0.8013)\n[[663   8  34]\n [ 22  34  17]\n [ 36  12 757]]")
c.o('''
ten_dt = tv_am.get_feature_names_out()                      # tên các n-gram
for lop in (0, 2):                                          # tiêu cực, tích cực
    print(TEN[lop], list(ten_dt[np.argsort(svm.coef_[lop])[::-1][:10]]))   # mười trọng số lớn nhất
''', "tiêu cực ['chưa', 'không', 'nên', 'cần', 'khó', 'ít', 'thiếu', 'hơi', 'quá', 'hơn']\ntích cực ['tốt', 'rất', 'vui', 'giúp', 'nhiệt', 'dễ', 'không nhàm', 'hay .', 'luôn', 'tình']")
c.o('''
sai = np.where(p_svm != y_va)[0]                            # chỉ số các câu sai
for i in sai[:8]:                                           # tám câu đầu
    print(TEN[y_va[i]], "->", TEN[p_svm[i]], "|", va.sentence[i])   # nhãn thật, nhãn đoán, câu
''', "trung tính -> tiêu cực | em không có bất cứ một lời phê bình nào .\ntiêu cực -> tích cực | đôi khi giảng dạy quá nhiệt tình mà quên mất cả thời gian ( hết giờ học giảng viên vẫn dạy thêm 10 - 15 phút ) .\ntrung tính -> tiêu cực | thầy cho tự tìm hiểu , và tự tìm hiểu khác với hiểu được vấn đề .\ntiêu cực -> tích cực | không đi đúng giờ .\ntiêu cực -> tích cực | cô rất nghiêm .\ntích cực -> tiêu cực | ngoài ra cung cấp một vài thông tin bổ sung về việc học công nghệ thông tin hiệu quả hơn .\ntích cực -> tiêu cực | thúc đẩy sinh viên tự học đạt điểm cao trong các kỳ thi .\ntiêu cực -> tích cực | giảng viên nói tiếng anh không hay .")

c.mo_trang(4, "BiLSTM với pack_padded_sequence (khoảng 70 giây), rồi chọn và đo test một lần.")
c.o('''
import copy                                                 # sao chép mô hình
import torch                                                # PyTorch
import torch.nn as nn                                       # các lớp mạng
import torch.nn.functional as F                             # hàm loss
from collections import Counter                             # đếm
from torch.nn.utils.rnn import pack_padded_sequence, pad_sequence   # xử lý chuỗi dài ngắn khác nhau
torch.set_num_threads(1)                                    # một luồng, kết quả lặp lại được
D_tr, D_va, D_te = ([s.split() for s in ds.sentence] for ds in (tr, va, te))   # âm tiết
dem = Counter(w for c in D_tr for w in c)                   # tần suất trên train
tu = ["<pad>", "<unk>"] + [w for w, n in dem.items() if n >= 2]   # từ điển, 0 là đệm, 1 là lạ
id_ = {w: i for i, w in enumerate(tu)}                      # âm tiết sang chỉ số
ma_hoa = lambda D: [torch.tensor([id_.get(w, 1) for w in c] or [1]) for c in D]   # âm tiết lạ thành <unk>
X_tr, X_va, X_te = ma_hoa(D_tr), ma_hoa(D_va), ma_hoa(D_te) # ba phần
def lo(X, idx):                                             # đệm một lô, kèm độ dài thật
    xs = [X[i] for i in idx]                                # các câu
    return pad_sequence(xs, batch_first=True), torch.tensor([len(x) for x in xs])   # tensor đã đệm, độ dài
class BiLSTM(nn.Module):                                    # LSTM hai chiều
    def __init__(self, V, d=100, h=128):                    # cỡ từ điển, chiều vector, chiều ẩn
        super().__init__()                                  # khởi tạo
        self.emb = nn.Embedding(V, d, padding_idx=0)        # bảng vector, đệm luôn bằng 0
        self.lstm = nn.LSTM(d, h, batch_first=True, bidirectional=True)   # đọc hai chiều
        self.ra = nn.Linear(2 * h, 3)                       # ba lớp
    def forward(self, x, dai):                              # x: lô đã đệm, dai: độ dài thật
        goi = pack_padded_sequence(self.emb(x), dai, batch_first=True, enforce_sorted=False)   # bỏ qua phần đệm
        _, (h_cuoi, _) = self.lstm(goi)                     # trạng thái ở từ cuối thật, hai chiều
        return self.ra(torch.cat([h_cuoi[0], h_cuoi[1]], 1))   # ghép hai chiều
x, dai = lo(X_va, [0, 1, 2])                                # ba câu đầu của val
print(len(tu), x.shape, dai.tolist())                       # cỡ từ điển, kích thước lô, độ dài
''', "1535 torch.Size([3, 8]) [6, 4, 8]")
c.o('''
def du_doan(m, X):                                          # dự đoán cả một tập
    m.eval()                                                # chế độ đánh giá
    with torch.no_grad():                                   # không cần gradient
        x, dai = lo(X, range(len(X)))                       # một lô lớn
        return m(x, dai).argmax(1).numpy()                  # lớp có điểm cao nhất
def huan_luyen(seed, so_epoch=8):                           # huấn luyện, giữ bản tốt nhất trên val
    torch.manual_seed(seed)                                 # khởi tạo và thứ tự lô
    m = BiLSTM(len(tu))                                     # mô hình
    opt = torch.optim.Adam(m.parameters(), lr=2e-3, fused=True)   # fused: lặp lại được trên CPU
    y_t = torch.tensor(y_tr)                                # nhãn dạng tensor
    tot, ban_tot = -1, None                                 # macro-F1 tốt nhất, bản tương ứng
    for ep in range(1, so_epoch + 1):                       # mỗi epoch
        m.train()                                           # chế độ huấn luyện
        thu_tu = torch.randperm(len(X_tr))                  # xáo trộn
        for k in range(0, len(thu_tu), 64):                 # lô 64 câu
            idx = thu_tu[k:k + 64]                          # chỉ số
            x, dai = lo(X_tr, idx)                          # đệm
            loss = F.cross_entropy(m(x, dai), y_t[idx])     # cross-entropy ba lớp
            opt.zero_grad()                                 # xóa gradient
            loss.backward()                                 # lượt ngược
            opt.step()                                      # cập nhật
        acc, f1 = cham(du_doan(m, X_va))                    # đo val
        print(ep, acc, f1)                                  # in
        if f1 > tot:                                        # tốt hơn mọi epoch trước
            tot, ban_tot = f1, copy.deepcopy(m)             # giữ bản này
    return ban_tot                                          # bản tốt nhất
t0 = time.time()                                            # đo thời gian
ban_tot = huan_luyen(0)                                     # seed 0
print(time.time() - t0 < 300)                               # dưới 5 phút
''', "1 0.9015 0.6907\n2 0.9122 0.759\n3 0.9027 0.7465\n4 0.916 0.7891\n5 0.9084 0.7893\n6 0.9116 0.7788\n7 0.9065 0.7765\n8 0.9198 0.7986\nTrue")
c.o('''
ung_vien = {"SVM": (p_svm, lambda: svm.predict(tv_am.transform(te.sentence))),   # dự đoán val, cách dự đoán test
            "SVM cân bằng": (p_cb, lambda: svm_cb.predict(tv_am.transform(te.sentence))),   # ứng viên thứ hai
            "BiLSTM": (du_doan(ban_tot, X_va), lambda: du_doan(ban_tot, X_te))}   # ứng viên thứ ba
chon = max(ung_vien, key=lambda k: f1_score(y_va, ung_vien[k][0], average="macro"))   # chọn theo macro-F1 trên val
print("chọn:", chon)                                        # mô hình được chọn
for ten, (_, test) in ung_vien.items():                     # đo test một lần
    p = test()                                              # dự đoán test
    print(ten, round(accuracy_score(y_te, p), 4), round(f1_score(y_te, p, average="macro"), 4))   # độ chính xác, macro-F1
''', "chọn: SVM cân bằng\nSVM 0.8951 0.7063\nSVM cân bằng 0.8967 0.7531\nBiLSTM 0.903 0.7461",
    khung("doc", ["Mô hình được chọn trên val (SVM cân bằng) đạt 89,67%, macro-F1 0,753 trên test. Hai dòng còn lại chỉ để tham khảo."]))

c.mo_trang(5, "Ba bài tập. Đoán trước, rồi mới mở đáp án.")
c.bai("41.1", "Phân loại chủ đề", "Cùng quy trình SVM bigram âm tiết cho nhãn chủ đề.",
      "87,7%, macro-F1 0,756; lớp khác chỉ đúng 30 trên 95 câu. Code ở ô ngay dưới.")
c.o('''
yc_tr, yc_va = tr.topic.values, va.topic.values             # nhãn chủ đề
tvc = TfidfVectorizer(token_pattern=r"\\S+", ngram_range=(1, 2))   # bigram âm tiết
pc = LinearSVC().fit(tvc.fit_transform(tr.sentence), yc_tr).predict(tvc.transform(va.sentence))   # SVM
print(np.bincount(yc_va), round(accuracy_score(yc_va, pc), 4), round(f1_score(yc_va, pc, average="macro"), 4))   # số câu mỗi lớp, hai thước đo
print(confusion_matrix(yc_va, pc))                          # ma trận nhầm lẫn
''', "[1151  267   70   95] 0.8774 0.756\n[[1089   52    3    7]\n [  53  207    2    5]\n [   4    3   63    0]\n [  44   19    2   30]]")
c.bai("41.2", "So hai mô hình trên cùng các câu", "Bootstrap theo cặp: SVM bigram âm tiết với hồi quy logistic unigram từ.",
      "SVM hơn 1,26 điểm, dương ở 98,6% số lần lấy mẫu lại, khoảng 95% từ 0,19 tới 2,40 điểm. Code ở ô ngay dưới.")
c.o('''
tv1 = TfidfVectorizer(analyzer=str.split)                   # unigram từ như trang 1
p_lr = LogisticRegression(max_iter=2000).fit(tv1.fit_transform(W_tr), tr.sentiment.values).predict(tv1.transform(W_va))   # hồi quy logistic
dung_svm, dung_lr = (p_svm == y_va), (p_lr == y_va)         # đúng hay sai ở từng câu
rng = np.random.default_rng(0)                              # ngẫu nhiên
hieu = []                                                   # hiệu độ chính xác mỗi lần
for _ in range(2000):                                       # 2000 lần lấy mẫu lại
    idx = rng.integers(len(y_va), size=len(y_va))           # cùng một mẫu câu cho cả hai mô hình
    hieu.append(dung_svm[idx].mean() - dung_lr[idx].mean()) # hiệu
hieu = np.array(hieu)                                       # sang mảng
print(round(dung_svm.mean() - dung_lr.mean(), 4), round((hieu > 0).mean(), 3), np.percentile(hieu, [2.5, 97.5]).round(4))   # hiệu, tỷ lệ dương, khoảng 95%
print(int((dung_svm & ~dung_lr).sum()), int((~dung_svm & dung_lr).sum()))   # số câu hai mô hình bất đồng
''', "0.0126 0.986 [0.0019 0.024 ]\n48 28")
c.bai("41.3", "BiLSTM đổi theo seed", "Huấn luyện lại với seed 1 và 2.",
      "Macro-F1 tốt nhất 0,799, 0,795, 0,784: dao động gần bằng khoảng cách với SVM. Code ở ô ngay dưới (khoảng 2,5 phút).")
c.o('''
for seed in (1, 2):                                         # hai seed khác
    m_s = huan_luyen(seed)                                  # huấn luyện lại
    print("seed", seed, cham(du_doan(m_s, X_va)))           # bản tốt nhất trên val
''', "1 0.909 0.7368\n2 0.9109 0.7743\n3 0.9217 0.7762\n4 0.9109 0.7791\n5 0.9071 0.7589\n6 0.9135 0.789\n7 0.9084 0.7701\n8 0.9172 0.7951\nseed 1 (0.9172, 0.7951)\n1 0.8951 0.6985\n2 0.9103 0.7647\n3 0.9128 0.7839\n4 0.9103 0.7647\n5 0.892 0.745\n6 0.909 0.7609\n7 0.9141 0.7839\n8 0.9116 0.7843\nseed 2 (0.9116, 0.7843)")

c.ghi(Path(__file__).resolve().parents[2] / "notebooks/ch41_phan_loai_van_ban.ipynb")
