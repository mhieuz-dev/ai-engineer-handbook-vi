"""Dựng notebooks/ch04_pandas_va_matplotlib.ipynb: python3 scripts/notebook/ch04.py"""
from pathlib import Path
from nblib import Chuong, khung

c = Chuong(4, "Pandas và Matplotlib", "ch04-pandas-va-matplotlib",
           "Đọc, làm sạch, gộp nhóm một bảng dữ liệu, rồi vẽ ba biểu đồ nên vẽ đầu tiên với mọi bộ dữ liệu mới.",
           ["Đọc CSV thành DataFrame, xem nhanh bằng head, dtypes, describe.",
            "Chọn cột, lọc hàng bằng loc, điền giá trị thiếu, tạo cột mới.",
            "So sánh nhóm bằng groupby, đo tương quan bằng corr.",
            "Vẽ và đọc biểu đồ chấm, histogram, biểu đồ cột."],
           [("DataFrame đầu tiên", "01-dataframe"), ("Chọn, lọc và tạo cột", "02-chon-loc-va-cot-moi"),
            ("Gộp nhóm, sắp xếp và tương quan", "03-gop-nhom-va-sap-xep"), ("Vẽ biểu đồ với Matplotlib", "04-ve-bieu-do"), ("Bài tập", "05-bai-tap")])

c.mo_trang(1, "Tạo file dữ liệu 10 sinh viên, đọc thành DataFrame và tóm tắt.")
c.o('''
import pandas as pd                       # quy ước: đặt tên ngắn là pd
import numpy as np                        # dùng ở bài tập
import matplotlib.pyplot as plt           # vẽ biểu đồ ở trang 4
hang = ["ten,lop,gio,ngu,diem",           # dòng tiêu đề
        "A,L1,1,7,2", "B,L1,2,6,4",       # Bảng 4.1, hai bạn mỗi dòng
        "C,L1,3,8,5", "D,L1,4,7,7",       # bốn bạn đầu như các chương trước
        "E,L2,5,6,6", "F,L2,2,,3.5",      # bạn F để trống giờ ngủ
        "G,L2,6,8,8.5", "H,L2,3,5,4",     # lớp L2
        "I,L1,7,7,9", "K,L2,4,6,6.5"]     # hai bạn cuối
noi_dung = "\\n".join(hang) + "\\n"         # nối các dòng bằng ký tự xuống dòng
with open("lop10.csv", "w", encoding="utf-8") as f:   # ghi ra file như một file CSV thật
    f.write(noi_dung)                     # ghi nội dung
df = pd.read_csv("lop10.csv")             # đọc cả file thành một bảng
print(df.head(3))                         # 3 hàng đầu
print(df.shape)                           # (số hàng, số cột)
''', "  ten lop  gio  ngu  diem\n0   A  L1    1  7.0   2.0\n1   B  L1    2  6.0   4.0\n2   C  L1    3  8.0   5.0\n(10, 5)")
c.o('''
print(df.dtypes)                 # kiểu của từng cột
print(df.describe().round(2))    # thống kê cho mọi cột số
''', "ten         str\nlop         str\ngio       int64\nngu     float64\ndiem    float64\ndtype: object\n         gio   ngu   diem\ncount  10.00  9.00  10.00\nmean    3.70  6.67   5.55\nstd     1.89  1.00   2.25\nmin     1.00  5.00   2.00\n25%     2.25  6.00   4.00\n50%     3.50  7.00   5.50\n75%     4.75  7.00   6.88\nmax     7.00  8.00   9.00",
    khung("doc", ["Cột <code>ngu</code> thành float64 và count chỉ có 9: dấu hiệu của một ô thiếu.",
                  "Output chạy với pandas 3.1, cột chữ ghi là <code>str</code>. Với pandas 2 (có thể là bản trên Colab), cột chữ ghi là <code>object</code>, cùng nghĩa."]))

c.mo_trang(2, "Chọn cột, lọc hàng, điền giá trị thiếu, tạo cột mới.")
c.o('''
print(df["diem"].mean(), type(df["diem"]).__name__)       # một cột là một Series
print(df[["ten", "diem"]].head(2))                        # nhiều cột: truyền một list
print(df.loc[df["diem"] >= 6, ["ten", "lop", "diem"]])    # lọc hàng, chọn cột
''', "5.55 Series\n  ten  diem\n0   A   2.0\n1   B   4.0\n  ten lop  diem\n3   D  L1   7.0\n4   E  L2   6.0\n6   G  L2   8.5\n8   I  L1   9.0\n9   K  L2   6.5")
c.o('''
print(df.isna().sum())                              # đếm ô thiếu từng cột
df["ngu"] = df["ngu"].fillna(df["ngu"].median())    # điền bằng trung vị của 9 ô còn lại
print(df.loc[5])                                    # hàng của bạn F
df["dat"] = df["diem"] >= 5                         # cột mới: đạt hay không
print(df[["ten", "diem", "dat"]].tail(3))           # 3 hàng cuối
''', "ten     0\nlop     0\ngio     0\nngu     1\ndiem    0\ndtype: int64\nten       F\nlop      L2\ngio       2\nngu     7.0\ndiem    3.5\nName: 5, dtype: object\n  ten  diem    dat\n7   H   4.0  False\n8   I   9.0   True\n9   K   6.5   True",
    khung("loi", ["<b>Dùng and để ghép điều kiện.</b> Phải dùng <code>&amp;</code>, <code>|</code> và bọc ngoặc từng điều kiện."]))

c.mo_trang(3, "So sánh hai lớp, sắp xếp, đo tương quan.")
c.o('''
print(df.groupby("lop")["diem"].mean())          # trung bình điểm mỗi lớp
bang = df.groupby("lop").agg(                    # nhiều con số cùng lúc
    so_ban=("ten", "count"),                     # đếm số bạn
    diem_tb=("diem", "mean"),                    # trung bình điểm
    gio_tb=("gio", "mean"),                      # trung bình giờ học
)                                                # kết thúc agg
print(bang.round(2))                             # in bảng tóm tắt
''', "lop\nL1    5.4\nL2    5.7\nName: diem, dtype: float64\n     so_ban  diem_tb  gio_tb\nlop                         \nL1        5      5.4     3.4\nL2        5      5.7     4.0")
c.o('''
print(df.sort_values("diem", ascending=False).head(3)[["ten", "diem"]])  # 3 bạn điểm cao nhất
print(round(df["gio"].corr(df["diem"]), 4))   # tương quan giờ học và điểm
print(round(df["ngu"].corr(df["diem"]), 4))   # tương quan giờ ngủ và điểm
print(df["dat"].mean())                       # tỷ lệ bạn đạt
''', "  ten  diem\n8   I   9.0\n6   G   8.5\n3   D   7.0\n0.9566\n0.2936\n0.6",
    khung("vi-sao", ["Tương quan 0,96 không chứng minh học nhiều gây ra điểm cao. Có thể có yếu tố thứ ba, ví dụ thích môn học, đứng sau cả hai."],
          nhan="VÌ SAO TƯƠNG QUAN CAO CHƯA PHẢI NHÂN QUẢ?"))

c.mo_trang(4, "Ba biểu đồ: chấm, histogram, cột.")
c.o('''
fig, ax = plt.subplots(figsize=(6, 4))                       # một hình, một khung vẽ
for lop, mau in [("L1", "#1F5F8B"), ("L2", "#E07A1F")]:      # mỗi lớp một màu
    d = df[df["lop"] == lop]                                 # lọc các bạn của lớp
    ax.scatter(d["gio"], d["diem"], color=mau, label=f"Lớp {lop}")  # mỗi bạn một chấm
    for _, h in d.iterrows():                                # ghi tên cạnh từng chấm
        ax.annotate(h["ten"], (h["gio"], h["diem"]), xytext=(5, -4), textcoords="offset points")  # lệch 5 điểm ảnh
ax.set_xlabel("Giờ tự học mỗi tuần")                         # tên trục ngang
ax.set_ylabel("Điểm thi")                                    # tên trục dọc
ax.legend()                                                  # chú giải màu
plt.show()                                                   # hiện hình
print(len(df), "chấm")                                       # kiểm tra số chấm
''', "10 chấm")
c.o('''
fig, ax = plt.subplots(figsize=(6, 3.5))                     # hình mới
dem, bien, _ = ax.hist(df["diem"], bins=[2, 4, 6, 8, 10])    # đếm số bạn mỗi khoảng
ax.set_xlabel("Điểm thi")                                    # tên trục ngang
ax.set_ylabel("Số bạn")                                      # tên trục dọc
plt.show()                                                   # hiện hình
print(dem)                                                   # chiều cao bốn cột
''', "[2. 3. 3. 2.]",
    khung("doc", ["Mỗi khoảng lấy đầu trái: B và H được đúng 4 điểm nên rơi vào khoảng 4 tới 6. Bốn cột cao 2, 3, 3, 2: điểm dồn ở giữa, khá cân đối."]))
c.o('''
tb = df.groupby("lop")["diem"].mean()       # trung bình mỗi lớp
fig, ax = plt.subplots(figsize=(4.5, 3.2))  # hình mới
cot = ax.bar(tb.index, tb.values, color=["#1F5F8B", "#E07A1F"])  # mỗi lớp một cột
ax.bar_label(cot)                           # ghi giá trị trên đầu cột
ax.set_ylabel("Điểm trung bình")            # tên trục dọc; trục bắt đầu từ 0
plt.show()                                  # hiện hình
print(tb.round(1).tolist())                 # hai giá trị vừa vẽ
''', "[5.4, 5.7]",
    khung("thu", ["<b>1.</b> Thêm <code>ax.set_ylim(5.3, 5.8)</code> trước <code>plt.show()</code>. Chênh lệch giữa hai lớp trông lớn hơn bao nhiêu?",
                  "<b>2.</b> Trong histogram, đổi <code>bins</code> thành <code>10</code> rồi thành <code>2</code>. Hình nào kể đúng câu chuyện nhất?"]))

c.mo_trang(5, "Ba bài tập. Tự viết code trước, rồi mới mở đáp án.")
c.bai("4.1", "Ai học hiệu quả nhất?", "Tạo cột `diem_moi_gio` bằng điểm chia giờ học, in 3 bạn cao nhất.",
      "A và B cùng 2,00, D 1,75. Bạn I (9 điểm) không có mặt vì $9/7 \\approx 1{,}29$. Chia thẳng cho giờ học ngầm giả định 0 giờ thì 0 điểm, nên người học ít được lợi. Code đáp án ở ô ngay dưới.")
c.o('''
d2 = df.copy()                                            # bản sao, để không đổi df
d2["diem_moi_gio"] = (d2["diem"] / d2["gio"]).round(2)    # chia từng hàng
print(d2.sort_values("diem_moi_gio", ascending=False, kind="stable").head(3)[["ten", "gio", "diem", "diem_moi_gio"]])  # stable: bằng nhau thì giữ thứ tự gốc
''', "  ten  gio  diem  diem_moi_gio\n0   A    1   2.0          2.00\n1   B    2   4.0          2.00\n3   D    4   7.0          1.75")
c.bai("4.2", "Hồi quy trên cả lớp", "Lấy `gio`, `diem` thành mảng NumPy, tính $w$ và $b$ bằng nghiệm đóng, so với 1,6 của bốn bạn đầu.",
      "$w \\approx 1{,}1417$, $b \\approx 1{,}3255$. E và K nằm dưới đường dốc 1,6 nên kéo đường thẳng thoải ra. Code đáp án ở ô ngay dưới.")
c.o('''
x = df["gio"].to_numpy(dtype=float)        # Series thành mảng số thực
y = df["diem"].to_numpy()                  # cột điểm thành mảng
w = ((x - x.mean()) * (y - y.mean())).sum() / ((x - x.mean()) ** 2).sum()  # độ dốc
b = y.mean() - w * x.mean()                # hệ số chặn
print(round(w, 4), round(b, 4))            # làm tròn 4 chữ số
''', "1.1417 1.3255")
c.bai("4.3", "Đếm histogram bằng tay", "Không chạy code, liệt kê bạn nào rơi vào từng khoảng 2 tới 4, 4 tới 6, 6 tới 8, 8 tới 10. Rồi chạy ô dưới để kiểm tra.",
      "2 tới dưới 4: A, F. 4 tới dưới 6: B, C, H. 6 tới dưới 8: D, E, K. 8 tới 10: G, I. Bạn đúng ranh giới thuộc khoảng bên phải.")
c.o('''
khoang = pd.cut(df["diem"], bins=[2, 4, 6, 8, 10], right=False)   # right=False: lấy đầu trái
print(df.groupby(khoang, observed=False)["ten"].apply(list))      # tên các bạn trong mỗi khoảng
''', "diem\n[2, 4)        [A, F]\n[4, 6)     [B, C, H]\n[6, 8)     [D, E, K]\n[8, 10)       [G, I]\nName: ten, dtype: object")

c.ghi(Path(__file__).resolve().parents[2] / "notebooks/ch04_pandas_va_matplotlib.ipynb")
