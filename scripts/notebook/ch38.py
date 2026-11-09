"""Dựng notebooks/ch38_tong_quan_nlp.ipynb: python3 scripts/notebook/ch38.py"""
from pathlib import Path
from nblib import Chuong, code, khung

c = Chuong(38, "Tổng quan NLP và tiền xử lý tiếng Việt", "ch38-tong-quan-nlp",
           "Mở đầu Phần IV: tải bộ phản hồi sinh viên UIT-VSFC, chuẩn hóa Unicode và vị trí dấu thanh, tách từ bằng underthesea, đếm từ vựng, thấy luật Zipf và cái giá của việc bỏ stopword.",
           ["Thấy vì sao hai chữ trông giống hệt mà máy coi là khác, và chuẩn hóa NFC, NFKC, kiểu đặt dấu.",
            "Tách từ tiếng Việt bằng underthesea, so âm tiết với từ.",
            "Tìm từ ghép chỉ bằng đếm (PMI).",
            "Đo luật Zipf, tỷ lệ từ ngoài từ vựng, và tác hại của bỏ stopword trên dữ liệu thật."],
           [("NLP là gì", "01-nlp-la-gi"), ("Unicode và chuẩn hóa", "02-unicode-va-chuan-hoa"), ("Tách từ tiếng Việt", "03-tach-tu"),
            ("Từ vựng và luật Zipf", "04-tu-vung-va-zipf"), ("Bài tập", "05-bai-tap")],
           thoi_gian="khoảng 1 phút")

c.mo_trang(1, "Tải UIT-VSFC và nhìn dữ liệu.")
c.cells.append(code('''
!pip install -q underthesea                                 # thư viện xử lý tiếng Việt
'''))
c.o('''
import os                                                   # đường dẫn
import re                                                   # biểu thức chính quy
import unicodedata                                          # chuẩn hóa Unicode
import urllib.request                                       # tải tệp
from collections import Counter                             # đếm
import numpy as np                                          # mảng
import pandas as pd                                         # bảng
URL = "https://huggingface.co/api/datasets/uitnlp/vietnamese_students_feedback/parquet/default/{}/0.parquet"   # tệp parquet trên Hugging Face
THU_MUC = os.path.expanduser("~/.cache/vsfc")               # lưu tạm
def tai(phan):                                              # tải một lần, lần sau đọc từ ổ đĩa
    os.makedirs(THU_MUC, exist_ok=True)                     # tạo thư mục
    tep = os.path.join(THU_MUC, phan + ".parquet")          # đường dẫn tệp
    if not os.path.exists(tep):                             # chưa có thì tải
        urllib.request.urlretrieve(URL.format(phan), tep)   # tải về
    return pd.read_parquet(tep)                             # đọc thành DataFrame
tr, va, te = tai("train"), tai("validation"), tai("test")   # ba phần chia sẵn của tác giả
print(len(tr), len(va), len(te), list(tr.columns))          # cỡ và các cột
print(tr.sentiment.value_counts().sort_index().tolist(), tr.topic.value_counts().sort_index().tolist())   # số câu theo nhãn
''', "11426 1583 3166 ['sentence', 'sentiment', 'topic']\n[5325, 458, 5643] [8166, 2201, 497, 562]")
c.o('''
for i in (0, 3, 6, 7):                                      # bốn câu
    print(tr.sentiment[i], tr.topic[i], tr.sentence[i])     # cảm xúc, chủ đề, câu
''', "2 1 slide giáo trình đầy đủ .\n0 0 chưa áp dụng công nghệ thông tin và các thiết bị hỗ trợ cho việc giảng dạy .\n1 3 em sẽ nợ môn này , nhưng em sẽ học lại ở các học kỳ kế tiếp .\n0 1 thời lượng học quá dài , không đảm bảo tiếp thu hiệu quả .",
    khung("doc", ["Dữ liệu đã qua xử lý một phần: chữ thường, dấu câu tách riêng, tên giảng viên thay bằng mã như wzjwz208."]))

c.mo_trang(2, "NFC, NFKC và vị trí dấu thanh.")
c.o('''
a = "Hòa"                                                   # dạng dựng sẵn
b = unicodedata.normalize("NFD", a)                         # tách thành chữ gốc cộng dấu tổ hợp
print(a == b, len(a), len(b), [hex(ord(c)) for c in b])     # khác nhau dù trông giống hệt
print(a == unicodedata.normalize("NFC", b))                 # gộp lại thì bằng
''', "False 3 4 ['0x48', '0x6f', '0x300', '0x61']\nTrue")
c.o('''
print("Đà Nẵng".lower(), "ＡＩ２０２６".lower(), unicodedata.normalize("NFKC", "ＡＩ２０２６"))   # chữ thường và ký tự toàn khổ
''', "đà nẵng ａｉ２０２６ AI2026")
c.o('''
print("hoà" == "hòa", unicodedata.normalize("NFC", "hoà") == "hòa")   # NFC không sửa được vị trí dấu
''', "False False")
c.o('''
CU_MOI = {"oà": "òa", "oá": "óa", "oả": "ỏa", "oã": "õa", "oạ": "ọa",   # vần oa: kiểu cũ sang kiểu mới
          "oè": "òe", "oé": "óe", "oẻ": "ỏe", "oẽ": "õe", "oẹ": "ọe",   # vần oe
          "uỳ": "ùy", "uý": "úy", "uỷ": "ủy", "uỹ": "ũy", "uỵ": "ụy"}   # vần uy; chỉ đổi khi không có âm cuối
mau = re.compile(r"(?<!q)(" + "|".join(CU_MOI) + r")(?!\\w)")   # bỏ qua sau q; không có chữ cái đứng sau
def dau_moi(s):                                             # đổi kiểu đặt dấu cũ sang mới
    return mau.sub(lambda m: CU_MOI[m.group(1)], s)         # thay từng chỗ khớp
print([dau_moi(w) for w in ["hoà", "thuý", "quý", "khoẻ", "hoàng", "hoà bình", "loè loẹt", "Quỳnh"]])   # thử các trường hợp
''', "['hòa', 'thúy', 'quý', 'khỏe', 'hoàng', 'hòa bình', 'lòe loẹt', 'Quỳnh']")
c.o('''
tat_ca = pd.concat([tr, va, te]).sentence                   # mọi câu
cu = tat_ca[tat_ca.map(lambda s: dau_moi(s) != s)]          # câu có kiểu dấu cũ
khac = Counter(w for s in cu for w in s.split() if dau_moi(w) != w)   # các chữ kiểu cũ
print(len(cu), khac.most_common(5))                         # số câu, chữ hay gặp
print(Counter(w for s in tat_ca for w in s.split() if w in {dau_moi(x) for x in khac}).most_common(5))   # cùng chữ viết kiểu mới
''', "39 [('hoà', 15), ('khoá', 14), ('hoạ', 8), ('hoá', 4), ('thoả', 1)]\n[('hòa', 94), ('họa', 52), ('khóa', 48), ('hóa', 15), ('thỏa', 6)]")

c.mo_trang(3, "Tách từ bằng underthesea và tìm từ ghép bằng PMI.")
c.o('''
from underthesea import word_tokenize                       # tách từ tiếng Việt
print(word_tokenize("Bác sĩ khám bệnh cho bệnh nhân"))      # từ ghép
print(word_tokenize("Ông già đi nhanh quá"))                # câu mơ hồ
print(word_tokenize("học sinh học sinh học", format="text"))   # nối âm tiết bằng gạch dưới
''', "['Bác sĩ', 'khám', 'bệnh', 'cho', 'bệnh nhân']\n['Ông già', 'đi', 'nhanh', 'quá']\nhọc_sinh học_sinh học")
c.o('''
import time                                                 # đo thời gian
t0 = time.time()                                            # bắt đầu
tu_tr = [word_tokenize(c) for c in tr.sentence]             # tách từ cả tập train
giay = time.time() - t0                                     # số giây
am_tiet_tr = [c.split() for c in tr.sentence]               # cắt theo dấu cách: âm tiết
n_am_tiet, n_tu = sum(map(len, am_tiet_tr)), sum(map(len, tu_tr))   # số token hai mức
dem_am_tiet = Counter(x for c in am_tiet_tr for x in c)     # từ vựng âm tiết
dem_tu = Counter(x for c in tu_tr for x in c)               # từ vựng từ
print(n_am_tiet, n_tu, round(n_am_tiet / n_tu, 3), len(dem_am_tiet), len(dem_tu), giay < 30)   # so hai mức
print([w for w, _ in dem_tu.most_common(40) if " " in w])   # từ ghép trong 40 từ đầu
''', "163492 127413 1.283 2514 4009 True\n['sinh viên', 'nhiệt tình', 'giảng viên', 'bài tập', 'giảng dạy', 'kiến thức', 'thực hành', 'môn học']")
c.o('''
import math                                                 # log
d1 = Counter(x for c in am_tiet_tr for x in c)              # đếm âm tiết
d2 = Counter((a, b) for c in am_tiet_tr for a, b in zip(c, c[1:]))   # đếm cặp liền nhau
N1, N2 = sum(d1.values()), sum(d2.values())                 # tổng
def pmi(a, b):                                              # cặp dính nhau hơn mức tình cờ bao nhiêu
    return math.log2((d2[(a, b)] / N2) / ((d1[a] / N1) * (d1[b] / N1)))   # log2 P(ab) / P(a)P(b)
cap = sorted(((round(pmi(a, b), 2), a + " " + b) for (a, b), n in d2.items()
              if n >= 20 and a.isalpha() and b.isalpha()), reverse=True)   # chỉ cặp gặp ít nhất 20 lần
print(cap[:8])                                              # tám cặp đầu
top30 = [w for _, w in cap[:30]]                            # 30 cặp đầu
print(sum(w in dem_tu for w in top30), [w for w in top30 if w not in dem_tu])   # trùng với từ của underthesea
''', "[(12.72, 'tinh thần'), (12.67, 'khô khan'), (12.61, 'đơn giản'), (12.57, 'sẵn sàng'), (12.38, 'mơ hồ'), (12.38, 'giới thiệu'), (12.28, 'ảnh hưởng'), (12.27, 'trách nhiệm')]\n29 ['sở vật']")

c.mo_trang(4, "Luật Zipf, tốc độ tăng từ vựng, OOV và stopword.")
c.o('''
print(dem_tu.most_common(12))                               # 12 từ thường gặp nhất
f = np.array(sorted(dem_tu.values(), reverse=True))         # tần suất theo hạng
print(round(f[:10].sum() / f.sum(), 3), round(f[:100].sum() / f.sum(), 3), int((f == 1).sum()))   # phần của 10, 100 từ đầu; số từ gặp 1 lần
''', "[('.', 11009), (',', 6836), ('thầy', 3039), ('sinh viên', 2697), ('dạy', 2155), ('và', 2068), ('không', 2033), ('rất', 1961), ('nhiệt tình', 1839), ('cho', 1713), ('có', 1695), ('hiểu', 1654)]\n0.277 0.677 1932")
c.o('''
hang = np.arange(1, len(f) + 1)                             # hạng 1, 2, 3...
giua = (hang >= 10) & (hang <= 1000)                        # bỏ hai đầu
print(np.polyfit(np.log(hang[giua]), np.log(f[giua]), 1).round(3))   # độ dốc trên trục log-log
''', "[-1.387 11.744]")
c.o('''
da_gap, n, diem = set(), 0, []                              # từ đã gặp, số token, các điểm
for c in tu_tr:                                             # đi dần qua tập train
    for x in c:                                             # mỗi token
        n += 1                                              # đếm token
        da_gap.add(x)                                       # thêm vào từ vựng
    diem.append((n, len(da_gap)))                           # ghi lại sau mỗi câu
print([diem[k - 1] for k in (1000, 3000, 6000, 11426)])     # (số token, số từ khác nhau)
''', "[(11075, 1236), (33107, 2079), (66621, 2896), (127413, 4009)]")
c.o('''
tu_te = [word_tokenize(c) for c in te.sentence]             # tách từ tập test
am_tiet_te = [c.split() for c in te.sentence]               # âm tiết tập test
oov = lambda ds, tu_vung: sum(x not in tu_vung for c in ds for x in c) / sum(map(len, ds))   # tỷ lệ token không có trong từ vựng
print(round(oov(am_tiet_te, dem_am_tiet), 4), round(oov(tu_te, dem_tu), 4))   # âm tiết, từ
''', "0.0065 0.0156")
c.o('''
tieu_cuc, tich_cuc = tr[tr.sentiment == 0].sentence, tr[tr.sentiment == 2].sentence   # hai nhóm cảm xúc
print(round(tieu_cuc.str.contains(r"\\bkhông\\b").mean(), 3), round(tich_cuc.str.contains(r"\\bkhông\\b").mean(), 3))   # tỷ lệ câu có "không"
''', "0.28 0.041",
    khung("loi", ["\"Không\" có trong 28% câu tiêu cực và 4,1% câu tích cực. Danh sách stopword có sẵn thường có từ này: bỏ đi là bỏ đúng tín hiệu cần nhất."], "BỎ STOPWORD"))

c.mo_trang(5, "Ba bài tập. Đoán trước, rồi mới mở đáp án.")
c.bai("38.1", "Một hàm làm sạch", "NFKC, chữ thường, đặt dấu kiểu mới, tách dấu câu, gộp khoảng trắng; thử trên một câu bẩn.",
      "68 ký tự thành 58; hoà, khoẻ về kiểu mới, số toàn khổ về số thường. Thứ tự các bước là then chốt. Code ở ô ngay dưới.")
c.o('''
def lam_sach(s):                                            # làm sạch theo đúng thứ tự
    s = unicodedata.normalize("NFKC", s)                    # 1. dạng chuẩn, kể cả ký tự toàn khổ
    s = s.lower()                                           # 2. chữ thường
    s = dau_moi(s)                                          # 3. đặt dấu kiểu mới
    s = re.sub(r"([.,!?;:()])", r" \\1 ", s)                # 4. tách dấu câu
    return re.sub(r"\\s+", " ", s).strip()                  # 5. gộp khoảng trắng
ban = unicodedata.normalize("NFD", "Thầy HOÀ dạy môn Toán ２ rất hay,dễ hiểu!!") + "  Khoẻ   không?"   # câu bẩn cố ý
print(len(ban), [lam_sach(ban)], len(lam_sach(ban)))        # trước và sau
print(lam_sach(ban).split() == word_tokenize(lam_sach(ban)))   # âm tiết có trùng với từ không
''', "68 ['thầy hòa dạy môn toán 2 rất hay , dễ hiểu ! ! khỏe không ?'] 58\nFalse")
c.bai("38.2", "Chọn cỡ từ vựng", "Giữ từ gặp ít nhất k lần, với k = 1, 2, 5.",
      "k = 2 cắt từ vựng gần một nửa (4009 xuống 2077) mà OOV chỉ tăng từ 1,56% lên 2,29%. Code ở ô ngay dưới.")
c.o('''
for k in (1, 2, 5):                                         # ba ngưỡng
    tu_vung = {w for w, n in dem_tu.items() if n >= k}      # từ đủ thường
    print(k, len(tu_vung), round(oov(tu_te, tu_vung), 4))   # cỡ từ vựng, OOV trên test
''', "1 4009 0.0156\n2 2077 0.0229\n5 1217 0.0371")
c.bai("38.3", "Cái giá của stopword", "Bỏ 15 stopword rồi đếm câu thành giống hệt một câu mang nhãn cảm xúc ngược lại.",
      "Không bỏ: 1 câu (lỗi nhãn sẵn có). Bỏ 15 stopword: 20 câu, vì 'không' đã bị xóa. Code ở ô ngay dưới.")
c.o('''
from collections import defaultdict                         # dict có giá trị mặc định
STOP = {"và", "của", "thì", "là", "không", "rất", "cho", "có", "được", "các", "những", "với", "này", ".", ","}   # danh sách hay gặp
def xung_dot(bo):                                           # câu giống hệt nhau mà có cả nhãn 0 và 2
    nhom = defaultdict(set)                                 # câu sau khi bỏ, tập nhãn
    for c, y in zip(tr.sentence, tr.sentiment):             # mọi câu train
        nhom[" ".join(w for w in word_tokenize(c) if w not in bo)].add(y)   # bỏ stopword rồi gom
    return [k for k, v in nhom.items() if {0, 2} <= v]      # có cả tiêu cực lẫn tích cực
print(len(xung_dot(set())), len(xung_dot(STOP)), xung_dot(STOP)[:6])   # không bỏ, có bỏ
''', "1 20 ['nhiệt tình sinh viên', 'thầy vui tính', 'thầy dạy hiệu quả', 'nhàm chán', 'thầy dạy tâm', 'giảng viên nhiệt tình tận tâm']")

c.ghi(Path(__file__).resolve().parents[2] / "notebooks/ch38_tong_quan_nlp.ipynb")
