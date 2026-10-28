"""Dựng notebooks/ch30_autoencoder_vae.ipynb: python3 scripts/notebook/ch30.py"""
from pathlib import Path
from nblib import Chuong, khung

c = Chuong(30, "Autoencoder và VAE", "ch30-autoencoder-vae",
           "Nén MNIST bằng autoencoder và so với PCA, khử nhiễu, phát hiện ảnh lạ, rồi tự viết VAE (tái tham số hóa, KL divergence) và chấm ảnh sinh ra bằng một CNN.",
           ["Tự viết autoencoder và so sai số tái tạo với PCA.",
            "Dùng autoencoder để khử nhiễu và phát hiện ảnh lạ.",
            "Hiểu mẹo tái tham số hóa và kiểm công thức KL bằng mẫu.",
            "Sinh ảnh mới bằng VAE và đo chất lượng một cách công bằng."],
           [("Autoencoder", "01-autoencoder"), ("Không gian ẩn, khử nhiễu và phát hiện ảnh lạ", "02-khong-gian-an"),
            ("VAE", "03-vae"), ("Sinh ảnh mới", "04-sinh-anh"), ("Bài tập", "05-bai-tap")])

c.mo_trang(1, "PCA và autoencoder trên MNIST (khoảng 40 giây trên CPU nhiều nhân).")
c.o('''
import torch                                                # PyTorch
import torch.nn as nn                                       # các lớp mạng
from torchvision import datasets                            # MNIST
from torch.utils.data import TensorDataset, DataLoader      # chia lô
tr = datasets.MNIST("data", train=True, download=True)      # 60 000 ảnh train
te = datasets.MNIST("data", train=False, download=True)     # 10 000 ảnh test
Xtr = tr.data.float().div(255).view(-1, 784)                # mỗi ảnh thành vector 784 số
Xte = te.data.float().div(255).view(-1, 784)                # test
ytr, yte = tr.targets, te.targets                           # nhãn, chỉ dùng để kiểm tra
print(Xtr.shape, round(((Xte - Xtr.mean(0)) ** 2).mean().item(), 4))   # sai số khi đoán ảnh trung bình
''', "torch.Size([60000, 784]) 0.0675")
c.o('''
from sklearn.decomposition import PCA                       # PCA của Chương 20
for k in (2, 32):                                           # hai mức nén
    pca = PCA(k, random_state=0).fit(Xtr.numpy())           # học trên train
    tai_tao = torch.tensor(pca.inverse_transform(pca.transform(Xte.numpy())))   # nén rồi bung
    print(k, round(((tai_tao - Xte) ** 2).mean().item(), 4))   # sai số tái tạo
''', "2 0.0557\n32 0.0168")
c.o('''
def tao_ae(k):                                              # mã hóa 784 -> k, giải mã k -> 784
    ma_hoa = nn.Sequential(nn.Linear(784, 256), nn.ReLU(), nn.Linear(256, k))   # bộ mã hóa
    giai_ma = nn.Sequential(nn.Linear(k, 256), nn.ReLU(), nn.Linear(256, 784), nn.Sigmoid())   # bộ giải mã
    return ma_hoa, giai_ma                                  # hai mạng
def huan_luyen_ae(ma_hoa, giai_ma, so_epoch=5, nhieu=0.0):  # trả về sai số tái tạo trên test
    torch.manual_seed(1)                                    # thứ tự lô lặp lại được
    dl = DataLoader(TensorDataset(Xtr), batch_size=128, shuffle=True)   # lô 128 ảnh
    opt = torch.optim.Adam([*ma_hoa.parameters(), *giai_ma.parameters()], lr=1e-3)   # Adam cho cả hai mạng
    for ep in range(so_epoch):                              # mỗi epoch
        for (xb,) in dl:                                    # mỗi lô
            vao = (xb + nhieu * torch.randn_like(xb)).clamp(0, 1)   # nhieu=0: đầu vào sạch
            loss = ((giai_ma(ma_hoa(vao)) - xb) ** 2).mean()        # đích luôn là ảnh sạch
            opt.zero_grad()                                 # xóa gradient
            loss.backward()                                 # lượt ngược
            opt.step()                                      # cập nhật
    with torch.no_grad():                                   # đánh giá
        return round(((giai_ma(ma_hoa(Xte)) - Xte) ** 2).mean().item(), 4)   # sai số trên test
ae = {}                                                     # lưu hai autoencoder
for k in (2, 32):                                           # hai mức nén
    torch.manual_seed(0)                                    # cùng khởi tạo
    ae[k] = tao_ae(k)                                       # dựng
    print(k, sum(p.numel() for m in ae[k] for p in m.parameters()), huan_luyen_ae(*ae[k]))   # tham số, sai số
''', "2 403730 0.0451\n32 419120 0.0081")

c.mo_trang(2, "Không gian ẩn, khử nhiễu, phát hiện ảnh lạ.")
c.o('''
from sklearn.neighbors import KNeighborsClassifier          # kNN của Chương 14
ma2, giai2 = ae[2]                                          # autoencoder 2 số
with torch.no_grad():                                       # không cần gradient
    z_tr, z_te = ma2(Xtr), ma2(Xte)                         # mã 2 số của mọi ảnh
print([round(v, 2) for v in z_te.mean(0).tolist()], [round(v, 2) for v in z_te.std(0).tolist()])   # trung bình, độ lệch chuẩn
print([round(v, 1) for v in z_te.min(0).values.tolist()], [round(v, 1) for v in z_te.max(0).values.tolist()])   # nhỏ nhất, lớn nhất
pca2 = PCA(2, random_state=0).fit(Xtr.numpy())              # PCA 2 thành phần
for ten, a, b in (("AE", z_tr.numpy(), z_te.numpy()), ("PCA", pca2.transform(Xtr.numpy()), pca2.transform(Xte.numpy()))):   # hai cách nén
    print(ten, round(KNeighborsClassifier(5).fit(a, ytr.numpy()).score(b, yte.numpy()), 4))   # kNN đoán nhãn từ 2 số
''', "[3.39, -2.82] [4.84, 3.5]\n[-8.8, -12.9] [21.4, 9.5]\nAE 0.5532\nPCA 0.4237")
c.o('''
torch.manual_seed(0)                                        # cùng nhiễu
Xn = (Xte + 0.5 * torch.randn_like(Xte)).clamp(0, 1)        # ảnh test thêm nhiễu
ma32, giai32 = ae[32]                                       # autoencoder thường
torch.manual_seed(0)                                        # cùng khởi tạo
ma_kn, giai_kn = tao_ae(32)                                 # autoencoder khử nhiễu
print(huan_luyen_ae(ma_kn, giai_kn, nhieu=0.5))             # vào ảnh nhiễu, đích ảnh sạch
with torch.no_grad():                                       # đánh giá
    print(round(((Xn - Xte) ** 2).mean().item(), 4),        # không làm gì
          round(((giai32(ma32(Xn)) - Xte) ** 2).mean().item(), 4),   # autoencoder thường
          round(((giai_kn(ma_kn(Xn)) - Xte) ** 2).mean().item(), 4))   # autoencoder khử nhiễu
''', "0.0218\n0.1155 0.0713 0.0179")
c.o('''
def sai_so(X):                                              # sai số tái tạo của từng ảnh
    with torch.no_grad():                                   # không cần gradient
        return ((giai32(ma32(X)) - X) ** 2).mean(1)         # một số mỗi ảnh
nguong = sai_so(Xtr).quantile(0.99)                         # 1% ảnh train vượt ngưỡng
xoay = torch.rot90(Xte.view(-1, 28, 28), 1, dims=(1, 2)).reshape(-1, 784)   # ảnh test xoay 90 độ
print(round(nguong.item(), 4), round((sai_so(Xte) > nguong).float().mean().item(), 4),   # ngưỡng, báo nhầm
      round((sai_so(xoay) > nguong).float().mean().item(), 4))   # bắt được ảnh xoay
phat_hien = sai_so(xoay) > nguong                           # ảnh xoay nào bị đánh dấu
print([round(phat_hien[yte == c].float().mean().item(), 2) for c in range(10)])   # theo từng chữ số
''', "0.0234 0.0079 0.4007\n[0.2, 0.01, 0.59, 0.46, 0.31, 0.33, 0.62, 0.34, 0.77, 0.43]")

c.mo_trang(3, "Tái tham số hóa, KL divergence, VAE 2 chiều (khoảng 25 giây).")
c.o('''
mu, log_var = torch.tensor([1.0, -2.0]), torch.tensor([0.0, -2.0])   # một phân phối chuẩn 2 chiều
torch.manual_seed(0)                                        # mẫu lặp lại được
z = mu + torch.exp(0.5 * log_var) * torch.randn(100000, 2)  # mẹo tái tham số hóa
print([round(v, 3) for v in z.mean(0).tolist()], [round(v, 3) for v in z.std(0).tolist()], round(torch.exp(torch.tensor(-1.0)).item(), 3))   # so với mu và sigma
''', "[0.998, -2.002] [0.998, 0.369] 0.368")
c.o('''
from torch.distributions import Normal                      # mật độ phân phối chuẩn
kl_cong_thuc = 0.5 * (log_var.exp() + mu ** 2 - 1 - log_var)   # công thức đóng
q, p = Normal(mu, torch.exp(0.5 * log_var)), Normal(0.0, 1.0)  # q và N(0, 1)
kl_mc = (q.log_prob(z) - p.log_prob(z)).mean(0)             # định nghĩa, ước lượng bằng mẫu
print([round(v, 4) for v in kl_cong_thuc.tolist()], [round(v, 4) for v in kl_mc.tolist()])   # so hai cách
''', "[0.5, 2.5677] [0.4976, 2.5691]")
c.o('''
import torch.nn.functional as F                             # hàm loss
class VAE(nn.Module):                                       # bien_phan=False: autoencoder thường
    def __init__(self, k, bien_phan=True):                  # k chiều ẩn
        super().__init__()                                  # bắt buộc
        self.ma_hoa = nn.Sequential(nn.Linear(784, 256), nn.ReLU())   # phần chung
        self.mu = nn.Linear(256, k)                         # trung bình
        self.log_var = nn.Linear(256, k)                    # log phương sai
        self.giai_ma = nn.Sequential(nn.Linear(k, 256), nn.ReLU(), nn.Linear(256, 784))   # ra logit
        self.bien_phan = bien_phan                          # có lấy mẫu và KL không
    def forward(self, x):                                   # lượt xuôi
        h = self.ma_hoa(x)                                  # đặc trưng
        mu, log_var = self.mu(h), self.log_var(h)           # tham số phân phối
        z = mu + torch.exp(0.5 * log_var) * torch.randn_like(mu) if self.bien_phan else mu   # tái tham số hóa
        return self.giai_ma(z), mu, log_var                 # logit ảnh, mu, log_var
def loss_vae(m, x):                                         # (tái tạo, KL) trên mỗi ảnh
    logit, mu, log_var = m(x)                               # lượt xuôi
    tai_tao = F.binary_cross_entropy_with_logits(logit, x, reduction="sum") / len(x)   # cộng trên điểm ảnh
    kl = 0.5 * (log_var.exp() + mu ** 2 - 1 - log_var).sum() / len(x) if m.bien_phan else torch.tensor(0.0)   # KL
    return tai_tao, kl                                      # hai số hạng
def huan_luyen_vae(m, so_epoch):                            # in sai số tái tạo và KL trên test
    torch.manual_seed(1)                                    # thứ tự lô
    dl = DataLoader(TensorDataset(Xtr), batch_size=128, shuffle=True)   # lô 128
    opt = torch.optim.Adam(m.parameters(), lr=1e-3)         # Adam
    for ep in range(so_epoch):                              # mỗi epoch
        m.train()                                           # huấn luyện
        for (xb,) in dl:                                    # mỗi lô
            tai_tao, kl = loss_vae(m, xb)                   # hai số hạng
            opt.zero_grad()                                 # xóa gradient
            (tai_tao + kl).backward()                       # loss = tái tạo + KL
            opt.step()                                      # cập nhật
    m.eval()                                                # đánh giá
    with torch.no_grad():                                   # không cần gradient
        tai_tao, kl = loss_vae(m, Xte)                      # trên test
    print(round(tai_tao.item(), 1), round(kl.item(), 1))    # in ra
torch.manual_seed(0)                                        # cùng khởi tạo
vae2 = VAE(2)                                               # VAE 2 chiều
huan_luyen_vae(vae2, 10)                                    # 10 epoch
with torch.no_grad():                                       # mã của ảnh: dùng mu
    mu_tr, mu_te = vae2.mu(vae2.ma_hoa(Xtr)), vae2.mu(vae2.ma_hoa(Xte))   # train và test
print([round(v, 2) for v in mu_te.mean(0).tolist()], [round(v, 2) for v in mu_te.std(0).tolist()])   # quanh gốc, thang cỡ 1
print(round(KNeighborsClassifier(5).fit(mu_tr.numpy(), ytr.numpy()).score(mu_te.numpy(), yte.numpy()), 4))   # kNN trên mã
''', "151.3 5.6\n[0.31, 0.08] [1.17, 1.39]\n0.6625")

c.mo_trang(4, "Bộ chấm CNN, autoencoder và VAE 16 chiều, ba cách lấy mẫu (khoảng 2 phút).")
c.o('''
torch.manual_seed(0)                                        # cùng khởi tạo
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
with torch.no_grad():                                       # độ chính xác của bộ chấm
    print(round((cham(Xte.view(-1, 1, 28, 28)).argmax(1) == yte).float().mean().item(), 4))   # trên test
print(cham_diem(Xte[:1000]))                                # mức trần: ảnh thật
''', "0.9817\n(0.927, [85, 125, 115, 111, 109, 84, 87, 98, 97, 89])")
c.o('''
torch.manual_seed(0)                                        # cùng khởi tạo
ae16 = VAE(16, bien_phan=False)                             # autoencoder thường: z = mu
huan_luyen_vae(ae16, 20)                                    # 20 epoch
torch.manual_seed(0)                                        # cùng khởi tạo
vae16 = VAE(16)                                             # VAE 16 chiều
huan_luyen_vae(vae16, 20)                                   # 20 epoch
''', "72.1 0.0\n82.7 23.2")
c.o('''
with torch.no_grad():                                       # không cần gradient
    z_ae = ae16.mu(ae16.ma_hoa(Xtr))                        # mã của 60 000 ảnh train
    z = torch.randn(1000, 16, generator=torch.Generator().manual_seed(0))   # 1000 điểm N(0, I)
    L = torch.linalg.cholesky(torch.cov(z_ae.T))            # Sigma = L L^T
    cach = {"AE, z ~ N(0, I)": z,                           # lấy mẫu bừa
            "AE, z theo phân phối chuẩn khớp với mã": z @ L.T + z_ae.mean(0),   # đúng trung bình, hiệp phương sai
            "VAE, z ~ N(0, I)": z}                          # VAE
    for ten, zz in cach.items():                            # ba cách
        m = vae16 if ten.startswith("VAE") else ae16        # mô hình tương ứng
        print(ten, cham_diem(torch.sigmoid(m.giai_ma(zz))))   # chấm ảnh sinh ra
''', "AE, z ~ N(0, I) (0.007, [16, 79, 273, 73, 17, 365, 6, 168, 1, 2])\nAE, z theo phân phối chuẩn khớp với mã (0.408, [72, 23, 136, 169, 87, 122, 87, 110, 135, 59])\nVAE, z ~ N(0, I) (0.365, [64, 50, 140, 152, 101, 91, 82, 135, 108, 77])",
    khung("thu", ["<b>1.</b> Tăng số epoch của VAE lên 40. Tỷ lệ CNN tin chắc có tăng không?",
                  "<b>2.</b> Đổi k thành 4 cho cả hai mô hình. Khoảng cách giữa AE khớp phân phối và VAE thay đổi thế nào?"]))

c.mo_trang(5, "Ba bài tập. Đoán trước, rồi mới mở đáp án.")
c.bai("30.1", "Autoencoder tuyến tính", "Bỏ hết hàm kích hoạt, so sai số với PCA 32 thành phần (0,0168).",
      "0,0170, sát PCA 0,0168: không có phi tuyến thì chỉ tìm được mặt phẳng của PCA. Code ở ô ngay dưới.")
c.o('''
torch.manual_seed(0)                                        # cùng khởi tạo
ma_tt, giai_tt = nn.Linear(784, 32), nn.Linear(32, 784)     # chỉ hai phép biến đổi tuyến tính
print(huan_luyen_ae(ma_tt, giai_tt))                        # 5 epoch như trang 1
''', "0.017")
c.bai("30.2", "KL bằng tay", "KL của N(0, 1), N(3, 1), N(0; 0,01) so với N(0, 1).",
      "0; 4,5; 1,808. Code ở ô ngay dưới.")
c.o('''
import math                                                 # log
for m, s in ((0.0, 1.0), (3.0, 1.0), (0.0, 0.1)):           # ba phân phối
    print(m, s, round(0.5 * (s ** 2 + m ** 2 - 1 - math.log(s ** 2)), 3))   # công thức đóng
''', "0.0 1.0 0.0\n3.0 1.0 4.5\n0.0 0.1 1.808")
c.bai("30.3", "Sinh riêng một chữ số", "Lấy mẫu quanh mã trung bình của các ảnh số 7.",
      "997 trên 1000 ảnh ra số 7, nhưng kém đa dạng. Code ở ô ngay dưới.")
c.o('''
with torch.no_grad():                                       # không cần gradient
    mu7 = vae16.mu(vae16.ma_hoa(Xtr[ytr == 7]))             # mã của mọi ảnh số 7
    z7 = mu7.mean(0) + 0.5 * mu7.std(0) * torch.randn(1000, 16, generator=torch.Generator().manual_seed(0))   # quanh trung bình
    anh7 = torch.sigmoid(vae16.giai_ma(z7))                 # giải mã
print(cham_diem(anh7))                                      # chấm
''', "(0.974, [0, 0, 0, 0, 0, 2, 0, 997, 0, 1])")

c.ghi(Path(__file__).resolve().parents[2] / "notebooks/ch30_autoencoder_vae.ipynb")
