"""Dựng notebooks/ch37_ppo_gymnasium.ipynb: python3 scripts/notebook/ch37.py"""
from pathlib import Path
from nblib import Chuong, code, khung

c = Chuong(37, "PPO và Gymnasium", "ch37-ppo-gymnasium",
           "Cài PPO với GAE và môi trường song song của Gymnasium, huấn luyện trên CartPole, trên Pendulum với hành động liên tục, và trên một môi trường quản lý kho do chính bạn viết. Chương cuối Phần III-B; mỗi lần huấn luyện 20 tới 60 giây trên CPU.",
           ["Thấy bằng autograd phép cắt của PPO chặn gradient ở đâu.",
            "Cài PPO: môi trường vector, tự động reset, GAE, nhiều epoch trên mỗi lô.",
            "Đổi sang chính sách chuẩn để điều khiển hành động liên tục.",
            "Viết một môi trường Gymnasium, kiểm bằng check_env, và so PPO với chính sách (s, S) của vận trù học."],
           [("Bước an toàn", "01-buoc-an-toan"), ("PPO trên CartPole", "02-ppo-tren-cartpole"),
            ("Hành động liên tục", "03-hanh-dong-lien-tuc"), ("Tự viết môi trường", "04-tu-viet-moi-truong"), ("Bài tập", "05-bai-tap")],
           thoi_gian="khoảng 7 phút")

c.mo_trang(1, "Mục tiêu cắt của PPO, kiểm bằng autograd.")
c.cells.append(code('''
!pip install -q gymnasium                                   # thư viện môi trường RL, Colab chưa chắc có sẵn
'''))
c.o('''
import gymnasium as gym                                     # môi trường RL
import numpy as np                                          # mảng
import torch                                                # PyTorch
import torch.nn as nn                                       # các lớp mạng
torch.set_num_threads(1)                                    # mạng nhỏ: một luồng, kết quả lặp lại được
ti_so = torch.tensor([0.5, 0.9, 1.0, 1.1, 1.3, 1.5], requires_grad=True)   # sáu giá trị của rho
for A in (1.0, -1.0):                                       # lợi thế dương và âm
    L = torch.min(ti_so * A, ti_so.clamp(0.8, 1.2) * A)     # mục tiêu cắt, epsilon = 0,2
    (g,) = torch.autograd.grad(L.sum(), ti_so)              # gradient theo rho
    print(A, L.detach().numpy().round(2), g.numpy())        # giá trị và gradient
''', "1.0 [0.5 0.9 1.  1.1 1.2 1.2] [1. 1. 1. 1. 0. 0.]\n-1.0 [-0.8 -0.9 -1.  -1.1 -1.3 -1.5] [ 0. -1. -1. -1. -1. -1.]",
    khung("doc", ["Ngoài khoảng 0,8 tới 1,2 về phía có lợi, gradient bằng 0: không đẩy tiếp. Về phía bất lợi, gradient vẫn khác 0: sai lầm luôn bị kéo về."]))

c.mo_trang(2, "Cài PPO và huấn luyện trên CartPole (khoảng 22 giây).")
c.o('''
def lop(vao, ra, std=np.sqrt(2)):                           # lớp tuyến tính khởi tạo trực giao
    l = nn.Linear(vao, ra)                                  # lớp thường
    nn.init.orthogonal_(l.weight, std)                      # trọng số trực giao
    nn.init.zeros_(l.bias)                                  # bias 0
    return l                                                # trả về lớp
class TacTu(nn.Module):                                     # diễn viên và nhà phê bình
    def __init__(self, n_obs, n_ra, lien_tuc=False):        # số chiều quan sát, số hành động hoặc số chiều hành động
        super().__init__()                                  # khởi tạo nn.Module
        self.lien_tuc = lien_tuc                            # hành động liên tục hay rời rạc
        self.critic = nn.Sequential(lop(n_obs, 64), nn.Tanh(), lop(64, 64), nn.Tanh(), lop(64, 1, 1.0))   # nhà phê bình V(s)
        self.actor = nn.Sequential(lop(n_obs, 64), nn.Tanh(), lop(64, 64), nn.Tanh(), lop(64, n_ra, 0.01))   # diễn viên, lớp cuối rất nhỏ
        self.log_std = nn.Parameter(torch.zeros(n_ra)) if lien_tuc else None   # độ lệch chuẩn học được (trang 3)
    def phan_phoi(self, o):                                 # phân phối hành động
        if self.lien_tuc:                                   # liên tục: phân phối chuẩn
            mu = self.actor(o)                              # trung bình
            return torch.distributions.Normal(mu, self.log_std.exp().expand_as(mu))   # chuẩn với sigma chung
        return torch.distributions.Categorical(logits=self.actor(o))   # rời rạc: softmax của logit
    def log_p_ent(self, o, a):                              # log xác suất và entropy
        d = self.phan_phoi(o)                               # phân phối hiện tại
        if self.lien_tuc:                                   # nhiều chiều độc lập
            return d.log_prob(a).sum(-1), d.entropy().sum(-1)   # cộng qua các chiều
        return d.log_prob(a), d.entropy()                   # một hành động rời rạc
    def tham_lam(self, o):                                  # dùng khi đánh giá
        return self.actor(o) if self.lien_tuc else self.actor(o).argmax(-1)   # trung bình hoặc argmax
def gae(R, V, V_sau, ket_thuc, het_tap, gamma, lam):        # lợi thế GAE, đi ngược thời gian
    A = torch.zeros_like(R)                                 # kết quả
    g = torch.zeros(R.shape[1])                             # tích lũy cho từng môi trường
    for t in reversed(range(R.shape[0])):                   # từ cuối lô về đầu
        delta = R[t] + gamma * (1 - ket_thuc[t]) * V_sau[t] - V[t]   # sai số TD; chỉ terminated mới bỏ V_sau
        g = delta + gamma * lam * (1 - het_tap[t]) * g      # không tích lũy qua ranh giới tập
        A[t] = g                                            # ghi lại
    return A                                                # lợi thế
def ppo(tao_mot, tong_buoc, n_env=4, n_buoc=128, epoch=4, n_lo=4, lr=2.5e-4, gamma=0.99, lam=0.95,
        clip=0.2, he_so_ent=0.01, lien_tuc=False, seed=0, in_moi=40):   # PPO đầy đủ
    torch.manual_seed(seed)                                 # khởi tạo và lấy mẫu
    envs = gym.vector.SyncVectorEnv([lambda: gym.wrappers.RecordEpisodeStatistics(tao_mot()) for _ in range(n_env)],
                                    autoreset_mode=gym.vector.AutoresetMode.SAME_STEP)   # n_env bản sao, tự reset
    n_obs = envs.single_observation_space.shape[0]          # số chiều quan sát
    n_ra = envs.single_action_space.shape[0] if lien_tuc else envs.single_action_space.n   # số đầu ra của diễn viên
    tt = TacTu(n_obs, n_ra, lien_tuc)                       # hai mạng
    opt = torch.optim.Adam(tt.parameters(), lr=lr, eps=1e-5, fused=True)   # fused: lặp lại được trên CPU
    so_vong = tong_buoc // (n_env * n_buoc)                 # số lô
    o, _ = envs.reset(seed=seed)                            # quan sát đầu của mọi bản sao
    o = torch.tensor(o, dtype=torch.float32)                # sang tensor
    diem = []                                               # điểm các tập đã xong
    for vong in range(1, so_vong + 1):                      # mỗi lô
        opt.param_groups[0]["lr"] = lr * (1 - (vong - 1) / so_vong)   # giảm learning rate tuyến tính
        O, A, LP, V, R, V_sau, KT, HT = [], [], [], [], [], [], [], []   # dữ liệu của lô
        for t in range(n_buoc):                             # 1. thu một lô bằng chính sách hiện tại
            with torch.no_grad():                           # thu dữ liệu, không cần gradient
                d = tt.phan_phoi(o)                         # phân phối hành động
                a = d.sample()                              # lấy mẫu
                lp = d.log_prob(a).sum(-1) if lien_tuc else d.log_prob(a)   # log xác suất CŨ, giữ cố định
                v = tt.critic(o).squeeze(-1)                # V(s)
            o2, r, ket_thuc, cat_ngang, info = envs.step(a.numpy())   # n_env bước cùng lúc
            het = ket_thuc | cat_ngang                      # bản sao nào vừa hết tập
            o_cuoi = o2.copy()                              # trạng thái thật sự đến
            for i in np.where(het)[0]:                      # với bản sao vừa hết tập
                o_cuoi[i] = info["final_obs"][i]            # o2 đã là trạng thái của tập mới
                diem.append(float(info["final_info"]["episode"]["r"][i]))   # điểm do RecordEpisodeStatistics ghi
            with torch.no_grad():                           # không cần gradient
                vs = tt.critic(torch.tensor(o_cuoi, dtype=torch.float32)).squeeze(-1)   # V(s_t+1)
            O.append(o); A.append(a); LP.append(lp); V.append(v); V_sau.append(vs)   # lưu
            R.append(torch.tensor(r, dtype=torch.float32))  # phần thưởng
            KT.append(torch.tensor(ket_thuc, dtype=torch.float32))   # kết thúc thật
            HT.append(torch.tensor(het, dtype=torch.float32))   # hết tập (kể cả bị cắt)
            o = torch.tensor(o2, dtype=torch.float32)       # sang bước sau
        O, A, LP, V, R, V_sau, KT, HT = map(torch.stack, (O, A, LP, V, R, V_sau, KT, HT))   # n_buoc x n_env
        with torch.no_grad():                               # 2. lợi thế bằng GAE
            adv = gae(R, V, V_sau, KT, HT, gamma, lam)      # lợi thế
            muc_tieu_v = adv + V                            # mục tiêu cho nhà phê bình
        N = n_buoc * n_env                                  # số mẫu trong lô
        O, A, LP, adv, muc_tieu_v = O.flatten(0, 1), A.flatten(0, 1), LP.flatten(0, 1), adv.flatten(0, 1), muc_tieu_v.flatten(0, 1)   # gộp hai chiều đầu
        co_lo = N // n_lo                                   # cỡ mini-batch
        for _ in range(epoch):                              # 3. học nhiều epoch trên cùng một lô
            thu_tu = torch.randperm(N)                      # xáo trộn
            for k in range(n_lo):                           # mỗi mini-batch
                j = thu_tu[k * co_lo:(k + 1) * co_lo]       # chỉ số của mini-batch
                lp, ent = tt.log_p_ent(O[j], A[j])          # log xác suất MỚI
                ti_so = (lp - LP[j]).exp()                  # rho = pi mới / pi cũ
                a_j = (adv[j] - adv[j].mean()) / (adv[j].std() + 1e-8)   # chuẩn hóa lợi thế
                loss_pi = -torch.min(ti_so * a_j, ti_so.clamp(1 - clip, 1 + clip) * a_j).mean()   # mục tiêu cắt, đổi dấu
                loss_v = ((tt.critic(O[j]).squeeze(-1) - muc_tieu_v[j]) ** 2).mean()   # nhà phê bình
                loss = loss_pi + 0.5 * loss_v - he_so_ent * ent.mean()   # thưởng entropy
                opt.zero_grad()                             # xóa gradient
                loss.backward()                             # lượt ngược
                nn.utils.clip_grad_norm_(tt.parameters(), 0.5)   # cắt độ lớn gradient
                opt.step()                                  # cập nhật
        if vong % in_moi == 0:                              # định kỳ
            print(vong * N, round(np.mean(diem[-20:]), 1))  # số bước, điểm 20 tập gần nhất
    return tt                                               # tác tử đã học
def danh_gia(tt, tao_mot, n=20, seed=10_000):               # chính sách tham lam trên n tập cố định
    e = tao_mot()                                           # môi trường riêng
    tong = []                                               # điểm mỗi tập
    for i in range(n):                                      # n tập
        o, _ = e.reset(seed=seed + i)                       # seed cố định
        G = 0                                               # điểm
        while True:                                         # mỗi bước
            with torch.no_grad():                           # không cần gradient
                a = tt.tham_lam(torch.tensor(o, dtype=torch.float32)).numpy()   # không lấy mẫu
            o, r, ket_thuc, cat_ngang, _ = e.step(a)        # đi
            G += r                                          # cộng thưởng
            if ket_thuc or cat_ngang:                       # hết tập
                break                                       # ra khỏi vòng
        tong.append(G)                                      # ghi lại
    return round(float(np.mean(tong)), 1)                   # trung bình
CP = lambda: gym.make("CartPole-v1")                        # hàm tạo môi trường
tt_cp = ppo(CP, 200_000)                                    # 200 000 bước
print(danh_gia(tt_cp, CP, n=100, seed=20_000))              # 100 tập test chưa dùng
''', "20480 118.6\n40960 256.9\n61440 222.4\n81920 273.8\n102400 352.5\n122880 312.7\n143360 342.4\n163840 351.5\n184320 341.5\n484.7",
    khung("doc", ["Điểm lúc học còn lấy mẫu và còn thưởng entropy; chính sách tham lam trên 100 tập test được 484,7."]))

c.mo_trang(3, "Pendulum: hành động là một số thực (khoảng 21 giây).")
c.o('''
PE = lambda: gym.make("Pendulum-v1")                        # con lắc ngược
e = PE()                                                    # một bản để xem
print(e.observation_space, e.action_space, e.spec.max_episode_steps)   # cos, sin, vận tốc góc; mô-men trong [-2, 2]
''', "Box([-1. -1. -8.], [1. 1. 8.], (3,), float32) Box(-2.0, 2.0, (1,), float32) 200")
c.o('''
rng = np.random.default_rng(0)                              # ngẫu nhiên
tong = []                                                   # điểm mỗi tập
for i in range(20):                                         # 20 tập
    o, _ = e.reset(seed=10_000 + i)                         # seed cố định
    G = 0                                                   # điểm
    while True:                                             # mỗi bước
        o, r, ket_thuc, cat_ngang, _ = e.step(rng.uniform(-2, 2, size=1).astype(np.float32))   # mô-men ngẫu nhiên
        G += r                                              # cộng thưởng
        if ket_thuc or cat_ngang:                           # hết 200 bước
            break                                           # ra khỏi vòng
    tong.append(G)                                          # ghi lại
print(round(np.mean(tong), 1))                              # mốc chọn bừa
''', "-1112.0")
c.o('''
tt_pe = ppo(PE, 100_000, n_buoc=512, epoch=10, n_lo=32, lr=1e-3, gamma=0.9, he_so_ent=0.0, lien_tuc=True, in_moi=5)   # chính sách chuẩn
print(danh_gia(tt_pe, PE, n=100, seed=20_000), round(tt_pe.log_std.exp().item(), 3))   # điểm test, độ lệch chuẩn đã học
''', "10240 -1261.0\n20480 -1085.1\n30720 -750.9\n40960 -207.7\n51200 -772.8\n61440 -479.7\n71680 -190.6\n81920 -241.7\n92160 -193.5\n-184.7 0.389")

c.mo_trang(4, "Môi trường quản lý kho tự viết, chính sách (s, S), và PPO (khoảng 40 giây).")
c.o('''
import warnings                                             # tắt cảnh báo của check_env
from gymnasium import spaces                                # không gian quan sát và hành động
from gymnasium.utils.env_checker import check_env           # bộ kiểm môi trường
class Kho(gym.Env):                                         # môi trường quản lý kho
    def __init__(self, so_ngay=60, nhu_cau=3.0, suc_chua=20, phi_luu=0.5, phat_thieu=4.0, phi_dat=3.0, gia_hang=1.0):   # tham số bài toán
        self.so_ngay, self.nhu_cau, self.suc_chua = so_ngay, nhu_cau, suc_chua   # kỳ 60 ngày, Poisson trung bình 3, chứa 20
        self.phi_luu, self.phat_thieu, self.phi_dat, self.gia_hang = phi_luu, phat_thieu, phi_dat, gia_hang   # bốn loại chi phí
        self.observation_space = spaces.Box(0.0, 1.0, (2,), np.float32)   # tồn kho, ngày; cả hai chia về [0, 1]
        self.action_space = spaces.Discrete(11)             # đặt 0 tới 10 thùng
    def _quan_sat(self):                                    # quan sát hiện tại
        return np.array([self.ton / self.suc_chua, self.ngay / self.so_ngay], np.float32)   # chuẩn hóa về [0, 1]
    def reset(self, seed=None, options=None):               # bắt đầu kỳ mới
        super().reset(seed=seed)                            # khởi tạo self.np_random
        self.ton, self.ngay = 5, 0                          # 5 thùng, ngày 0
        return self._quan_sat(), {}                         # quan sát, thông tin
    def step(self, a):                                      # một ngày
        dat = min(int(a), self.suc_chua - self.ton)         # không đặt quá sức chứa
        self.ton += dat                                     # hàng về ngay
        cau = int(self.np_random.poisson(self.nhu_cau))     # khách muốn mua
        ban = min(cau, self.ton)                            # bán được
        thieu = cau - ban                                   # thiếu
        self.ton -= ban                                     # còn lại
        self.ngay += 1                                      # sang ngày sau
        chi_phi = (self.phi_luu * self.ton + self.phat_thieu * thieu
                   + (self.phi_dat if dat > 0 else 0) + self.gia_hang * dat)   # lưu kho, thiếu hàng, phí đặt, tiền hàng
        return self._quan_sat(), -chi_phi, False, self.ngay >= self.so_ngay, {"thieu": thieu}   # hết kỳ là bị cắt, không phải kết thúc
with warnings.catch_warnings():                             # cảnh báo duy nhất: không có chế độ vẽ hình
    warnings.simplefilter("ignore")                         # bỏ qua
    check_env(Kho())                                        # kiểm reset, step, seed, kiểu dữ liệu
print("hợp lệ")                                             # không lỗi
''', "hợp lệ")
c.o('''
def chinh_sach_sS(s_, S_, n, seed):                         # tồn kho <= s thì đặt cho đủ S
    e = Kho()                                               # môi trường
    tong = []                                               # tổng phần thưởng mỗi kỳ
    for i in range(n):                                      # n kỳ
        e.reset(seed=seed + i)                              # seed cố định
        G = 0                                               # tổng
        while True:                                         # mỗi ngày
            _, r, ket_thuc, cat_ngang, _ = e.step(min(10, S_ - e.ton) if e.ton <= s_ else 0)   # quy tắc (s, S)
            G += r                                          # cộng
            if ket_thuc or cat_ngang:                       # hết kỳ
                break                                       # ra khỏi vòng
        tong.append(G)                                      # ghi lại
    return round(float(np.mean(tong)), 1)                   # trung bình
luoi = sorted((chinh_sach_sS(s_, S_, 500, 0), s_, S_) for s_ in range(6) for S_ in range(s_ + 1, 13))   # thử mọi cặp
print(luoi[-3:])                                            # ba cặp tốt nhất
_, s_tot, S_tot = luoi[-1]                                  # cặp tốt nhất
print(chinh_sach_sS(s_tot, S_tot, 2000, 20_000))            # đo lại trên 2000 kỳ test
''', "[(-379.2, 1, 8), (-376.6, 2, 8), (-376.1, 2, 7)]\n-374.9")
c.o('''
tt_kho = ppo(Kho, 300_000, n_buoc=512, epoch=10, n_lo=8, lr=1e-3, in_moi=50)   # cùng hàm ppo
print(danh_gia(tt_kho, Kho, n=2000, seed=20_000))           # cùng 2000 kỳ test
with torch.no_grad():                                       # không cần gradient
    print([int(tt_kho.tham_lam(torch.tensor([t / 20, 0.5]))) for t in range(13)])   # số thùng đặt ở ngày 30 theo tồn kho 0 tới 12
''', "102400 -424.2\n204800 -401.2\n-377.6\n[7, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]",
    khung("doc", ["PPO tốn 377,6 so với 374,9 của (s, S) tốt nhất, và tự học ra đúng dạng (s, S): hết hàng hoặc còn 1 thùng thì đặt 7, còn lại không đặt."]))

c.mo_trang(5, "Ba bài tập. Đoán trước, rồi mới mở đáp án.")
c.bai("37.1", "Bỏ phép cắt", "(a) PPO trên CartPole với clip=100.0. (b) 30 epoch mỗi lô, có cắt và không cắt.",
      "(a) Lên 436 rồi sụp về 134 chỉ một lô sau; test 210,8 so với 484,7. (b) Có cắt: 500 từ bước 40 960 và giữ nguyên; không cắt: nhảy loạn từ 31 tới 500. Phép cắt làm việc dùng lại dữ liệu trở nên an toàn. Code ở hai ô ngay dưới (ô thứ hai khoảng 2 phút).")
c.o('''
tt = ppo(CP, 200_000, clip=100.0)                           # tỷ số không bao giờ chạm ngưỡng
print(danh_gia(tt, CP, n=100, seed=20_000))                 # điểm test
''', "20480 125.0\n40960 225.8\n61440 349.4\n81920 412.8\n102400 436.2\n122880 133.7\n143360 202.7\n163840 214.4\n184320 178.5\n210.8")
c.o('''
for clip in (0.2, 100.0):                                   # có cắt, không cắt
    tt = ppo(CP, 200_000, epoch=30, clip=clip)              # 30 epoch mỗi lô
    print("clip", clip, danh_gia(tt, CP, n=100, seed=20_000))   # điểm test
''', "20480 222.1\n40960 500.0\n61440 500.0\n81920 500.0\n102400 500.0\n122880 500.0\n143360 500.0\n163840 500.0\n184320 500.0\nclip 0.2 500.0\n20480 450.4\n40960 260.2\n61440 31.0\n81920 429.2\n102400 123.5\n122880 225.0\n143360 108.6\n163840 500.0\n184320 500.0\nclip 100.0 500.0")
c.bai("37.2", "Hai đầu của GAE", "lambda = 0 và lambda = 1.",
      "lambda = 0 hỏng hẳn (19,7); lambda = 1 học được (498,3) nhưng gồ ghề hơn. Code ở ô ngay dưới.")
c.o('''
for lam in (0.0, 1.0):                                      # TD một bước, lợi nhuận thật
    tt = ppo(CP, 200_000, lam=lam)                          # chỉ đổi lambda
    print("lambda", lam, danh_gia(tt, CP, n=100, seed=20_000))   # điểm test
''', "20480 64.0\n40960 56.6\n61440 33.0\n81920 30.7\n102400 27.8\n122880 22.5\n143360 22.8\n163840 20.8\n184320 19.2\nlambda 0.0 19.7\n20480 89.6\n40960 173.6\n61440 325.2\n81920 325.0\n102400 393.4\n122880 381.2\n143360 291.8\n163840 374.2\n184320 463.3\nlambda 1.0 498.3")
c.bai("37.3", "Khách khó tính hơn", "Phạt thiếu hàng 10 thay vì 4: tìm lại (s, S), huấn luyện lại PPO.",
      "(s, S) tốt nhất thành (3, 9), test 412,8; PPO 415,4 và tự nâng ngưỡng đặt hàng từ 1 lên 3. Code ở ô ngay dưới.")
c.o('''
Kho10 = lambda: Kho(phat_thieu=10.0)                        # thiếu hàng đắt hơn
def chinh_sach_sS_10(s_, S_, n, seed):                      # (s, S) trên môi trường mới
    e = Kho10()                                             # môi trường
    tong = []                                               # tổng mỗi kỳ
    for i in range(n):                                      # n kỳ
        e.reset(seed=seed + i)                              # seed cố định
        G = 0                                               # tổng
        while True:                                         # mỗi ngày
            _, r, ket_thuc, cat_ngang, _ = e.step(min(10, S_ - e.ton) if e.ton <= s_ else 0)   # quy tắc (s, S)
            G += r                                          # cộng
            if ket_thuc or cat_ngang:                       # hết kỳ
                break                                       # ra khỏi vòng
        tong.append(G)                                      # ghi lại
    return round(float(np.mean(tong)), 1)                   # trung bình
luoi = sorted((chinh_sach_sS_10(s_, S_, 500, 0), s_, S_) for s_ in range(6) for S_ in range(s_ + 1, 13))   # lưới
print(luoi[-3:], chinh_sach_sS_10(luoi[-1][1], luoi[-1][2], 2000, 20_000))   # ba cặp tốt nhất, đo lại cặp tốt nhất
tt10 = ppo(Kho10, 300_000, n_buoc=512, epoch=10, n_lo=8, lr=1e-3, in_moi=50)   # huấn luyện lại
print(danh_gia(tt10, Kho10, n=2000, seed=20_000))           # điểm test
with torch.no_grad():                                       # không cần gradient
    print([int(tt10.tham_lam(torch.tensor([t / 20, 0.5]))) for t in range(13)])   # chính sách mới
''', "[(-416.6, 3, 10), (-415.7, 3, 8), (-415.3, 3, 9)] -412.8\n102400 -474.9\n204800 -429.9\n-415.4\n[7, 7, 7, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0]")

c.ghi(Path(__file__).resolve().parents[2] / "notebooks/ch37_ppo_gymnasium.ipynb")
