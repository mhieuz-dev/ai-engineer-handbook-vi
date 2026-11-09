"""Dựng notebooks/ch44_transformer.ipynb: python3 scripts/notebook/ch44.py"""
from pathlib import Path
from nblib import Chuong, code, khung

c = Chuong(44, "Transformer từ đầu", "ch44-transformer",
           "Tự cài self-attention bằng NumPy, multi-head attention và mã hóa vị trí sin, cos bằng PyTorch, lắp khối Transformer, thấy vì sao cần mã hóa vị trí, rồi huấn luyện trên UIT-VSFC và so trung thực với Chương 41.",
           ["Tính self-attention có tỷ lệ bằng tay và bằng NumPy, hiểu mặt nạ nhân quả.",
            "Cài multi-head attention, kiểm rằng self-attention không biết thứ tự.",
            "Cài mã hóa vị trí sin, cos và thấy nó quyết định bài toán phụ thuộc thứ tự.",
            "Huấn luyện Transformer trên UIT-VSFC, so với SVM và BiLSTM."],
           [("Self-attention", "01-self-attention"), ("Multi-head và mã hóa vị trí", "02-multi-head-va-vi-tri"),
            ("Khối Transformer", "03-khoi-transformer"), ("Transformer trên UIT-VSFC", "04-transformer-tren-vsfc"), ("Bài tập", "05-bai-tap")],
           thoi_gian="khoảng 3 phút")

c.mo_trang(1, "Self-attention bằng NumPy, phép chia căn số chiều, mặt nạ nhân quả.")
c.cells.append(code('''
!pip install -q pyarrow                                     # đọc parquet ở trang 4 (Colab thường có sẵn)
'''))
c.o('''
import math                                                 # căn bậc hai
import numpy as np                                          # mảng
np.set_printoptions(suppress=True)                          # in số gọn
rng = np.random.default_rng(0)                              # ngẫu nhiên cố định
X = rng.normal(size=(3, 4))                                 # 3 token, mỗi token 4 chiều
W_Q, W_K, W_V = (rng.normal(size=(4, 4)) for _ in range(3)) # ba ma trận chiếu
Q, K, V = X @ W_Q, X @ W_K, X @ W_V                         # query, key, value
def softmax(z):                                             # softmax theo hàng
    z = z - z.max(-1, keepdims=True)                        # trừ max cho ổn định số
    e = np.exp(z)                                           # mũ
    return e / e.sum(-1, keepdims=True)                     # chuẩn hóa
diem = Q @ K.T / math.sqrt(4)                               # 3 x 3: token i nhìn mọi token
A = softmax(diem)                                           # trọng số
ra = A @ V                                                  # trung bình có trọng số của value
print(A.round(3))                                           # ma trận trọng số
print(A.sum(1), ra.shape)                                   # mỗi hàng cộng bằng 1, đầu ra cùng hình dạng
''', "[[0.384 0.3   0.315]\n [0.321 0.206 0.473]\n [0.053 0.008 0.939]]\n[1. 1. 1.] (3, 4)")
c.o('''
import torch                                                # PyTorch
import torch.nn.functional as F                             # hàm có sẵn
torch_ra = F.scaled_dot_product_attention(*(torch.tensor(M)[None] for M in (Q, K, V)))[0].numpy()   # attention của PyTorch
print(np.abs(torch_ra - ra).max() < 1e-6)                   # khớp tới sai số làm tròn
''', "True")
c.o('''
q, k = rng.normal(size=(10000, 64)), rng.normal(size=(10000, 64))   # 10 000 cặp vector 64 chiều
tich = (q * k).sum(1)                                       # tích vô hướng
print(round(tich.std(), 2), round((tich / 8).std(), 2))     # độ lệch chuẩn trước và sau khi chia căn 64
print(softmax(rng.normal(size=8) * 8).round(3), softmax(rng.normal(size=8)).round(3))   # softmax bão hòa và không bão hòa
''', "8.06 1.01\n[0.001 0.042 0.001 0.029 0.    0.    0.    0.927] [0.003 0.137 0.099 0.085 0.031 0.021 0.596 0.028]")
c.o('''
mat_na = np.triu(np.ones((3, 3), dtype=bool), k=1)          # True ở ô token nhìn về tương lai
A_nq = softmax(np.where(mat_na, -np.inf, diem))             # che trước softmax
print(A_nq.round(3))                                        # tam giác dưới
''', "[[1.    0.    0.   ]\n [0.609 0.391 0.   ]\n [0.053 0.008 0.939]]")

c.mo_trang(2, "Multi-head attention, phép kiểm xáo trộn, mã hóa vị trí.")
c.o('''
import torch.nn as nn                                       # các lớp mạng
torch.set_num_threads(4)                                    # 4 luồng
class MultiHead(nn.Module):                                 # attention nhiều đầu
    def __init__(self, d, h):                               # d chiều, h đầu
        super().__init__()                                  # khởi tạo
        self.h = h                                          # số đầu
        self.qkv = nn.Linear(d, 3 * d)                      # Q, K, V cho mọi đầu trong một phép nhân
        self.ra = nn.Linear(d, d)                           # ghép các đầu
    def forward(self, x, mask):                             # x: (lô, n, d); mask: True ở token thật
        B, n, d = x.shape                                   # kích thước
        q, k, v = self.qkv(x).view(B, n, 3, self.h, d // self.h).permute(2, 0, 3, 1, 4)   # mỗi cái (lô, h, n, d/h)
        diem = q @ k.transpose(-1, -2) / math.sqrt(d // self.h)   # điểm có tỷ lệ
        diem = diem.masked_fill(~mask[:, None, None, :], -1e9)   # không nhìn vào ô đệm
        return self.ra((diem.softmax(-1) @ v).transpose(1, 2).reshape(B, n, d))   # ghép đầu, chiếu ra
torch.manual_seed(0)                                        # khởi tạo cố định
mh = MultiHead(8, 2)                                        # d = 8, 2 đầu
x = torch.randn(1, 5, 8)                                    # 5 token
print(mh(x, torch.ones(1, 5, dtype=torch.bool)).shape, sum(p.numel() for p in mh.parameters()))   # hình dạng, số tham số
''', "torch.Size([1, 5, 8]) 288")
c.o('''
hoan_vi = torch.tensor([3, 0, 4, 1, 2])                     # một cách xáo
ra_goc = mh(x, torch.ones(1, 5, dtype=torch.bool))          # đầu ra gốc
ra_xao = mh(x[:, hoan_vi], torch.ones(1, 5, dtype=torch.bool))   # đầu ra khi xáo đầu vào
print(torch.allclose(ra_xao, ra_goc[:, hoan_vi], atol=1e-6))   # đầu ra chỉ bị xáo theo
''', "True", khung("doc", ["Xáo đầu vào thì đầu ra chỉ bị xáo theo: self-attention không biết thứ tự."]))
c.o('''
def vi_tri(n, d):                                           # mã hóa vị trí sin, cos
    p = torch.arange(n).unsqueeze(1)                        # vị trí
    goc = p / 10000 ** (torch.arange(0, d, 2) / d)          # tần số giảm dần
    P = torch.zeros(n, d)                                   # ma trận vị trí
    P[:, 0::2], P[:, 1::2] = torch.sin(goc), torch.cos(goc) # chiều chẵn sin, chiều lẻ cos
    return P                                                # n x d
P = vi_tri(64, 128)                                         # 64 vị trí, 128 chiều
tich = P @ P.T                                              # tích vô hướng giữa các vị trí
print(P.shape, [round(tich[i, i + 5].item(), 3) for i in (0, 10, 30)], [round(tich[10, 10 + k].item(), 2) for k in (0, 1, 5, 20)])   # chỉ phụ thuộc khoảng cách, giảm khi xa
''', "torch.Size([64, 128]) [47.185, 47.185, 47.185] [64.0, 62.09, 47.19, 38.93]")

c.mo_trang(3, "Khối Transformer và bài toán A đứng trước B (vài giây).")
c.o('''
class Khoi(nn.Module):                                      # một khối Transformer pre-norm
    def __init__(self, d, h, f):                            # d chiều, h đầu, lớp ẩn f
        super().__init__()                                  # khởi tạo
        self.att, self.n1 = MultiHead(d, h), nn.LayerNorm(d)   # attention, LayerNorm
        self.ff = nn.Sequential(nn.Linear(d, f), nn.GELU(), nn.Linear(f, d))   # mạng truyền thẳng từng token
        self.n2, self.drop = nn.LayerNorm(d), nn.Dropout(0.1)   # LayerNorm, dropout
    def forward(self, x, mask):                             # x: (lô, n, d)
        x = x + self.drop(self.att(self.n1(x), mask))       # kết nối tắt quanh attention
        return x + self.drop(self.ff(self.n2(x)))           # kết nối tắt quanh mạng truyền thẳng
class Transformer(nn.Module):                               # bộ phân loại Transformer encoder
    def __init__(self, V, so_lop=3, d=128, h=4, f=256, L=2, vt=True, toi_da=64):   # vt: có mã hóa vị trí không
        super().__init__()                                  # khởi tạo
        self.emb, self.vt = nn.Embedding(V, d, padding_idx=0), vt   # vector từ
        self.register_buffer("P", vi_tri(toi_da, d))        # mã hóa vị trí cố định
        self.khoi = nn.ModuleList([Khoi(d, h, f) for _ in range(L)])   # L khối
        self.n, self.ra = nn.LayerNorm(d), nn.Linear(d, so_lop)   # chuẩn hóa cuối, lớp ra
    def forward(self, x):                                   # x: lô chỉ số
        mask = x != 0                                       # token thật
        z = self.emb(x) * math.sqrt(self.emb.embedding_dim) # vector từ nhân căn d
        if self.vt:                                         # có mã hóa vị trí
            z = z + self.P[:x.shape[1]]                     # cộng vị trí
        for k in self.khoi:                                 # qua các khối
            z = k(z, mask)                                  # một khối
        z = self.n(z)                                       # LayerNorm cuối
        z = (z * mask[..., None]).sum(1) / mask.sum(1, keepdim=True)   # trung bình các token thật
        return self.ra(z)                                   # điểm các lớp
def tao(n, seed):                                           # bài A đứng trước B
    g = torch.Generator().manual_seed(seed)                 # ngẫu nhiên cố định
    X = torch.randint(3, 22, (n, 12), generator=g)          # token nhiễu từ 3 tới 21
    for i in range(n):                                      # mỗi chuỗi
        a, b = torch.randperm(12, generator=g)[:2].tolist() # hai vị trí khác nhau
        X[i, a], X[i, b] = 1, 2                             # đặt A và B
    y = ((X == 1).float().argmax(1) < (X == 2).float().argmax(1)).long()   # nhãn: A trước B
    return X, y                                             # dữ liệu
X_ab, y_ab = tao(5000, 0)                                   # train
X_ab_va, y_ab_va = tao(1000, 1)                             # val
def hoc_thu_tu(vt, so_epoch=10):                            # huấn luyện trên bài thứ tự
    torch.manual_seed(0)                                    # khởi tạo cố định
    m = Transformer(22, so_lop=2, vt=vt)                    # 22 token, 2 lớp
    opt = torch.optim.AdamW(m.parameters(), lr=1e-3, fused=True)   # fused: lặp lại được trên CPU
    for ep in range(1, so_epoch + 1):                       # mỗi epoch
        m.train()                                           # chế độ huấn luyện
        thu_tu = torch.randperm(5000)                       # xáo trộn
        for k in range(0, 5000, 64):                        # lô 64
            idx = thu_tu[k:k + 64]                          # chỉ số
            loss = F.cross_entropy(m(X_ab[idx]), y_ab[idx]) # loss
            opt.zero_grad()                                 # xóa gradient
            loss.backward()                                 # lượt ngược
            opt.step()                                      # cập nhật
        m.eval()                                            # chế độ đánh giá
        with torch.no_grad():                               # không cần gradient
            acc = (m(X_ab_va).argmax(1) == y_ab_va).float().mean().item()   # độ chính xác val
        if ep in (1, 5, 10):                                # vài epoch để xem
            print(vt, ep, round(acc, 3))                    # in
hoc_thu_tu(vt=True)                                         # có mã hóa vị trí
hoc_thu_tu(vt=False)                                        # không có
''', "True 1 0.496\nTrue 5 0.935\nTrue 10 0.994\nFalse 1 0.499\nFalse 5 0.534\nFalse 10 0.503",
    khung("doc", ["Có mã hóa vị trí 99,4%; không có thì 50,3%, bằng đoán bừa: hai chuỗi chỉ khác thứ tự là cùng một đầu vào với mô hình đó."]))

c.mo_trang(4, "Transformer trên UIT-VSFC (khoảng 2 phút), so với Chương 41.")
c.o('''
import copy                                                 # sao chép mô hình
import os                                                   # đường dẫn
import time                                                 # đo thời gian
import urllib.request                                       # tải tệp
from collections import Counter                             # đếm
import pandas as pd                                         # bảng
from torch.nn.utils.rnn import pad_sequence                 # đệm lô
from sklearn.metrics import accuracy_score, f1_score        # thước đo
URL = "https://huggingface.co/api/datasets/uitnlp/vietnamese_students_feedback/parquet/default/{}/0.parquet"   # UIT-VSFC
THU_MUC = os.path.expanduser("~/.cache/vsfc")               # lưu tạm
def tai(phan):                                              # tải một lần
    os.makedirs(THU_MUC, exist_ok=True)                     # tạo thư mục
    tep = os.path.join(THU_MUC, phan + ".parquet")          # đường dẫn
    if not os.path.exists(tep):                             # chưa có thì tải
        urllib.request.urlretrieve(URL.format(phan), tep)   # tải về
    return pd.read_parquet(tep)                             # đọc
tr, va, te = tai("train"), tai("validation"), tai("test")   # ba phần
D_tr, D_va, D_te = ([s.split() for s in ds.sentence] for ds in (tr, va, te))   # âm tiết
dem = Counter(w for c in D_tr for w in c)                   # tần suất trên train
tu = ["<pad>", "<unk>"] + [w for w, n in dem.items() if n >= 2]   # từ điển như Chương 41
id_ = {w: i for i, w in enumerate(tu)}                      # âm tiết sang chỉ số
ma_hoa = lambda D: [torch.tensor([id_.get(w, 1) for w in c[:64]] or [1]) for c in D]   # cắt ở 64 âm tiết
X_tr, X_va, X_te = ma_hoa(D_tr), ma_hoa(D_va), ma_hoa(D_te) # ba phần
y_tr, y_va, y_te = torch.tensor(tr.sentiment.values), va.sentiment.values, te.sentiment.values   # nhãn
print(len(tu), max(len(c) for c in D_tr), sum(len(c) > 64 for c in D_tr))   # cỡ từ điển, câu dài nhất, số câu bị cắt
''', "1535 159 44")
c.o('''
def du_doan(m, X):                                          # dự đoán cả một tập
    m.eval()                                                # chế độ đánh giá
    with torch.no_grad():                                   # không cần gradient
        return m(pad_sequence(X, batch_first=True)).argmax(1).numpy()   # lớp có điểm cao nhất
def cham(y, p):                                             # độ chính xác, macro-F1
    return round(accuracy_score(y, p), 4), round(f1_score(y, p, average="macro"), 4)   # hai thước đo
def hoc_vsfc(vt, so_epoch=8, seed=0):                       # huấn luyện, giữ bản tốt nhất theo macro-F1 val
    torch.manual_seed(seed)                                 # khởi tạo cố định
    m = Transformer(len(tu), vt=vt)                         # 3 lớp cảm xúc
    opt = torch.optim.AdamW(m.parameters(), lr=1e-3, weight_decay=0.01, fused=True)   # AdamW
    tot, ban_tot = -1, None                                 # tốt nhất
    for ep in range(1, so_epoch + 1):                       # mỗi epoch
        m.train()                                           # chế độ huấn luyện
        thu_tu = torch.randperm(len(X_tr))                  # xáo trộn
        for k in range(0, len(thu_tu), 64):                 # lô 64
            idx = thu_tu[k:k + 64]                          # chỉ số
            x = pad_sequence([X_tr[i] for i in idx], batch_first=True)   # đệm
            loss = F.cross_entropy(m(x), y_tr[idx])         # loss
            opt.zero_grad()                                 # xóa gradient
            loss.backward()                                 # lượt ngược
            opt.step()                                      # cập nhật
        acc, f1 = cham(y_va, du_doan(m, X_va))              # đo val
        print(vt, ep, acc, f1)                              # in
        if f1 > tot:                                        # tốt hơn
            tot, ban_tot = f1, copy.deepcopy(m)             # giữ bản này
    return ban_tot                                          # bản tốt nhất
t0 = time.time()                                            # đo thời gian
tf_vt = hoc_vsfc(vt=True)                                   # có mã hóa vị trí
tf_khong = hoc_vsfc(vt=False)                               # không có
print(sum(p.numel() for p in tf_vt.parameters()), time.time() - t0 < 600)   # số tham số, dưới 10 phút
''', "True 1 0.8781 0.6607\nTrue 2 0.9084 0.7305\nTrue 3 0.9109 0.7401\nTrue 4 0.9046 0.7547\nTrue 5 0.9078 0.7536\nTrue 6 0.9059 0.7635\nTrue 7 0.9021 0.7466\nTrue 8 0.8964 0.7418\nFalse 1 0.8774 0.6684\nFalse 2 0.909 0.7271\nFalse 3 0.9109 0.7443\nFalse 4 0.909 0.7587\nFalse 5 0.909 0.7475\nFalse 6 0.9002 0.7411\nFalse 7 0.9002 0.7463\nFalse 8 0.9052 0.7652\n462083 True",
    khung("doc", ["Bỏ mã hóa vị trí không làm gì kém đi trên bài này; cả hai thua SVM cân bằng (0,801) và BiLSTM (0,799) của Chương 41."]))
c.o('''
ung_vien = {"có vị trí": tf_vt, "không vị trí": tf_khong}   # hai bản
chon = max(ung_vien, key=lambda k: f1_score(y_va, du_doan(ung_vien[k], X_va), average="macro"))   # chọn theo val
print("chọn:", chon, cham(y_te, du_doan(ung_vien[chon], X_te)))   # đo test một lần
''', "chọn: không vị trí (0.8879, 0.7278)")

c.mo_trang(5, "Ba bài tập. Đoán trước, rồi mới mở đáp án.")
c.bai("44.1", "Self-attention bằng tay", "Hai token với Q, K, V cho sẵn.",
      "Trọng số 0,8044 và 0,1956; đầu ra token thứ nhất (1,3911; 2,3911). Code ở ô ngay dưới.")
c.o('''
Q2, K2, V2 = np.array([[1, 0], [0, 1.0]]), np.array([[2, 0], [0, 2.0]]), np.array([[1, 2], [3, 4.0]])   # cho sẵn
diem2 = Q2 @ K2.T / math.sqrt(2)                            # điểm chia căn 2
A2 = softmax(diem2)                                         # trọng số
print(diem2.round(4), A2.round(4), (A2 @ V2).round(4), sep="\\n")   # điểm, trọng số, đầu ra
''', "[[1.4142 0.    ]\n [0.     1.4142]]\n[[0.8044 0.1956]\n [0.1956 0.8044]]\n[[1.3911 2.3911]\n [2.6089 3.6089]]")
c.bai("44.2", "Cái giá của độ dài", "Bộ nhớ của ma trận điểm attention khi câu dài 512, 2048, 8192 token.",
      "33,6 MB, 537 MB, 8,6 GB cho một lớp, so với 12,6 MB tham số của một khối d = 512. Code ở ô ngay dưới.")
c.o('''
for n in (512, 2048, 8192):                                 # ba độ dài
    print(n, round(8 * 4 * n * n * 4 / 1e6, 1), "MB")       # lô 8, 4 đầu, n x n ô, 4 byte
d, f = 512, 2048                                            # một khối cỡ vừa
print("tham số một khối:", 4 * d * d + 4 * d + 2 * d * f + d + f + 4 * d)   # attention, truyền thẳng, LayerNorm
''', "512 33.6 MB\n2048 536.9 MB\n8192 8589.9 MB\ntham số một khối: 3152384")
c.bai("44.3", "Vị trí học được", "Thay sin, cos bằng nn.Embedding(64, 128) trên bài A trước B.",
      "100% từ epoch 5; nhưng không có vector cho vị trí chưa từng thấy. Code ở ô ngay dưới.")
c.o('''
class TransformerViTriHoc(Transformer):                     # vị trí học được
    def __init__(self, V, **kw):                            # như Transformer
        super().__init__(V, **kw)                           # khởi tạo cha
        self.vt_hoc = nn.Embedding(64, 128)                 # một vector học được cho mỗi vị trí
    def forward(self, x):                                   # thay phần cộng vị trí
        mask = x != 0                                       # token thật
        z = self.emb(x) * math.sqrt(128) + self.vt_hoc(torch.arange(x.shape[1]))   # cộng vị trí học được
        for k in self.khoi:                                 # qua các khối
            z = k(z, mask)                                  # một khối
        z = self.n(z)                                       # LayerNorm cuối
        return self.ra((z * mask[..., None]).sum(1) / mask.sum(1, keepdim=True))   # trung bình rồi lớp ra
torch.manual_seed(0)                                        # khởi tạo cố định
m = TransformerViTriHoc(22, so_lop=2, vt=False)             # tắt sin, cos
opt = torch.optim.AdamW(m.parameters(), lr=1e-3, fused=True)   # AdamW
for ep in range(1, 11):                                     # 10 epoch
    m.train()                                               # chế độ huấn luyện
    thu_tu = torch.randperm(5000)                           # xáo trộn
    for k in range(0, 5000, 64):                            # lô 64
        idx = thu_tu[k:k + 64]                              # chỉ số
        loss = F.cross_entropy(m(X_ab[idx]), y_ab[idx])     # loss
        opt.zero_grad()                                     # xóa gradient
        loss.backward()                                     # lượt ngược
        opt.step()                                          # cập nhật
    m.eval()                                                # chế độ đánh giá
    with torch.no_grad():                                   # không cần gradient
        acc = (m(X_ab_va).argmax(1) == y_ab_va).float().mean().item()   # độ chính xác val
    if ep in (1, 5, 10):                                    # vài epoch
        print(ep, round(acc, 3))                            # in
''', "1 0.527\n5 1.0\n10 1.0")

c.ghi(Path(__file__).resolve().parents[2] / "notebooks/ch44_transformer.ipynb")
