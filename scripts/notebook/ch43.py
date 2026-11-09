"""Dựng notebooks/ch43_seq2seq_attention.ipynb: python3 scripts/notebook/ch43.py"""
from pathlib import Path
from nblib import Chuong, code, khung

c = Chuong(43, "Seq2Seq và attention", "ch43-seq2seq-attention",
           "Dịch Anh sang Việt bằng encoder-decoder GRU trên IWSLT'15 (câu ngắn), tự cài BLEU, huấn luyện có và không có attention, nhìn ma trận attention, và thử giải mã chùm. Hai lần huấn luyện tổng cộng khoảng 8 phút trên CPU; trong Colab có thể bật GPU cho nhanh.",
           ["Làm sạch dữ liệu song ngữ và phát hiện tập validation trùng tập test.",
            "Cài encoder-decoder, teacher forcing, giải mã tham lam.",
            "Tự cài BLEU và đọc đúng nó.",
            "Thêm attention, đo nó giúp bao nhiêu, đọc ma trận attention một cách trung thực."],
           [("Dịch máy và dữ liệu", "01-dich-may-va-du-lieu"), ("Encoder-decoder", "02-encoder-decoder"),
            ("BLEU và huấn luyện", "03-bleu-va-huan-luyen"), ("Attention", "04-attention"), ("Bài tập", "05-bai-tap")],
           thoi_gian="khoảng 10 phút")

c.mo_trang(1, "Tải IWSLT'15, làm sạch, chọn câu ngắn, dựng từ điển.")
c.cells.append(code('''
!pip install -q pyarrow                                     # đọc tệp parquet (Colab thường có sẵn)
'''))
c.o('''
import html                                                 # đổi ký tự HTML
import math                                                 # log, exp
import os                                                   # đường dẫn
import time                                                 # đo thời gian
import urllib.request                                       # tải tệp
from collections import Counter                             # đếm
import numpy as np                                          # mảng
import pandas as pd                                         # bảng
URL = ("https://huggingface.co/datasets/thainq107/iwslt2015-en-vi/resolve/"
       "4abfde30435395d5d3f031fea5e3f6600543521e/data/{}-00000-of-00001.parquet")   # bản sao ghim commit
THU_MUC = os.path.expanduser("~/.cache/iwslt15")            # lưu tạm
def tai(phan):                                              # tải một lần
    os.makedirs(THU_MUC, exist_ok=True)                     # tạo thư mục
    tep = os.path.join(THU_MUC, phan + ".parquet")          # đường dẫn
    if not os.path.exists(tep):                             # chưa có thì tải
        urllib.request.urlretrieve(URL.format(phan), tep)   # tải về
    return pd.read_parquet(tep)                             # đọc
tr, va_goc, te = tai("train"), tai("validation"), tai("test")   # ba tệp
print(len(tr), len(va_goc), len(te), va_goc.equals(te))     # validation trùng test
print(te.en[0])                                             # còn ký tự HTML
print(te.vi[0])                                             # bản dịch
''', "133317 1268 1268 True\nWhen I was little , I thought my country was the best on the planet , and I grew up singing a song called &quot; Nothing To Envy . &quot;\nKhi tôi còn nhỏ , Tôi nghĩ rằng BắcTriều Tiên là đất nước tốt nhất trên thế giới và tôi thường hát bài &quot; Chúng ta chẳng có gì phải ghen tị . &quot;",
    khung("loi", ["Tệp validation trùng hệt tệp test: phải tự tách val từ train, và chỉ đo test một lần."], "DỮ LIỆU"))
c.o('''
sach = lambda s: html.unescape(s).lower().split()           # đổi ký tự HTML, chữ thường, cắt theo dấu cách
cap = [(sach(e), sach(v)) for e, v in zip(tr.en, tr.vi)]    # mọi cặp câu
cap = [(e, v) for e, v in cap if 3 <= len(e) <= 12 and 3 <= len(v) <= 12]   # chỉ câu 3 tới 12 token
thu_tu = np.random.default_rng(0).permutation(len(cap))     # xáo trộn cố định
C_va, C_tr = [cap[i] for i in thu_tu[:2000]], [cap[i] for i in thu_tu[2000:]]   # 2000 cặp val, còn lại train
C_te = [(sach(e), sach(v)) for e, v in zip(te.en, te.vi)]   # test là tst2013
C_te = [(e, v) for e, v in C_te if 3 <= len(e) <= 12 and 3 <= len(v) <= 12]   # cùng bộ lọc
print(len(cap), len(C_tr), len(C_va), len(C_te))            # số cặp
print(C_te[1])                                              # một cặp test
''', "30951 28951 2000 259\n(['i', 'was', 'so', 'shocked', '.'], ['tôi', 'đã', 'bị', 'sốc', '.'])")
c.o('''
def tu_dien(ds, k=5):                                       # từ gặp ít nhất k lần
    dem = Counter(w for s in ds for w in s)                 # đếm
    tu = ["<pad>", "<unk>", "<s>", "</s>"] + [w for w, n in dem.most_common() if n >= k]   # 4 ký hiệu đặc biệt
    return tu, {w: i for i, w in enumerate(tu)}             # danh sách, từ sang chỉ số
tu_e, id_e = tu_dien([e for e, _ in C_tr])                  # tiếng Anh
tu_v, id_v = tu_dien([v for _, v in C_tr])                  # tiếng Việt
ma = lambda s, d: [d.get(w, 1) for w in s]                  # từ ngoài từ điển thành <unk>
la_v = sum(w not in id_v for _, v in C_va for w in v) / sum(len(v) for _, v in C_va)   # tỷ lệ <unk> tiếng Việt trên val
print(len(tu_e), len(tu_v), round(la_v, 4))                 # cỡ hai từ điển
''', "2866 2231 0.0331")

c.mo_trang(2, "Bộ mã hóa, bộ giải mã, teacher forcing, giải mã tham lam.")
c.o('''
import copy                                                 # sao chép mô hình
import torch                                                # PyTorch
import torch.nn as nn                                       # các lớp mạng
import torch.nn.functional as F                             # hàm loss
from torch.nn.utils.rnn import pad_sequence                 # đệm lô
torch.set_num_threads(4)                                    # 4 luồng, kết quả lặp lại được
class MaHoa(nn.Module):                                     # bộ mã hóa
    def __init__(self, V, d=256, h=256):                    # từ điển, chiều vector, chiều ẩn
        super().__init__()                                  # khởi tạo
        self.emb = nn.Embedding(V, d, padding_idx=0)        # vector từ
        self.gru = nn.GRU(d, h, batch_first=True)           # GRU một chiều
    def forward(self, x):                                   # x: lô chỉ số
        return self.gru(self.emb(x))                        # trạng thái mọi bước, trạng thái cuối
class GiaiMa(nn.Module):                                    # bộ giải mã
    def __init__(self, V, d=256, h=256, chu_y=False):       # chu_y: có attention không
        super().__init__()                                  # khởi tạo
        self.chu_y = chu_y                                  # cờ attention
        self.emb = nn.Embedding(V, d, padding_idx=0)        # vector từ đích
        self.gru = nn.GRU(d + (h if chu_y else 0), h, batch_first=True)   # thêm vector ngữ cảnh nếu có attention
        self.ra = nn.Linear(h * (2 if chu_y else 1), V)     # điểm cho mọi từ đích
    def buoc(self, y, h, enc, mask):                        # một bước giải mã
        e = self.emb(y)                                     # vector của từ trước
        if not self.chu_y:                                  # không attention
            o, h = self.gru(e, h)                           # một bước GRU
            return self.ra(o).squeeze(1), h, None           # điểm, trạng thái mới
        diem = (enc @ h[-1].unsqueeze(2)).squeeze(2).masked_fill(~mask, -1e9)   # điểm hợp, che phần đệm
        a = diem.softmax(1)                                 # trọng số attention
        ngu_canh = a.unsqueeze(1) @ enc                     # trung bình có trọng số của câu nguồn
        o, h = self.gru(torch.cat([e, ngu_canh], 2), h)     # GRU nhận thêm ngữ cảnh
        return self.ra(torch.cat([o, ngu_canh], 2)).squeeze(1), h, a   # điểm, trạng thái, trọng số
def lo(ds, idx):                                            # một lô đã đệm
    X = [torch.tensor(ma(ds[i][0], id_e)) for i in idx]     # câu nguồn
    Y = [torch.tensor([2] + ma(ds[i][1], id_v) + [3]) for i in idx]   # câu đích có <s> và </s>
    return pad_sequence(X, batch_first=True), pad_sequence(Y, batch_first=True)   # đệm
def loss_lo(mh, gm, X, Y):                                  # loss với teacher forcing
    enc, h = mh(X)                                          # mã hóa
    mask = X != 0                                           # vị trí thật
    diem = []                                               # điểm từng bước
    for t in range(Y.shape[1] - 1):                         # mỗi bước giải mã
        o, h, _ = gm.buoc(Y[:, t:t + 1], h, enc, mask)      # đưa từ đúng Y[:, t]
        diem.append(o)                                      # lưu
    return F.cross_entropy(torch.stack(diem, 1).reshape(-1, len(tu_v)), Y[:, 1:].reshape(-1), ignore_index=0)   # bỏ ô đệm
def dich(mh, gm, ds, toi_da=20):                            # giải mã tham lam theo lô
    mh.eval()                                               # chế độ đánh giá
    gm.eval()                                               # chế độ đánh giá
    ra = []                                                 # các bản dịch
    with torch.no_grad():                                   # không cần gradient
        for k in range(0, len(ds), 256):                    # lô 256 câu
            X = pad_sequence([torch.tensor(ma(e, id_e)) for e, _ in ds[k:k + 256]], batch_first=True)   # câu nguồn
            enc, h = mh(X)                                  # mã hóa
            mask = X != 0                                   # vị trí thật
            y, cau = torch.full((len(X), 1), 2), []         # bắt đầu từ <s>
            for _ in range(toi_da):                         # tối đa 20 từ
                o, h, _ = gm.buoc(y, h, enc, mask)          # một bước
                y = o.argmax(1, keepdim=True)               # tham lam
                cau.append(y)                               # lưu
            for s in torch.cat(cau, 1).tolist():            # mỗi câu
                s = s[:s.index(3)] if 3 in s else s         # cắt ở </s>
                ra.append([tu_v[i] for i in s])             # chỉ số sang từ
    return ra                                               # danh sách câu dịch
torch.manual_seed(0)                                        # khởi tạo cố định
mh0, gm0 = MaHoa(len(tu_e)), GiaiMa(len(tu_v))              # mạng chưa học
print(" ".join(dich(mh0, gm0, C_va[:1])[0]))                # dịch thử
X, Y = lo(C_tr, range(64))                                  # một lô
print(X.shape, Y.shape, round(loss_lo(mh0, gm0, X, Y).item(), 3), round(math.log(len(tu_v)), 3))   # loss ban đầu so với ln V
''', "chặn giáng thế vọng để rào ngày chó can xạ khám bẩn iraq cạn cởi mạc và người rực sáu\ntorch.Size([64, 12]) torch.Size([64, 14]) 7.725 7.71")

c.mo_trang(3, "BLEU tự cài, rồi huấn luyện mô hình không attention (khoảng 2,5 phút).")
c.o('''
def bleu(tham_chieu, dich_may, N=4):                        # BLEU trên cả tập
    khop, tong, r, c = [0] * N, [0] * N, 0, 0               # số trùng, tổng n-gram, độ dài
    for R, H in zip(tham_chieu, dich_may):                  # mỗi cặp câu
        r, c = r + len(R), c + len(H)                       # cộng độ dài
        for n in range(1, N + 1):                           # n-gram 1 tới 4
            h_ng = Counter(tuple(H[i:i + n]) for i in range(len(H) - n + 1))   # n-gram của bản dịch máy
            r_ng = Counter(tuple(R[i:i + n]) for i in range(len(R) - n + 1))   # n-gram của tham chiếu
            khop[n - 1] += sum(min(so, r_ng[g]) for g, so in h_ng.items())     # đếm có cắt
            tong[n - 1] += max(len(H) - n + 1, 0)           # tổng n-gram
    if min(khop) == 0:                                      # một precision bằng 0
        return 0.0                                          # trung bình nhân bằng 0
    log_p = sum(math.log(k / t) for k, t in zip(khop, tong)) / N   # log trung bình nhân
    bp = 1 if c > r else math.exp(1 - r / c)                # phạt ngắn
    return round(100 * bp * math.exp(log_p), 2)             # thang 0 tới 100
R = "tôi đã rất tự hào về đất nước tôi .".split()           # tham chiếu
for H in ("tôi đã rất tự hào về đất nước tôi .", "tôi rất tự hào về đất nước của tôi .", "tôi rất tự hào .", "đất nước tôi tự hào ."):   # bốn bản dịch
    print(bleu([R], [H.split()]), "|", H)                   # BLEU một câu
''', "100.0 | tôi đã rất tự hào về đất nước tôi .\n59.88 | tôi rất tự hào về đất nước của tôi .\n0.0 | tôi rất tự hào .\n0.0 | đất nước tôi tự hào .")
c.o('''
def huan_luyen(chu_y, so_epoch=8, seed=0):                  # huấn luyện, giữ bản có BLEU val cao nhất
    torch.manual_seed(seed)                                 # khởi tạo cố định
    mh, gm = MaHoa(len(tu_e)), GiaiMa(len(tu_v), chu_y=chu_y)   # hai mạng
    tham_so = list(mh.parameters()) + list(gm.parameters()) # mọi tham số
    opt = torch.optim.Adam(tham_so, lr=1e-3, fused=True)    # fused: lặp lại được trên CPU
    tot, ban_tot = -1, None                                 # BLEU tốt nhất, bản tương ứng
    for ep in range(1, so_epoch + 1):                       # mỗi epoch
        mh.train()                                          # chế độ huấn luyện
        gm.train()                                          # chế độ huấn luyện
        thu_tu, tong, n = torch.randperm(len(C_tr)), 0.0, 0 # xáo trộn
        for k in range(0, len(thu_tu), 64):                 # lô 64
            X, Y = lo(C_tr, thu_tu[k:k + 64])               # một lô
            loss = loss_lo(mh, gm, X, Y)                    # teacher forcing
            opt.zero_grad()                                 # xóa gradient
            loss.backward()                                 # lượt ngược
            nn.utils.clip_grad_norm_(tham_so, 1.0)          # cắt gradient
            opt.step()                                      # cập nhật
            tong, n = tong + loss.item(), n + 1             # cộng loss
        b = bleu([v for _, v in C_va], dich(mh, gm, C_va))  # BLEU trên val
        print(ep, round(tong / n, 3), b)                    # epoch, loss, BLEU
        if b > tot:                                         # tốt hơn mọi epoch trước
            tot, ban_tot = b, (copy.deepcopy(mh), copy.deepcopy(gm))   # giữ bản này
    return ban_tot                                          # bản tốt nhất
t0 = time.time()                                            # đo thời gian
mh_tron, gm_tron = huan_luyen(chu_y=False)                  # không attention
print(time.time() - t0 < 600)                               # dưới 10 phút
''', "1 4.3 3.95\n2 3.376 5.44\n3 3.016 6.73\n4 2.762 7.33\n5 2.553 7.83\n6 2.372 8.21\n7 2.206 8.66\n8 2.056 8.89\nTrue")

c.mo_trang(4, "Huấn luyện có attention (khoảng 5 phút), nhìn ma trận attention, đo test một lần.")
c.o('''
t0 = time.time()                                            # đo thời gian
mh_cy, gm_cy = huan_luyen(chu_y=True)                       # có attention
print(time.time() - t0 < 900)                               # dưới 15 phút
for e, v in C_va[:3]:                                       # ba câu val
    print(" ".join(e), "|", " ".join(v), "|", " ".join(dich(mh_cy, gm_cy, [(e, v)])[0]))   # nguồn, tham chiếu, dịch máy
''', "1 4.092 6.9\n2 3.052 10.29\n3 2.583 11.23\n4 2.243 12.51\n5 1.965 12.75\n6 1.733 12.81\n7 1.53 12.76\n8 1.353 12.32\nTrue\nif they get it for free , they use it . | nếu họ nhận được nó miễn phí , họ sẽ dùng . | họ lấy nó lên lên .\nwhy can 't we ? why can 't humans regenerate ? | vậy tại sao con người không thể ? | tại sao không thể không ?\nall these red parts are favelas . | những vùng màu đỏ là khu ổ chuột . | tất cả đều là những con ruồi .")
c.o('''
def dich_kem_attention(mh, gm, e, toi_da=20):               # dịch một câu, ghi lại trọng số attention
    mh.eval()                                               # chế độ đánh giá
    gm.eval()                                               # chế độ đánh giá
    with torch.no_grad():                                   # không cần gradient
        X = torch.tensor([ma(e, id_e)])                     # một câu
        enc, h = mh(X)                                      # mã hóa
        y, tu, A = torch.tensor([[2]]), [], []              # bắt đầu từ <s>
        for _ in range(toi_da):                             # mỗi bước
            o, h, a = gm.buoc(y, h, enc, X != 0)            # một bước có attention
            y = o.argmax(1, keepdim=True)                   # tham lam
            if y.item() == 3:                               # gặp </s>
                break                                       # dừng
            tu.append(tu_v[y.item()])                       # từ sinh ra
            A.append(a[0].numpy())                          # trọng số trên câu nguồn
    return tu, np.array(A)                                  # bản dịch, ma trận attention
cau_nguon = "i was very proud .".split()                    # câu thử
tu_dich, A = dich_kem_attention(mh_cy, gm_cy, cau_nguon)    # dịch
print(tu_dich)                                              # bản dịch
print(A.round(2))                                           # hàng là từ đích, cột là từ nguồn
''', "['tôi', 'tự', 'hào', 'hứng', ',', 'vì', 'vậy', '.']\n[[0.   0.   0.   0.   1.  ]\n [0.   0.   0.   0.05 0.95]\n [0.   0.   0.   0.63 0.37]\n [0.   0.   0.   0.22 0.78]\n [0.   0.   0.   0.   1.  ]\n [0.   0.   0.01 0.   0.99]\n [0.   0.   0.   0.   1.  ]\n [0.   0.   0.   0.   1.  ]]",
    khung("doc", ["Phần lớn trọng số dồn vào dấu chấm cuối (trạng thái đã đọc hết câu của GRU một chiều); bước sinh \"tự\" và \"hào\" mới nhìn sang \"proud\"."]))
c.o('''
ung_vien = {"không attention": (mh_tron, gm_tron), "attention": (mh_cy, gm_cy)}   # hai mô hình
diem_val = {k: bleu([v for _, v in C_va], dich(*m, C_va)) for k, m in ung_vien.items()}   # BLEU val
chon = max(diem_val, key=diem_val.get)                      # chọn theo val
print(diem_val, "chọn:", chon)                              # kết quả chọn
for k, m in ung_vien.items():                               # đo test một lần
    print(k, bleu([v for _, v in C_te], dich(*m, C_te)))    # BLEU test
''', "{'không attention': 8.89, 'attention': 12.81} chọn: attention\nkhông attention 8.14\nattention 11.6")

c.mo_trang(5, "Ba bài tập. Đoán trước, rồi mới mở đáp án.")
c.bai("43.1", "BLEU bằng tay", "Tham chiếu 'con mèo ngồi trên tấm thảm', bản dịch 'con mèo mèo ngồi trên thảm'.",
      "p1 = 5/6, p2 = 3/5, p3 = 1/4, p4 = 0: BLEU-4 bằng 0, BLEU-2 bằng 70,71. Code ở ô ngay dưới.")
c.o('''
R = "con mèo ngồi trên tấm thảm".split()                    # tham chiếu
H = "con mèo mèo ngồi trên thảm".split()                    # bản dịch máy
for n in (1, 2, 3, 4):                                      # n-gram 1 tới 4
    h_ng = Counter(tuple(H[i:i + n]) for i in range(len(H) - n + 1))   # của bản dịch
    r_ng = Counter(tuple(R[i:i + n]) for i in range(len(R) - n + 1))   # của tham chiếu
    print(n, sum(min(so, r_ng[g]) for g, so in h_ng.items()), len(H) - n + 1)   # số trùng sau cắt, tổng
print(bleu([R], [H]), bleu([R], [H], N=2))                  # BLEU-4, BLEU-2
''', "1 5 6\n2 3 5\n3 1 4\n4 0 3\n0.0 70.71")
c.bai("43.2", "Câu dài có khổ hơn không", "BLEU của hai mô hình trên câu nguồn 3 tới 6 từ và 7 tới 12 từ.",
      "Attention giúp gần bằng nhau ở hai nhóm (+4,5 và +3,9 điểm): nút thắt chưa lộ rõ ở câu dưới 12 từ. Code ở ô ngay dưới.")
c.o('''
for ten, (lo_ngan, lo_dai) in (("ngắn (3-6)", (3, 6)), ("dài (7-12)", (7, 12))):   # hai nhóm độ dài
    nhom = [(e, v) for e, v in C_va if lo_ngan <= len(e) <= lo_dai]   # câu val trong nhóm
    ref = [v for _, v in nhom]                              # tham chiếu
    print(ten, len(nhom), bleu(ref, dich(mh_tron, gm_tron, nhom)), bleu(ref, dich(mh_cy, gm_cy, nhom)))   # số câu, hai BLEU
''', "ngắn (3-6) 632 9.63 14.1\ndài (7-12) 1368 7.79 11.67")
c.bai("43.3", "Giải mã chùm", "Beam search k = 3 cho mô hình có attention, 500 câu val đầu.",
      "Tham lam 13,33, chùm 14,09: thêm 0,76 điểm. Code ở ô ngay dưới.")
c.o('''
def chum(mh, gm, e, k=3, toi_da=20):                        # giải mã chùm một câu
    with torch.no_grad():                                   # không cần gradient
        X = torch.tensor([ma(e, id_e)])                     # câu nguồn
        enc, h0 = mh(X)                                     # mã hóa
        mask = X != 0                                       # vị trí thật
        chum_hien = [(0.0, [2], h0)]                        # (tổng log xác suất, các token, trạng thái)
        xong = []                                           # câu đã gặp </s>
        for _ in range(toi_da):                             # mỗi bước
            ung = []                                        # ứng viên mở rộng
            for diem, toks, h in chum_hien:                 # mỗi câu dở dang
                o, h2, _ = gm.buoc(torch.tensor([[toks[-1]]]), h, enc, mask)   # một bước
                lp = o.log_softmax(1)[0]                    # log xác suất từ tiếp theo
                gia_tri, chi_so = lp.topk(k)                # k từ tốt nhất
                for g, i in zip(gia_tri.tolist(), chi_so.tolist()):   # mở rộng
                    ung.append((diem + g, toks + [i], h2))  # câu dài thêm một từ
            ung.sort(key=lambda x: -x[0])                   # xếp theo tổng log xác suất
            chum_hien = []                                  # chùm mới
            for u in ung[:k]:                               # giữ k ứng viên tốt nhất
                (xong if u[1][-1] == 3 else chum_hien).append(u)   # tách câu đã xong
            if not chum_hien:                               # mọi nhánh đã xong
                break                                       # dừng
        tot = max(xong + chum_hien, key=lambda x: x[0] / len(x[1]))   # chia độ dài: không thiên vị câu ngắn
        return [tu_v[i] for i in tot[1][1:] if i != 3]      # bỏ <s> và </s>
mh_cy.eval()                                                # chế độ đánh giá
gm_cy.eval()                                                # chế độ đánh giá
mau = C_va[:500]                                            # 500 câu val đầu
ref = [v for _, v in mau]                                   # tham chiếu
t0 = time.time()                                            # đo thời gian
print(bleu(ref, dich(mh_cy, gm_cy, mau)), bleu(ref, [chum(mh_cy, gm_cy, e) for e, _ in mau]), time.time() - t0 < 300)   # tham lam, chùm
''', "13.33 14.09 True")

c.ghi(Path(__file__).resolve().parents[2] / "notebooks/ch43_seq2seq_attention.ipynb")
