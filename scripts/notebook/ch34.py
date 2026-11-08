"""Dựng notebooks/ch34_q_learning.ipynb: python3 scripts/notebook/ch34.py"""
from pathlib import Path
from nblib import Chuong, code, khung

c = Chuong(34, "Quy hoạch động và Q-learning", "ch34-q-learning",
           "Tìm chính sách tối ưu của FrozenLake bằng policy iteration và value iteration, rồi học lại nó bằng Q-learning mà không cần bảng chuyển. So Q-learning với SARSA trên bài vách đá.",
           ["Cài policy iteration và value iteration, kiểm phương trình tối ưu Bellman.",
            "Cài Q-learning, thấy khám phá quyết định thế nào khi phần thưởng thưa.",
            "So bảng Q học được với Q* tính chính xác.",
            "Cài SARSA, so on-policy với off-policy trên bài vách đá qua 50 lần chạy."],
           [("Policy iteration", "01-policy-iteration"), ("Value iteration", "02-value-iteration"),
            ("Q-learning", "03-q-learning"), ("SARSA và vách đá", "04-sarsa-va-vach-da"), ("Bài tập", "05-bai-tap")],
           thoi_gian="khoảng 1 phút")

c.mo_trang(1, "Dựng lại MDP của FrozenLake, chạy policy iteration, kiểm phương trình tối ưu Bellman.")
c.cells.append(code('''
!pip install -q gymnasium                                   # thư viện môi trường RL, Colab chưa chắc có sẵn
'''))
c.cells.append(code('''
import gymnasium as gym                                     # môi trường RL
import numpy as np                                          # mảng
env = gym.make("FrozenLake-v1")                             # hồ băng 4x4 trơn
P = env.unwrapped.P                                         # bảng chuyển dạng danh sách
T = np.zeros((16, 4, 16))                                   # T[s, a, s'] = p(s' | s, a)
R = np.zeros((16, 4))                                       # phần thưởng kỳ vọng
for s in range(16):                                         # mỗi trạng thái
    for a in range(4):                                      # mỗi hành động
        for p, s2, r, xong in P[s][a]:                      # mỗi khả năng
            T[s, a, s2] += p                                # cộng dồn xác suất
            R[s, a] += p * r                                # thưởng nhân xác suất
CUOI = [5, 7, 11, 12, 15]                                   # bốn hố và đích
GAMMA = 0.99                                                # hệ số chiết khấu của cả chương
def danh_gia(pi, gamma=GAMMA):                              # giải hệ Bellman cho chính sách pi
    P_pi = np.einsum("sa,sat->st", pi, T)                   # xác suất một bước theo pi
    R_pi = (pi * R).sum(1)                                  # thưởng kỳ vọng theo pi
    P_pi[CUOI] = 0                                          # trạng thái kết thúc không đi đâu
    R_pi[CUOI] = 0                                          # và không có thưởng
    return np.linalg.solve(np.eye(16) - gamma * P_pi, R_pi) # V
def q_tu_v(V, gamma=GAMMA):                                 # nhìn trước một bước
    Q = R + gamma * np.einsum("sat,t->sa", T, V)            # Q = R + gamma T V
    Q[CUOI] = 0                                             # trạng thái kết thúc
    return Q                                                # bảng 16 x 4
print(T.shape, R.shape)                                     # kiểm kích thước
'''))
c.cells.append({"cell_type": "markdown", "metadata": {}, "source": ["Output mong đợi:\n", "\n", "```text\n", "(16, 4, 16) (16, 4)\n", "```"]})
c.o('''
pi = np.full((16, 4), 0.25)                                 # bắt đầu từ chính sách ngẫu nhiên
for vong in range(10):                                      # tối đa 10 vòng
    V = danh_gia(pi)                                        # đánh giá
    tham = q_tu_v(V).round(10).argmax(1)                    # cải thiện: tham lam theo Q
    pi_moi = np.eye(4)[tham]                                # chính sách tất định dạng bảng
    print(vong, round(V[0], 4), round(danh_gia(pi, 1.0)[0], 4), int((pi_moi != pi).any(1).sum()))   # V(0), xác suất tới đích, số ô đổi
    if (pi_moi == pi).all():                                # không ô nào đổi
        break                                               # dừng
    pi = pi_moi                                             # sang vòng sau
''', "0 0.0124 0.0139 16\n1 0.5325 0.7805 1\n2 0.542 0.8235 0",
    khung("doc", ["Ba lần đánh giá là xong: 1,39%, rồi 78,05%, rồi 82,35% và chính sách không đổi nữa."]))
c.o('''
MUI = "←↓→↑"                                                # mũi tên cho 4 hành động
desc = env.unwrapped.desc.astype(str).flatten()             # bản đồ dạng chữ
for i in range(4):                                          # mỗi hàng
    print(" ".join(desc[4 * i + j] if desc[4 * i + j] in "HG" else MUI[tham[4 * i + j]] for j in range(4)))   # hố, đích hoặc mũi tên
''', "← ↑ ↑ ↑\n← H ← H\n↑ ↓ ← H\nH → ↓ G")
c.o('''
chenh = np.abs(q_tu_v(V).max(1) - V).max()                  # vế phải trừ vế trái của phương trình tối ưu
print(chenh < 1e-12)                                        # chỉ còn sai số làm tròn
''', "True")

c.mo_trang(2, "Value iteration: giá trị lan từ đích ra, chính sách đúng trước khi giá trị đúng.")
c.o('''
V = np.zeros(16)                                            # bắt đầu từ 0
for k in range(1, 2001):                                    # tối đa 2000 vòng
    V_moi = q_tu_v(V).max(1)                                # một vòng: lấy hành động tốt nhất
    chenh = np.abs(V_moi - V).max()                         # thay đổi lớn nhất
    V = V_moi                                               # cập nhật
    if k in (1, 2, 5, 10, 20, 50, 100, 200) or chenh < 1e-10:   # vài vòng để xem
        print(k, round(V[0], 4), round(V[14], 4), f"{chenh:.1e}")   # V(0), V(14), chênh lệch
    if chenh < 1e-10:                                       # đã hội tụ
        break                                               # dừng
''', "1 0.0 0.3333 3.3e-01\n2 0.0 0.4433 1.1e-01\n5 0.0 0.6034 5.1e-02\n10 0.0384 0.7113 2.4e-02\n20 0.1742 0.7852 1.4e-02\n50 0.4251 0.8391 4.5e-03\n100 0.5223 0.8586 1.2e-03\n200 0.5414 0.8627 3.7e-05\n571 0.542 0.8628 9.8e-11")
c.o('''
V = np.zeros(16)                                            # chạy lại từ đầu
for k in range(1, 572):                                     # đủ 571 vòng
    V = q_tu_v(V).max(1)                                    # một vòng
    dung = (q_tu_v(V).round(10).argmax(1) == tham).all()    # tham lam theo V_k đã là tối ưu chưa
    if k in (10, 20, 40, 44, 45, 46, 100, 571):             # vài vòng để xem
        print(k, round(V[0], 4), dung)                      # V(0) và kết quả so
''', "10 0.0384 False\n20 0.1742 False\n40 0.3712 False\n44 0.3954 False\n45 0.4009 True\n46 0.4061 True\n100 0.5223 True\n571 0.542 True",
    khung("truc-giac", ["Từ vòng 45 chính sách đã đúng, dù V(0) mới khoảng 0,40 so với 0,542. Cần thứ tự của các hành động, không cần giá trị chính xác."]))

c.mo_trang(3, "Q-learning không dùng T: hai mức khám phá, so bảng Q với Q*.")
c.o('''
def ti_le_toi_dich(Q, so_buoc=10_000):                      # chấm chính sách tham lam; chỉ người chấm dùng T
    pi = Q.argmax(1)                                        # hành động tham lam ở mỗi ô
    P_pi, R_pi = T[np.arange(16), pi], R[np.arange(16), pi].copy()   # một bước theo chính sách đó
    P_pi[CUOI] = 0                                          # trạng thái kết thúc
    R_pi[CUOI] = 0                                          # không thưởng
    V = np.zeros(16)                                        # xác suất tới đích trong 0 bước
    for _ in range(so_buoc):                                # thêm từng bước
        V = R_pi + P_pi @ V                                 # đúng cả khi chính sách đi lòng vòng mãi
    return round(V[0], 4)                                   # từ ô xuất phát
def q_learning(n_tap, eps, alpha=0.1, gamma=GAMMA, seed=0, moi=2000):   # Q-learning dạng bảng
    rng = np.random.default_rng(seed)                       # ngẫu nhiên của tác tử
    Q = np.zeros((16, 4))                                   # bảng Q ban đầu
    env.reset(seed=seed)                                    # seed môi trường
    for tap in range(1, n_tap + 1):                         # mỗi tập
        s, _ = env.reset()                                  # về ô xuất phát
        while True:                                         # mỗi bước
            a = int(rng.integers(4)) if rng.random() < eps else int(Q[s].argmax())   # epsilon-greedy
            s2, r, ket_thuc, cat_ngang, _ = env.step(a)     # chỉ dùng env.step, không dùng T
            muc_tieu = r if ket_thuc else r + gamma * Q[s2].max()   # mục tiêu TD
            Q[s, a] += alpha * (muc_tieu - Q[s, a])         # cập nhật
            s = s2                                          # sang ô mới
            if ket_thuc or cat_ngang:                       # hết tập
                break                                       # ra khỏi vòng
        if tap % moi == 0:                                  # định kỳ
            print(tap, ti_le_toi_dich(Q))                   # chấm chính sách tham lam
    return Q                                                # bảng đã học
Q_01 = q_learning(20_000, eps=0.1)                          # khám phá 10%
''', "2000 0.0\n4000 0.0\n6000 0.0\n8000 0.0\n10000 0.0\n12000 0.7805\n14000 0.7805\n16000 0.7568\n18000 0.7805\n20000 0.7805",
    khung("doc", ["Phần thưởng thưa và Q bằng 0 ở mọi nơi: argmax luôn chọn trái, tác tử gần như không khám phá. Trong 10 000 tập đầu nó chỉ tới đích một lần, ở tập 9313."]))
c.o('''
Q_05 = q_learning(20_000, eps=0.5)                          # khám phá 50%
''', "2000 0.625\n4000 0.7368\n6000 0.7368\n8000 0.8235\n10000 0.8235\n12000 0.8235\n14000 0.8235\n16000 0.8235\n18000 0.8235\n20000 0.8235")
c.o('''
Q_sao = q_tu_v(V)                                           # V của trang 2 là V*, nên đây là Q*
print(np.abs(Q_05 - Q_sao).max().round(3))                  # sai lệch lớn nhất
print(Q_05[0].round(3), Q_sao[0].round(3))                  # ô xuất phát
print(Q_05[14].round(3), Q_sao[14].round(3))                # ô sát đích
''', "0.207\n[0.549 0.536 0.523 0.524] [0.542 0.528 0.528 0.522]\n[0.715 0.867 0.757 0.811] [0.733 0.863 0.821 0.781]")

c.mo_trang(4, "Bài vách đá: SARSA và Q-learning, mỗi thuật toán 50 lần chạy (khoảng 6 giây).")
c.o('''
vd = gym.make("CliffWalking-v1")                            # lưới 4 x 12, hành động 0 lên, 1 phải, 2 xuống, 3 trái
print(vd.observation_space, vd.action_space)                # 48 ô, 4 hành động
print(vd.unwrapped.P[36][1], vd.unwrapped.P[36][0], vd.unwrapped.P[35][2])   # xuất phát đi phải, đi lên; ô trên đích đi xuống
''', "Discrete(48) Discrete(4)\n[(1.0, np.int64(36), -100, False)] [(1.0, np.int64(24), -1, False)] [(1.0, np.int64(47), -1, True)]")
c.o('''
from collections import Counter                             # đếm
def hoc_vach(cach, n_tap=500, alpha=0.5, eps=0.1, seed=0):  # SARSA hoặc Q-learning trên vách đá
    rng = np.random.default_rng(seed)                       # ngẫu nhiên của tác tử
    Q = np.zeros((48, 4))                                   # bảng Q
    vd.reset(seed=seed)                                     # seed môi trường
    def chon(s):                                            # epsilon-greedy
        return int(rng.integers(4)) if rng.random() < eps else int(Q[s].argmax())   # khám phá hay khai thác
    tong = []                                               # lợi nhuận thực nhận mỗi tập
    for _ in range(n_tap):                                  # mỗi tập
        s, _ = vd.reset()                                   # về ô xuất phát
        a = chon(s)                                         # hành động đầu
        G = 0                                               # cộng dồn phần thưởng
        while True:                                         # mỗi bước
            s2, r, ket_thuc, cat_ngang, _ = vd.step(a)      # làm a
            G += r                                          # cộng thưởng
            a2 = chon(s2)                                   # hành động sẽ làm ở bước sau
            if ket_thuc:                                    # tới đích
                muc_tieu = r                                # không còn gì phía sau
            elif cach == "sarsa":                           # SARSA
                muc_tieu = r + Q[s2, a2]                    # theo hành động sẽ làm, gamma = 1
            else:                                           # Q-learning
                muc_tieu = r + Q[s2].max()                  # theo hành động tốt nhất
            Q[s, a] += alpha * (muc_tieu - Q[s, a])         # cập nhật
            s, a = s2, a2                                   # làm đúng a2 ở bước sau
            if ket_thuc or cat_ngang:                       # hết tập
                break                                       # ra khỏi vòng
        tong.append(G)                                      # ghi lợi nhuận tập này
    return Q, np.array(tong)                                # bảng và điểm số
def duong_tham_lam(Q, toi_da=60):                           # số bước tới đích khi đi tham lam
    s, _ = vd.reset()                                       # về ô xuất phát
    for buoc in range(1, toi_da + 1):                       # tối đa 60 bước
        s, r, ket_thuc, cat_ngang, _ = vd.step(int(Q[s].argmax()))   # đi tham lam
        if ket_thuc:                                        # tới đích
            return buoc                                     # độ dài đường
    return None                                             # kẹt
ket_qua = {}                                                # kết quả hai thuật toán
for cach in ("sarsa", "q"):                                 # hai thuật toán
    ket_qua[cach] = [hoc_vach(cach, seed=k) for k in range(50)]   # 50 lần chạy
    tong = np.array([t for _, t in ket_qua[cach]])          # 50 x 500 lợi nhuận
    print(cach, tong[:, -100:].mean().round(1), Counter(duong_tham_lam(Q) for Q, _ in ket_qua[cach]))   # điểm 100 tập cuối, độ dài đường tham lam
''', "sarsa -25.7 Counter({17: 38, None: 8, 19: 4})\nq -48.5 Counter({13: 50})",
    khung("doc", ["Q-learning học đúng đường 13 bước ở cả 50 lần chạy nhưng trong lúc học chỉ được -48,5 mỗi tập, vì đi sát mép vực mà vẫn chọn bừa 10% số bước. SARSA tính cả những bước bừa đó vào giá trị, nên đi vòng xa vực và được -25,7."]))

c.mo_trang(5, "Ba bài tập. Đoán trước, rồi mới mở đáp án.")
c.bai("34.1", "Không chiết khấu thì sao", "Chạy Q-learning với epsilon 0,5 nhưng gamma = 1.",
      "Chạm 82,35% rồi sụp về 0%: hàng trên cùng chọn đi lên, tác tử đi lòng vòng mãi vì lần lữa không bị phạt. Q ở ô 0 là 0,876, cao hơn mức 0,8235 mà không chính sách nào vượt được: phép max đánh giá quá cao. Code ở ô ngay dưới.")
c.o('''
Q_g1 = q_learning(20_000, eps=0.5, gamma=1.0)               # không chiết khấu
print(Q_g1.argmax(1).reshape(4, 4))                         # chính sách tham lam cuối
print(Q_g1[:4].round(3))                                    # Q của hàng trên cùng
''', "2000 0.625\n4000 0.8235\n6000 0.8235\n8000 0.0\n10000 0.0\n12000 0.0\n14000 0.0\n16000 0.0\n18000 0.0\n20000 0.0\n[[3 3 3 3]\n [0 0 2 0]\n [3 1 0 0]\n [0 2 1 0]]\n[[0.875 0.875 0.875 0.876]\n [0.757 0.605 0.512 0.876]\n [0.809 0.812 0.743 0.876]\n [0.594 0.577 0.583 0.876]]")
c.bai("34.2", "Hồ lớn hơn", "Value iteration trên FrozenLake 8 x 8, rồi xác suất tới đích khi không giới hạn bước và khi chỉ có 100 bước.",
      "662 vòng; 89,4% nếu không giới hạn, chỉ 63,2% trong 100 bước vì chính sách an toàn đi rất chậm. Code ở ô ngay dưới.")
c.o('''
env8 = gym.make("FrozenLake-v1", map_name="8x8")            # hồ 8 x 8
n = 64                                                      # số trạng thái
T8, R8 = np.zeros((n, 4, n)), np.zeros((n, 4))              # bảng chuyển và thưởng
for s in range(n):                                          # mỗi trạng thái
    for a in range(4):                                      # mỗi hành động
        for p, s2, r, xong in env8.unwrapped.P[s][a]:       # mỗi khả năng
            T8[s, a, s2] += p                               # cộng dồn
            R8[s, a] += p * r                               # thưởng kỳ vọng
cuoi8 = [s for s, o in enumerate(env8.unwrapped.desc.astype(str).flatten()) if o in "HG"]   # hố và đích
V8 = np.zeros(n)                                            # value iteration từ 0
for k in range(1, 5001):                                    # tối đa 5000 vòng
    Q8 = R8 + GAMMA * T8 @ V8                               # T8 @ V8 có dạng (64, 4)
    Q8[cuoi8] = 0                                           # trạng thái kết thúc
    chenh = np.abs(Q8.max(1) - V8).max()                    # thay đổi lớn nhất
    V8 = Q8.max(1)                                          # cập nhật
    if chenh < 1e-10:                                       # hội tụ
        break                                               # dừng
pi8 = Q8.round(10).argmax(1)                                # chính sách tối ưu
P8, R8_pi = T8[np.arange(n), pi8], R8[np.arange(n), pi8].copy()   # một bước theo chính sách đó
P8[cuoi8] = 0                                               # kết thúc
R8_pi[cuoi8] = 0                                            # không thưởng
def toi_dich(so_buoc):                                      # xác suất tới đích trong so_buoc bước
    V = np.zeros(n)                                         # 0 bước
    for _ in range(so_buoc):                                # thêm từng bước
        V = R8_pi + P8 @ V                                  # một bước nữa
    return round(V[0], 4)                                   # từ ô xuất phát
print(len(cuoi8), k, round(V8[0], 4), toi_dich(10_000), toi_dich(100))   # số ô kết thúc, số vòng, V*(0), không giới hạn, 100 bước
''', "11 662 0.4146 0.8938 0.6317")
c.bai("34.3", "Khám phá ít đi", "Bài vách đá với epsilon 0,01, vẫn 50 lần mỗi thuật toán.",
      "SARSA -16,9, Q-learning -16,3: khoảng cách gần biến mất, và SARSA dịch lại gần vực (đường 15 bước). Code ở ô ngay dưới.")
c.o('''
for cach in ("sarsa", "q"):                                 # hai thuật toán
    kq = [hoc_vach(cach, seed=k, eps=0.01) for k in range(50)]   # 50 lần chạy, khám phá 1%
    tong = np.array([t for _, t in kq])                     # lợi nhuận thực nhận
    print(cach, tong[:, -100:].mean().round(1), Counter(duong_tham_lam(Q) for Q, _ in kq))   # điểm và đường tham lam
''', "sarsa -16.9 Counter({15: 31, 17: 18, None: 1})\nq -16.3 Counter({13: 50})")

c.ghi(Path(__file__).resolve().parents[2] / "notebooks/ch34_q_learning.ipynb")
