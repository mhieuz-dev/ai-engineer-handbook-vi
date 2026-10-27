"""Dựng notebooks/ch07_xac_suat_thong_ke.ipynb: python3 scripts/notebook/ch07.py"""
from pathlib import Path
from nblib import Chuong, khung

c = Chuong(7, "Xác suất và thống kê", "ch07-xac-suat-thong-ke",
           "Mô phỏng, phân phối chuẩn, tương quan, định lý Bayes và hợp lý cực đại: nền thống kê để hiểu vì sao các hàm mất mát có dạng như vậy.",
           ["Mô phỏng hiện tượng ngẫu nhiên và thấy luật số lớn.",
            "Kiểm quy tắc 68-95-99,7 và lý do phương sai mẫu chia n - 1.",
            "Tính tương quan, giải bài toán xét nghiệm bằng Bayes.",
            "Tìm tham số bằng hợp lý cực đại và thấy MSE từ đâu ra."],
           [("Xác suất và mô phỏng", "01-xac-suat-va-mo-phong"), ("Phân phối chuẩn và phương sai mẫu", "02-phan-phoi-chuan"),
            ("Tương quan và định lý Bayes", "03-tuong-quan-va-bayes"), ("Ước lượng hợp lý cực đại", "04-hop-ly-cuc-dai"), ("Bài tập", "05-bai-tap")],
           runtime="CPU là đủ, không cần GPU. Output chạy với NumPy 2.5; bản khác có thể cho số ngẫu nhiên hơi khác")

c.mo_trang(1, "Tung đồng xu và xúc xắc bằng máy.")
c.o('''
import numpy as np                           # thư viện tính toán
rng = np.random.default_rng(0)               # seed 0 để chạy lại ra đúng kết quả
tung = rng.integers(0, 2, size=10000)        # 0 là sấp, 1 là ngửa
for n in [10, 100, 1000, 10000]:             # nhìn tỷ lệ sau n lần đầu
    print(n, tung[:n].mean())                # trung bình của 0 và 1 là tỷ lệ số 1
''', "10 0.4\n100 0.56\n1000 0.537\n10000 0.503",
    khung("doc", ["Càng tung nhiều, tỷ lệ càng sát 0,5: luật số lớn. 10 lần đầu chỉ ra 0,4, lệch xa nhất."]))
c.o('''
rng = np.random.default_rng(3)               # seed khác cho xúc xắc
xx = rng.integers(1, 7, size=60000)          # 60 000 lần tung, mặt từ 1 tới 6
print(round(xx.mean(), 4), round(xx.var(), 4), 35 / 12)   # so với kỳ vọng 3,5 và phương sai 35/12
''', "3.4955 2.9232 2.9166666666666665")

c.mo_trang(2, "Quy tắc 68-95-99,7 và phương sai mẫu.")
c.o('''
rng = np.random.default_rng(1)                   # seed cho phân phối chuẩn
z = rng.normal(0, 1, size=100000)                # 100 000 mẫu từ N(0, 1)
for k in [1, 2, 3]:                              # trong 1, 2, 3 độ lệch chuẩn
    print(k, round(np.mean(np.abs(z) < k), 4))   # tỷ lệ mẫu nằm trong khoảng
print(round(z.mean(), 4), round(z.std(), 4))     # gần 0 và 1
''', "1 0.6841\n2 0.955\n3 0.9971\n-0.0046 0.9965")
c.o('''
rng = np.random.default_rng(2)                    # seed cho thí nghiệm phương sai mẫu
mau = rng.normal(0, 2, size=(100000, 4))          # 100 000 mẫu, mỗi mẫu 4 số; phương sai thật = 4
print(round(mau.var(axis=1, ddof=0).mean(), 4))   # chia n: trung bình khoảng 3
print(round(mau.var(axis=1, ddof=1).mean(), 4))   # chia n - 1: trung bình khoảng 4
''', "3.0049\n4.0066",
    khung("vi-sao", ["Chia n cho trung bình bằng (n - 1)/n lần giá trị thật: 3/4 × 4 = 3. Chia n - 1 sửa được độ chệch đó."],
          nhan="VÌ SAO LẠI LÀ 3 CHỨ KHÔNG PHẢI 4?"))

c.mo_trang(3, "Hiệp phương sai, tương quan, xét nghiệm dương tính.")
c.o('''
x = np.array([1, 2, 3, 4.0])                         # giờ học của A, B, C, D
y = np.array([2, 4, 5, 7.0])                         # điểm thi
cov = np.mean((x - x.mean()) * (y - y.mean()))       # hiệp phương sai (7.4)
print(cov, round(cov / (x.std() * y.std()), 4))      # và tương quan (7.5)
print(round(np.corrcoef(x, y)[0, 1], 4))             # hàm có sẵn
p_benh, nhay, dac_hieu = 0.01, 0.99, 0.95            # tỷ lệ bệnh, độ nhạy, độ đặc hiệu
p_duong = nhay * p_benh + (1 - dac_hieu) * (1 - p_benh)   # P(dương tính)
print(round(p_duong, 4), round(nhay * p_benh / p_duong, 4))  # Bayes: chỉ khoảng 17%
''', "2.0 0.9923\n0.9923\n0.0594 0.1667",
    khung("truc-giac", ["Trong 10 000 người: 99 người bệnh ra dương tính, 495 người khỏe dương tính nhầm. Chỉ 99 trên 594 người dương tính là có bệnh."]))

c.mo_trang(4, "Hợp lý cực đại cho đồng xu.")
c.o('''
p = np.linspace(0.01, 0.99, 99)                 # thử 99 giá trị p
ll = 7 * np.log(p) + 3 * np.log(1 - p)          # log-likelihood của 7 ngửa 3 sấp
print(p[np.argmax(ll)], round(ll.max(), 4))     # p tốt nhất và giá trị cực đại
print(round(10 * np.log(0.5), 4))               # so sánh với đồng xu cân
''', "0.7000000000000001 -6.1086\n-6.9315",
    khung("loi", ["<b>Tính likelihood bằng tích trực tiếp.</b> Tích hàng nghìn xác suất nhỏ tràn dưới thành 0. Luôn dùng log-likelihood."]))

c.mo_trang(5, "Ba bài tập. Tính tay trước, rồi mới mở đáp án.")
c.bai("7.1", "Tổng hai xúc xắc", "Tính tay xác suất tổng hai xúc xắc bằng 7, rồi mô phỏng 100 000 lần.",
      "6 cách trên 36: $1/6 \\approx 0{,}1667$. Mô phỏng ra 0,1672. Code ở ô ngay dưới.")
c.o('''
rng = np.random.default_rng(4)            # seed của bài tập
a = rng.integers(1, 7, size=100000)       # xúc xắc thứ nhất
b = rng.integers(1, 7, size=100000)       # xúc xắc thứ hai
print(round(np.mean(a + b == 7), 4), round(6 / 36, 4))   # mô phỏng và lý thuyết
''', "0.1672 0.1667")
c.bai("7.2", "Xét nghiệm lần hai", "Sau lần đầu dương tính, xét nghiệm lại và lại dương tính. Xác suất có bệnh là bao nhiêu?",
      "Kết quả lần một ($1/6$) thành tỷ lệ nền cho lần hai. Ra khoảng 0,7984. Code ở ô ngay dưới.")
c.o('''
truoc = nhay * p_benh / p_duong                               # sau lần một: khoảng 1/6
p_duong_2 = nhay * truoc + (1 - dac_hieu) * (1 - truoc)       # P(dương tính lần hai)
print(round(nhay * truoc / p_duong_2, 4))                     # Bayes lần hai
''', "0.7984")
c.bai("7.3", "Hợp lý cực đại cho trung bình", "Với điểm 2, 4, 5, 7 từ $\\mathcal N(\\mu, \\sigma^2)$, tìm $\\hat\\mu$ bằng đạo hàm, rồi thử 301 giá trị $\\mu$.",
      "$\\hat\\mu = \\bar y = 4{,}5$. Hợp lý cực đại cho phương sai là chia $n$: 3,25. Code ở ô ngay dưới.")
c.o('''
mu = np.linspace(3, 6, 301)                          # 301 giá trị cách nhau 0,01
ll = [-np.sum((y - m) ** 2) for m in mu]             # log-likelihood, bỏ hằng số
print(mu[np.argmax(ll)], y.mean(), y.var())          # trùng trung bình mẫu
''', "4.5 4.5 3.25")

c.ghi(Path(__file__).resolve().parents[2] / "notebooks/ch07_xac_suat_thong_ke.ipynb")
