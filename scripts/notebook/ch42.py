"""Dựng notebooks/ch42_gan_nhan_chuoi.ipynb: python3 scripts/notebook/ch42.py"""
from pathlib import Path
from nblib import Chuong, code, khung

c = Chuong(42, "Gán nhãn chuỗi", "ch42-gan-nhan-chuoi",
           "Gán nhãn từ loại trên Vietnamese Treebank (Universal Dependencies): baseline, HMM với Viterbi tự cài, CRF với đặc trưng tự chọn. Rồi dùng CRF để tách từ tiếng Việt theo lược đồ B/I và so với underthesea.",
           ["Đọc dữ liệu CoNLL-U, hiểu lược đồ BIO.",
            "Cài HMM và thuật toán Viterbi, xử lý từ chưa gặp bằng hapax.",
            "Huấn luyện CRF bằng python-crfsuite, đọc trọng số, đo test một lần.",
            "Tách từ bằng CRF, chấm bằng F1 trên từ, và nhận ra nguy cơ rò rỉ dữ liệu khi so với mô hình công bố sẵn."],
           [("Gán nhãn chuỗi", "01-gan-nhan-chuoi"), ("HMM và Viterbi", "02-hmm-va-viterbi"), ("CRF", "03-crf"),
            ("Tách từ bằng CRF", "04-tach-tu-bang-crf"), ("Bài tập", "05-bai-tap")],
           thoi_gian="khoảng 30 giây")

c.mo_trang(1, "Tải UD_Vietnamese-VTB, đếm nhãn, baseline nhãn hay gặp nhất.")
c.cells.append(code('''
!pip install -q python-crfsuite underthesea                 # thư viện CRF và xử lý tiếng Việt
'''))
c.o('''
import math                                                 # log
import os                                                   # đường dẫn
import time                                                 # đo thời gian
import urllib.request                                       # tải tệp
from collections import Counter, defaultdict                # đếm
import numpy as np                                          # mảng
URL = ("https://raw.githubusercontent.com/UniversalDependencies/UD_Vietnamese-VTB/"
       "3c971fd1c5d03561e00b267d3d0057b81a9bea84/vi_vtb-ud-{}.conllu")   # ghim commit
THU_MUC = os.path.expanduser("~/.cache/ud_vi")              # lưu tạm
def doc(phan):                                              # danh sách câu, mỗi câu là danh sách (từ, nhãn)
    os.makedirs(THU_MUC, exist_ok=True)                     # tạo thư mục
    tep = os.path.join(THU_MUC, f"vi_vtb-ud-{phan}.conllu") # đường dẫn
    if not os.path.exists(tep):                             # chưa có thì tải
        urllib.request.urlretrieve(URL.format(phan), tep)   # tải về
    cau, hien = [], []                                      # các câu, câu đang đọc
    for dong in open(tep, encoding="utf-8"):                # mỗi dòng
        dong = dong.rstrip("\\n")                            # bỏ xuống dòng
        if not dong:                                        # dòng trống: hết một câu
            if hien:                                        # có câu đang đọc
                cau.append(hien)                            # lưu
                hien = []                                   # câu mới
        elif not dong.startswith("#"):                      # bỏ dòng chú thích
            cot = dong.split("\\t")                          # các cột
            if cot[0].isdigit():                            # dòng một từ
                hien.append((cot[1], cot[3]))               # từ, nhãn UPOS
    return cau                                              # mọi câu
tr, dv, te = doc("train"), doc("dev"), doc("test")          # ba phần
dem_nhan = Counter(t for c in tr for _, t in c)             # đếm nhãn trên train
print(len(tr), len(dv), len(te), sum(map(len, tr)))         # số câu, số từ train
print(tr[0][:8])                                            # tám từ đầu
print(dem_nhan.most_common())                               # 17 nhãn
''', "1400 1123 800 20215\n[('Tôi', 'PRON'), ('nhớ', 'VERB'), ('lời', 'NOUN'), ('anh', 'NOUN'), ('chủ tịch', 'NOUN'), ('xã', 'NOUN'), ('Bùi Văn Luyến', 'PROPN'), ('nhắc', 'VERB')]\n[('NOUN', 5617), ('VERB', 3821), ('PUNCT', 2931), ('ADV', 1481), ('ADP', 1207), ('ADJ', 1097), ('PROPN', 895), ('PRON', 803), ('NUM', 622), ('SCONJ', 501), ('AUX', 475), ('DET', 300), ('CCONJ', 256), ('PART', 106), ('X', 67), ('SYM', 33), ('INTJ', 3)]")
c.o('''
nhan_cua = defaultdict(Counter)                             # với mỗi từ: đếm các nhãn nó mang
for c in tr:                                                # mỗi câu train
    for w, t in c:                                          # mỗi từ
        nhan_cua[w.lower()][t] += 1                         # đếm
NHAN_NHIEU = dem_nhan.most_common(1)[0][0]                  # nhãn phổ biến nhất
def baseline(c):                                            # nhãn hay gặp nhất của từ, NOUN nếu từ lạ
    return [nhan_cua[w.lower()].most_common(1)[0][0] if w.lower() in nhan_cua else NHAN_NHIEU for w, _ in c]   # từng từ
def do(ds, gan):                                            # độ chính xác chung, trên từ chưa gặp, số từ chưa gặp
    dung = n = dung_la = n_la = 0                           # bộ đếm
    for c in ds:                                            # mỗi câu
        for (w, t), q in zip(c, gan(c)):                    # nhãn thật, nhãn đoán
            dung, n = dung + (t == q), n + 1                # đếm chung
            if w.lower() not in nhan_cua:                   # từ chưa gặp trong train
                dung_la, n_la = dung_la + (t == q), n_la + 1   # đếm riêng
    return round(dung / n, 4), round(dung_la / n_la, 4), n_la   # ba con số
print(do(dv, baseline))                                     # trên dev
''', "(0.8118, 0.43, 4449)")

c.mo_trang(2, "HMM, Viterbi, và hai cách xử lý từ chưa gặp.")
c.o('''
NHAN = sorted(dem_nhan)                                     # danh sách nhãn
so = {t: i for i, t in enumerate(NHAN)}                     # nhãn sang chỉ số
K = len(NHAN)                                               # số nhãn
chuyen = np.full((K + 1, K), 0.1)                           # hàng cuối là "đầu câu"; làm trơn add-0,1
phat = defaultdict(lambda: np.zeros(K))                     # với mỗi từ: số lần đi với từng nhãn
for c in tr:                                                # mỗi câu
    truoc = K                                               # bắt đầu từ "đầu câu"
    for w, t in c:                                          # mỗi từ
        chuyen[truoc, so[t]] += 1                           # đếm chuyển
        phat[w.lower()][so[t]] += 1                         # đếm phát
        truoc = so[t]                                       # sang từ sau
log_chuyen = np.log(chuyen / chuyen.sum(1, keepdims=True))  # log xác suất chuyển
so_lan_nhan = np.array([dem_nhan[t] for t in NHAN], dtype=float)   # số lần mỗi nhãn
V_tu = len(phat)                                            # số từ khác nhau
print(K, V_tu, NHAN[np.exp(log_chuyen[so["ADV"]]).argmax()], NHAN[np.exp(log_chuyen[K]).argmax()])   # nhãn hay đi sau ADV, nhãn hay mở đầu câu
''', "17 3398 VERB NOUN")
c.o('''
def viterbi(c, log_phat):                                   # chuỗi nhãn tốt nhất
    n = len(c)                                              # số từ
    delta, quay_lui = np.zeros((n, K)), np.zeros((n, K), dtype=int)   # điểm tốt nhất, con trỏ
    delta[0] = log_chuyen[K] + log_phat(c[0][0])            # bước đầu
    for i in range(1, n):                                   # mỗi vị trí sau
        diem = delta[i - 1][:, None] + log_chuyen[:K]       # diem[t', t]: đi từ t' sang t
        quay_lui[i] = diem.argmax(0)                        # nhãn trước tốt nhất
        delta[i] = diem.max(0) + log_phat(c[i][0])          # cộng xác suất phát
    y = [int(delta[-1].argmax())]                           # nhãn cuối tốt nhất
    for i in range(n - 1, 0, -1):                           # đi ngược
        y.append(quay_lui[i][y[-1]])                        # theo con trỏ
    return [NHAN[k] for k in y[::-1]]                       # đúng thứ tự
def phat_ngay_tho(w, k=0.1):                                # add-k cho mọi từ
    e = phat[w.lower()] if w.lower() in phat else np.zeros(K)   # đếm, 0 nếu từ lạ
    return np.log((e + k) / (so_lan_nhan + k * (V_tu + 1))) # log xác suất phát
print(do(dv, lambda c: viterbi(c, phat_ngay_tho)))          # trên dev
''', "(0.7809, 0.2018, 4449)",
    khung("loi", ["Tệ hơn baseline: với từ lạ, add-k cho xác suất phát lớn nhất ở nhãn hiếm nhất."], "TỪ CHƯA GẶP"))
c.o('''
dem_tu = Counter(w.lower() for c in tr for w, _ in c)       # tần suất từ
hapax = np.zeros(K)                                         # nhãn của những từ chỉ gặp một lần
for c in tr:                                                # mỗi câu
    for w, t in c:                                          # mỗi từ
        if dem_tu[w.lower()] == 1:                          # hapax
            hapax[so[t]] += 1                               # đếm nhãn
p_la = (hapax + 0.1) / (hapax + 0.1).sum()                  # P(nhãn | từ lạ)
log_phat_la = np.log(p_la) - np.log(so_lan_nhan)            # tỷ lệ với P(từ lạ | nhãn), theo Bayes
def phat_hapax(w):                                          # xác suất phát dùng hapax cho từ lạ
    if w.lower() not in phat:                               # từ lạ
        return log_phat_la                                  # phân phối của hapax
    return np.log((phat[w.lower()] + 1e-3) / (so_lan_nhan + 1e-3 * V_tu))   # từ đã gặp: làm trơn rất nhẹ
print([(NHAN[i], round(p_la[i], 3)) for i in np.argsort(-p_la)[:5]])   # năm nhãn hay gặp ở hapax
print(do(dv, lambda c: viterbi(c, phat_hapax)))             # trên dev
''', "[('NOUN', np.float64(0.351)), ('VERB', np.float64(0.327)), ('ADJ', np.float64(0.161)), ('PROPN', np.float64(0.077)), ('NUM', np.float64(0.038))]\n(0.8138, 0.4026, 4449)")

c.mo_trang(3, "CRF bằng python-crfsuite, đọc trọng số, đo test một lần.")
c.o('''
import pycrfsuite                                           # CRFsuite
def dac_trung(c, i):                                        # đặc trưng của từ thứ i
    w = c[i][0]                                             # từ
    f = ["bias", "w=" + w.lower(), "dau=" + w.lower().split()[0], "cuoi=" + w.lower().split()[-1]]   # từ, âm tiết đầu, cuối
    if w[:1].isupper():                                     # viết hoa
        f.append("hoa")                                     # gợi ý tên riêng
    if any(ch.isdigit() for ch in w):                       # có chữ số
        f.append("so")                                      # gợi ý số
    if " " in w:                                            # nhiều âm tiết
        f.append("nhieu_am_tiet")                           # từ ghép
    f.append("w-1=" + c[i - 1][0].lower() if i > 0 else "dau_cau")   # từ trước
    f.append("w+1=" + c[i + 1][0].lower() if i < len(c) - 1 else "cuoi_cau")   # từ sau
    return f                                                # danh sách đặc trưng
print(dac_trung(tr[0], 4))                                  # đặc trưng của "chủ tịch"
''', "['bias', 'w=chủ tịch', 'dau=chủ', 'cuoi=tịch', 'nhieu_am_tiet', 'w-1=anh', 'w+1=xã']")
c.o('''
t0 = time.time()                                            # đo thời gian
hoc = pycrfsuite.Trainer(verbose=False)                     # bộ huấn luyện
for c in tr:                                                # mỗi câu train
    hoc.append([dac_trung(c, i) for i in range(len(c))], [t for _, t in c])   # đặc trưng và nhãn
hoc.set_params({"c1": 0.1, "c2": 0.01, "max_iterations": 100})   # điều chuẩn L1, L2
hoc.train("pos.crfsuite")                                   # học, lưu ra tệp
gan_nhan = pycrfsuite.Tagger()                              # bộ gán nhãn
gan_nhan.open("pos.crfsuite")                               # mở mô hình
crf = lambda c: gan_nhan.tag([dac_trung(c, i) for i in range(len(c))])   # gán nhãn một câu
print(do(dv, crf), time.time() - t0 < 60)                   # trên dev
''', "(0.8551, 0.6267, 4449) True")
c.o('''
info = gan_nhan.info()                                      # trọng số đã học
manh = sorted(info.state_features.items(), key=lambda x: -x[1])   # đặc trưng trạng thái
print([(f, t, round(v, 2)) for (f, t), v in manh[:8]])      # tám trọng số lớn nhất
chuyen_crf = sorted(info.transitions.items(), key=lambda x: -x[1])   # cặp nhãn liền nhau
print([(a, b, round(v, 2)) for (a, b), v in chuyen_crf[:5]])   # năm cặp được ưa nhất
''', "[('so', 'NUM', 11.37), ('w+1=gd', 'PROPN', 10.15), ('w-1=lương bổng', 'PART', 9.34), ('w+1=hồng lĩnh', 'PROPN', 9.0), ('w-1=thứ', 'NUM', 7.84), ('dau=nếu', 'SCONJ', 7.75), ('hoa', 'PROPN', 7.45), ('w-1=tiếc', 'PART', 7.08)]\n[('PROPN', 'CCONJ', 3.39), ('NUM', 'SYM', 3.22), ('ADJ', 'CCONJ', 3.21), ('NOUN', 'CCONJ', 2.7), ('VERB', 'CCONJ', 2.7)]")
c.o('''
for ten, gan in (("baseline", baseline), ("HMM", lambda c: viterbi(c, phat_hapax)), ("CRF", crf)):   # ba mô hình
    print(ten, do(te, gan))                                 # đo test một lần
''', "baseline (0.823, 0.3446, 1506)\nHMM (0.8366, 0.3964, 1506)\nCRF (0.8795, 0.66, 1506)")

c.mo_trang(4, "Tách từ là gán nhãn B/I trên âm tiết.")
c.o('''
def bio(c):                                                 # câu đã tách từ thành (âm tiết, nhãn B/I)
    am, nh = [], []                                         # âm tiết, nhãn
    for w, _ in c:                                          # mỗi từ
        for k, s in enumerate(w.split()):                   # mỗi âm tiết của từ
            am.append(s)                                    # âm tiết
            nh.append("B" if k == 0 else "I")               # đầu từ là B
    return am, nh                                           # hai danh sách
print(bio(tr[0][:8]))                                       # tám từ đầu
''', "(['Tôi', 'nhớ', 'lời', 'anh', 'chủ', 'tịch', 'xã', 'Bùi', 'Văn', 'Luyến', 'nhắc'], ['B', 'B', 'B', 'B', 'B', 'I', 'B', 'B', 'I', 'I', 'B'])")
c.o('''
def dt_am(am, i):                                           # đặc trưng của âm tiết thứ i
    s = am[i].lower()                                       # âm tiết
    f = ["bias", "s=" + s]                                  # chính nó
    if am[i][:1].isupper():                                 # viết hoa
        f.append("hoa")                                     # đặc trưng hoa
    if am[i].isdigit():                                     # là số
        f.append("so")                                      # đặc trưng số
    for d in (-2, -1, 1, 2):                                # hai âm tiết mỗi bên
        j = i + d                                           # vị trí
        f.append(f"s{d}=" + (am[j].lower() if 0 <= j < len(am) else "#"))   # # nếu ra ngoài câu
    if i > 0:                                               # có âm tiết trước
        f.append("cap_truoc=" + am[i - 1].lower() + "_" + s)   # cặp với âm tiết trước
    if i < len(am) - 1:                                     # có âm tiết sau
        f.append("cap_sau=" + s + "_" + am[i + 1].lower())  # cặp với âm tiết sau
    return f                                                # danh sách đặc trưng
hoc_tach = pycrfsuite.Trainer(verbose=False)                # bộ huấn luyện tách từ
for c in tr:                                                # mỗi câu train
    am, nh = bio(c)                                         # âm tiết và nhãn
    hoc_tach.append([dt_am(am, i) for i in range(len(am))], nh)   # thêm vào
hoc_tach.set_params({"c1": 0.1, "c2": 0.01, "max_iterations": 100})   # như trang 3
hoc_tach.train("tach_tu.crfsuite")                          # học
tach_crf = pycrfsuite.Tagger()                              # bộ gán nhãn
tach_crf.open("tach_tu.crfsuite")                           # mở
crf_tach = lambda am: tach_crf.tag([dt_am(am, i) for i in range(len(am))])   # tách một câu
def khoang(nh):                                             # nhãn B/I thành tập (đầu, cuối) của các từ
    ra, dau = set(), None                                   # tập từ, vị trí đầu từ hiện tại
    for i, l in enumerate(nh):                              # mỗi âm tiết
        if l == "B":                                        # mở đầu từ mới
            if dau is not None:                             # đóng từ trước
                ra.add((dau, i))                            # thêm
            dau = i                                         # từ mới bắt đầu
    ra.add((dau, len(nh)))                                  # từ cuối câu
    return ra                                               # tập các từ
def f1_tu(ds, tach):                                        # precision, recall, F1 trên từ
    dung = du = that = 0                                    # bộ đếm
    for c in ds:                                            # mỗi câu
        am, nh = bio(c)                                     # âm tiết, nhãn thật
        a, b = khoang(nh), khoang(tach(am))                 # từ thật, từ đoán
        dung, du, that = dung + len(a & b), du + len(b), that + len(a)   # đếm
    P, R = dung / du, dung / that                           # precision, recall
    return round(P, 4), round(R, 4), round(2 * P * R / (P + R), 4)   # ba con số
print("toàn B", f1_tu(dv, lambda am: ["B"] * len(am)))      # mỗi âm tiết một từ
print("CRF   ", f1_tu(dv, crf_tach))                        # CRF
''', "toàn B (0.6473, 0.7899, 0.7115)\nCRF    (0.8568, 0.8806, 0.8686)")
c.o('''
from underthesea import word_tokenize                       # bộ tách từ công bố sẵn
def tach_uts(am):                                           # tách bằng underthesea, đổi thành nhãn B/I
    nh = []                                                 # nhãn
    for w in word_tokenize(" ".join(am)):                   # đưa vào cùng chuỗi âm tiết
        nh += ["B"] + ["I"] * (len(w.split()) - 1)          # từ n âm tiết: B rồi n - 1 cái I
    return nh if len(nh) == len(am) else ["B"] * len(am)    # phòng khi số âm tiết lệch
for ten, tach in (("toàn B", lambda am: ["B"] * len(am)), ("CRF", crf_tach), ("underthesea", tach_uts)):   # ba cách
    print(ten, f1_tu(te, tach))                             # đo trên test
''', "toàn B (0.6937, 0.8222, 0.7525)\nCRF (0.8862, 0.9001, 0.8931)\nunderthesea (0.9594, 0.9548, 0.9571)",
    khung("loi", ["underthesea có thể đã học trên dữ liệu chồng lấn với Vietnamese Treebank, nên con số 95,7% có thể lạc quan."], "RÒ RỈ DỮ LIỆU"))

c.mo_trang(5, "Ba bài tập. Đoán trước, rồi mới mở đáp án.")
c.bai("42.1", "Viterbi bằng tay", "HMM đồ chơi hai nhãn N, V cho câu 'cá bơi'.",
      "Chuỗi tốt nhất N V với xác suất 0,147; Viterbi cho cùng đáp án. Code ở ô ngay dưới.")
c.o('''
from itertools import product                               # liệt kê mọi tổ hợp
dau = {"N": 0.7, "V": 0.3}                                  # xác suất đầu câu
cv = {("N", "N"): 0.3, ("N", "V"): 0.7, ("V", "N"): 0.6, ("V", "V"): 0.4}   # xác suất chuyển
pt = {("N", "cá"): 0.6, ("V", "cá"): 0.1, ("N", "bơi"): 0.1, ("V", "bơi"): 0.5}   # xác suất phát
cau_do_choi = ["cá", "bơi"]                                 # câu hai từ
for t1, t2 in product("NV", repeat=2):                      # bốn chuỗi nhãn
    print(t1 + t2, round(dau[t1] * pt[(t1, "cá")] * cv[(t1, t2)] * pt[(t2, "bơi")], 4))   # xác suất chung
d1 = {t: dau[t] * pt[(t, "cá")] for t in "NV"}              # Viterbi bước 1
d2 = {t: max(d1[s] * cv[(s, t)] for s in "NV") * pt[(t, "bơi")] for t in "NV"}   # bước 2
print({t: round(v, 4) for t, v in d1.items()}, {t: round(v, 4) for t, v in d2.items()})   # hai bước
''', "NN 0.0126\nNV 0.147\nVN 0.0018\nVV 0.006\n{'N': 0.42, 'V': 0.03} {'N': 0.0126, 'V': 0.147}")
c.bai("42.2", "Đặc trưng nào quan trọng", "Bỏ đặc trưng từ hai bên, rồi bỏ âm tiết đầu và cuối.",
      "Bỏ âm tiết đầu và cuối làm từ chưa gặp tụt từ 62,7% xuống 57,1%; bỏ từ hai bên chỉ giảm 0,2 điểm. Code ở ô ngay dưới.")
c.o('''
def crf_bo(bo):                                             # CRF bỏ những đặc trưng có tiền tố trong bo
    loc = lambda f: [x for x in f if not x.startswith(bo)]  # lọc
    h = pycrfsuite.Trainer(verbose=False)                   # bộ huấn luyện
    for c in tr:                                            # mỗi câu
        h.append([loc(dac_trung(c, i)) for i in range(len(c))], [t for _, t in c])   # đặc trưng đã lọc
    h.set_params({"c1": 0.1, "c2": 0.01, "max_iterations": 100})   # như trang 3
    h.train("tam.crfsuite")                                 # học
    g = pycrfsuite.Tagger()                                 # bộ gán nhãn
    g.open("tam.crfsuite")                                  # mở
    return do(dv, lambda c: g.tag([loc(dac_trung(c, i)) for i in range(len(c))]))   # đo dev
print("bỏ từ hai bên  ", crf_bo(("w-1", "w+1", "dau_cau", "cuoi_cau")))   # bỏ ngữ cảnh
print("bỏ âm tiết đầu, cuối", crf_bo(("dau=", "cuoi=")))     # bỏ hình thức
''', "bỏ từ hai bên   (0.8528, 0.6109, 4449)\nbỏ âm tiết đầu, cuối (0.8407, 0.5711, 4449)")
c.bai("42.3", "Thêm dữ liệu giúp bao nhiêu", "CRF trên 350, 700, 1400 câu train.",
      "80,5%, 83,7%, 85,5%: đường học chưa chững, thêm dữ liệu vẫn đáng giá. Code ở ô ngay dưới.")
c.o('''
for n in (350, 700, 1400):                                  # ba cỡ dữ liệu
    h = pycrfsuite.Trainer(verbose=False)                   # bộ huấn luyện
    for c in tr[:n]:                                        # n câu đầu
        h.append([dac_trung(c, i) for i in range(len(c))], [t for _, t in c])   # đặc trưng đủ
    h.set_params({"c1": 0.1, "c2": 0.01, "max_iterations": 100})   # như trang 3
    h.train("tam.crfsuite")                                 # học
    g = pycrfsuite.Tagger()                                 # bộ gán nhãn
    g.open("tam.crfsuite")                                  # mở
    print(n, do(dv, lambda c: g.tag([dac_trung(c, i) for i in range(len(c))])))   # đo dev
''', "350 (0.8052, 0.5887, 4449)\n700 (0.8369, 0.6159, 4449)\n1400 (0.8551, 0.6267, 4449)")

c.ghi(Path(__file__).resolve().parents[2] / "notebooks/ch42_gan_nhan_chuoi.ipynb")
