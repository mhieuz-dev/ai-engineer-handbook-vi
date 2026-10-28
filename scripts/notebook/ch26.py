"""Dựng notebooks/ch26_huan_luyen_mang_sau.ipynb: python3 scripts/notebook/ch26.py"""
from pathlib import Path
from nblib import Chuong, khung

c = Chuong(26, "Huấn luyện mạng sâu", "ch26-huan-luyen-mang-sau",
           "Đo gradient biến mất trên mạng 10 lớp, chữa bằng khởi tạo He và batch norm, chống overfitting bằng dropout, weight decay, dừng sớm, rồi lịch learning rate và kẹp gradient.",
           ["Đo gradient từng lớp và giải thích gradient biến mất.",
            "Chọn khởi tạo He và dùng batch norm với hai chế độ train, eval.",
            "So sánh dropout, weight decay và dừng sớm trên cùng thí nghiệm.",
            "Dùng lịch cosine và kẹp gradient."],
           [("Gradient biến mất và khởi tạo", "01-gradient-bien-mat"), ("Batch normalization", "02-batch-norm"),
            ("Dropout, weight decay và dừng sớm", "03-chong-overfitting"), ("Lịch learning rate và các mẹo khác", "04-lich-learning-rate"),
            ("Bài tập", "05-bai-tap")])

c.mo_trang(1, "Gradient từng lớp của mạng 10 lớp ẩn.")
c.o('''
import torch                                                # PyTorch
import torch.nn as nn                                       # các lớp mạng
import numpy as np                                          # argmin ở trang 3
from sklearn.datasets import load_digits                    # chữ số 8x8
from sklearn.model_selection import train_test_split        # chia train, test
dg = load_digits()                                          # 1797 ảnh
A, B, C, E = train_test_split(dg.data / 16.0, dg.target, test_size=0.2, random_state=0, stratify=dg.target)   # 1437 và 360
Xtr, ytr = torch.tensor(A, dtype=torch.float32), torch.tensor(C)   # train
Xte, yte = torch.tensor(B, dtype=torch.float32), torch.tensor(E)   # test
ce = nn.CrossEntropyLoss()                                  # loss phân loại
def sau(kich_hoat, bn=False):                               # 10 lớp ẩn, mỗi lớp 64 nơ-ron
    lop = []                                                # danh sách lớp
    for _ in range(10):                                     # 10 lớp ẩn
        lop.append(nn.Linear(64, 64))                       # lớp dày đặc
        if bn:                                              # có batch norm không
            lop.append(nn.BatchNorm1d(64))                  # chuẩn hóa trước kích hoạt
        lop.append(kich_hoat())                             # kích hoạt
    lop.append(nn.Linear(64, 10))                           # lớp ra 10 logit
    return nn.Sequential(*lop)                              # nối lại
def chuan_grad(m):                                          # độ lớn gradient lớp 1, 3, 5, 7, 9, 11
    ce(m(Xtr), ytr).backward()                              # một lượt ngược trên cả train
    lin = [l for l in m if isinstance(l, nn.Linear)]        # 11 lớp Linear
    return [f"{l.weight.grad.norm().item():.1e}" for l in lin[::2]]   # cách một lớp lấy một
for kh in (nn.Sigmoid, nn.ReLU):                            # hai kích hoạt
    torch.manual_seed(0)                                    # cùng khởi tạo
    print(kh.__name__, chuan_grad(sau(kh)))                 # gradient theo lớp
''', "Sigmoid ['1.3e-09', '4.1e-08', '2.1e-06', '9.6e-05', '5.2e-03', '2.7e-01']\nReLU ['6.3e-05', '4.4e-05', '6.5e-05', '2.1e-04', '1.5e-03', '1.3e-02']")
c.o('''
torch.manual_seed(0)                                        # seed
x = torch.randn(512, 256)                                   # 512 mẫu, 256 đặc trưng
for ten, std in [("1", 1.0), ("0.01", 0.01), ("He", (2 / 256) ** 0.5)]:   # ba mức khởi tạo
    h = x                                                   # bắt đầu từ đầu vào
    for _ in range(10):                                     # 10 lớp ReLU
        h = torch.relu(h @ (torch.randn(256, 256) * std))   # trọng số N(0, std^2)
    print(ten, f"{h.std().item():.1e}")                     # độ lệch chuẩn sau 10 lớp
''', "1 2.9e+10\n0.01 2.9e-10\nHe 7.0e-01")
c.o('''
def he(m):                                                  # khởi tạo He cho mọi lớp Linear
    for l in m:                                             # duyệt các lớp
        if isinstance(l, nn.Linear):                        # chỉ lớp Linear
            nn.init.kaiming_normal_(l.weight, nonlinearity="relu")   # std = căn(2/d)
            nn.init.zeros_(l.bias)                          # hệ số chặn bằng 0
    return m                                                # trả lại mạng
torch.manual_seed(0)                                        # cùng seed
print("ReLU + He", chuan_grad(he(sau(nn.ReLU))))            # gradient đều qua các lớp
''', "ReLU + He ['5.4e-01', '7.1e-01', '7.8e-01', '6.8e-01', '4.8e-01', '3.3e-01']")

c.mo_trang(2, "Bốn phiên bản của mạng 10 lớp, huấn luyện 30 epoch.")
c.o('''
from torch.utils.data import TensorDataset, DataLoader      # chia lô
def huan_luyen(m, opt, so_epoch=30, X=Xtr, y=ytr, lich=None):   # dùng lại cả chương
    torch.manual_seed(1)                                    # cố định thứ tự xáo trộn
    dl = DataLoader(TensorDataset(X, y), batch_size=64, shuffle=True)   # lô 64
    ls = []                                                 # lịch sử theo epoch
    for ep in range(so_epoch):                              # mỗi epoch
        m.train()                                           # chế độ huấn luyện
        for xb, yb in dl:                                   # mỗi lô
            opt.zero_grad()                                 # xóa gradient
            ce(m(xb), yb).backward()                        # lượt xuôi và ngược
            opt.step()                                      # cập nhật
        if lich:                                            # có lịch learning rate
            lich.step()                                     # cập nhật sau mỗi epoch
        m.eval()                                            # chế độ đánh giá
        with torch.no_grad():                               # không cần gradient
            ls.append((ce(m(X), y).item(), ce(m(Xte), yte).item(), (m(Xte).argmax(1) == yte).float().mean().item()))   # loss train, loss test, độ chính xác
    return ls                                               # trả lịch sử
for ten, tao in [("Sigmoid", lambda: sau(nn.Sigmoid)), ("ReLU", lambda: sau(nn.ReLU)),   # bốn phiên bản
                 ("ReLU + He", lambda: he(sau(nn.ReLU))), ("Sigmoid + BN", lambda: sau(nn.Sigmoid, bn=True))]:
    torch.manual_seed(0)                                    # cùng seed
    m = tao()                                               # dựng mạng
    ls = huan_luyen(m, torch.optim.Adam(m.parameters(), lr=1e-3))   # 30 epoch Adam
    print(ten, [round(ls[i][2], 4) for i in (0, 9, 29)])    # test sau epoch 1, 10, 30
''', "Sigmoid [0.1028, 0.1, 0.1028]\nReLU [0.0972, 0.6306, 0.85]\nReLU + He [0.5639, 0.9556, 0.9667]\nSigmoid + BN [0.0972, 0.9611, 0.9806]",
    khung("vi-sao", ["Batch norm giữ đầu vào của mỗi sigmoid quanh 0, vùng dốc nhất của đường chữ S, nên gradient không biến mất."],
          nhan="VÌ SAO SIGMOID + BN LẠI THẮNG?"))

c.mo_trang(3, "300 ảnh train, mạng 85 nghìn tham số.")
c.o('''
Xit, yit = Xtr[:300], ytr[:300]                             # chỉ 300 ảnh train
def rong(p=0.0):                                            # 64 -> 256 -> 256 -> 10
    return nn.Sequential(nn.Linear(64, 256), nn.ReLU(), nn.Dropout(p),   # lớp ẩn 1 và dropout
                         nn.Linear(256, 256), nn.ReLU(), nn.Dropout(p), nn.Linear(256, 10))   # lớp ẩn 2, lớp ra
print(sum(p.numel() for p in rong().parameters()))          # số tham số
kq = {}                                                     # lịch sử từng cách
for ten, p, wd in [("không gì", 0.0, 0.0), ("dropout 0.5", 0.5, 0.0), ("weight decay 0.1", 0.0, 0.1)]:   # ba cách
    torch.manual_seed(0)                                    # cùng khởi tạo
    m = rong(p)                                             # dựng mạng
    kq[ten] = huan_luyen(m, torch.optim.AdamW(m.parameters(), lr=1e-3, weight_decay=wd), so_epoch=200, X=Xit, y=yit)   # 200 epoch
    tr, te, acc = kq[ten][-1]                               # epoch cuối
    print(ten, round(tr, 4), round(te, 4), round(acc, 4))   # loss train, loss test, độ chính xác
''', "85002\nkhông gì 0.0005 0.3208 0.9361\ndropout 0.5 0.0009 0.2135 0.9417\nweight decay 0.1 0.001 0.2823 0.9333")
c.o('''
for ten, ls in kq.items():                                  # từng cách
    tot = int(np.argmin([l[1] for l in ls]))                # epoch có loss test thấp nhất
    print(ten, tot + 1, round(ls[tot][1], 4), round(ls[tot][2], 4))   # epoch, loss, độ chính xác
''', "không gì 42 0.2498 0.9333\ndropout 0.5 174 0.1989 0.9472\nweight decay 0.1 42 0.2467 0.9333",
    khung("thu", ["<b>1.</b> Tăng weight decay lên 1 và 10. Loss test đổi thế nào?",
                  "<b>2.</b> Đổi dropout thành 0,2. Tốt hơn hay kém hơn 0,5?"]))

c.mo_trang(4, "Learning rate cố định và lịch cosine.")
c.o('''
for ten in ("cố định", "cosine"):                           # hai cách
    torch.manual_seed(0)                                    # cùng khởi tạo
    m = he(sau(nn.ReLU))                                    # mạng 10 lớp ReLU + He
    opt = torch.optim.SGD(m.parameters(), lr=0.02, momentum=0.9)   # SGD momentum
    lich = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=30) if ten == "cosine" else None   # lịch cosine
    ls = huan_luyen(m, opt, lich=lich)                      # 30 epoch
    print(ten, round(ls[-1][0], 4), round(ls[-1][1], 4), round(ls[-1][2], 4), round(opt.param_groups[0]["lr"], 4))   # loss train, loss test, độ chính xác, lr cuối
''', "cố định 0.003 0.1867 0.9611 0.02\ncosine 0.0026 0.1448 0.9667 0.0")

c.mo_trang(5, "Ba bài tập. Đoán trước, rồi mới mở đáp án.")
c.bai("26.1", "Std của khởi tạo He", "Lớp nn.Linear(256, 128) theo sau là ReLU. Std khởi tạo He bằng bao nhiêu?",
      "$\\sqrt{2/256} \\approx 0{,}0884$; số đầu ra không vào công thức. Code ở ô ngay dưới.")
c.o('''
print(round((2 / 256) ** 0.5, 4))                           # căn(2/d) với d = 256
''', "0.0884")
c.bai("26.2", "Cứu một lần huấn luyện bị nan", "SGD momentum lr 0,05 trên mạng trang 4, có và không có kẹp gradient ở 1,0.",
      "Không kẹp: nan, 10%. Kẹp ở 1,0: test 95,8%. Code ở ô ngay dưới.")
c.o('''
def huan_luyen_kep(m, opt, nguong, so_epoch=30):            # huấn luyện có kẹp gradient
    torch.manual_seed(1)                                    # cùng thứ tự lô
    dl = DataLoader(TensorDataset(Xtr, ytr), batch_size=64, shuffle=True)   # lô 64
    for ep in range(so_epoch):                              # mỗi epoch
        m.train()                                           # chế độ huấn luyện
        for xb, yb in dl:                                   # mỗi lô
            opt.zero_grad()                                 # xóa gradient
            ce(m(xb), yb).backward()                        # lượt ngược
            if nguong:                                      # có kẹp không
                nn.utils.clip_grad_norm_(m.parameters(), nguong)   # kẹp độ dài vector gradient
            opt.step()                                      # cập nhật
    m.eval()                                                # đánh giá
    with torch.no_grad():                                   # không cần gradient
        return round(ce(m(Xte), yte).item(), 4), round((m(Xte).argmax(1) == yte).float().mean().item(), 4)   # loss, độ chính xác
for nguong in (None, 1.0):                                  # không kẹp và kẹp ở 1
    torch.manual_seed(0)                                    # cùng khởi tạo
    m = he(sau(nn.ReLU))                                    # mạng trang 4
    print(nguong, huan_luyen_kep(m, torch.optim.SGD(m.parameters(), lr=0.05, momentum=0.9), nguong))   # kết quả
''', "None (nan, 0.1)\n1.0 (0.289, 0.9583)")
c.bai("26.3", "Quên model.eval với dropout", "Huấn luyện lại mạng dropout 0,5, đánh giá hai lần ở chế độ train và một lần ở chế độ eval.",
      "93,1% và 91,9% ở chế độ train, 94,2% ở chế độ eval. Code ở ô ngay dưới.")
c.o('''
torch.manual_seed(0)                                        # cùng khởi tạo trang 3
m = rong(0.5)                                               # mạng dropout
huan_luyen(m, torch.optim.AdamW(m.parameters(), lr=1e-3, weight_decay=0.0), so_epoch=200, X=Xit, y=yit)   # huấn luyện lại
with torch.no_grad():                                       # đánh giá
    m.train()                                               # quên eval: dropout vẫn bật
    a1, a2 = (m(Xte).argmax(1) == yte).float().mean().item(), (m(Xte).argmax(1) == yte).float().mean().item()   # hai lần đo
    m.eval()                                                # chế độ đúng
    a3 = (m(Xte).argmax(1) == yte).float().mean().item()    # một lần đo
print(round(a1, 4), round(a2, 4), round(a3, 4))             # so sánh
''', "0.9306 0.9194 0.9417")

c.ghi(Path(__file__).resolve().parents[2] / "notebooks/ch26_huan_luyen_mang_sau.ipynb")
