"""Dựng notebooks/ch28_kien_truc_cnn.ipynb: python3 scripts/notebook/ch28.py"""
from pathlib import Path
from nblib import Chuong, khung

c = Chuong(28, "Kiến trúc CNN và transfer learning", "ch28-kien-truc-cnn",
           "Pooling toàn cục, khối dư của ResNet, đọc ảnh thật từ đĩa bằng ImageFolder, rồi dùng ResNet-18 huấn luyện sẵn trên ImageNet để phân loại kiến và ong với 244 ảnh.",
           ["Dùng pooling toàn cục và đo độ bền khi dịch ảnh.",
            "Tự viết khối dư và thấy kết nối tắt cứu mạng 52 lớp.",
            "Đọc ảnh từ đĩa bằng ImageFolder, transforms, DataLoader.",
            "Transfer learning: đóng băng, tinh chỉnh, so với học từ đầu."],
           [("Từ LeNet tới ResNet", "01-tu-lenet-toi-resnet"), ("ResNet và kết nối tắt", "02-resnet"),
            ("Đọc ảnh từ đĩa và tăng cường dữ liệu", "03-doc-anh-tu-dia"), ("Transfer learning", "04-transfer-learning"),
            ("Bài tập", "05-bai-tap")])

c.mo_trang(1, "Pooling toàn cục trên MNIST (khoảng 20 giây trên CPU nhiều nhân).")
c.o('''
import torch                                                # PyTorch
import torch.nn as nn                                       # các lớp mạng
from torchvision import datasets                            # MNIST
from torch.utils.data import TensorDataset, DataLoader      # chia lô
tr = datasets.MNIST("data", train=True, download=True)      # 60 000 ảnh train
te = datasets.MNIST("data", train=False, download=True)     # 10 000 ảnh test
Xtr, ytr = tr.data.float().div(255).unsqueeze(1), tr.targets   # (60000, 1, 28, 28)
Xte, yte = te.data.float().div(255).unsqueeze(1), te.targets   # (10000, 1, 28, 28)
ce = nn.CrossEntropyLoss()                                  # loss
def huan_luyen(m, so_epoch=2):                              # như Chương 27
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
def dich(X, d):                                             # dịch sang phải d điểm ảnh
    Y = torch.zeros_like(X)                                 # nền đen
    Y[..., d:] = X[..., :-d]                                # chép phần còn lại
    return Y                                                # ảnh đã dịch
def khoi(vao, ra):                                          # tích chập, batch norm, ReLU
    return [nn.Conv2d(vao, ra, 3, padding=1), nn.BatchNorm2d(ra), nn.ReLU()]   # ba lớp
torch.manual_seed(0)                                        # khởi tạo lặp lại được
gap = nn.Sequential(*khoi(1, 16), nn.MaxPool2d(2), *khoi(16, 32), nn.MaxPool2d(2), *khoi(32, 64),   # ba khối
                    nn.AdaptiveAvgPool2d(1),                # pooling toàn cục
                    nn.Flatten(), nn.Linear(64, 10))        # lớp cuối nhỏ
print(sum(p.numel() for p in gap.parameters()), sum(p.numel() for p in gap[-1].parameters()))   # tổng, lớp cuối
huan_luyen(gap)                                             # 2 epoch
with torch.no_grad():                                       # đo độ bền
    print([round((gap(dich(Xte, d)).argmax(1) == yte).float().mean().item(), 4) for d in (1, 2, 3, 4)])   # dịch 1 tới 4
''', "24170 650\n1 0.9667\n2 0.9735\n[0.9732, 0.9701, 0.9717, 0.9673]")

c.mo_trang(2, "Mạng thường và mạng có kết nối tắt, sâu 12, 32, 52 lớp.")
c.o('''
from sklearn.datasets import load_digits                    # chữ số 8x8
from sklearn.model_selection import train_test_split        # chia
dg = load_digits()                                          # 1797 ảnh
A, B, C, E = train_test_split(dg.data / 16.0, dg.target, test_size=0.2, random_state=0, stratify=dg.target)   # 1437 và 360
Xtr, ytr = torch.tensor(A, dtype=torch.float32), torch.tensor(C)   # train
Xte, yte = torch.tensor(B, dtype=torch.float32), torch.tensor(E)   # test
class Khoi(nn.Module):                                      # khối hai lớp, có hoặc không kết nối tắt
    def __init__(self, tat):                                # khai báo lớp con
        super().__init__()                                  # bắt buộc
        self.f = nn.Sequential(nn.Linear(64, 64), nn.ReLU(), nn.Linear(64, 64))   # phần f(x)
        self.tat = tat                                      # có kết nối tắt không
    def forward(self, x):                                   # lượt xuôi
        return torch.relu(x + self.f(x)) if self.tat else torch.relu(self.f(x))   # x + f(x) hoặc f(x)
def mang(tat, n):                                           # 2n + 2 lớp Linear
    return nn.Sequential(nn.Linear(64, 64), nn.ReLU(), *[Khoi(tat) for _ in range(n)], nn.Linear(64, 10))   # vào, n khối, ra
for n in (5, 15, 25):                                       # ba độ sâu
    for tat in (False, True):                               # không và có kết nối tắt
        torch.manual_seed(0)                                # cùng khởi tạo
        m = mang(tat, n)                                    # dựng mạng
        ce(m(Xtr), ytr).backward()                          # một lượt ngược
        g = m[0].weight.grad.norm().item()                  # gradient lớp đầu
        m.zero_grad()                                       # xóa trước khi huấn luyện
        torch.manual_seed(1)                                # thứ tự lô
        dl = DataLoader(TensorDataset(Xtr, ytr), batch_size=64, shuffle=True)   # lô 64
        opt = torch.optim.Adam(m.parameters(), lr=1e-3)     # Adam
        for ep in range(30):                                # 30 epoch
            m.train()                                       # chế độ huấn luyện
            for xb, yb in dl:                               # mỗi lô
                opt.zero_grad()                             # xóa gradient
                ce(m(xb), yb).backward()                    # lượt ngược
                opt.step()                                  # cập nhật
        m.eval()                                            # đánh giá
        with torch.no_grad():                               # không cần gradient
            acc = (m(Xte).argmax(1) == yte).float().mean().item()   # độ chính xác test
        print(2 * n + 2, tat, f"{g:.1e}", round(acc, 4))    # số lớp, có tắt, gradient, test
''', "12 False 2.1e-05 0.7944\n12 True 2.1e-01 0.9583\n32 False 9.0e-13 0.1\n32 True 2.1e-01 0.9667\n52 False 2.8e-20 0.1\n52 True 3.1e-01 0.975")

c.mo_trang(3, "Kiến và ong: ImageFolder, transforms, Dataset tự viết.")
c.o('''
from pathlib import Path                                    # đường dẫn
from PIL import Image                                       # mở ảnh
from torchvision.datasets.utils import download_and_extract_archive   # tải và giải nén
download_and_extract_archive("https://download.pytorch.org/tutorial/hymenoptera_data.zip", "data")   # 47 MB, lần đầu
goc = Path("data/hymenoptera_data")                         # thư mục gốc
for phan in ("train", "val"):                               # hai phần
    print(phan, {lop.name: len(list(lop.iterdir())) for lop in sorted((goc / phan).iterdir())})   # số tệp mỗi lớp
print([Image.open(p).size for p in sorted((goc / "train/ants").iterdir())[:4]])   # kích thước 4 ảnh đầu
''', "train {'ants': 124, 'bees': 121}\nval {'ants': 70, 'bees': 83}\n[(768, 512), (500, 333), (500, 282), (500, 335)]")
c.o('''
from torchvision import transforms                          # biến đổi ảnh
TB, DL = [0.485, 0.456, 0.406], [0.229, 0.224, 0.225]       # trung bình, độ lệch chuẩn của ImageNet
bd_train = transforms.Compose([transforms.RandomResizedCrop(224),    # cắt ngẫu nhiên rồi phóng về 224
                               transforms.RandomHorizontalFlip(),    # lật ngang ngẫu nhiên
                               transforms.ToTensor(), transforms.Normalize(TB, DL)])   # tensor, chuẩn hóa
bd_test = transforms.Compose([transforms.Resize(256), transforms.CenterCrop(224),   # cố định
                              transforms.ToTensor(), transforms.Normalize(TB, DL)])  # tensor, chuẩn hóa
ds_tr = datasets.ImageFolder(goc / "train", transform=bd_train)    # mỗi thư mục con là một lớp
ds_te = datasets.ImageFolder(goc / "val", transform=bd_test)       # tập val
print(len(ds_tr), len(ds_te), ds_tr.classes, ds_tr[0][0].shape)    # số ảnh, lớp, shape
torch.manual_seed(0)                                        # seed
dl_tr = DataLoader(ds_tr, batch_size=32, shuffle=True, num_workers=2)   # 2 tiến trình phụ
dl_te = DataLoader(ds_te, batch_size=64, num_workers=2)     # lô val
xb, yb = next(iter(dl_tr))                                  # một lô
print(xb.shape, yb[:8].tolist(), len(dl_tr))                # shape, 8 nhãn, số lô
''', "244 153 ['ants', 'bees'] torch.Size([3, 224, 224])\ntorch.Size([32, 3, 224, 224]) [1, 0, 0, 1, 0, 0, 0, 1] 8",
    khung("vi-sao", ["245 tệp nhưng 244 ảnh: train/ants có một tệp imageNotFound.gif, và ImageFolder không nhận đuôi .gif."],
          nhan="VÌ SAO THIẾU MỘT ẢNH?"))
c.o('''
from torch.utils.data import Dataset                        # lớp cha
class KienOng(Dataset):                                     # Dataset tự viết
    def __init__(self, thu_muc, bien_doi):                  # chỉ liệt kê tệp, chưa đọc
        self.tep = sorted(p for p in Path(thu_muc).glob("*/*") if p.suffix in (".jpg", ".jpeg"))   # mọi tệp ảnh
        self.lop = sorted({p.parent.name for p in self.tep})   # tên lớp theo thư mục
        self.bien_doi = bien_doi                            # chuỗi biến đổi
    def __len__(self):                                      # số mẫu
        return len(self.tep)                                # số tệp
    def __getitem__(self, i):                               # mẫu thứ i
        p = self.tep[i]                                     # đường dẫn
        return self.bien_doi(Image.open(p).convert("RGB")), self.lop.index(p.parent.name)   # ảnh, nhãn
ds2 = KienOng(goc / "val", bd_test)                         # tập val
print(len(ds2), ds2.lop, ds2[0][0].shape, ds2[0][1], torch.equal(ds2[0][0], ds_te[0][0]))   # giống ImageFolder
''', "153 ['ants', 'bees'] torch.Size([3, 224, 224]) 0 True")

c.mo_trang(4, "Học từ đầu, đóng băng, tinh chỉnh (tổng khoảng 4 phút trên CPU, nhanh hơn nhiều trên GPU).")
c.o('''
ce = nn.CrossEntropyLoss()                                  # loss
def danh_gia(m):                                            # độ chính xác trên val
    m.eval()                                                # chế độ đánh giá
    dung = 0                                                # đếm đúng
    with torch.no_grad():                                   # không cần gradient
        for xb, yb in dl_te:                                # mỗi lô val
            dung += (m(xb).argmax(1) == yb).sum().item()    # cộng số đúng
    return round(dung / len(ds_te), 4)                      # tỷ lệ
def huan_luyen(m, tham_so, so_epoch, lr):                   # chỉ cập nhật tham_so
    torch.manual_seed(1)                                    # cố định thứ tự lô
    opt = torch.optim.Adam(tham_so, lr=lr)                  # Adam
    for ep in range(so_epoch):                              # mỗi epoch
        m.train()                                           # chế độ huấn luyện
        for xb, yb in dl_tr:                                # mỗi lô
            opt.zero_grad()                                 # xóa gradient
            ce(m(xb), yb).backward()                        # lượt ngược
            opt.step()                                      # cập nhật
        print(ep + 1, danh_gia(m))                          # độ chính xác val
def khoi(vao, ra):                                          # một khối CNN
    return nn.Sequential(nn.Conv2d(vao, ra, 3, padding=1), nn.BatchNorm2d(ra), nn.ReLU(), nn.MaxPool2d(2))   # tích chập, BN, ReLU, pooling
torch.manual_seed(0)                                        # khởi tạo
tu_dau = nn.Sequential(khoi(3, 16), khoi(16, 32), khoi(32, 64), khoi(64, 128),   # bốn khối
                       nn.AdaptiveAvgPool2d(1), nn.Flatten(), nn.Linear(128, 2))  # pooling toàn cục, lớp ra
print(sum(p.numel() for p in tu_dau.parameters()))          # số tham số
huan_luyen(tu_dau, tu_dau.parameters(), 10, 1e-3)           # 10 epoch từ đầu
''', "98178\n1 0.6667\n2 0.6667\n3 0.6993\n4 0.6732\n5 0.7255\n6 0.7124\n7 0.7516\n8 0.6732\n9 0.7255\n10 0.7059")
c.o('''
from torchvision import models                              # mô hình có sẵn
w = models.ResNet18_Weights.IMAGENET1K_V1                   # trọng số ImageNet, 45 MB lần đầu
torch.manual_seed(0)                                        # seed
net = models.resnet18(weights=w)                            # ResNet-18 huấn luyện sẵn
print(sum(p.numel() for p in net.parameters()), net.fc)     # số tham số, lớp cuối
net.eval()                                                  # chế độ đánh giá
with torch.no_grad():                                       # không cần gradient
    for i in (0, 1, 70, 71):                                # hai kiến, hai ong
        x, y = ds_te[i]                                     # ảnh, nhãn
        p = net(x.unsqueeze(0)).softmax(1)[0]               # xác suất 1000 lớp
        print(ds_te.classes[y], w.meta["categories"][p.argmax().item()], round(p.max().item(), 3))   # nhãn thật, đoán, xác suất
''', "11689512 Linear(in_features=512, out_features=1000, bias=True)\nants fountain 0.118\nants ant 0.552\nbees apiary 0.477\nbees bee 0.555")
c.o('''
for p in net.parameters():                                  # mọi tham số
    p.requires_grad = False                                 # đóng băng
net.fc = nn.Linear(512, 2)                                  # lớp cuối mới: kiến, ong
print(sum(p.numel() for p in net.parameters() if p.requires_grad))   # số tham số được học
huan_luyen(net, net.fc.parameters(), 5, 1e-3)               # 5 epoch, chỉ lớp cuối
''', "1026\n1 0.732\n2 0.9085\n3 0.9216\n4 0.9281\n5 0.9281")
c.o('''
torch.manual_seed(0)                                        # seed
net2 = models.resnet18(weights=w)                           # bản mới
net2.fc = nn.Linear(512, 2)                                 # lớp cuối mới
huan_luyen(net2, net2.parameters(), 5, 1e-4)                # tinh chỉnh toàn bộ, lr nhỏ
''', "1 0.902\n2 0.9216\n3 0.9346\n4 0.9346\n5 0.9281")
c.o('''
torch.manual_seed(0)                                        # seed
net3 = models.resnet18(weights=None)                        # trọng số ngẫu nhiên
net3.fc = nn.Linear(512, 2)                                 # lớp cuối
huan_luyen(net3, net3.parameters(), 5, 1e-3)                # học toàn bộ từ đầu
''', "1 0.5425\n2 0.5686\n3 0.6078\n4 0.6601\n5 0.6928",
    khung("thu", ["<b>1.</b> Đổi ResNet-18 thành ResNet-50 (models.resnet50, ResNet50_Weights.IMAGENET1K_V2). Đóng băng có tốt hơn không?",
                  "<b>2.</b> Bỏ tăng cường dữ liệu (dùng bd_test cho train). Mạng học từ đầu kém đi bao nhiêu?"]))

c.mo_trang(5, "Ba bài tập. Đoán trước, rồi mới mở đáp án.")
c.bai("28.1", "Mười tám lớp ở đâu", "Đếm Conv2d và Linear trong ResNet-18.",
      "20 tích chập (3 cái 1x1 trên đường tắt) và 1 Linear: 17 + 1 = 18 trên đường chính. Code ở ô ngay dưới.")
c.o('''
print(sum(isinstance(l, nn.Conv2d) for l in net.modules()), sum(isinstance(l, nn.Linear) for l in net.modules()))   # đếm
print([n for n, l in net.named_modules() if isinstance(l, nn.Conv2d) and l.kernel_size == (1, 1)])   # tích chập 1x1
''', "20 1\n['layer2.0.downsample.0', 'layer3.0.downsample.0', 'layer4.0.downsample.0']")
c.bai("28.2", "Điểm ảnh sau chuẩn hóa", "Điểm ảnh 0 và 1 thành bao nhiêu sau Normalize của ImageNet?",
      "Khoảng -2,1 tới -1,8 và 2,2 tới 2,6 tùy kênh. Code ở ô ngay dưới.")
c.o('''
print([round((0 - m) / s, 4) for m, s in zip(TB, DL)], [round((1 - m) / s, 4) for m, s in zip(TB, DL)])   # đen, trắng
''', "[-2.1179, -2.0357, -1.8044] [2.2489, 2.4286, 2.64]")
c.bai("28.3", "Learning rate quá lớn khi tinh chỉnh", "Tinh chỉnh toàn bộ với lr 1e-3 thay vì 1e-4.",
      "Chỉ 79,7% sau 5 epoch so với 92,8%. Code ở ô ngay dưới.")
c.o('''
torch.manual_seed(0)                                        # seed
net4 = models.resnet18(weights=w)                           # bản mới
net4.fc = nn.Linear(512, 2)                                 # lớp cuối mới
huan_luyen(net4, net4.parameters(), 5, 1e-3)                # learning rate gấp 10 lần
''', "1 0.6928\n2 0.5621\n3 0.6863\n4 0.6732\n5 0.7974")

c.ghi(Path(__file__).resolve().parents[2] / "notebooks/ch28_kien_truc_cnn.ipynb")
