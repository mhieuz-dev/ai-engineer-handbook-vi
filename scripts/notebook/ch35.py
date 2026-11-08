"""Dựng notebooks/ch35_dqn.ipynb: python3 scripts/notebook/ch35.py"""
from pathlib import Path
from nblib import Chuong, code, khung

c = Chuong(35, "Deep Q-Network", "ch35-dqn",
           "Thay bảng Q bằng mạng nơ-ron, cài DQN với replay buffer và mạng đích, huấn luyện trên CartPole tới 500 điểm, rồi bỏ từng mẹo để thấy vì sao cần nó. Mỗi lần huấn luyện khoảng 40 giây trên CPU, không cần GPU.",
           ["Hiểu vì sao Q-learning với mạng nơ-ron dễ phân kỳ (tam giác chết).",
            "Cài replay buffer, mạng đích, epsilon giảm dần và mục tiêu tách terminated với truncated.",
            "Huấn luyện DQN trên CartPole, giữ bản tốt nhất, đo lại trên tập mới.",
            "Bỏ mạng đích, bỏ replay, thử Double DQN, và đọc kết quả qua nhiều seed."],
           [("Từ bảng sang mạng", "01-tu-bang-sang-mang"), ("Replay buffer và mạng đích", "02-replay-va-mang-dich"),
            ("Huấn luyện trên CartPole", "03-huan-luyen-cartpole"), ("Bỏ từng mẹo", "04-bo-tung-meo"), ("Bài tập", "05-bai-tap")],
           thoi_gian="khoảng 5 phút")

c.mo_trang(1, "CartPole, mốc chọn bừa, và mạng Q.")
c.cells.append(code('''
!pip install -q gymnasium                                   # thư viện môi trường RL, Colab chưa chắc có sẵn
'''))
c.o('''
import copy                                                 # sao chép mạng
import gymnasium as gym                                     # môi trường RL
import numpy as np                                          # mảng
import torch                                                # PyTorch
import torch.nn as nn                                       # các lớp mạng
import torch.nn.functional as F                             # hàm loss
torch.set_num_threads(1)                                    # mạng nhỏ: một luồng nhanh hơn và lặp lại được
env = gym.make("CartPole-v1")                               # xe đẩy và cây sào
print(env.observation_space.shape, env.action_space, env.spec.max_episode_steps)   # 4 số, 2 hành động, tối đa 500 bước
s, _ = env.reset(seed=0)                                    # trạng thái đầu
print(s)                                                    # vị trí, vận tốc, góc, vận tốc góc
''', "(4,) Discrete(2) 500\n[ 0.01369617 -0.02302133 -0.04590265 -0.04834723]")
c.o('''
rng = np.random.default_rng(0)                              # ngẫu nhiên của tác tử
env.reset(seed=0)                                           # seed môi trường
diem = []                                                   # điểm mỗi tập
for _ in range(100):                                        # 100 tập
    env.reset()                                             # tập mới
    G = 0                                                   # điểm tập này
    while True:                                             # mỗi bước
        _, r, ket_thuc, cat_ngang, _ = env.step(int(rng.integers(2)))   # đẩy bừa trái hoặc phải
        G += r                                              # cộng thưởng
        if ket_thuc or cat_ngang:                           # sào đổ hoặc đủ 500 bước
            break                                           # hết tập
    diem.append(G)                                          # ghi lại
print(np.mean(diem), np.max(diem))                          # trung bình, tốt nhất
''', "21.77 72.0")
c.o('''
def tao_mang():                                             # MLP: 4 số vào, Q của 2 hành động ra
    return nn.Sequential(nn.Linear(4, 128), nn.ReLU(), nn.Linear(128, 128), nn.ReLU(), nn.Linear(128, 2))   # hai lớp ẩn 128
torch.manual_seed(0)                                        # khởi tạo cố định
q = tao_mang()                                              # mạng chưa học
print(sum(p.numel() for p in q.parameters()), q(torch.as_tensor(s)).detach().numpy().round(3))   # số tham số, Q ở trạng thái đầu
''', "17410 [ 0.013 -0.048]")

c.mo_trang(2, "Cài DQN: replay buffer, mạng đích, epsilon giảm dần, đánh giá định kỳ.")
c.o('''
def danh_gia(mang, n=20, seed=10_000):                      # điểm trung bình của chính sách tham lam
    e = gym.make("CartPole-v1")                             # môi trường riêng để đánh giá
    tong = []                                               # điểm mỗi tập
    for i in range(n):                                      # n tập với seed cố định
        s, _ = e.reset(seed=seed + i)                       # tập thứ i
        G = 0                                               # điểm
        while True:                                         # mỗi bước
            with torch.no_grad():                           # không cần gradient
                a = int(mang(torch.as_tensor(s)).argmax())  # tham lam, không khám phá
            s, r, ket_thuc, cat_ngang, _ = e.step(a)        # đi
            G += r                                          # cộng thưởng
            if ket_thuc or cat_ngang:                       # hết tập
                break                                       # ra khỏi vòng
        tong.append(G)                                      # ghi lại
    return float(np.mean(tong))                             # trung bình
def dqn(n_buoc=50_000, seed=0, muc_tieu_rieng=True, replay=True, double=False, ket_thuc_khi_cat=False,
        lr=5e-4, cap_nhat_dich=100, bo_nho=50_000, lo=128, gamma=0.99, eps_cuoi=0.05, eps_buoc=10_000,
        bat_dau=1000, danh_gia_moi=5000):                   # DQN; các cờ dùng cho thí nghiệm trang 4 và bài tập
    torch.manual_seed(seed)                                 # khởi tạo mạng
    rng = np.random.default_rng(seed)                       # khám phá và rút lô
    q = tao_mang()                                          # mạng chính
    q_dich = copy.deepcopy(q)                               # mạng đích: bản sao đóng băng
    opt = torch.optim.Adam(q.parameters(), lr=lr, fused=True)   # fused: lặp lại được trên CPU
    S, S2 = np.zeros((bo_nho, 4), np.float32), np.zeros((bo_nho, 4), np.float32)   # replay buffer: trạng thái, trạng thái mới
    A, Rw, D = np.zeros(bo_nho, np.int64), np.zeros(bo_nho, np.float32), np.zeros(bo_nho, np.float32)   # hành động, thưởng, cờ kết thúc
    n, G, diem_tap = 0, 0, []                               # số bước đã lưu, điểm tập hiện tại, điểm các tập
    tot_nhat, ban_tot = -1, None                            # bản tốt nhất theo đánh giá
    s, _ = env.reset(seed=seed)                             # tập đầu
    for t in range(1, n_buoc + 1):                          # mỗi bước môi trường
        eps = max(eps_cuoi, 1 - (1 - eps_cuoi) * t / eps_buoc)   # giảm tuyến tính rồi giữ nguyên
        if rng.random() < eps:                              # khám phá
            a = int(rng.integers(2))                        # hành động ngẫu nhiên
        else:                                               # khai thác
            with torch.no_grad():                           # không cần gradient
                a = int(q(torch.as_tensor(s)).argmax())     # hành động tham lam
        s2, r, ket_thuc, cat_ngang, _ = env.step(a)         # đi một bước
        G += r                                              # cộng thưởng
        i = n % bo_nho                                      # ghi đè vòng tròn
        S[i], A[i], Rw[i], S2[i] = s, a, r, s2              # lưu bước
        D[i] = float(ket_thuc or (ket_thuc_khi_cat and cat_ngang))   # chỉ kết thúc thật mới bỏ phần tương lai
        n += 1                                              # đếm
        s = s2                                              # sang trạng thái mới
        if ket_thuc or cat_ngang:                           # hết tập
            diem_tap.append(G)                              # ghi điểm
            G = 0                                           # tập mới
            s, _ = env.reset()                              # về đầu
        if n >= bat_dau:                                    # đủ dữ liệu thì học
            idx = rng.integers(min(n, bo_nho), size=lo) if replay else np.array([i])   # lô ngẫu nhiên, hoặc chỉ bước vừa đi
            sb, ab, rb, s2b, db = map(torch.as_tensor, (S[idx], A[idx], Rw[idx], S2[idx], D[idx]))   # sang tensor
            with torch.no_grad():                           # mục tiêu không nhận gradient
                mang_dich = q_dich if muc_tieu_rieng else q # có hay không có mạng đích
                if double:                                  # Double DQN
                    q_sau = mang_dich(s2b).gather(1, q(s2b).argmax(1, keepdim=True)).squeeze(1)   # mạng chính chọn, mạng đích chấm
                else:                                       # DQN chuẩn
                    q_sau = mang_dich(s2b).max(1).values    # max theo mạng đích
                y = rb + gamma * (1 - db) * q_sau           # mục tiêu
            q_sa = q(sb).gather(1, ab.unsqueeze(1)).squeeze(1)   # Q của đúng hành động đã làm
            loss = F.smooth_l1_loss(q_sa, y)                # Huber
            opt.zero_grad()                                 # xóa gradient
            loss.backward()                                 # lượt ngược
            opt.step()                                      # cập nhật
            if t % cap_nhat_dich == 0:                      # định kỳ
                q_dich.load_state_dict(q.state_dict())      # chép sang mạng đích
        if t % danh_gia_moi == 0:                           # đánh giá định kỳ
            diem = danh_gia(q)                              # chính sách tham lam, 20 tập
            print(t, len(diem_tap), round(np.mean(diem_tap[-20:]), 1), diem)   # bước, số tập, điểm lúc học, điểm đánh giá
            if diem > tot_nhat:                             # tốt hơn mọi lần trước
                tot_nhat, ban_tot = diem, copy.deepcopy(q)  # giữ bản này
    return ban_tot, q                                       # bản tốt nhất và bản cuối
print(danh_gia(q))                                          # mạng chưa học của trang 1
''', "91.05", khung("doc", ["Mạng chưa học đã giữ sào 91 bước, gấp bốn lần chọn bừa: argmax của một mạng ngẫu nhiên vẫn đổi hướng theo góc sào, tình cờ thành một phản xạ thô."]))

c.mo_trang(3, "Một lần huấn luyện (khoảng 40 giây), rồi đo lại trên 100 tập mới.")
c.o('''
ban_tot, ban_cuoi = dqn()                                   # seed 0, 50 000 bước
''', "5000 132 62.0 177.35\n10000 193 72.6 95.2\n15000 245 98.0 101.2\n20000 296 100.7 129.95\n25000 349 82.8 90.05\n30000 369 252.4 151.1\n35000 421 78.2 104.2\n40000 458 164.1 500.0\n45000 537 32.6 56.15\n50000 564 220.6 500.0",
    khung("doc", ["Cột cuối là điểm của chính sách tham lam: dao động 90 tới 177, chạm 500 ở bước 40 000, rơi xuống 56 ở bước 45 000, rồi lại 500. Đường học của DQN không đi lên đều."]))
c.o('''
print(danh_gia(ban_tot, n=100, seed=20_000), danh_gia(ban_cuoi, n=100, seed=20_000))   # 100 tập chưa dùng lần nào
''', "500.0 500.0")

c.mo_trang(4, "Bỏ mạng đích, bỏ replay buffer.")
c.o('''
_, q_khong_dich = dqn(muc_tieu_rieng=False)                 # mục tiêu tính bằng chính mạng đang học
with torch.no_grad():                                       # không cần gradient
    print(q_khong_dich(torch.as_tensor(s)).numpy())         # Q ở trạng thái đầu
''', "5000 254 16.9 9.45\n10000 691 9.1 9.45\n15000 1212 9.3 9.45\n20000 1733 9.5 9.45\n25000 2250 9.7 9.45\n30000 2771 9.3 9.45\n35000 3289 9.8 9.45\n40000 3809 9.6 9.45\n45000 4332 9.4 9.45\n50000 4849 9.8 9.45\n[1.9254470e+08 2.6113987e+08]",
    khung("loi", ["Q lên hàng trăm triệu trong khi giá trị thật không thể vượt 100: phân kỳ. Chính sách luôn đẩy về một phía và sào đổ sau khoảng 9 bước."], "PHÂN KỲ"))
c.o('''
_ = dqn(replay=False)                                       # chỉ học từ bước vừa đi, vẫn có mạng đích
''', "5000 193 29.4 19.3\n10000 450 10.2 14.8\n15000 729 56.0 45.7\n20000 1034 31.0 14.1\n25000 1315 13.8 66.2\n30000 1559 51.6 49.45\n35000 1678 56.8 60.7\n40000 1861 28.0 93.5\n45000 2175 9.8 9.45\n50000 2360 13.0 11.9")

c.mo_trang(5, "Ba bài tập. Đoán trước, rồi mới mở đáp án. Mỗi bài khoảng 40 giây.")
c.bai("35.1", "Đánh giá quá cao, đo bằng số", "So max Q ở trạng thái đầu với lợi nhuận chiết khấu thật 99,34, cho DQN và Double DQN.",
      "DQN dự đoán 134,77, cao hơn cả trần 100. Double DQN 127,63 ở seed này, nhưng trên 5 seed trung bình 137,0 so với 128,1: trên CartPole với mạng đích chép mỗi 100 bước, Double DQN không giúp. Code ở ô ngay dưới.")
c.o('''
that = sum(0.99 ** k for k in range(500))                   # lợi nhuận chiết khấu thật khi giữ sào đủ 500 bước
_, cuoi_double = dqn(double=True)                           # Double DQN
with torch.no_grad():                                       # không cần gradient
    for ten, m in (("DQN", ban_cuoi), ("Double DQN", cuoi_double)):   # hai mạng cuối
        print(ten, danh_gia(m, n=100, seed=20_000), round(m(torch.as_tensor(s)).max().item(), 2), round(that, 2))   # điểm test, Q dự đoán, giá trị thật
''', "5000 142 56.6 143.95\n10000 211 90.4 100.55\n15000 268 85.4 97.5\n20000 306 129.4 451.3\n25000 317 327.8 259.15\n30000 356 146.0 500.0\n35000 367 364.1 358.5\n40000 423 67.6 88.0\n45000 473 91.5 79.45\n50000 523 125.2 352.35\nDQN 500.0 134.77 99.34\nDouble DQN 310.53 127.63 99.34")
c.bai("35.2", "Chép mạng đích thưa hơn", "Chạy lại với cap_nhat_dich=500.",
      "Seed 0 không lần nào chạm 500; trên 5 seed chỉ 1 seed chạm 500. Tần suất chép mạng đích phải tương xứng với tổng số bước huấn luyện. Code ở ô ngay dưới.")
c.o('''
_ = dqn(cap_nhat_dich=500)                                  # chép mạng đích mỗi 500 bước
''', "5000 173 48.4 199.3\n10000 210 162.6 151.45\n15000 241 170.6 126.7\n20000 274 164.4 197.25\n25000 309 143.2 136.45\n30000 340 137.0 120.35\n35000 375 155.0 117.75\n40000 411 127.0 110.55\n45000 455 114.8 227.65\n50000 497 119.1 143.4")
c.bai("35.3", "Nhầm bị cắt ngang với kết thúc", "Chạy lại với ket_thuc_khi_cat=True.",
      "Giống hệt bản đúng tới bước 25 000, rồi tách ra; mạng cuối chỉ được 166,8 trên test. Trên 5 seed, 360,6 so với 479,2. Code ở ô ngay dưới.")
c.o('''
_, cuoi_sai = dqn(ket_thuc_khi_cat=True)                    # bước 500 cũng bị ghi là kết thúc
with torch.no_grad():                                       # không cần gradient
    print(danh_gia(cuoi_sai, n=100, seed=20_000), round(cuoi_sai(torch.as_tensor(s)).max().item(), 2))   # điểm test, Q ở trạng thái đầu
''', "5000 132 62.0 177.35\n10000 193 72.6 95.2\n15000 245 98.0 101.2\n20000 296 100.7 129.95\n25000 349 82.8 90.05\n30000 368 251.8 151.25\n35000 421 87.2 82.9\n40000 457 148.9 500.0\n45000 604 21.0 24.9\n50000 641 218.5 167.7\n166.81 142.33")

c.ghi(Path(__file__).resolve().parents[2] / "notebooks/ch35_dqn.ipynb")
