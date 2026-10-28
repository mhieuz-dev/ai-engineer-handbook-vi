"""Dựng notebooks/ch27_cnn.ipynb: python3 scripts/notebook/ch27.py"""
from pathlib import Path
from nblib import Chuong, khung

c = Chuong(27, "CNN", "ch27-cnn",
           "Tích chập bằng tay, lớp Conv2d và pooling, một CNN 20 nghìn tham số đạt 98,2% trên MNIST, rồi nhìn bộ lọc nó học và thử dịch ảnh.",
           ["Tính tay một phép tích chập và kích thước đầu ra.",
            "Đếm tham số của lớp tích chập, so với lớp dày đặc.",
            "Huấn luyện CNN trên MNIST, so với MLP.",
            "Đo độ bền của CNN và MLP khi dịch ảnh."],
           [("Phép tích chập", "01-phep-tich-chap"), ("Lớp tích chập và pooling", "02-lop-tich-chap-va-pooling"),
            ("CNN trên MNIST", "03-cnn-tren-mnist"), ("Bên trong một CNN", "04-ben-trong-cnn"), ("Bài tập", "05-bai-tap")])

c.mo_trang(1, "Trượt một bộ lọc cạnh dọc qua ảnh 6x6.")
c.o('''
import numpy as np                             # tính tay bằng NumPy
anh = np.zeros((6, 6))                         # ảnh 6x6 toàn 0
anh[:, 3:] = 1                                 # nửa phải sáng
k = np.array([[-1, 0, 1],                      # bộ lọc cạnh dọc
              [-1, 0, 1],                      # cột trái âm
              [-1, 0, 1]])                     # cột phải dương
ra = np.zeros((4, 4))                          # kết quả 4x4
for i in range(4):                             # mỗi hàng của kết quả
    for j in range(4):                         # mỗi cột của kết quả
        ra[i, j] = (anh[i:i + 3, j:j + 3] * k).sum()   # nhân từng ô của cửa sổ rồi cộng
print(ra)                                      # bản đồ cạnh
''', "[[0. 3. 3. 0.]\n [0. 3. 3. 0.]\n [0. 3. 3. 0.]\n [0. 3. 3. 0.]]")
c.o('''
import torch                                   # PyTorch
import torch.nn.functional as F                # hàm conv2d
x = torch.tensor(anh, dtype=torch.float32).reshape(1, 1, 6, 6)    # (lô, kênh, cao, rộng)
w = torch.tensor(k, dtype=torch.float32).reshape(1, 1, 3, 3)      # (kênh ra, kênh vào, cao, rộng)
print(F.conv2d(x, w)[0, 0])                    # giống vòng lặp tay
''', "tensor([[0., 3., 3., 0.],\n        [0., 3., 3., 0.],\n        [0., 3., 3., 0.],\n        [0., 3., 3., 0.]])")
c.o('''
print(F.conv2d(x, w).shape, F.conv2d(x, w, padding=1).shape, F.conv2d(x, w, stride=2).shape)   # không padding, padding 1, stride 2
''', "torch.Size([1, 1, 4, 4]) torch.Size([1, 1, 6, 6]) torch.Size([1, 1, 2, 2])")

c.mo_trang(2, "Conv2d, pooling và một CNN hoàn chỉnh.")
c.o('''
import torch.nn as nn                          # các lớp mạng
conv = nn.Conv2d(3, 16, kernel_size=3)         # 3 kênh vào, 16 bộ lọc 3x3
print(conv.weight.shape, sum(p.numel() for p in conv.parameters()))   # shape trọng số, số tham số
lo = torch.randn(32, 3, 224, 224)              # 32 ảnh màu 224x224
print(conv(lo).shape)                          # 16 bản đồ 222x222 mỗi ảnh
vao, ra_ = 3 * 224 * 224, 16 * 222 * 222       # nếu dùng lớp dày đặc
print(f"{vao * ra_:.2e}")                      # số trọng số cần có
''', "torch.Size([16, 3, 3, 3]) 448\ntorch.Size([32, 16, 222, 222])\n1.19e+11")
c.o('''
a = torch.tensor([[1., 3., 2., 0.],            # bản đồ 4x4
                  [4., 2., 1., 1.],            # hàng 2
                  [0., 1., 5., 6.],            # hàng 3
                  [2., 2., 7., 3.]]).reshape(1, 1, 4, 4)   # hàng 4
print(nn.MaxPool2d(2)(a)[0, 0])                # số lớn nhất trong mỗi ô 2x2
''', "tensor([[4., 2.],\n        [2., 7.]])")
c.o('''
torch.manual_seed(0)                           # khởi tạo lặp lại được
cnn = nn.Sequential(nn.Conv2d(1, 16, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),     # khối 1
                    nn.Conv2d(16, 32, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),    # khối 2
                    nn.Flatten(), nn.Linear(32 * 7 * 7, 10))                        # phân loại
h = torch.zeros(1, 1, 28, 28)                  # một ảnh giả
for lop in cnn:                                # qua từng lớp
    h = lop(h)                                 # lượt xuôi
    print(type(lop).__name__, tuple(h.shape))  # tên lớp và shape
print(sum(p.numel() for p in cnn.parameters()))   # tổng tham số
''', "Conv2d (1, 16, 28, 28)\nReLU (1, 16, 28, 28)\nMaxPool2d (1, 16, 14, 14)\nConv2d (1, 32, 14, 14)\nReLU (1, 32, 14, 14)\nMaxPool2d (1, 32, 7, 7)\nFlatten (1, 1568)\nLinear (1, 10)\n20490")

c.mo_trang(3, "MLP và CNN trên MNIST, 2 epoch mỗi mô hình (CNN khoảng 5 giây mỗi epoch trên CPU nhiều nhân).")
c.o('''
from torchvision import datasets                            # bộ dữ liệu ảnh
from torch.utils.data import TensorDataset, DataLoader      # chia lô
tr = datasets.MNIST("data", train=True, download=True)      # 60 000 ảnh train, tải lần đầu
te = datasets.MNIST("data", train=False, download=True)     # 10 000 ảnh test
Xtr, ytr = tr.data.float().div(255).unsqueeze(1), tr.targets   # (60000, 1, 28, 28), 0 tới 1
Xte, yte = te.data.float().div(255).unsqueeze(1), te.targets   # test
print(Xtr.shape, Xte.shape)                                 # shape
ce = nn.CrossEntropyLoss()                                  # loss
def huan_luyen(m, so_epoch=2):                              # huấn luyện và in độ chính xác test
    torch.manual_seed(1)                                    # cố định thứ tự lô
    dl = DataLoader(TensorDataset(Xtr, ytr), batch_size=64, shuffle=True)   # lô 64
    opt = torch.optim.Adam(m.parameters(), lr=1e-3)         # Adam
    for ep in range(so_epoch):                              # mỗi epoch
        m.train()                                           # chế độ huấn luyện
        for xb, yb in dl:                                   # mỗi lô
            opt.zero_grad()                                 # xóa gradient
            ce(m(xb), yb).backward()                        # lượt ngược
            opt.step()                                      # cập nhật
        m.eval()                                            # đánh giá
        with torch.no_grad():                               # không cần gradient
            print(ep + 1, round((m(Xte).argmax(1) == yte).float().mean().item(), 4))   # độ chính xác test
    return m                                                # mô hình đã huấn luyện
torch.manual_seed(0)                                        # seed cho MLP
mlp = nn.Sequential(nn.Flatten(), nn.Linear(784, 128), nn.ReLU(), nn.Linear(128, 10))   # MLP 784-128-10
print("MLP", sum(p.numel() for p in mlp.parameters()))      # số tham số MLP
huan_luyen(mlp)                                             # 2 epoch
print("CNN", sum(p.numel() for p in cnn.parameters()))      # số tham số CNN
huan_luyen(cnn)                                             # 2 epoch
''', "torch.Size([60000, 1, 28, 28]) torch.Size([10000, 1, 28, 28])\nMLP 101770\n1 0.9455\n2 0.9631\nCNN 20490\n1 0.9792\n2 0.9817",
    khung("thu", ["<b>1.</b> Bật GPU trên Colab, chuyển mô hình và dữ liệu sang cuda. Mỗi epoch CNN nhanh hơn bao nhiêu lần?",
                  "<b>2.</b> Huấn luyện thêm 3 epoch. CNN có vượt 98,5% không?"]))

c.mo_trang(4, "Dịch ảnh test sang phải vài điểm ảnh.")
c.o('''
def dich(X, d):                                # dịch sang phải d điểm ảnh
    Y = torch.zeros_like(X)                    # nền đen
    Y[..., d:] = X[..., :-d]                   # chép phần còn lại
    return Y                                   # ảnh đã dịch
with torch.no_grad():                          # chỉ đánh giá
    for d in (1, 2, 3, 4):                     # bốn mức dịch
        Xd = dich(Xte, d)                      # tập test đã dịch
        print(d, round((mlp(Xd).argmax(1) == yte).float().mean().item(), 4),   # MLP
              round((cnn(Xd).argmax(1) == yte).float().mean().item(), 4))      # CNN
''', "1 0.9366 0.9757\n2 0.7431 0.9367\n3 0.4623 0.8054\n4 0.2721 0.6059",
    khung("vi-sao", ["Tích chập dùng cùng bộ lọc ở mọi vị trí nên chịu dịch tốt hơn, nhưng lớp Linear cuối vẫn có trọng số riêng cho từng vị trí trên bản đồ 7x7."],
          nhan="VÌ SAO CNN VẪN GIẢM KHI DỊCH 4 ĐIỂM ẢNH?"))

c.mo_trang(5, "Ba bài tập. Tính tay trước, rồi mới mở đáp án.")
c.bai("27.1", "Shape qua LeNet", "Conv2d(1, 6, kernel_size=5) rồi MaxPool2d(2) trên ảnh 28x28. Shape sau mỗi lớp?",
      "(1, 6, 24, 24) rồi (1, 6, 12, 12). Code ở ô ngay dưới.")
c.o('''
lenet = nn.Sequential(nn.Conv2d(1, 6, kernel_size=5), nn.MaxPool2d(2))   # không padding, stride 1
print(lenet[0](torch.zeros(1, 1, 28, 28)).shape, lenet(torch.zeros(1, 1, 28, 28)).shape)   # sau tích chập, sau pooling
''', "torch.Size([1, 6, 24, 24]) torch.Size([1, 6, 12, 12])")
c.bai("27.2", "Đếm tham số bằng tay", "Conv2d(16, 32, kernel_size=3) có bao nhiêu tham số?",
      "$32 \\times 16 \\times 9 + 32 = 4640$. Code ở ô ngay dưới.")
c.o('''
print(sum(p.numel() for p in nn.Conv2d(16, 32, 3).parameters()), 16 * 32 * 9 + 32)   # PyTorch đếm và tính tay
''', "4640 4640")
c.bai("27.3", "Bỏ pooling", "Bỏ hai lớp MaxPool2d khỏi CNN trang 2. Tổng tham số và phần của lớp cuối?",
      "255 690 tham số, gấp 12,5 lần; lớp cuối 250 890, chiếm 98%. Code ở ô ngay dưới.")
c.o('''
khong_pool = nn.Sequential(nn.Conv2d(1, 16, 3, padding=1), nn.ReLU(),   # khối 1 không pooling
                           nn.Conv2d(16, 32, 3, padding=1), nn.ReLU(),  # khối 2 không pooling
                           nn.Flatten(), nn.Linear(32 * 28 * 28, 10))   # lớp cuối nhận 25 088 đầu vào
print(sum(p.numel() for p in khong_pool.parameters()), sum(p.numel() for p in khong_pool[-1].parameters()))   # tổng và lớp cuối
''', "255690 250890")

c.ghi(Path(__file__).resolve().parents[2] / "notebooks/ch27_cnn.ipynb")
