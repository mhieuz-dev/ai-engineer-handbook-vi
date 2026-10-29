"""Dựng notebooks/ch32_du_an_phan_3.ipynb: python3 scripts/notebook/ch32.py"""
from pathlib import Path
from nblib import Chuong, khung

c = Chuong(32, "Dự án Phần III", "ch32-du-an-phan-3",
           "Dự án tổng kết deep learning: phân loại 27 000 ảnh vệ tinh Sentinel-2 (EuroSAT) vào 10 loại đất. Baseline màu, MLP, CNN học từ đầu, tăng cường dữ liệu, ResNet-18 đóng băng và tinh chỉnh, đo test một lần, phân tích lỗi và ngưỡng tin cậy.",
           ["Kiểm tra dữ liệu ảnh trước khi chia, chia train, val, test cố định theo từng lớp.",
            "Đặt một baseline mạnh bằng công cụ của Phần II trước khi dùng mạng sâu.",
            "So MLP với CNN, dùng tăng cường dữ liệu hợp với loại ảnh, đọc khoảng cách train và val.",
            "Chọn giữa đóng băng và tinh chỉnh một mạng đã huấn luyện sẵn bằng val.",
            "Đo test một lần, đọc ma trận nhầm lẫn, nhìn ảnh sai và dùng ngưỡng tin cậy."],
           [("Bài toán và dữ liệu", "01-bai-toan-va-du-lieu"), ("CNN học từ đầu", "02-cnn-tu-dau"),
            ("Transfer learning", "03-transfer-learning"), ("Đo test và phân tích lỗi", "04-do-test-va-phan-tich-loi"),
            ("Bài tập", "05-bai-tap")],
           thoi_gian="khoảng 1 giờ trên CPU 16 nhân (phần lớn là huấn luyện ở trang 2, 3 và bài tập 32.2)")

c.mo_trang(1, "Đọc 27 000 ảnh vào RAM, kiểm tra trùng lặp, chia tập, hai baseline.")
c.o('''
import numpy as np                                          # mảng số
import torch                                                # PyTorch
from torch import nn                                        # các lớp mạng
from torchvision.datasets import EuroSAT                    # bộ dữ liệu ảnh vệ tinh
ds = EuroSAT("data", download=True)                         # tải 94 MB lần đầu
X = torch.from_numpy(np.stack([np.array(ds.loader(p)) for p, _ in ds.samples]))   # đọc cả 27 000 ảnh vào RAM
X = X.permute(0, 3, 1, 2).contiguous()                      # (N, 3, 64, 64) cho PyTorch
y = torch.tensor(ds.targets)                                # nhãn 0 tới 9
print(X.shape, X.dtype, round(X.numel() / 1e6), "triệu byte")   # cỡ dữ liệu
for i, ten in enumerate(ds.classes):                        # mỗi lớp
    print(i, ten, int((y == i).sum()))                      # số ảnh
''', 'torch.Size([27000, 3, 64, 64]) torch.uint8 332 triệu byte\n0 AnnualCrop 3000\n1 Forest 3000\n2 HerbaceousVegetation 3000\n3 Highway 2500\n4 Industrial 2500\n5 Pasture 2000\n6 PermanentCrop 2500\n7 Residential 3000\n8 River 2500\n9 SeaLake 3000')
c.o('''
import hashlib                                              # mã băm
bam = [hashlib.md5(x.numpy().tobytes()).hexdigest() for x in X]   # mã băm từng ảnh
print(len(bam), len(set(bam)))                              # bao nhiêu ảnh khác nhau
''', '27000 27000')
c.o('''
from sklearn.model_selection import train_test_split        # chia tập
chi_so = np.arange(len(y))                                  # chỉ số mọi ảnh
i_tr, i_con = train_test_split(chi_so, test_size=0.3, stratify=y.numpy(), random_state=0)   # 70% train
i_va, i_te = train_test_split(i_con, test_size=0.5, stratify=y.numpy()[i_con], random_state=0)   # 15% val, 15% test
i_tr, i_va, i_te = torch.from_numpy(i_tr), torch.from_numpy(i_va), torch.from_numpy(i_te)   # thành tensor
print(len(i_tr), len(i_va), len(i_te))                      # cỡ ba phần
print(torch.bincount(y[i_va]).tolist())                     # số ảnh mỗi lớp trong val
''', '18900 4050 4050\n[450, 450, 450, 375, 375, 300, 375, 450, 375, 450]')
c.o('''
lop_dong = torch.bincount(y[i_tr]).argmax()                 # lớp đông nhất của train
print(ds.classes[lop_dong], round((y[i_va] == lop_dong).float().mean().item(), 4))   # baseline một
''', 'AnnualCrop 0.1111')
c.o('''
from sklearn.ensemble import HistGradientBoostingClassifier   # gradient boosting của Chương 18
def dac_trung_mau(X):                                       # 54 số chỉ về màu cho mỗi ảnh
    f = X.float().div(255).flatten(2)                       # (N, 3, 4096)
    hist = torch.stack([torch.stack([torch.histc(k, bins=16, min=0, max=1) for k in anh]) for anh in f])   # histogram 16 khoảng mỗi kênh
    return torch.cat([f.mean(2), f.std(2), hist.flatten(1) / 4096], 1).numpy()   # trung bình, độ lệch chuẩn, histogram
F_mau = dac_trung_mau(X)                                    # cho cả 27 000 ảnh
gb = HistGradientBoostingClassifier(random_state=0).fit(F_mau[i_tr], y[i_tr])   # chỉ học trên train
print(F_mau.shape, round(gb.score(F_mau[i_va], y[i_va]), 4))   # baseline hai
''', '(27000, 54) 0.836')

c.mo_trang(2, "MLP và CNN học từ đầu, có và không có tăng cường dữ liệu (khoảng 30 phút trên CPU).")
c.o('''
import time                                                 # đo thời gian
tb = X[i_tr].float().div(255).mean((0, 2, 3)).view(1, 3, 1, 1)   # trung bình từng kênh, chỉ train
dl = X[i_tr].float().div(255).std((0, 2, 3)).view(1, 3, 1, 1)    # độ lệch chuẩn từng kênh, chỉ train
def chuan(xb):                                              # uint8 thành số thực đã chuẩn hóa
    return (xb.float().div(255) - tb) / dl                  # trung bình 0, độ lệch chuẩn 1
print([round(v, 4) for v in tb.flatten().tolist()], [round(v, 4) for v in dl.flatten().tolist()])   # thống kê
''', '[0.3453, 0.381, 0.4082] [0.2036, 0.1376, 0.1161]')
c.o('''
ce = nn.CrossEntropyLoss()                                  # loss phân loại
@torch.no_grad()                                            # không cần gradient
def du_doan(m, idx, pre=chuan, bs=500):                     # logit cho các ảnh idx
    m.eval()                                                # chế độ đánh giá
    return torch.cat([m(pre(X[idx[i:i + bs]])) for i in range(0, len(idx), bs)])   # từng lô 500 ảnh
def do_acc(m, idx, pre=chuan):                              # độ chính xác
    return round((du_doan(m, idx, pre).argmax(1) == y[idx]).float().mean().item(), 4)   # tỷ lệ đoán đúng
def huan_luyen(m, so_epoch, lr=1e-3, tang=None, pre=chuan, tham_so=None, bs=128):   # AdamW và OneCycleLR
    torch.manual_seed(1)                                    # thứ tự lô cố định
    opt = torch.optim.AdamW(tham_so if tham_so is not None else m.parameters(), lr=lr, weight_decay=1e-4, fused=True)   # bản gộp, lặp lại được từng chữ số
    lich = torch.optim.lr_scheduler.OneCycleLR(opt, max_lr=lr, total_steps=so_epoch * ((len(i_tr) + bs - 1) // bs))   # warmup rồi cosine
    for ep in range(so_epoch):                              # mỗi epoch
        m.train()                                           # chế độ huấn luyện
        thu_tu, tong = i_tr[torch.randperm(len(i_tr))], 0.0   # xáo train
        for i in range(0, len(thu_tu), bs):                 # mỗi lô
            xb, yb = X[thu_tu[i:i + bs]], y[thu_tu[i:i + bs]]   # ảnh và nhãn của lô
            if tang is not None:                            # có tăng cường
                xb = tang(xb)                               # chỉ lúc huấn luyện
            loss = ce(m(pre(xb)), yb)                       # lượt xuôi
            opt.zero_grad()                                 # xóa gradient
            loss.backward()                                 # lượt ngược
            opt.step()                                      # cập nhật
            lich.step()                                     # OneCycleLR đếm theo lô
            tong += loss.item() * len(xb)                   # cộng loss
        print(ep + 1, round(tong / len(i_tr), 4), do_acc(m, i_va, pre))   # epoch, loss train, độ chính xác val
torch.manual_seed(0)                                        # cùng khởi tạo
mlp = nn.Sequential(nn.Flatten(), nn.Linear(3 * 64 * 64, 512), nn.ReLU(),   # duỗi ảnh, lớp ẩn 512
                    nn.Linear(512, 256), nn.ReLU(), nn.Linear(256, 10))     # lớp ẩn 256, 10 lớp ra
print(sum(p.numel() for p in mlp.parameters()))             # số tham số
huan_luyen(mlp, 15)                                         # 15 epoch
''', '6425866\n1 1.6186 0.5143\n2 1.2844 0.5193\n3 1.2611 0.5556\n4 1.1679 0.5494\n5 1.069 0.5795\n6 0.9668 0.5667\n7 0.821 0.6062\n8 0.7278 0.5968\n9 0.6421 0.618\n10 0.5397 0.6284\n11 0.4466 0.6341\n12 0.3706 0.6472\n13 0.3141 0.6496\n14 0.2782 0.6496\n15 0.2619 0.6509')
c.o('''
def khoi(vao, ra):                                          # tích chập, batch norm, ReLU, pooling
    return nn.Sequential(nn.Conv2d(vao, ra, 3, padding=1), nn.BatchNorm2d(ra), nn.ReLU(), nn.MaxPool2d(2))   # cạnh ảnh giảm một nửa
def tao_cnn():                                              # CNN bốn khối
    torch.manual_seed(0)                                    # cùng khởi tạo
    return nn.Sequential(khoi(3, 32), khoi(32, 64), khoi(64, 128), khoi(128, 256),   # 64, 32, 16, 8, 4
                         nn.AdaptiveAvgPool2d(1), nn.Flatten(), nn.Dropout(0.2), nn.Linear(256, 10))   # trung bình toàn cục, lớp cuối
cnn = tao_cnn()                                             # mạng mới
print(sum(p.numel() for p in cnn.parameters()))             # số tham số
huan_luyen(cnn, 15)                                         # khoảng 14 phút trên CPU
''', '391946\n1 1.2943 0.7294\n2 0.6912 0.8025\n3 0.5424 0.8301\n4 0.4767 0.8306\n5 0.3822 0.8267\n6 0.3155 0.9207\n7 0.2783 0.8677\n8 0.2379 0.8501\n9 0.2044 0.9212\n10 0.1744 0.9407\n11 0.1557 0.9356\n12 0.1373 0.9548\n13 0.1148 0.962\n14 0.1054 0.9635\n15 0.0943 0.9635')
c.o('''
def lat_xoay(x):                                            # 8 phép lật và xoay ngẫu nhiên
    x = x.clone()                                           # không sửa dữ liệu gốc
    m = torch.rand(len(x)) < 0.5                            # chọn một nửa lô
    x[m] = x[m].flip(3)                                     # lật ngang
    m = torch.rand(len(x)) < 0.5                            # chọn một nửa lô
    x[m] = x[m].flip(2)                                     # lật dọc
    m = torch.rand(len(x)) < 0.5                            # chọn một nửa lô
    x[m] = x[m].transpose(2, 3)                             # lật theo đường chéo
    return x                                                # lô đã biến đổi
cnn_tang = tao_cnn()                                        # cùng khởi tạo
huan_luyen(cnn_tang, 15, tang=lat_xoay)                     # có tăng cường
''', '1 1.2986 0.7257\n2 0.7074 0.779\n3 0.5725 0.8165\n4 0.481 0.8543\n5 0.4068 0.8758\n6 0.3522 0.8926\n7 0.3112 0.8746\n8 0.2791 0.92\n9 0.2418 0.9242\n10 0.2154 0.9375\n11 0.1948 0.9486\n12 0.1731 0.9449\n13 0.1552 0.9583\n14 0.1421 0.9612\n15 0.136 0.96')
c.o('''
for ten, m in [("không tăng cường", cnn), ("lật và xoay", cnn_tang)]:   # hai CNN
    print(ten, do_acc(m, i_tr[:4050]), do_acc(m, i_va))     # train so với val
''', 'không tăng cường 0.9795 0.9635\nlật và xoay 0.9602 0.96', khung("thu", ["<b>1.</b> Huấn luyện cnn_tang 30 epoch thay vì 15. Khoảng cách với bản không tăng cường thay đổi thế nào?"]))

c.mo_trang(3, "ResNet-18 đóng băng và tinh chỉnh (khoảng 12 phút trên CPU).")
c.o('''
import torch.nn.functional as F                             # nội suy ảnh
from torchvision import models                              # mạng đã huấn luyện sẵn
from sklearn.linear_model import LogisticRegression         # hồi quy logistic
w = models.ResNet18_Weights.IMAGENET1K_V1                   # trọng số ImageNet
tb_in = torch.tensor([0.485, 0.456, 0.406]).view(1, 3, 1, 1)   # trung bình ImageNet
dl_in = torch.tensor([0.229, 0.224, 0.225]).view(1, 3, 1, 1)   # độ lệch chuẩn ImageNet
def chuan_in(kich):                                         # chuẩn hóa theo ImageNet, phóng ảnh nếu cần
    def f(xb):                                              # hàm tiền xử lý
        x = (xb.float().div(255) - tb_in) / dl_in           # chuẩn hóa
        return x if kich == 64 else F.interpolate(x, size=kich, mode="bilinear", align_corners=False)   # phóng ảnh
    return f                                                # trả về hàm
for kich in (64, 128):                                      # ảnh gốc và ảnh phóng gấp đôi
    torch.manual_seed(0)                                    # cùng khởi tạo
    than = models.resnet18(weights=w)                       # ResNet-18 ImageNet
    than.fc = nn.Identity()                                 # giữ vector 512 số
    F_tr, F_va = du_doan(than, i_tr, chuan_in(kich)).numpy(), du_doan(than, i_va, chuan_in(kich)).numpy()   # đặc trưng
    lr_dau = LogisticRegression(max_iter=3000).fit(F_tr, y[i_tr])   # chỉ học lớp cuối
    print(kich, F_tr.shape, round(lr_dau.score(F_va, y[i_va]), 4))   # độ chính xác val
''', '64 (18900, 512) 0.9044\n128 (18900, 512) 0.9264')
c.o('''
torch.manual_seed(0)                                        # cùng khởi tạo
net = models.resnet18(weights=w)                            # ResNet-18 ImageNet
net.fc = nn.Linear(512, 10)                                 # lớp cuối mới cho 10 loại đất
huan_luyen(net, 5, tang=lat_xoay, pre=chuan_in(64))         # tinh chỉnh toàn bộ, khoảng 9 phút trên CPU
''', '1 0.5214 0.9323\n2 0.2233 0.9101\n3 0.1463 0.9642\n4 0.0847 0.9741\n5 0.0551 0.9807')

c.mo_trang(4, "Đo test một lần, ma trận nhầm lẫn, ngưỡng tin cậy.")
c.o('''
P_te = du_doan(net, i_te, chuan_in(64)).softmax(1)          # xác suất cho mỗi ảnh test
doan = P_te.argmax(1)                                       # lớp đoán
dung = doan == y[i_te]                                      # đúng hay sai
print(round(dung.float().mean().item(), 4), int((~dung).sum()), len(i_te))   # độ chính xác, số ảnh sai
''', '0.9753 100 4050')
c.o('''
from sklearn.metrics import confusion_matrix                # ma trận nhầm lẫn
M = confusion_matrix(y[i_te], doan)                         # hàng thật, cột đoán
for i, ten in enumerate(ds.classes):                        # mỗi lớp
    print(f"{ten:21s} {M[i, i] / M[i].sum():.4f}")        # tỷ lệ đúng của lớp
cap = sorted(((int(M[i, j]), ds.classes[i], ds.classes[j]) for i in range(10) for j in range(10) if i != j), reverse=True)   # các cặp nhầm
print(cap[:4])                                              # bốn cặp nhầm nhiều nhất
''', "AnnualCrop            0.9756\nForest                0.9911\nHerbaceousVegetation  0.9756\nHighway               0.9787\nIndustrial            0.9867\nPasture               0.9400\nPermanentCrop         0.9280\nResidential           0.9956\nRiver                 0.9707\nSeaLake               0.9933\n[(14, 'PermanentCrop', 'HerbaceousVegetation'), (7, 'PermanentCrop', 'AnnualCrop'), (7, 'Pasture', 'HerbaceousVegetation'), (7, 'AnnualCrop', 'PermanentCrop')]")
c.o('''
tin = P_te.max(1).values                                    # xác suất của lớp được chọn
for nguong in (0.9, 0.99):                                  # hai ngưỡng
    giu = tin >= nguong                                     # ảnh mô hình tự quyết
    print(nguong, round(giu.float().mean().item(), 4), round(dung[giu].float().mean().item(), 4),   # tỷ lệ giữ, độ chính xác
          round(dung[~giu].float().mean().item(), 4))       # độ chính xác phần chuyển cho người
''', '0.9 0.9412 0.9924 0.7017\n0.99 0.8207 0.9991 0.8664')

c.mo_trang(5, "Ba bài tập. Đoán trước, rồi mới mở đáp án.")
c.bai("32.1", "Tăng cường lúc dự đoán", "Trung bình xác suất của 8 phép lật và xoay, cho cả hai CNN của trang 2.",
      "Chỉ mô hình đã học bằng lật và xoay được lợi (96,0% lên 96,27%); mô hình kia giảm. Code ở ô ngay dưới.")
c.o('''
def du_doan_8(m, idx):                                      # trung bình 8 biến thể
    P = 0                                                   # tổng xác suất
    for a in (0, 1):                                        # lật ngang hay không
        for b in (0, 1):                                    # lật dọc hay không
            for c in (0, 1):                                # lật chéo hay không
                def bien(xb, a=a, b=b, c=c):                # một trong 8 phép
                    if a:                                   # lật ngang
                        xb = xb.flip(3)                     # đảo cột
                    if b:                                   # lật dọc
                        xb = xb.flip(2)                     # đảo hàng
                    if c:                                   # lật chéo
                        xb = xb.transpose(2, 3)             # đổi hàng thành cột
                    return chuan(xb)                        # chuẩn hóa
                P = P + du_doan(m, idx, bien).softmax(1)    # cộng xác suất
    return P / 8                                            # trung bình
for ten, m in [("không tăng cường", cnn), ("lật và xoay", cnn_tang)]:   # hai CNN
    print(ten, do_acc(m, i_va), round((du_doan_8(m, i_va).argmax(1) == y[i_va]).float().mean().item(), 4))   # một ảnh so với 8 biến thể
''', 'không tăng cường 0.9635 0.9605\nlật và xoay 0.96 0.9627')
c.bai("32.2", "Trọng số hay kiến trúc", "ResNet-18 cùng cách huấn luyện nhưng weights=None.",
      "90,1% sau 5 epoch so với 98,1% khi dùng trọng số ImageNet: với ngân sách ngắn, trọng số đã học đóng góp gần 8 điểm. Code ở ô ngay dưới.")
c.o('''
torch.manual_seed(0)                                        # cùng khởi tạo
net_moi = models.resnet18(weights=None)                     # trọng số ngẫu nhiên
net_moi.fc = nn.Linear(512, 10)                             # 10 loại đất
huan_luyen(net_moi, 5, tang=lat_xoay, pre=chuan_in(64))     # cùng 5 epoch, khoảng 9 phút trên CPU
''', '1 1.0187 0.6817\n2 0.7209 0.6183\n3 0.5591 0.7121\n4 0.3972 0.8773\n5 0.2904 0.9012')
c.bai("32.3", "Chọn ngưỡng theo yêu cầu", "Ngưỡng thấp nhất để ảnh mô hình tự quyết đúng ít nhất 99,5%.",
      "Ngưỡng 0,95: đúng 99,51%, chuyển 348 ảnh cho người. Code ở ô ngay dưới.")
c.o('''
for nguong in (0.8, 0.9, 0.95, 0.97):                       # bốn ngưỡng
    giu = tin >= nguong                                     # ảnh mô hình tự quyết
    print(nguong, int((~giu).sum()), round(dung[giu].float().mean().item(), 4))   # số ảnh chuyển cho người, độ chính xác
''', '0.8 147 0.99\n0.9 238 0.9924\n0.95 348 0.9951\n0.97 475 0.9978')

c.ghi(Path(__file__).resolve().parents[2] / "notebooks/ch32_du_an_phan_3.ipynb")
