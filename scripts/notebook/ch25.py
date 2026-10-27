"""Dựng notebooks/ch25_pytorch_can_ban.ipynb: python3 scripts/notebook/ch25.py"""
from pathlib import Path
from nblib import Chuong, khung

c = Chuong(25, "PyTorch căn bản", "ch25-pytorch-can-ban",
           "Tensor, autograd, nn.Module và vòng huấn luyện bốn dòng, DataLoader và GPU: viết lại mạng của Chương 24 bằng PyTorch rồi phân loại chữ số viết tay.",
           ["Dùng tensor như mảng NumPy và tránh bẫy dùng chung bộ nhớ.",
            "Tính gradient bằng autograd, kiểm bằng số của Chương 24.",
            "Viết vòng huấn luyện zero_grad, loss, backward, step.",
            "Huấn luyện theo lô bằng DataLoader tới 95,8% trên chữ số viết tay."],
           [("Tensor", "01-tensor"), ("Autograd", "02-autograd"), ("nn.Module và vòng huấn luyện", "03-nn-module"),
            ("DataLoader, nhiều lớp và GPU", "04-dataloader-va-gpu"), ("Bài tập", "05-bai-tap")])

c.mo_trang(1, "Tensor như mảng NumPy.")
c.o('''
import torch                       # PyTorch
import numpy as np                 # để so sánh
print(torch.__version__)           # phiên bản
t = torch.tensor([[1.0, 2.0], [3.0, 4.0]])   # tensor 2x2
print(t.shape, t.dtype)            # shape và kiểu
print(t @ t)                       # nhân ma trận, như NumPy
print(t.T)                         # chuyển vị
print(t.sum(0))                    # tổng theo trục 0
''', "2.14.1+cpu\ntorch.Size([2, 2]) torch.float32\ntensor([[ 7., 10.],\n        [15., 22.]])\ntensor([[1., 3.],\n        [2., 4.]])\ntensor([4., 6.])")
c.o('''
a = np.array([1.0, 2.0])           # mảng NumPy
ta = torch.from_numpy(a)           # KHÔNG chép: dùng chung bộ nhớ
ta[0] = 99                         # sửa qua tensor
print(a)                           # mảng NumPy cũng đổi
''', "[99.  2.]",
    khung("vi-sao", ["torch.from_numpy và .numpy() không chép dữ liệu. Muốn bản sao độc lập, dùng torch.tensor(a) hoặc .clone()."],
          nhan="VÌ SAO MẢNG NUMPY BỊ ĐỔI?"))

c.mo_trang(2, "Autograd: số của Chương 24, không viết lượt ngược.")
c.o('''
w = torch.tensor(0.5, requires_grad=True)       # cần gradient theo w
b = torch.tensor(0.1, requires_grad=True)       # cần gradient theo b
x, y = 2.0, 1.0                                 # đầu vào, nhãn
L = (torch.sigmoid(w * x + b) - y) ** 2         # lượt xuôi
L.backward()                                    # lượt ngược tự động
print(round(L.item(), 4), round(w.grad.item(), 4), round(b.grad.item(), 4))   # loss và gradient
''', "0.0624 -0.1872 -0.0936")
c.o('''
w = torch.tensor(0.5, requires_grad=True)       # tạo lại w
for lan in range(3):                            # ba lần backward
    L = (torch.sigmoid(w * 2.0 + 0.1) - 1.0) ** 2   # lượt xuôi
    L.backward()                                # không xóa gradient
    print(lan, round(w.grad.item(), 4))         # gradient cộng dồn
''', "0 -0.1872\n1 -0.3743\n2 -0.5615")
c.o('''
with torch.no_grad():                           # tắt autograd
    z = w * 2.0 + 0.1                           # không ghi đồ thị
print(z.requires_grad)                          # False
''', "False")

c.mo_trang(3, "nn.Sequential và vòng huấn luyện bốn dòng.")
c.o('''
import torch.nn as nn                           # các lớp mạng
torch.manual_seed(0)                            # khởi tạo lặp lại được
lin = nn.Linear(2, 3)                           # 2 đầu vào, 3 nơ-ron
print(lin.weight.shape, lin.bias.shape, sum(p.numel() for p in lin.parameters()))   # shape và số tham số
''', "torch.Size([3, 2]) torch.Size([3]) 9")
c.o('''
from sklearn.datasets import make_moons                     # dữ liệu
from sklearn.model_selection import train_test_split        # chia
Xm, ym = make_moons(300, noise=0.3, random_state=0)         # hai vầng trăng
a, b_, c, e = train_test_split(Xm, ym, test_size=0.3, random_state=0)   # 210 train, 90 test
Xtr, ytr = torch.tensor(a, dtype=torch.float32), torch.tensor(c, dtype=torch.float32)   # train
Xte, yte = torch.tensor(b_, dtype=torch.float32), torch.tensor(e, dtype=torch.float32)  # test
torch.manual_seed(0)                                        # seed
m = nn.Sequential(nn.Linear(2, 32), nn.ReLU(), nn.Linear(32, 1))   # 2 -> 32 ReLU -> 1
print(sum(p.numel() for p in m.parameters()))               # số tham số
''', "129")
c.o('''
opt = torch.optim.SGD(m.parameters(), lr=0.5)      # gradient descent
lf = nn.BCEWithLogitsLoss()                        # sigmoid + cross-entropy
dung = lambda X, y: ((m(X).squeeze(1) > 0).float() == y).float().mean().item()   # độ chính xác
for buoc in range(3001):                           # 3000 bước
    if buoc in (0, 100, 1000, 3000):               # in vài mốc
        with torch.no_grad():                      # đánh giá, không cần gradient
            print(buoc, round(lf(m(Xtr).squeeze(1), ytr).item(), 4), round(dung(Xtr, ytr), 4), round(dung(Xte, yte), 4))   # loss, train, test
    opt.zero_grad()                                # 1. xóa gradient cũ
    loss = lf(m(Xtr).squeeze(1), ytr)              # 2. lượt xuôi và loss
    loss.backward()                                # 3. lượt ngược
    opt.step()                                     # 4. cập nhật
''', "0 0.6924 0.5 0.3444\n100 0.3181 0.8476 0.8222\n1000 0.1711 0.9476 0.9556\n3000 0.1567 0.9476 0.9444")

c.mo_trang(4, "DataLoader và 10 chữ số viết tay.")
c.o('''
from sklearn.datasets import load_digits                    # chữ số 8x8
from torch.utils.data import TensorDataset, DataLoader      # chia lô
dg = load_digits()                                          # 1797 ảnh
X = dg.data / 16.0                                          # đưa về 0 tới 1
A, B, C, E = train_test_split(X, dg.target, test_size=0.2, random_state=0, stratify=dg.target)   # 1437 train, 360 test
torch.manual_seed(0)                                        # seed
dl = DataLoader(TensorDataset(torch.tensor(A, dtype=torch.float32), torch.tensor(C)), batch_size=64, shuffle=True)   # lô 64
net = nn.Sequential(nn.Linear(64, 64), nn.ReLU(), nn.Linear(64, 10))   # 10 logit
opt = torch.optim.Adam(net.parameters(), lr=1e-3)           # Adam
ce = nn.CrossEntropyLoss()                                  # softmax + cross-entropy
Bt, Et = torch.tensor(B, dtype=torch.float32), torch.tensor(E)   # test
print(len(dl), sum(p.numel() for p in net.parameters()))   # số lô, số tham số
for ep in range(1, 31):                                     # 30 epoch
    for xb, yb in dl:                                       # mỗi vòng một lô
        opt.zero_grad()                                     # xóa gradient
        loss = ce(net(xb), yb)                              # loss
        loss.backward()                                     # lượt ngược
        opt.step()                                          # cập nhật
    if ep in (1, 5, 10, 30):                                # in vài mốc
        with torch.no_grad():                               # đánh giá
            print(ep, round(loss.item(), 4), round((net(Bt).argmax(1) == Et).float().mean().item(), 4))   # loss lô cuối, test
''', "23 4810\n1 2.1383 0.5861\n5 1.1455 0.8944\n10 0.5501 0.9278\n30 0.1534 0.9583",
    khung("thu", ["<b>1.</b> Bật GPU trên Colab, chuyển net và từng lô sang cuda. Có nhanh hơn không?",
                  "<b>2.</b> Đổi batch_size thành 16. Có bao nhiêu lô mỗi epoch?"]))
c.o('''
thiet_bi = "cuda" if torch.cuda.is_available() else "cpu"   # chọn thiết bị
print(thiet_bi)                                             # cpu hoặc cuda
''', "cpu")

c.mo_trang(5, "Ba bài tập. Đoán trước, rồi mới mở đáp án.")
c.bai("25.1", "Autograd trên một đa thức", "Với $y = x^3 + 2x$ tại $x = 2$, tính tay $dy/dx$ rồi kiểm bằng backward.",
      "$dy/dx = 3x^2 + 2 = 14$, $y = 12$. Code ở ô ngay dưới.")
c.o('''
x = torch.tensor(2.0, requires_grad=True)   # biến
y = x ** 3 + 2 * x                          # đa thức
y.backward()                                # đạo hàm
print(y.item(), x.grad.item())              # 12 và 14
''', "12.0 14.0")
c.bai("25.2", "Thay SGD bằng Adam", "Mạng trang 3, Adam lr 0,01, 1000 bước. In loss, train, test.",
      "Loss 0,151, train 94,3%, test 94,4%: chỉ đổi một dòng. Code ở ô ngay dưới.")
c.o('''
def chay(tao_opt, xoa=True, n=1000):                     # huấn luyện lại từ đầu
    torch.manual_seed(0)                                 # cùng khởi tạo
    m = nn.Sequential(nn.Linear(2, 32), nn.ReLU(), nn.Linear(32, 1))   # mạng trang 3
    opt = tao_opt(m.parameters())                        # optimizer tùy chọn
    for _ in range(n):                                   # n bước
        if xoa:                                          # có xóa gradient không
            opt.zero_grad()                              # xóa
        loss = lf(m(Xtr).squeeze(1), ytr)                # loss
        loss.backward()                                  # lượt ngược
        opt.step()                                       # cập nhật
    with torch.no_grad():                                # đánh giá
        d = lambda X, y: ((m(X).squeeze(1) > 0).float() == y).float().mean().item()   # độ chính xác
        print(round(lf(m(Xtr).squeeze(1), ytr).item(), 4), round(d(Xtr, ytr), 4), round(d(Xte, yte), 4))   # loss, train, test
chay(lambda p: torch.optim.Adam(p, lr=0.01))             # Adam
''', "0.151 0.9429 0.9444")
c.bai("25.3", "Quên zero_grad", "Mạng trang 3, SGD lr 0,5, 1000 bước, bỏ zero_grad.",
      "Loss kẹt 0,4852, train 70%, test 83,3%, không có lỗi nào được báo. Code ở ô ngay dưới.")
c.o('''
chay(lambda p: torch.optim.SGD(p, lr=0.5), xoa=False)    # không xóa gradient
''', "0.4852 0.7 0.8333")

c.ghi(Path(__file__).resolve().parents[2] / "notebooks/ch25_pytorch_can_ban.ipynb")
