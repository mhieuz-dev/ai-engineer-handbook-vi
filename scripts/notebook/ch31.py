"""Dựng notebooks/ch31_gan_diffusion.ipynb: python3 scripts/notebook/ch31.py"""
from pathlib import Path
from nblib import Chuong, khung

c = Chuong(31, "GAN và Diffusion", "ch31-gan-diffusion",
           "Huấn luyện một GAN trên MNIST và đo sụp mode, rồi tự cài quá trình thêm nhiễu của diffusion, huấn luyện một U-Net nhỏ đoán nhiễu và sinh ảnh bằng DDIM. Chương nặng nhất Phần III: trong Colab nên bật GPU (Runtime, Change runtime type).",
           ["Huấn luyện GAN xen kẽ hai mạng, đọc đúng loss của GAN.",
            "Đo sụp mode bằng phân bố lớp và kiểm tra GAN có chép ảnh không.",
            "Kiểm công thức đóng của quá trình thêm nhiễu.",
            "Huấn luyện mô hình diffusion và sinh ảnh bằng DDIM, so công bằng với GAN và VAE."],
           [("GAN", "01-gan"), ("Vì sao GAN khó huấn luyện", "02-gan-kho-huan-luyen"),
            ("Diffusion: thêm nhiễu", "03-diffusion-them-nhieu"), ("Diffusion: học khử nhiễu", "04-diffusion-khu-nhieu"),
            ("Bài tập", "05-bai-tap")])

c.mo_trang(1, "Bộ chấm CNN và GAN 20 epoch (khoảng 2 phút trên CPU 16 nhân).")
c.o('''
import torch                                                # PyTorch
import torch.nn as nn                                       # các lớp mạng
import torch.nn.functional as F                             # hàm loss
from torchvision import datasets                            # MNIST
from torch.utils.data import TensorDataset, DataLoader      # chia lô
tr = datasets.MNIST("data", train=True, download=True)      # 60 000 ảnh train
te = datasets.MNIST("data", train=False, download=True)     # 10 000 ảnh test
Xtr = tr.data.float().div(255).view(-1, 784)                # vector 784 số trong [0, 1]
Xte = te.data.float().div(255).view(-1, 784)                # test
ytr, yte = tr.targets, te.targets                           # nhãn, chỉ để huấn luyện bộ chấm
torch.manual_seed(0)                                        # bộ chấm của Chương 30
cham = nn.Sequential(nn.Conv2d(1, 16, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),   # CNN của Chương 27
                     nn.Conv2d(16, 32, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),  # khối thứ hai
                     nn.Flatten(), nn.Linear(32 * 7 * 7, 10))   # lớp cuối
torch.manual_seed(1)                                        # thứ tự lô
opt = torch.optim.Adam(cham.parameters(), lr=1e-3)          # Adam
for ep in range(2):                                         # 2 epoch
    for xb, yb in DataLoader(TensorDataset(Xtr.view(-1, 1, 28, 28), ytr), batch_size=64, shuffle=True):   # mỗi lô
        opt.zero_grad()                                     # xóa gradient
        F.cross_entropy(cham(xb), yb).backward()            # lượt ngược
        opt.step()                                          # cập nhật
cham.eval()                                                 # chế độ đánh giá
def cham_diem(anh):                                         # tỷ lệ ảnh CNN tin trên 90%, số ảnh mỗi lớp
    with torch.no_grad():                                   # không cần gradient
        p = cham(anh.view(-1, 1, 28, 28)).softmax(1)        # xác suất 10 lớp
    return round((p.max(1).values > 0.9).float().mean().item(), 3), torch.bincount(p.argmax(1), minlength=10).tolist()   # hai số đo
print(cham_diem(Xte[:1000]))                                # mức trần: ảnh thật
''', "(0.927, [85, 125, 115, 111, 109, 84, 87, 98, 97, 89])")
c.o('''
Z = 64                                                      # số chiều của nhiễu đầu vào
torch.manual_seed(0)                                        # cùng khởi tạo
G = nn.Sequential(nn.Linear(Z, 256), nn.LeakyReLU(0.2), nn.Linear(256, 512), nn.LeakyReLU(0.2),   # bộ sinh
                  nn.Linear(512, 784), nn.Tanh())           # ảnh trong [-1, 1]
D = nn.Sequential(nn.Linear(784, 512), nn.LeakyReLU(0.2), nn.Linear(512, 256), nn.LeakyReLU(0.2),   # bộ phân biệt
                  nn.Linear(256, 1))                        # một logit "thật"
print(sum(p.numel() for p in G.parameters()), sum(p.numel() for p in D.parameters()))   # số tham số
''', "550416 533505")
c.o('''
opt_G = torch.optim.Adam(G.parameters(), lr=2e-4, betas=(0.5, 0.999))   # Adam cho G
opt_D = torch.optim.Adam(D.parameters(), lr=2e-4, betas=(0.5, 0.999))   # Adam cho D
torch.manual_seed(1)                                        # thứ tự lô
dl = DataLoader(TensorDataset(Xtr * 2 - 1), batch_size=128, shuffle=True)   # ảnh thật về [-1, 1]
z_co_dinh = torch.randn(1000, Z, generator=torch.Generator().manual_seed(0))   # 1000 điểm nhiễu cố định để chấm
mot, khong = torch.ones(128, 1), torch.zeros(128, 1)        # nhãn thật, giả
for ep in range(20):                                        # 20 epoch
    for (that,) in dl:                                      # mỗi lô ảnh thật
        n = len(that)                                       # lô cuối nhỏ hơn
        gia = G(torch.randn(n, Z))                          # ảnh giả
        loss_D = F.binary_cross_entropy_with_logits(D(that), mot[:n]) + F.binary_cross_entropy_with_logits(D(gia.detach()), khong[:n])   # bước 1: D phân biệt
        opt_D.zero_grad()                                   # xóa gradient của D
        loss_D.backward()                                   # lượt ngược
        opt_D.step()                                        # cập nhật D
        loss_G = F.binary_cross_entropy_with_logits(D(gia), mot[:n])   # bước 2: G muốn D gọi ảnh giả là thật
        opt_G.zero_grad()                                   # xóa gradient của G
        loss_G.backward()                                   # lượt ngược qua D vào G
        opt_G.step()                                        # cập nhật G
    with torch.no_grad():                                   # chấm sau mỗi epoch
        diem = cham_diem((G(z_co_dinh) + 1) / 2)            # về [0, 1] rồi chấm
    print(ep + 1, round(loss_D.item(), 3), round(loss_G.item(), 3), diem)   # epoch, hai loss, điểm
''', "1 0.989 1.797 (0.0, [0, 2, 1, 93, 0, 0, 0, 0, 904, 0])\n2 0.347 2.52 (0.047, [70, 0, 262, 56, 0, 0, 0, 2, 610, 0])\n3 0.647 2.691 (0.073, [36, 33, 240, 154, 152, 6, 56, 82, 213, 28])\n4 0.666 3.17 (0.089, [1, 6, 176, 137, 83, 33, 13, 1, 545, 5])\n5 0.473 2.182 (0.121, [46, 18, 28, 277, 124, 72, 47, 84, 243, 61])\n6 0.516 2.879 (0.24, [23, 0, 163, 325, 197, 36, 0, 69, 181, 6])\n7 0.519 1.659 (0.296, [6, 24, 171, 239, 75, 53, 14, 115, 292, 11])\n8 1.694 1.607 (0.255, [4, 2, 151, 315, 173, 43, 0, 111, 159, 42])\n9 0.355 3.559 (0.278, [6, 0, 272, 129, 104, 25, 19, 181, 206, 58])\n10 0.463 2.201 (0.257, [23, 0, 222, 164, 113, 96, 2, 102, 204, 74])\n11 0.461 2.305 (0.348, [0, 0, 176, 361, 165, 14, 0, 55, 193, 36])\n12 0.419 2.554 (0.255, [0, 1, 253, 255, 100, 165, 6, 42, 126, 52])\n13 0.493 2.86 (0.257, [0, 20, 164, 285, 117, 42, 5, 112, 192, 63])\n14 0.442 2.156 (0.312, [7, 30, 157, 234, 130, 51, 9, 132, 101, 149])\n15 0.639 2.502 (0.298, [14, 90, 70, 113, 191, 96, 10, 109, 162, 145])\n16 1.114 0.732 (0.44, [3, 128, 144, 164, 102, 41, 25, 157, 107, 129])\n17 0.76 1.931 (0.383, [18, 168, 74, 140, 65, 64, 3, 187, 214, 67])\n18 0.88 1.35 (0.447, [16, 153, 111, 189, 115, 75, 18, 148, 102, 73])\n19 0.915 1.574 (0.443, [19, 158, 88, 173, 47, 66, 32, 158, 166, 93])\n20 1.184 2.413 (0.47, [19, 138, 135, 132, 110, 71, 33, 168, 128, 66])")

c.mo_trang(2, "Đo sụp mode và kiểm tra GAN có chép ảnh train không.")
c.o('''
import math                                                 # log
def entropy(dem):                                           # entropy phân bố lớp, tối đa ln 10
    p = torch.tensor(dem, dtype=torch.float) / sum(dem)     # thành xác suất
    p = p[p > 0]                                            # bỏ lớp trống
    return round(-(p * p.log()).sum().item(), 3)            # -tổng p log p
with torch.no_grad():                                       # không cần gradient
    anh_gan = (G(z_co_dinh) + 1) / 2                        # 1000 ảnh GAN
print(entropy(cham_diem(Xte[:1000])[1]), entropy(cham_diem(anh_gan)[1]), round(math.log(10), 3))   # thật, GAN, tối đa
''', "2.294 2.172 2.303")
c.o('''
def gan_nhat(A, B):                                         # khoảng cách tới ảnh gần nhất trong B
    return torch.cdist(A, B).min(1).values                  # một số mỗi ảnh của A
print(round(gan_nhat(anh_gan, Xtr).mean().item(), 2), round(gan_nhat(Xte[:1000], Xtr).mean().item(), 2))   # GAN, ảnh test thật
''', "5.2 4.24")

c.mo_trang(3, "Quá trình thêm nhiễu và công thức đóng.")
c.o('''
T = 1000                                                    # số bước
beta = torch.linspace(1e-4, 0.02, T)                        # nhiễu mỗi bước, như DDPM
alpha = 1 - beta                                            # phần giữ lại mỗi bước
ab = torch.cumprod(alpha, dim=0)                            # alpha ngang
print([round(ab[t].item(), 4) for t in (0, 99, 249, 499, 999)])   # bước 1, 100, 250, 500, 1000
print([round((ab[t] / (1 - ab[t])).sqrt().item(), 3) for t in (0, 99, 249, 499, 999)])   # tỷ lệ tín hiệu trên nhiễu
''', "[0.9999, 0.897, 0.5241, 0.0786, 0.0]\n[99.987, 2.951, 1.049, 0.292, 0.006]")
c.o('''
torch.manual_seed(0)                                        # mẫu lặp lại được
x = torch.ones(100000)                                      # 100 000 bản của một điểm ảnh trắng
for t in range(500):                                        # 500 bước thêm nhiễu
    x = alpha[t].sqrt() * x + beta[t].sqrt() * torch.randn(100000)   # một bước
print(round(x.mean().item(), 4), round(x.std().item(), 4), round(ab[499].sqrt().item(), 4), round((1 - ab[499]).sqrt().item(), 4))   # mô phỏng, công thức
''', "0.2771 0.9587 0.2803 0.9599")
c.o('''
def them_nhieu(x0, t, eps):                                 # công thức đóng, mỗi ảnh một bước t
    a = ab[t].view(-1, *[1] * (x0.dim() - 1))               # alpha ngang đúng shape
    return a.sqrt() * x0 + (1 - a).sqrt() * eps             # x_t
torch.manual_seed(0)                                        # cùng nhiễu
X0 = Xte * 2 - 1                                            # ảnh test trong [-1, 1]
xT = them_nhieu(X0, torch.full((len(X0),), T - 1), torch.randn_like(X0))   # bước 1000
print(round(X0.mean().item(), 4), round(X0.std().item(), 4), round(xT.mean().item(), 4), round(xT.std().item(), 4))   # trước, sau
''', "-0.735 0.621 -0.0047 0.9998")

c.mo_trang(4, "U-Net nhỏ, huấn luyện 3 epoch (khoảng 3,5 phút trên CPU, dưới 1 phút với GPU), sinh bằng DDIM.")
c.o('''
def nhung_t(t, d=32):                                       # bước t thành vector sin, cos
    f = torch.exp(-math.log(10000) * torch.arange(d // 2) / (d // 2))   # các tần số
    a = t.float()[:, None] * f[None]                        # t nhân mỗi tần số
    return torch.cat([a.sin(), a.cos()], dim=1)             # (n, d)
class KhuNhieu(nn.Module):                                  # U-Net rất nhỏ
    def __init__(self, c=32):                               # c kênh
        super().__init__()                                  # bắt buộc
        self.t1 = nn.Sequential(nn.Linear(32, c), nn.SiLU(), nn.Linear(c, c))   # nhúng bước t
        self.vao = nn.Conv2d(1, c, 3, padding=1)            # 28x28
        self.k1 = nn.Sequential(nn.SiLU(), nn.Conv2d(c, c, 3, padding=1))   # khối 28x28
        self.xuong = nn.Conv2d(c, c, 4, stride=2, padding=1)   # xuống 14x14
        self.k2 = nn.Sequential(nn.SiLU(), nn.Conv2d(c, c, 3, padding=1), nn.SiLU(), nn.Conv2d(c, c, 3, padding=1))   # khối 14x14
        self.len = nn.ConvTranspose2d(c, c, 4, stride=2, padding=1)   # lên 28x28
        self.ra = nn.Sequential(nn.SiLU(), nn.Conv2d(2 * c, c, 3, padding=1), nn.SiLU(), nn.Conv2d(c, 1, 3, padding=1))   # ra nhiễu đoán
    def forward(self, x, t):                                # lượt xuôi
        e = self.t1(nhung_t(t))[:, :, None, None]           # mạng biết đang ở bước nào
        h1 = self.k1(self.vao(x) + e)                       # 28x28
        h2 = self.xuong(h1)                                 # 14x14
        h2 = h2 + self.k2(h2 + e)                           # khối dư
        return self.ra(torch.cat([self.len(h2), h1], dim=1))   # nối với đặc trưng 28x28, như U-Net
torch.manual_seed(0)                                        # cùng khởi tạo
khu = KhuNhieu()                                            # mạng khử nhiễu
print(sum(p.numel() for p in khu.parameters()))             # số tham số
''', "81761")
c.o('''
opt = torch.optim.Adam(khu.parameters(), lr=1e-3)           # Adam
torch.manual_seed(1)                                        # thứ tự lô
dl = DataLoader(TensorDataset((Xtr * 2 - 1).view(-1, 1, 28, 28)), batch_size=128, shuffle=True)   # ảnh train [-1, 1]
for ep in range(3):                                         # 3 epoch
    khu.train()                                             # huấn luyện
    for (x0,) in dl:                                        # mỗi lô
        t = torch.randint(0, T, (len(x0),))                 # mỗi ảnh một bước ngẫu nhiên
        eps = torch.randn_like(x0)                          # nhiễu thêm vào
        loss = F.mse_loss(khu(them_nhieu(x0, t, eps), t), eps)   # đoán lại nhiễu
        opt.zero_grad()                                     # xóa gradient
        loss.backward()                                     # lượt ngược
        opt.step()                                          # cập nhật
    print(ep + 1, round(loss.item(), 4))                    # loss lô cuối
khu.eval()                                                  # chế độ đánh giá
''', "1 0.0495\n2 0.0399\n3 0.0327")
c.o('''
@torch.no_grad()                                            # không cần gradient khi sinh
def sinh(n, so_buoc=25, seed=0):                            # lấy mẫu DDIM
    g = torch.Generator().manual_seed(seed)                 # điểm xuất phát cố định
    x = torch.randn(n, 1, 28, 28, generator=g)              # nhiễu thuần
    cac_t = torch.linspace(T - 1, 0, so_buoc).long()        # các bước sẽ đi qua
    for i, t in enumerate(cac_t):                           # đi lùi
        eps = khu(x, torch.full((n,), int(t)))              # nhiễu đoán
        x0 = ((x - (1 - ab[t]).sqrt() * eps) / ab[t].sqrt()).clamp(-1, 1)   # ảnh sạch đoán
        eps = (x - ab[t].sqrt() * x0) / (1 - ab[t]).sqrt()  # nhiễu khớp với ảnh đã cắt
        if i + 1 < len(cac_t):                              # chưa tới bước cuối
            t_sau = cac_t[i + 1]                            # bước kế tiếp
            x = ab[t_sau].sqrt() * x0 + (1 - ab[t_sau]).sqrt() * eps   # về mức nhiễu của bước đó
        else:                                               # bước cuối
            x = x0                                          # ảnh sạch
    return (x.view(n, 784) + 1) / 2                         # về [0, 1]
anh_dif = sinh(1000)                                        # 1000 ảnh
print(cham_diem(anh_dif), entropy(cham_diem(anh_dif)[1]))   # chấm, độ đa dạng
''', "(0.373, [27, 28, 193, 72, 181, 95, 29, 97, 267, 11]) 1.969",
    khung("thu", ["<b>1.</b> Nếu có GPU: đưa khu và dữ liệu lên cuda, huấn luyện 20 epoch. Bộ chấm và entropy thay đổi thế nào?",
                  "<b>2.</b> Tăng c từ 32 lên 64 (gấp khoảng 4 lần phép tính). Có đáng không?"]))

c.mo_trang(5, "Ba bài tập. Đoán trước, rồi mới mở đáp án.")
c.bai("31.1", "Nhiều bước hơn có tốt hơn không", "DDIM 100 bước thay vì 25.",
      "37,5% so với 37,3%: gần như không đổi, tốn gấp 4 lần thời gian. Code ở ô ngay dưới.")
c.o('''
anh100 = sinh(1000, so_buoc=100)                            # 100 bước
print(cham_diem(anh100), entropy(cham_diem(anh100)[1]))     # so với 25 bước
''', "(0.375, [26, 28, 193, 78, 188, 97, 25, 96, 256, 13]) 1.974")
c.bai("31.2", "Bao lâu thì ảnh biến mất", "Với beta cố định 0,02, sau bao nhiêu bước alpha ngang dưới 0,01?",
      "228 bước; với lịch tăng dần của trang 3 là bước 674. Code ở ô ngay dưới.")
c.o('''
print(math.log(0.01) / math.log(0.98), 0.98 ** 228, int((ab < 0.01).nonzero()[0]) + 1)   # beta cố định, và lịch tăng dần
''', "227.94817118369878 0.009989534655931522 674")
c.bai("31.3", "Đi giữa hai điểm nhiễu", "Nội suy giữa hai vector nhiễu của GAN.",
      "Từ số 7 sang số 1, đổi lớp một lần ở giữa, độ tin thấp nhất 0,44. Code ở ô ngay dưới.")
c.o('''
with torch.no_grad():                                       # không cần gradient
    z = torch.stack([(1 - a) * z_co_dinh[0] + a * z_co_dinh[1] for a in torch.linspace(0, 1, 11)])   # 11 điểm trên đoạn thẳng
    p = cham(((G(z) + 1) / 2).view(-1, 1, 28, 28)).softmax(1)   # chấm
print(p.argmax(1).tolist())                                 # chữ số dọc đường
print([round(v, 2) for v in p.max(1).values.tolist()])      # độ tin
''', "[7, 7, 7, 7, 7, 7, 1, 1, 1, 1, 1]\n[0.97, 0.96, 0.95, 0.9, 0.77, 0.47, 0.44, 0.78, 0.88, 0.9, 0.85]")

c.ghi(Path(__file__).resolve().parents[2] / "notebooks/ch31_gan_diffusion.ipynb")
