"""Dựng notebooks/ch29_rnn_lstm_gru.ipynb: python3 scripts/notebook/ch29.py"""
from pathlib import Path
from nblib import Chuong, khung

c = Chuong(29, "RNN, LSTM, GRU", "ch29-rnn-lstm-gru",
           "Tự cài RNN, đo gradient biến mất và gradient nổ qua thời gian, kẹp gradient, so RNN với LSTM và GRU trên bài nhớ ký hiệu đầu, rồi huấn luyện một mô hình ngôn ngữ ký tự trên Truyện Kiều.",
           ["Tự viết vòng lặp RNN và khớp nn.RNN.",
            "Đo gradient qua thời gian và dùng kẹp gradient.",
            "Thấy bias cổng quyết định LSTM, GRU có nhớ được xa hay không.",
            "Huấn luyện mô hình ngôn ngữ ký tự và sinh thơ lục bát theo nhiệt độ."],
           [("Dữ liệu chuỗi và RNN", "01-du-lieu-chuoi-va-rnn"), ("Gradient qua thời gian", "02-gradient-qua-thoi-gian"),
            ("LSTM và GRU", "03-lstm-va-gru"), ("Mô hình ngôn ngữ ký tự trên Truyện Kiều", "04-mo-hinh-ngon-ngu-ky-tu"),
            ("Bài tập", "05-bai-tap")])

c.mo_trang(1, "nn.RNN và vòng lặp tự cài.")
c.o('''
import torch                                                # PyTorch
import torch.nn as nn                                       # các lớp mạng
torch.manual_seed(0)                                        # khởi tạo lặp lại được
rnn = nn.RNN(input_size=3, hidden_size=4, batch_first=True) # shape (lô, bước, đặc trưng)
x = torch.randn(2, 5, 3)                                    # 2 chuỗi, 5 bước, 3 đặc trưng
ra, h_cuoi = rnn(x)                                         # trạng thái mọi bước, trạng thái cuối
print(ra.shape, h_cuoi.shape)                               # (2, 5, 4) và (1, 2, 4)
print([(n, tuple(p.shape)) for n, p in rnn.named_parameters()])   # W_x, W_h, hai bias
''', "torch.Size([2, 5, 4]) torch.Size([1, 2, 4])\n[('weight_ih_l0', (4, 3)), ('weight_hh_l0', (4, 4)), ('bias_ih_l0', (4,)), ('bias_hh_l0', (4,))]")
c.o('''
h = torch.zeros(2, 4)                                       # h_0 = 0
cac_h = []                                                  # trạng thái từng bước
for t in range(5):                                          # đọc lần lượt từng bước
    h = torch.tanh(x[:, t] @ rnn.weight_ih_l0.T + rnn.bias_ih_l0 + h @ rnn.weight_hh_l0.T + rnn.bias_hh_l0)   # công thức RNN
    cac_h.append(h)                                         # lưu lại
tu_cai = torch.stack(cac_h, dim=1)                          # (2, 5, 4)
print(torch.allclose(tu_cai, ra, atol=1e-6), torch.allclose(h, h_cuoi[0], atol=1e-6))   # so với nn.RNN
''', "True True")
c.o('''
print(sum(p.numel() for p in rnn.parameters()), rnn(torch.randn(2, 500, 3))[0].shape)   # 36 tham số, chuỗi 500 bước
''', "36 torch.Size([2, 500, 4])")

c.mo_trang(2, "Gradient theo khoảng cách, gradient nổ, kẹp gradient.")
c.o('''
def do_grad(mang, T, seed=0):                               # gradient của h_T theo từng x_t
    torch.manual_seed(seed)                                 # cùng chuỗi vào
    x = torch.randn(1, T, 8, requires_grad=True)            # một chuỗi T bước
    ra, _ = mang(x)                                         # lượt xuôi
    ra[0, -1].sum().backward()                              # loss giả: tổng trạng thái cuối
    return x.grad[0].norm(dim=1)                            # một số cho mỗi bước
torch.manual_seed(0)                                        # seed
r = nn.RNN(8, 32, batch_first=True)                         # khởi tạo mặc định
g = do_grad(r, 100)                                         # chuỗi 100 bước
print([f"{g[t].item():.1e}" for t in (99, 90, 50, 0)])      # gần cuối tới bước đầu
print([f"{do_grad(r, T)[0].item():.1e}" for T in (2, 10, 20, 50, 100)])   # về bước đầu theo độ dài
''', "['2.0e+00', '5.5e-03', '3.0e-14', '0.0e+00']\n['9.6e-01', '3.4e-03', '1.3e-05', '1.0e-13', '0.0e+00']")
c.o('''
with torch.no_grad():                                       # sửa trọng số trực tiếp
    r.weight_hh_l0 *= 3                                     # phóng to ma trận hồi quy
print([f"{do_grad(r, T)[0].item():.1e}" for T in (2, 10, 20, 50, 100)])   # gradient lớn dần
''', "['2.3e+00', '1.5e+00', '1.4e+01', '1.8e+01', '6.1e+01']")
c.o('''
w = nn.Parameter(torch.zeros(3))                            # một tham số giả
w.grad = torch.tensor([30.0, 40.0, 0.0])                    # gradient độ dài 50
print(nn.utils.clip_grad_norm_([w], max_norm=1.0).item(), [round(v, 4) for v in w.grad.tolist()])   # độ dài trước khi kẹp, gradient sau khi kẹp
''', "50.0 [0.6, 0.8, 0.0]")

c.mo_trang(3, "LSTM, GRU và bài nhớ ký hiệu đầu (khoảng 2 phút trên CPU).")
c.o('''
for loai in (nn.RNN, nn.LSTM, nn.GRU):                      # ba loại lớp hồi quy
    print(loai.__name__, sum(p.numel() for p in loai(8, 32).parameters()))   # số tham số
''', "RNN 1344\nLSTM 5376\nGRU 4032")
c.o('''
H = 32                                                      # kích thước ẩn
for b in (0.0, 1.0, 3.0):                                   # cộng thêm vào bias cổng quên
    torch.manual_seed(0)                                    # cùng khởi tạo
    lstm = nn.LSTM(8, H, batch_first=True)                  # LSTM mặc định
    with torch.no_grad():                                   # sửa trọng số trực tiếp
        lstm.bias_ih_l0[H:2 * H] += b                       # khối thứ hai là cổng quên (i, f, g, o)
    f = torch.sigmoid(lstm.bias_ih_l0[H:2 * H] + lstm.bias_hh_l0[H:2 * H]).mean().item()   # cổng quên trung bình lúc đầu
    print(b, round(f, 3), [f"{do_grad(lstm, T)[0].item():.1e}" for T in (2, 10, 20, 50, 100)])   # gradient về bước đầu
''', "0.0 0.507 ['2.3e-01', '1.7e-03', '2.2e-05', '2.7e-11', '7.1e-22']\n1.0 0.736 ['3.4e-01', '2.4e-02', '5.8e-03', '5.3e-05', '1.7e-09']\n3.0 0.953 ['4.3e-01', '1.9e-01', '2.6e-01', '6.7e-02', '4.4e-02']")
c.o('''
def tao_lo(n, T, g):                                        # n chuỗi T ký hiệu 0..9, nhãn là ký hiệu đầu
    X = torch.randint(0, 10, (n, T), generator=g)           # ký hiệu ngẫu nhiên
    return X, X[:, 0].clone()                               # chuỗi, nhãn
X, y = tao_lo(2, 12, torch.Generator().manual_seed(0))      # hai chuỗi ví dụ
print(X.tolist(), y.tolist())                               # nhãn là cột đầu
''', "[[4, 9, 3, 0, 3, 9, 7, 3, 7, 3, 1, 6], [6, 9, 8, 6, 6, 8, 4, 3, 6, 9, 1, 4]] [4, 6]")
c.o('''
class Nho(nn.Module):                                       # embedding, lớp hồi quy, Linear
    def __init__(self, loai, bias_cong=0.0):                # loai: nn.RNN, nn.LSTM hoặc nn.GRU
        super().__init__()                                  # bắt buộc
        self.nhung = nn.Embedding(10, 16)                   # ký hiệu thành vector 16 số
        self.loi = loai(16, 64, batch_first=True)           # lớp hồi quy 64 chiều
        self.ra = nn.Linear(64, 10)                         # 10 lớp
        if bias_cong:                                       # LSTM: cổng quên; GRU: cổng cập nhật z
            with torch.no_grad():                           # sửa trọng số trực tiếp
                self.loi.bias_ih_l0[64:128] += bias_cong    # khối thứ hai của bias
    def forward(self, x):                                   # lượt xuôi
        ra, _ = self.loi(self.nhung(x))                     # trạng thái mọi bước
        return self.ra(ra[:, -1])                           # chỉ dùng bước cuối
ce = nn.CrossEntropyLoss()                                  # loss
def huan_luyen(loai, bias_cong=0.0, kep=None, T=50, so_buoc=1500):   # huấn luyện và in độ chính xác
    torch.manual_seed(0)                                    # cùng khởi tạo
    m = Nho(loai, bias_cong)                                # mô hình
    opt = torch.optim.Adam(m.parameters(), lr=1e-3)         # Adam
    g = torch.Generator().manual_seed(1)                    # nguồn lô train
    Xte, yte = tao_lo(2000, T, torch.Generator().manual_seed(2))   # 2000 chuỗi test cố định
    acc, g_max = [], 0.0                                    # kết quả
    for b in range(1, so_buoc + 1):                         # mỗi bước
        x, y = tao_lo(64, T, g)                             # một lô mới
        opt.zero_grad()                                     # xóa gradient
        ce(m(x), y).backward()                              # lượt ngược
        do_dai = nn.utils.clip_grad_norm_(m.parameters(), kep or float("inf"))   # kep=None: chỉ đo
        g_max = max(g_max, do_dai.item())                   # gradient lớn nhất từng gặp
        opt.step()                                          # cập nhật
        if b % 250 == 0:                                    # mỗi 250 bước
            with torch.no_grad():                           # đánh giá
                acc.append(round((m(Xte).argmax(1) == yte).float().mean().item(), 3))   # độ chính xác test
    print(loai.__name__, bias_cong, kep, acc, round(g_max, 1))   # một dòng kết quả
for loai in (nn.RNN, nn.LSTM, nn.GRU):                      # ba loại, khởi tạo mặc định
    huan_luyen(loai)                                        # chuỗi 50 bước
''', "RNN 0.0 None [0.105, 0.094, 0.091, 0.1, 0.101, 0.095] 0.6\nLSTM 0.0 None [0.101, 0.087, 0.097, 0.101, 0.101, 0.102] 0.2\nGRU 0.0 None [0.101, 0.089, 0.099, 0.1, 0.096, 0.102] 0.3")
c.o('''
huan_luyen(nn.LSTM, bias_cong=3.0)                          # cổng quên mở sẵn
huan_luyen(nn.GRU, bias_cong=3.0)                           # cổng cập nhật mở sẵn
''', "LSTM 3.0 None [0.746, 0.867, 0.988, 1.0, 0.899, 1.0] 140.0\nGRU 3.0 None [0.231, 0.999, 1.0, 1.0, 1.0, 1.0] 53.2")
c.o('''
huan_luyen(nn.LSTM, bias_cong=3.0, kep=1.0)                 # thêm kẹp gradient ở 1,0
''', "LSTM 3.0 1.0 [0.697, 0.983, 0.999, 1.0, 0.994, 0.994] 723.6",
    khung("thu", ["<b>1.</b> Thử bias_cong=1.0 cho LSTM. Có đủ cho chuỗi 50 bước không?",
                  "<b>2.</b> Đổi lr của Adam thành 3e-3 với LSTM bias 3. Cú rơi độ chính xác có nhiều hơn không?"]))

c.mo_trang(4, "Mô hình ngôn ngữ ký tự trên Truyện Kiều (khoảng 2 phút trên CPU, nhanh hơn nếu bật GPU).")
c.o(r'''
import re                                                   # biểu thức chính quy
import urllib.request                                       # tải trang web
URL = "https://vi.wikisource.org/w/index.php?oldid=205132&action=raw"   # Truyện Kiều trên Wikisource, ghim một phiên bản
yc = urllib.request.Request(URL, headers={"User-Agent": "ai-and-robotics-handbook/1.0 (giao trinh hoc AI)"})   # Wikimedia cần User-Agent
tho = urllib.request.urlopen(yc).read().decode("utf-8")     # mã nguồn trang
than = tho.split("<poem>")[1].split("</poem>")[0]           # phần thơ
cau = [re.sub(r"\{\{số\|\d+\}\}", "", d).strip() for d in than.splitlines()]   # bỏ số thứ tự câu
cau = [c for c in cau if c]                                 # bỏ dòng trống
print(len(cau), cau[0], "/", cau[1])                        # số câu, hai câu đầu
print(sum(len(c.split()) == (6 if k % 2 == 0 else 8) for k, c in enumerate(cau)))   # số câu đúng nhịp 6-8
''', "3254 Trăm năm trong cõi người ta, / Chữ tài chữ mệnh khéo là ghét nhau.\n3254")
c.o('''
import math                                                 # log, exp
van = "\\n".join(cau) + "\\n"                               # cả bài thơ, xuống dòng cũng là ký tự
chu = sorted(set(van))                                      # bảng ký tự
so = {c: i for i, c in enumerate(chu)}                      # ký tự thành số
du_lieu = torch.tensor([so[c] for c in van])                # cả văn bản thành số
cat = int(0.9 * len(du_lieu))                               # chia theo vị trí
tr, va = du_lieu[:cat], du_lieu[cat:]                       # 90% đầu học, 10% cuối đánh giá
print(len(van), len(chu), len(tr), len(va))                 # kích thước
dem = torch.bincount(tr, minlength=len(chu)).float()        # tần suất từng ký tự trong train
print(round(math.log(len(chu)), 3), round(-torch.log(dem[va] / dem.sum()).mean().item(), 3))   # hai mốc loss
''', "104204 132 93783 10421\n4.883 3.59")
c.o('''
import copy                                                 # chép trạng thái mô hình
class MoHinhKyTu(nn.Module):                                # embedding, LSTM, Linear
    def __init__(self, V, H=256):                           # V ký tự, ẩn H
        super().__init__()                                  # bắt buộc
        self.nhung = nn.Embedding(V, 64)                    # ký tự thành vector 64 số
        self.lstm = nn.LSTM(64, H, batch_first=True)        # LSTM 256 chiều
        self.ra = nn.Linear(H, V)                           # logit cho mọi ký tự
    def forward(self, x, tt=None):                          # tt: trạng thái (h, c) mang theo khi sinh
        h, tt = self.lstm(self.nhung(x), tt)                # trạng thái mọi bước
        return self.ra(h), tt                               # đoán ký tự tiếp theo ở mọi bước
def loss_val(m):                                            # loss trên toàn bộ tập val
    m.eval()                                                # chế độ đánh giá
    with torch.no_grad():                                   # không cần gradient
        lg, _ = m(va[:-1].unsqueeze(0))                     # cả tập val như một chuỗi
    m.train()                                               # trở lại huấn luyện
    return ce(lg[0], va[1:]).item()                         # cross-entropy trung bình
torch.manual_seed(0)                                        # khởi tạo lặp lại được
m = MoHinhKyTu(len(chu))                                    # mô hình
opt = torch.optim.Adam(m.parameters(), lr=3e-3)             # Adam
g = torch.Generator().manual_seed(1)                        # nguồn vị trí ngẫu nhiên
L, B = 128, 64                                              # độ dài đoạn, số đoạn mỗi lô
tot_nhat, ban_tot = float("inf"), None                      # bản tốt nhất
for b in range(1, 1001):                                    # 1000 bước
    i = torch.randint(0, len(tr) - L - 1, (B,), generator=g)   # 64 vị trí bắt đầu
    x = torch.stack([tr[j:j + L] for j in i])               # đầu vào
    y = torch.stack([tr[j + 1:j + L + 1] for j in i])       # đích: lệch phải 1 ký tự
    lg, _ = m(x)                                            # logit (64, 128, 132)
    opt.zero_grad()                                         # xóa gradient
    ce(lg.reshape(-1, len(chu)), y.reshape(-1)).backward()  # loss trên mọi bài đoán
    nn.utils.clip_grad_norm_(m.parameters(), 1.0)           # kẹp gradient
    opt.step()                                              # cập nhật
    if b % 100 == 0:                                        # mỗi 100 bước
        l = loss_val(m)                                     # đo trên val
        print(b, round(l, 3))                               # in ra
        if l < tot_nhat:                                    # tốt hơn bản đã giữ
            tot_nhat, ban_tot = l, copy.deepcopy(m.state_dict())   # giữ lại
m.load_state_dict(ban_tot)                                  # dùng bản tốt nhất
print(sum(p.numel() for p in m.parameters()), round(tot_nhat, 3), round(math.exp(tot_nhat), 2))   # tham số, loss, perplexity
''', "100 1.887\n200 1.703\n300 1.622\n400 1.586\n500 1.567\n600 1.576\n700 1.586\n800 1.627\n900 1.677\n1000 1.725\n372100 1.567 4.79")
c.o('''
def sinh(m, dau, n, nhiet, seed=0):                         # sinh n ký tự sau đoạn mở đầu
    torch.manual_seed(seed)                                 # lấy mẫu lặp lại được
    m.eval()                                                # chế độ đánh giá
    ra = dau                                                # văn bản sinh ra
    with torch.no_grad():                                   # không cần gradient
        lg, tt = m(torch.tensor([[so[c] for c in dau]]))    # đọc đoạn mở đầu
        for _ in range(n):                                  # mỗi ký tự mới
            p = torch.softmax(lg[0, -1] / nhiet, dim=0)     # nhiệt độ chia logit
            k = torch.multinomial(p, 1)                     # lấy mẫu một ký tự
            ra += chu[k.item()]                             # nối vào
            lg, tt = m(k.view(1, 1), tt)                    # chỉ đưa ký tự mới, mang trạng thái
    return ra                                               # kết quả
print(sinh(m, "Trăm năm trong cõi người ta,\\n", 300, 0.8)) # 300 ký tự ở nhiệt độ 0,8
''', "Trăm năm trong cõi người ta,\nCó lâu mây thấy thảy vào,\nXuân thu khuyết thấy xuân tàn,\nMáu suy lại gió con đọng thâm.\nNàng rằng: Hiếc dắc vạnh thì thôi!\nLi liều vâng tấm thì bời,\nDưới rưung đủ đã rõ rầm nghe thuy,\nTrong thuyền ví lắm chi nàng thân.\nDặm nghe viện trả, trong này,\nSởn nghe nàng cũng này trời mai.\nBây giờ sách nhớ c")
c.o('''
for nhiet in (0.2, 1.2):                                    # hai đầu thang nhiệt độ
    print(nhiet, sinh(m, "Trăm năm trong cõi người ta,\\n", 150, nhiet).split("\\n")[1:4])   # ba dòng đầu sinh ra
''', "0.2 ['Cho nghe nghe những nghĩa cho người cho thang.', 'Chàng chi chẳng thấy một ngày một người.', 'Nghĩ lời nghĩ chẳng thiệt đào,']\n1.2 ['Ôi lây mẹ Giám tình.', 'Bay giờ mực, cóm nhi thân,', 'Trước nào phục tủi việt tinh,']")
c.o(r'''
tieng_kieu = {w.strip(",.;:!?\"'").lower() for c in cau for w in c.split()}   # mọi tiếng có trong Truyện Kiều
for nhiet in (0.2, 0.5, 0.8, 1.2):                          # bốn nhiệt độ
    dong = sinh(m, "Trăm năm trong cõi người ta,\n", 3000, nhiet).split("\n")[1:-1]   # bỏ câu mở đầu, dòng dở cuối
    so_tieng = [len(d.split()) for d in dong]               # số tiếng mỗi dòng
    tieng = [w.strip(",.;:!?\"'").lower() for d in dong for w in d.split()]   # mọi tiếng sinh ra
    print(nhiet, len(dong), round(sum(s in (6, 8) for s in so_tieng) / len(dong), 3),   # tỷ lệ dòng 6 hoặc 8 tiếng
          round(sum(w in tieng_kieu for w in tieng) / len(tieng), 3), sum(d in cau for d in dong))   # tiếng có thật, dòng chép nguyên văn
''', "0.2 80 0.637 0.998 0\n0.5 85 0.741 0.984 0\n0.8 91 0.571 0.929 0\n1.2 95 0.663 0.816 0",
    khung("thu", ["<b>1.</b> Đổi đoạn mở đầu thành một câu 6 tiếng của bạn. Câu tiếp theo có 8 tiếng không?",
                  "<b>2.</b> Thay nn.LSTM bằng nn.GRU trong MoHinhKyTu. Loss val tốt nhất thay đổi thế nào?"]))

c.mo_trang(5, "Ba bài tập. Đoán trước, rồi mới mở đáp án.")
c.bai("29.1", "LSTM hai lớp", "Shape của ra, h_n, c_n và số tham số của nn.LSTM(16, 64, num_layers=2).",
      "ra (8, 20, 64), h_n và c_n (2, 8, 64), 54 272 tham số. Code ở ô ngay dưới.")
c.o('''
lstm2 = nn.LSTM(16, 64, num_layers=2, batch_first=True)     # hai lớp chồng lên nhau
ra, (h_n, c_n) = lstm2(torch.randn(8, 20, 16))              # LSTM trả về một cặp (h, c)
print(ra.shape, h_n.shape, c_n.shape)                       # shape
print(sum(p.numel() for p in lstm2.parameters()), [(n, p.numel()) for n, p in lstm2.named_parameters() if "weight" in n])   # tham số
''', "torch.Size([8, 20, 64]) torch.Size([2, 8, 64]) torch.Size([2, 8, 64])\n54272 [('weight_ih_l0', 4096), ('weight_hh_l0', 16384), ('weight_ih_l1', 16384), ('weight_hh_l1', 16384)]")
c.bai("29.2", "Nhớ qua 100 bước", "LSTM bias cổng quên 3, kẹp 1,0, chuỗi 100 bước.",
      "99,9% sau 1500 bước nhưng chậm hơn chuỗi 50 bước nhiều. Code ở ô ngay dưới.")
c.o('''
huan_luyen(nn.LSTM, bias_cong=3.0, kep=1.0, T=100)          # chuỗi dài gấp đôi
''', "LSTM 3.0 1.0 [0.327, 0.518, 0.668, 0.814, 0.975, 0.999] 1168.3")
c.bai("29.3", "Nhiệt độ bằng tay", "Xác suất của logit [2, 1, 0] ở nhiệt độ 1; 0,5; 2.",
      "0,665 / 0,245 / 0,09 ở nhiệt độ 1. Code ở ô ngay dưới.")
c.o('''
z = torch.tensor([2.0, 1.0, 0.0])                           # ba logit
for nhiet in (1.0, 0.5, 2.0):                               # ba nhiệt độ
    print(nhiet, [round(v, 3) for v in torch.softmax(z / nhiet, 0).tolist()])   # xác suất
''', "1.0 [0.665, 0.245, 0.09]\n0.5 [0.867, 0.117, 0.016]\n2.0 [0.506, 0.307, 0.186]")

c.ghi(Path(__file__).resolve().parents[2] / "notebooks/ch29_rnn_lstm_gru.ipynb")
