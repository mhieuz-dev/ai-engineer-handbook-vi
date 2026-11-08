"""Dựng notebooks/ch33_bai_toan_rl.ipynb: python3 scripts/notebook/ch33.py"""
from pathlib import Path
from nblib import Chuong, code, khung

c = Chuong(33, "Bài toán RL", "ch33-bai-toan-rl",
           "Mở đầu Phần III-B Reinforcement Learning: chạy môi trường FrozenLake của Gymnasium, đo chính sách bằng mô phỏng, thấy thế giằng co giữa khám phá và khai thác qua bài toán bandit 10 tay, rồi tính chính xác hàm giá trị bằng phương trình Bellman.",
           ["Dùng vòng lặp reset và step của Gymnasium, phân biệt terminated với truncated.",
            "So tham lam với epsilon-greedy trên bàn thử bandit 10 tay.",
            "Đọc bảng chuyển của một MDP và tính lợi nhuận có chiết khấu.",
            "Giải phương trình Bellman để có giá trị chính xác của một chính sách, đối chiếu với mô phỏng."],
           [("Học từ phần thưởng", "01-hoc-tu-phan-thuong"), ("Khám phá và khai thác", "02-kham-pha-khai-thac"),
            ("MDP và lợi nhuận", "03-mdp-va-loi-nhuan"), ("Chính sách và hàm giá trị", "04-chinh-sach-va-ham-gia-tri"),
            ("Bài tập", "05-bai-tap")])

c.mo_trang(1, "Cài Gymnasium, chạy FrozenLake, đo hai chính sách bằng 10 000 tập.")
c.cells.append(code('''
!pip install -q gymnasium                                   # thư viện môi trường RL, Colab chưa chắc có sẵn
'''))
c.o('''
import gymnasium as gym                                     # môi trường chuẩn cho RL
import numpy as np                                          # mảng
env = gym.make("FrozenLake-v1")                             # hồ băng 4x4, mặc định băng trơn
print(env.unwrapped.desc.astype(str))                       # bản đồ: S xuất phát, F băng, H hố, G đích
print(env.observation_space, env.action_space, env.spec.max_episode_steps)   # 16 trạng thái, 4 hành động, tối đa 100 bước
''', "[['S' 'F' 'F' 'F']\n ['F' 'H' 'F' 'H']\n ['F' 'F' 'F' 'H']\n ['H' 'F' 'F' 'G']]\nDiscrete(16) Discrete(4) 100")
c.o('''
TEN = ["trái", "xuống", "phải", "lên"]                       # tên 4 hành động
rng = np.random.default_rng(0)                              # bộ sinh số ngẫu nhiên của tác tử
s, info = env.reset(seed=0)                                 # bắt đầu một tập, seed để lặp lại được
while True:                                                 # mỗi bước
    a = int(rng.integers(4))                                # chọn bừa một hướng
    s_moi, r, ket_thuc, cat_ngang, info = env.step(a)       # môi trường trả về 5 thứ
    print(s, TEN[a], "->", s_moi, r, ket_thuc, cat_ngang)   # đọc từng bước
    s = s_moi                                               # sang trạng thái mới
    if ket_thuc or cat_ngang:                               # tới đích, rơi hố, hoặc quá 100 bước
        break                                               # hết tập
''', "0 lên -> 1 0 False False\n1 phải -> 5 0 True False",
    khung("doc", ["Ở ô 0 tác tử chọn lên, đụng tường lẽ ra đứng yên, nhưng băng trượt và nó sang phải tới ô 1. Ở ô 1 nó chọn phải nhưng trượt xuống hố 5: phần thưởng 0, terminated là True."]))
c.o('''
def chay(chinh_sach, n=10_000, seed=0):                     # đo một chính sách bằng n tập
    rng = np.random.default_rng(seed)                       # ngẫu nhiên của tác tử
    env.reset(seed=seed)                                    # seed môi trường một lần
    thang = buoc = 0                                        # số lần tới đích, tổng số bước
    for _ in range(n):                                      # mỗi tập
        s, _ = env.reset()                                  # về ô xuất phát
        while True:                                         # mỗi bước
            s, r, ket_thuc, cat_ngang, _ = env.step(chinh_sach(s, rng))   # làm theo chính sách
            buoc += 1                                       # đếm bước
            if ket_thuc or cat_ngang:                       # hết tập
                break                                       # ra khỏi vòng
        thang += r                                          # r bước cuối: 1 nếu tới đích
    return thang / n, buoc / n                              # tỷ lệ tới đích, số bước trung bình
print(chay(lambda s, rng: int(rng.integers(4))))            # chính sách ngẫu nhiên
''', "(0.0156, 7.7812)")
c.o('''
DUONG = {0: 1, 4: 1, 8: 2, 9: 1, 13: 2, 14: 2}              # đường ngắn nhất: ô và hướng cần đi
print(chay(lambda s, rng: DUONG.get(s, 1)))                 # ngoài đường thì đi xuống
''', "(0.0495, 5.4324)",
    khung("truc-giac", ["Đường ngắn nhất chỉ tới đích 4,95% số lần: mỗi bước có 2/3 khả năng trượt ngang, và đường này chạy sát hố 5 và hố 12. Kế hoạch hợp lý với người nhìn bản đồ chưa chắc là chính sách tốt khi kết quả của hành động là ngẫu nhiên."]))

c.mo_trang(2, "Bàn thử bandit 10 tay: 2000 lần chạy, mỗi lần 1000 lượt kéo, chạy cùng lúc bằng ma trận.")
c.o('''
def bandit(eps, n_lan=2000, n_buoc=1000, k=10, seed=0):     # epsilon-greedy trên bàn thử Sutton và Barto
    rng = np.random.default_rng(seed)                       # ngẫu nhiên
    q_that = rng.normal(0, 1, (n_lan, k))                   # mức trả thật của 10 tay, mỗi lần chạy một bộ mới
    tot_nhat = q_that.argmax(1)                             # tay tốt nhất thật sự
    Q = np.zeros((n_lan, k))                                # ước lượng của tác tử
    N = np.zeros((n_lan, k))                                # số lần đã kéo mỗi tay
    hang = np.arange(n_lan)                                 # chỉ số hàng
    thuong, dung = np.zeros(n_buoc), np.zeros(n_buoc)       # ghi lại theo lượt
    for t in range(n_buoc):                                 # mỗi lượt
        a = np.where(rng.random(n_lan) < eps, rng.integers(k, size=n_lan), Q.argmax(1))   # khám phá hay khai thác
        r = rng.normal(q_that[hang, a], 1)                  # phần thưởng có nhiễu
        N[hang, a] += 1                                     # đếm
        Q[hang, a] += (r - Q[hang, a]) / N[hang, a]         # cập nhật trung bình
        thuong[t], dung[t] = r.mean(), (a == tot_nhat).mean()   # phần thưởng trung bình, tỷ lệ chọn đúng
    return thuong, dung, q_that.max(1).mean()               # kèm mức trần
for eps in (0, 0.01, 0.1):                                  # ba mức khám phá
    th, d, tran = bandit(eps)                               # chạy
    print(eps, round(th[:100].mean(), 3), round(th[-100:].mean(), 3), round(d[-100:].mean(), 3))   # đầu, cuối, tỷ lệ đúng
print("trần", round(tran, 3))                               # luôn kéo tay tốt nhất
''', "0 0.963 1.039 0.355\n0.01 0.975 1.318 0.587\n0.1 1.005 1.37 0.797\ntrần 1.535",
    khung("doc", ["Tham lam dừng ở 1,04 và chỉ chọn đúng tay tốt nhất 35,5% số lượt cuối: nó kéo mãi tay đầu tiên cho thưởng dương. Với epsilon 0,1, tác tử chọn bừa 10% số lượt nhưng tìm ra tay tốt nhất ở 79,7% số lượt cuối và đạt 1,37, gần trần 1,535."]))

c.mo_trang(3, "Đọc bảng chuyển của FrozenLake, đổi thành mảng NumPy, tính lợi nhuận có chiết khấu.")
c.o('''
P = env.unwrapped.P                                         # toàn bộ MDP: P[s][a] = [(xác suất, s mới, thưởng, kết thúc)]
print(P[14][2])                                             # ô 14, sát đích, đi phải
print(P[0][1])                                              # ô xuất phát, đi xuống
print(P[5][0])                                              # đang ở hố 5
''', "[(0.33333333333333337, 14, 0, False), (0.3333333333333333, 15, 1, True), (0.33333333333333337, 10, 0, False)]\n[(0.33333333333333337, 0, 0, False), (0.3333333333333333, 4, 0, False), (0.33333333333333337, 1, 0, False)]\n[(1.0, 5, 0, True)]")
c.o('''
T = np.zeros((16, 4, 16))                                   # T[s, a, s'] = p(s' | s, a)
R = np.zeros((16, 4))                                       # R[s, a] = phần thưởng kỳ vọng
for s in range(16):                                         # mỗi trạng thái
    for a in range(4):                                      # mỗi hành động
        for p, s2, r, xong in P[s][a]:                      # mỗi khả năng
            T[s, a, s2] += p                                # cộng dồn: hai khả năng có thể tới cùng một ô
            R[s, a] += p * r                                # thưởng nhân xác suất
print(T.sum(2).min(), T.sum(2).max(), R[14], R[15])         # mỗi hàng cộng bằng 1; thưởng ở ô 14 và đích
''', "1.0 1.0 [0.         0.33333333 0.33333333 0.33333333] [0. 0. 0. 0.]")
c.o('''
def loi_nhuan(thuong, gamma):                               # G = r1 + gamma r2 + gamma^2 r3 + ...
    G = 0.0                                                 # từ cuối tập
    for r in reversed(thuong):                              # đi ngược
        G = r + gamma * G                                   # G_t = r_(t+1) + gamma G_(t+1)
    return G                                                # lợi nhuận từ bước đầu
for k in (6, 10, 30):                                       # tới đích ở bước k
    print(k, [round(loi_nhuan([0] * (k - 1) + [1], g), 4) for g in (1, 0.99, 0.9)])   # ba hệ số chiết khấu
''', "6 [1.0, 0.951, 0.5905]\n10 [1.0, 0.9135, 0.3874]\n30 [1.0, 0.7472, 0.0471]")

c.mo_trang(4, "Giải phương trình Bellman cho chính sách ngẫu nhiên, kiểm lại, rồi tính bảng Q.")
c.o('''
CUOI = [5, 7, 11, 12, 15]                                   # bốn hố và đích
def danh_gia(pi, gamma=1.0):                                # giá trị chính xác của chính sách pi (bảng 16 x 4)
    P_pi = np.einsum("sa,sat->st", pi, T)                   # xác suất đi từ s tới s' sau một bước
    R_pi = (pi * R).sum(1)                                  # phần thưởng kỳ vọng ở mỗi trạng thái
    P_pi[CUOI] = 0                                          # trạng thái kết thúc không đi đâu nữa
    R_pi[CUOI] = 0                                          # và không có thưởng
    return np.linalg.solve(np.eye(16) - gamma * P_pi, R_pi) # giải (I - gamma P_pi) V = R_pi
ngau = np.full((16, 4), 0.25)                               # chính sách ngẫu nhiên
V = danh_gia(ngau)                                          # 16 giá trị
print(V.reshape(4, 4).round(4))                             # xếp theo bản đồ
''', "[[0.0139 0.0116 0.021  0.0105]\n [0.0162 0.     0.0408 0.    ]\n [0.0348 0.0882 0.1421 0.    ]\n [0.     0.1758 0.4393 0.    ]]",
    khung("doc", ["Với gamma = 1, V(s) là xác suất tới đích khi xuất phát từ s. Ô xuất phát: 0,0139, khớp 0,0156 đo bằng 10 000 tập trong phạm vi dao động của mô phỏng (độ lệch chuẩn khoảng 0,0012)."]))
c.o('''
s = 14                                                      # kiểm phương trình Bellman ở ô 14
ve_phai = sum(ngau[s, a] * sum(p * (r + V[s2]) for p, s2, r, _ in P[s][a]) for a in range(4))   # vế phải từ bảng P gốc
print(round(V[s], 6), round(ve_phai, 6))                    # hai vế
''', "0.439291 0.439291")
c.o('''
pi_duong = np.eye(4)[[DUONG.get(s, 1) for s in range(16)]] # chính sách đường ngắn nhất dạng bảng
print(round(danh_gia(pi_duong)[0], 4))                      # giá trị chính xác ở ô xuất phát
''', "0.049")
c.o('''
Q = R + np.einsum("sat,t->sa", T, V)                        # Q(s, a) = R[s, a] + tổng T[s, a, s'] V(s'), gamma = 1
Q[CUOI] = 0                                                 # trạng thái kết thúc
print(Q[14].round(4), Q[0].round(4))                        # thứ tự: trái, xuống, phải, lên
''', "[0.2524 0.5384 0.5271 0.4393] [0.0147 0.0139 0.0139 0.0132]",
    khung("truc-giac", ["Ở ô 14, sát đích bên phải, hành động tốt nhất là đi xuống chứ không phải đi phải: đụng tường đáy thì không bao giờ bị trượt lên ô 10. Ở ô xuất phát, tốt nhất là đi trái, vào tường, để không bị trượt về phía hàng hố."]))

c.mo_trang(5, "Ba bài tập. Đoán trước, rồi mới mở đáp án.")
c.bai("33.1", "Khám phá nhiều hơn có tốt hơn", "Chạy bandit với epsilon 0,5, và so phần thưởng trung bình trên cả 1000 lượt của bốn mức epsilon.",
      "Epsilon 0,5 chỉ còn 0,77 ở cuối, thấp hơn cả tham lam; trên cả 1000 lượt, 0,1 đứng đầu (1,299). Code ở ô ngay dưới.")
c.o('''
th, d, _ = bandit(0.5)                                      # khám phá nửa số lượt
print(0.5, round(th[-100:].mean(), 3), round(d[-100:].mean(), 3))   # 100 lượt cuối
for eps in (0, 0.01, 0.1, 0.5):                             # bốn mức
    print(eps, round(bandit(eps)[0].mean(), 3))             # trung bình cả 1000 lượt
''', "0.5 0.77 0.515\n0 1.025\n0.01 1.2\n0.1 1.299\n0.5 0.752")
c.bai("33.2", "Hệ số chiết khấu đổi giá trị thế nào", "Giá trị chính sách ngẫu nhiên ở ô 0 và ô 14 với gamma 1, 0,9 và 0,5.",
      "Ô 0 giảm 3 lần khi gamma = 0,9, ô 14 chỉ giảm 11%: phần thưởng càng xa càng bị chiết khấu nhiều. Code ở ô ngay dưới.")
c.o('''
for g in (1, 0.9, 0.5):                                     # ba hệ số chiết khấu
    print(g, danh_gia(ngau, g)[[0, 14]].round(4))           # ô xuất phát, ô cạnh đích
''', "1 [0.0139 0.4393]\n0.9 [0.0045 0.3915]\n0.5 [1.000e-04 2.976e-01]")
c.bai("33.3", "Một bước cải thiện", "Ở mỗi ô chọn hành động có Q lớn nhất, với Q của chính sách ngẫu nhiên. Tính chính xác và đo bằng mô phỏng.",
      "Chính xác 78,05%, mô phỏng 73,6%: chính sách an toàn đi chậm, 639 trên 10 000 tập bị cắt ở bước 100. Code ở hai ô ngay dưới.")
c.o('''
tham = Q.round(10).argmax(1)                                # làm tròn trước để hai hành động bằng nhau luôn chọn cái đầu
print(tham.reshape(4, 4))                                   # 0 trái, 1 xuống, 2 phải, 3 lên
print(round(danh_gia(np.eye(4)[tham])[0], 4))               # chính xác, không giới hạn số bước
print(chay(lambda s, rng: int(tham[s])))                    # mô phỏng, mỗi tập tối đa 100 bước
''', "[[0 3 0 3]\n [0 0 0 0]\n [3 1 0 0]\n [0 2 1 0]]\n0.7805\n(0.736, 41.0014)")
c.o('''
env.reset(seed=0)                                           # cùng seed như chay
bi_cat = 0                                                  # số tập bị cắt ngang
for _ in range(10_000):                                     # 10 000 tập
    s, _ = env.reset()                                      # về ô xuất phát
    while True:                                             # mỗi bước
        s, r, ket_thuc, cat_ngang, _ = env.step(int(tham[s]))   # theo chính sách mới
        if ket_thuc or cat_ngang:                           # hết tập
            break                                           # ra khỏi vòng
    bi_cat += cat_ngang                                     # đếm tập đủ 100 bước
print(bi_cat)                                               # số tập bị cắt
''', "639")

c.ghi(Path(__file__).resolve().parents[2] / "notebooks/ch33_bai_toan_rl.ipynb")
