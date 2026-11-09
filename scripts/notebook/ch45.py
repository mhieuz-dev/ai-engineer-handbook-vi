"""Dựng notebooks/ch45_tokenization_pretrained.ipynb: python3 scripts/notebook/ch45.py"""
from pathlib import Path
from nblib import Chuong, code, khung

c = Chuong(45, "Tokenization và mô hình tiền huấn luyện", "ch45-tokenization-pretrained",
           "Đo OOV và độ dài dãy trên UIT-VSFC, tự cài BPE, so tokenizer của PhoBERT, XLM-R, GPT-2, cho PhoBERT đoán từ bị che, rồi dùng PhoBERT đóng băng làm bộ trích đặc trưng cho phân loại cảm xúc.",
           ["Hiểu đánh đổi giữa từ, ký tự và mảnh từ; chuẩn hóa Unicode trước khi cắt.",
            "Tự cài BPE và huấn luyện trên UIT-VSFC.",
            "Đọc đầu ra tokenizer của PhoBERT, XLM-R, GPT-2; đo thuế token của tiếng Việt.",
            "Dùng PhoBERT đoán từ bị che và làm bộ trích đặc trưng đóng băng."],
           [("Cắt văn bản thành đơn vị nào", "01-cat-van-ban"), ("BPE từ đầu", "02-bpe-tu-dau"),
            ("Tokenizer của mô hình thật", "03-tokenizer-cua-mo-hinh-that"), ("Mô hình tiền huấn luyện", "04-mo-hinh-tien-huan-luyen"),
            ("Bài tập", "05-bai-tap")],
           thoi_gian="khoảng 12 phút trên CPU (phần lớn ở trang 4 và bài 45.3); chọn GPU trong Colab sẽ nhanh hơn nhiều")

c.mo_trang(1, "OOV ở mức âm tiết, độ dài dãy theo âm tiết, ký tự, byte, và chuẩn hóa Unicode.")
c.cells.append(code('''
!pip install -q pyarrow underthesea transformers sentencepiece   # đọc parquet, tách từ tiếng Việt, mô hình Hugging Face
'''))
c.o('''
import os                                                   # đường dẫn
import unicodedata                                          # chuẩn hóa Unicode
import urllib.request                                       # tải tệp
from collections import Counter                             # đếm
import numpy as np                                          # mảng
import pandas as pd                                         # bảng
URL = "https://huggingface.co/api/datasets/uitnlp/vietnamese_students_feedback/parquet/default/{}/0.parquet"   # UIT-VSFC
THU_MUC = os.path.expanduser("~/.cache/vsfc")               # lưu tạm
def tai(phan):                                              # tải một lần
    os.makedirs(THU_MUC, exist_ok=True)                     # tạo thư mục
    tep = os.path.join(THU_MUC, phan + ".parquet")          # đường dẫn
    if not os.path.exists(tep):                             # chưa có thì tải
        urllib.request.urlretrieve(URL.format(phan), tep)   # tải về
    return pd.read_parquet(tep)                             # đọc
tr, va, te = tai("train"), tai("validation"), tai("test")   # ba phần
dem = Counter(w for s in tr.sentence for w in s.split())    # tần suất âm tiết trên train
tu = {w for w, n in dem.items() if n >= 2}                  # từ điển âm tiết như Chương 41
am_va = [w for s in va.sentence for w in s.split()]         # âm tiết của val
la = [w for w in am_va if w not in tu]                      # âm tiết lạ
print(len(dem), len(tu), len(am_va), len(la), round(100 * len(la) / len(am_va), 2))   # tỷ lệ lạ (%)
print(Counter(la).most_common(8))                           # âm tiết lạ thường gặp nhất
''', "2514 1533 21642 169 0.78\n[('tạm', 4), ('ngoái', 3), ('centrality', 2), ('bát', 2), ('mập', 2), ('he', 2), ('ngơi', 1), ('rât', 1)]",
    khung("doc", ["Chỉ 0,78% âm tiết của val là lạ; trong số đó có từ tiếng Anh và lỗi gõ."]))
c.o('''
print(round(np.mean([len(s.split()) for s in va.sentence]), 2),   # đơn vị cách nhau bởi dấu cách mỗi câu
      round(np.mean([len(s) for s in va.sentence]), 2),           # ký tự
      round(np.mean([len(s.encode("utf-8")) for s in va.sentence]), 2))   # byte
print([(ch, len(ch.encode("utf-8"))) for ch in "aăệ"])     # số byte UTF-8 của từng chữ
''', "13.67 56.36 73.94\n[('a', 1), ('ă', 2), ('ệ', 3)]")
c.o('''
a, b = unicodedata.normalize("NFC", "tiếng"), unicodedata.normalize("NFD", "tiếng")   # dạng dựng sẵn và dạng tổ hợp
print(a, b, len(a), len(b), a == b)                         # trông giống, nhưng khác chuỗi
print(sum(s != unicodedata.normalize("NFC", s) for s in tr.sentence))   # số câu train chưa ở dạng NFC
''', "tiếng tie\u0302\u0301ng 5 7 False\n0")

c.mo_trang(2, "BPE khoảng 30 dòng, học 3000 lần gộp trên UIT-VSFC (vài giây).")
c.o('''
import time                                                 # đo thời gian
dem = Counter(w for s in tr.sentence for w in s.split())    # tần suất âm tiết trên train
def gop(t, a, b):                                           # gộp mọi cặp (a, b) kề nhau trong dãy t
    ra, i = [], 0                                           # kết quả, vị trí
    while i < len(t):                                       # duyệt dãy
        if i < len(t) - 1 and t[i] == a and t[i + 1] == b:  # gặp cặp cần gộp
            ra.append(a + b)                                # token mới
            i += 2                                          # bỏ qua hai phần tử
        else:                                               # không phải cặp
            ra.append(t[i])                                 # giữ nguyên
            i += 1                                          # sang phần tử sau
    return tuple(ra)                                        # dãy sau khi gộp
def hoc_bpe(dem, so_lan):                                   # học so_lan quy tắc gộp
    tach = {w: tuple(w) + ("_",) for w in dem}              # mỗi từ thành dãy ký tự, thêm dấu cuối từ
    quy_tac = []                                            # danh sách quy tắc theo thứ tự
    for _ in range(so_lan):                                 # mỗi lần gộp
        cap = Counter()                                     # đếm cặp
        for w, n in dem.items():                            # mọi từ
            t = tach[w]                                     # dãy hiện tại của từ
            for a, b in zip(t, t[1:]):                      # các cặp kề nhau
                cap[a, b] += n                              # nhân tần suất từ
        if not cap:                                         # hết cặp
            break                                           # dừng
        (a, b), n = cap.most_common(1)[0]                   # cặp thường gặp nhất
        quy_tac.append((a, b))                              # ghi quy tắc
        tach = {w: gop(t, a, b) for w, t in tach.items()}   # áp lên mọi từ
    return quy_tac                                          # các quy tắc
t0 = time.time()                                            # bắt đầu đo
quy_tac = hoc_bpe(dem, 3000)                                # 3000 lần gộp
print(round(time.time() - t0) < 60, len(quy_tac))           # dưới một phút, số quy tắc
print(quy_tac[:8])                                          # tám lần gộp đầu tiên
print(quy_tac[99], quy_tac[999])                            # lần thứ 100 và 1000
''', "True 3000\n[('n', '_'), ('n', 'g'), ('ng', '_'), ('n', 'h'), ('i', '_'), ('t', 'h'), ('.', '_'), ('c', '_')]\n('t', 'iế') ('qu', 'át_')",
    khung("doc", ["Thuật toán tự tìm ra các phụ âm ghép ng, nh, th; càng về sau càng gộp cả âm tiết."]))
c.o('''
def ma_hoa(w, quy_tac):                                     # cắt một từ bằng các quy tắc đã học
    t = tuple(w) + ("_",)                                   # bắt đầu từ ký tự
    for a, b in quy_tac:                                    # áp theo đúng thứ tự đã học
        if a in t:                                          # bỏ qua nhanh quy tắc không liên quan
            t = gop(t, a, b)                                # gộp
    return t                                                # các mảnh
for w in ["giảng", "nhiệt", "ngoái", "rât", "centrality", "betweenness", "chatgpt"]:   # thường gặp, hiếm, lỗi gõ, tiếng Anh
    print(w, ma_hoa(w, quy_tac))                            # các mảnh
''', "giảng ('giảng_',)\nnhiệt ('nhiệt_',)\nngoái ('ngo', 'ái_')\nrât ('r', 'â', 't_')\ncentrality ('c', 'e', 'n', 'tra', 'li', 'ty_')\nbetweenness ('be', 't', 'we', 'e', 'n', 'ne', 'ss_')\nchatgpt ('cha', 't', 'g', 'p', 't_')")
c.o('''
am_va = [w for s in va.sentence for w in s.split()]         # âm tiết của val
dem_va = Counter(am_va)                                     # tần suất
for k in (0, 100, 500, 1000, 2000, 3000):                   # số lần gộp
    tong = sum(n * len(ma_hoa(w, quy_tac[:k])) for w, n in dem_va.items())   # tổng số token
    print(k, round(tong / len(am_va), 3))                   # token trên mỗi âm tiết
''', "0 4.196\n100 1.96\n500 1.207\n1000 1.056\n2000 1.013\n3000 1.01",
    khung("doc", ["Vài trăm lần gộp đầu cho lợi ích lớn nhất; sau khoảng 1000 lần, gần như mọi âm tiết là một token (hình 45.1 trên web)."]))

c.mo_trang(3, "Tokenizer của PhoBERT, XLM-R, GPT-2 (tải vài MB), thuế token, kiểu bỏ dấu.")
c.o('''
from transformers import AutoTokenizer                      # tải tokenizer từ Hugging Face
from underthesea import word_tokenize                       # tách từ tiếng Việt
PHIEN_BAN = {"vinai/phobert-base": "01daacda68afe13d83023d16ec647239e344a1e6",   # ghim phiên bản
             "FacebookAI/xlm-roberta-base": "e73636d4f797dec63c3081bb6ed5c7b0bb3f2089",
             "openai-community/gpt2": "607a30d783dfa663caf39e06633721c8d4cfcd7e"}
bo_tach = {ten: AutoTokenizer.from_pretrained(ten, revision=rev) for ten, rev in PHIEN_BAN.items()}   # ba tokenizer
cau = "Thầy giảng dạy rất nhiệt tình, slide đầy đủ."         # câu thử
cau_tach = word_tokenize(cau, format="text")                # PhoBERT cần câu đã tách từ
print(cau_tach)                                             # câu đã tách
for ten, t in bo_tach.items():                              # mỗi tokenizer
    vao = cau_tach if "phobert" in ten else cau             # PhoBERT nhận câu đã tách
    print(ten, len(t), t.tokenize(vao))                     # cỡ từ điển, các token
''', "Thầy giảng_dạy rất nhiệt_tình , slide đầy_đủ .\nvinai/phobert-base 64001 ['Thầy', 'giảng_dạy', 'rất', 'nhiệt_tình', ',', 'slide', 'đầy_đủ', '.']\nFacebookAI/xlm-roberta-base 250002 ['▁Thầy', '▁giảng', '▁dạy', '▁rất', '▁nhiệt', '▁tình', ',', '▁slide', '▁đầy', '▁đủ', '.']\nopenai-community/gpt2 50257 ['Th', 'á', 'º', '§', 'y', 'Ġg', 'i', 'á', 'º', '£', 'ng', 'Ġd', 'á', 'º', '¡', 'y', 'Ġr', 'á', 'º', '¥', 't', 'Ġn', 'hi', 'á', '»', 'ĩ', 't', 'Ġt', 'Ã', '¬', 'n', 'h', ',', 'Ġslide', 'ĠÄ', 'ĳ', 'á', 'º', '§', 'y', 'ĠÄ', 'ĳ', 'á', '»', '§', '.']",
    khung("doc", ["PhoBERT 8 token, XLM-R 11, GPT-2 46. Các ký tự lạ của GPT-2 là cách nó hiển thị từng byte."]))
c.o('''
cau_va = va.sentence.tolist()                               # câu val
tach_va = [word_tokenize(s, format="text") for s in cau_va] # câu val đã tách từ
print("âm tiết", round(np.mean([len(s.split()) for s in cau_va]), 2))   # đơn vị cách nhau bởi dấu cách
for ten, t in bo_tach.items():                              # mỗi tokenizer
    vao = tach_va if "phobert" in ten else cau_va           # đầu vào đúng kiểu
    print(ten, round(np.mean([len(t.tokenize(s)) for s in vao]), 2))   # token trung bình mỗi câu
''', "âm tiết 13.67\nvinai/phobert-base 10.94\nFacebookAI/xlm-roberta-base 15.56\nopenai-community/gpt2 49.77",
    khung("doc", ["GPT-2 dùng gấp khoảng 3,6 lần số âm tiết: ngữ cảnh ngắn hơn, chi phí theo token cao hơn."]))
c.o('''
pho = bo_tach["vinai/phobert-base"]                         # tokenizer PhoBERT
for w in ["khóa_học", "khoá_học", "hòa_bình", "hoà_bình"]:  # kiểu bỏ dấu mới và cũ
    print(w, pho.tokenize(w), pho.unk_token_id in pho.convert_tokens_to_ids(pho.tokenize(w)))   # các mảnh, có token lạ không
''', "khóa_học ['khó@@', 'a_học'] True\nkhoá_học ['khoá@@', '_học'] False\nhòa_bình ['hò@@', 'a_@@', 'bình'] False\nhoà_bình ['hoà_bình'] False")

c.mo_trang(4, "PhoBERT đoán từ bị che (tải khoảng 540 MB), rồi làm bộ trích đặc trưng đóng băng (khoảng 6 phút trên CPU).")
c.o('''
os.environ["DISABLE_SAFETENSORS_CONVERSION"] = "1"          # không tải thêm bản chuyển đổi 540 MB
import torch                                                # PyTorch
from transformers import AutoModel, AutoModelForMaskedLM    # mô hình mã hóa, mô hình đoán từ bị che
torch.set_num_threads(4)                                    # 4 luồng
R = PHIEN_BAN["vinai/phobert-base"]                         # phiên bản đã ghim
mlm = AutoModelForMaskedLM.from_pretrained("vinai/phobert-base", revision=R).eval()   # PhoBERT kèm đầu đoán từ
print(sum(p.numel() for p in mlm.parameters()))             # số tham số
def doan(cau, k=5):                                         # k từ có xác suất cao nhất cho ô che
    x = pho(cau, return_tensors="pt")                       # mã hóa
    with torch.no_grad():                                   # không cần gradient
        p = mlm(**x).logits[0].softmax(-1)                  # phân phối trên từ điển ở mọi vị trí
    vt = (x["input_ids"][0] == pho.mask_token_id).nonzero().item()   # vị trí bị che
    xs, ids = p[vt].topk(k)                                 # k từ tốt nhất
    return [(pho.convert_ids_to_tokens(i.item()), round(v.item(), 3)) for v, i in zip(xs, ids)]   # từ và xác suất
for c_ in ["Hà_Nội là thủ_đô của <mask> .",                 # câu đã tách từ, có một ô che
           "Môn này khó quá , em không <mask> gì cả .",
           "Thầy giảng_dạy rất <mask> , sinh_viên dễ hiểu ."]:
    print(doan(c_))                                         # năm từ đoán
''', "135127810\n[('Việt_Nam', 0.837), ('hoà_bình', 0.036), ('đất_nước', 0.031), ('thế_giới', 0.012), ('quốc_gia', 0.009)]\n[('biết', 0.504), ('nghĩ', 0.069), ('hiểu', 0.05), ('suy_nghĩ', 0.047), ('làm', 0.046)]\n[('hay', 0.068), ('kỹ', 0.067), ('khoa_học', 0.049), ('rõ_ràng', 0.048), ('thoải_mái', 0.038)]")
c.o('''
from sklearn.linear_model import LogisticRegression         # hồi quy logistic
from sklearn.metrics import accuracy_score, f1_score        # thước đo
pho_ma_hoa = AutoModel.from_pretrained("vinai/phobert-base", revision=R).eval()   # chỉ phần mã hóa
def vector_cau(cau, lo=64):                                 # vector câu: trung bình vector các token
    ra = []                                                 # kết quả từng lô
    for k in range(0, len(cau), lo):                        # lô 64 câu
        x = pho([word_tokenize(s, format="text") for s in cau[k:k + lo]],
                padding=True, truncation=True, max_length=64, return_tensors="pt")   # tách từ, mã hóa, đệm
        with torch.no_grad():                               # không cần gradient
            h = pho_ma_hoa(**x).last_hidden_state           # (lô, số token, 768)
        m = x["attention_mask"][..., None]                  # 1 ở token thật
        ra.append(((h * m).sum(1) / m.sum(1)).numpy())      # trung bình các token thật
    return np.concatenate(ra)                               # mọi câu
t0 = time.time()                                            # đo thời gian
V_tr, V_va, V_te = (vector_cau(d.sentence.tolist()) for d in (tr, va, te))   # vector của ba phần
print(V_tr.shape, round(time.time() - t0) < 1200)           # hình dạng, dưới 20 phút
for C in (0.03, 0.1, 0.3):                                  # chọn C trên val
    lr = LogisticRegression(C=C, max_iter=3000).fit(V_tr, tr.sentiment)   # huấn luyện
    p = lr.predict(V_va)                                    # dự đoán val
    print(C, round(accuracy_score(va.sentiment, p), 4), round(f1_score(va.sentiment, p, average="macro"), 4))   # độ chính xác, macro-F1
''', "(11426, 768) True\n0.03 0.9292 0.7755\n0.1 0.9324 0.797\n0.3 0.9311 0.7844",
    khung("doc", ["C = 0,1: val 93,24%, macro-F1 0,797, ngang mô hình tốt nhất của Chương 41 mà PhoBERT không học gì từ UIT-VSFC."]))
c.o('''
lr = LogisticRegression(C=0.1, max_iter=3000).fit(V_tr, tr.sentiment)   # C đã chọn trên val
p = lr.predict(V_te)                                        # đo test một lần
print(round(accuracy_score(te.sentiment, p), 4), round(f1_score(te.sentiment, p, average="macro"), 4))   # độ chính xác, macro-F1
''', "0.9217 0.7733",
    khung("doc", ["Test 92,17% / 0,773, hơn SVM cân bằng của Chương 41 (89,67% / 0,753) và Transformer học từ đầu của Chương 44 (88,79% / 0,728)."]))

c.mo_trang(5, "Ba bài tập. Đoán trước, rồi mới mở đáp án.")
c.bai("45.1", "BPE bằng tay", "Kho: hoa 5 lần, hoan 3, loan 4, lo 2. Tính tay 4 lần gộp đầu tiên, rồi cắt hoan, lo, toan.",
      "Gộp lần lượt o+a (12), h+oa (8), n+_ (7), hoa+_ (5). hoan thành hoa, n_; lo giữ nguyên; toan thành t, oa, n_. Code ở ô ngay dưới.")
c.o('''
dem2 = Counter({"hoa": 5, "hoan": 3, "loan": 4, "lo": 2})   # kho bốn từ
qt2 = hoc_bpe(dem2, 4)                                      # 4 lần gộp
print(qt2)                                                  # các quy tắc
print([ma_hoa(w, qt2) for w in ["hoan", "lo", "toan"]])     # cắt ba từ
''', "[('o', 'a'), ('h', 'oa'), ('n', '_'), ('hoa', '_')]\n[('hoa', 'n_'), ('l', 'o', '_'), ('t', 'oa', 'n_')]")
c.bai("45.2", "Kiểu bỏ dấu cho PhoBERT", "Đổi vần oa, oe, uy không có phụ âm cuối sang kiểu bỏ dấu cũ trên UIT-VSFC val, đếm thay đổi về token PhoBERT.",
      "33 câu bị đổi, tổng token giảm 45 (khoảng 0,3%), token lạ từ 7 xuống 5: ảnh hưởng nhỏ trên bộ này. Code ở ô ngay dưới.")
c.o('''
import re                                                   # biểu thức chính quy
DAU = "\\u0300\\u0301\\u0303\\u0309\\u0323"                      # huyền, sắc, ngã, hỏi, nặng dưới dạng dấu kết hợp
MAU = re.compile(f"(o)([{DAU}])([ae])(?![^\\\\W_])|(u)([{DAU}])(y)(?![^\\\\W_])")   # dấu ở nguyên âm đầu, hết âm tiết
def kieu_cu(s):                                             # đổi sang kiểu bỏ dấu cũ
    s = unicodedata.normalize("NFD", s)                     # tách dấu thanh thành ký tự riêng
    s = MAU.sub(lambda m: m.group(1) + m.group(3) + m.group(2) if m.group(1)
                else m.group(4) + m.group(6) + m.group(5), s)   # chuyển dấu ra sau nguyên âm thứ hai
    return unicodedata.normalize("NFC", s)                  # dựng lại
print([kieu_cu(w) for w in ["khóa", "hòa_bình", "khỏe", "thủy", "quý", "hoặc", "hoàn", "toán"]])   # thử
tach_cu = [kieu_cu(s) for s in tach_va]                     # val sau khi đổi
print(sum(a != b for a, b in zip(tach_va, tach_cu)))        # số câu bị đổi
for ten, D in (("kiểu mới", tach_va), ("kiểu cũ", tach_cu)):   # hai kiểu
    ids = [pho(s, add_special_tokens=False)["input_ids"] for s in D]   # mã hóa
    print(ten, sum(map(len, ids)), sum(i.count(pho.unk_token_id) for i in ids))   # tổng token, số token lạ
''', "['khoá', 'hoà_bình', 'khoẻ', 'thuỷ', 'quý', 'hoặc', 'hoàn', 'toán']\n33\nkiểu mới 17319 7\nkiểu cũ 17274 5")
c.bai("45.3", "Token đầu câu hay trung bình", "Trên 3000 câu train đầu tiên, so vector token đầu câu với trung bình các token, hồi quy logistic C = 0,1 và 1.",
      "Trung bình tốt hơn: 0,772 so với 0,762. Token đầu câu chỉ tóm tắt câu sau khi được tinh chỉnh (Chương 46). Code ở ô ngay dưới (khoảng 2 phút).")
c.o('''
def vector_dau(cau, lo=64):                                 # vector của token đầu câu
    ra = []                                                 # kết quả từng lô
    for k in range(0, len(cau), lo):                        # lô 64 câu
        x = pho([word_tokenize(s, format="text") for s in cau[k:k + lo]],
                padding=True, truncation=True, max_length=64, return_tensors="pt")   # tách từ, mã hóa, đệm
        with torch.no_grad():                               # không cần gradient
            ra.append(pho_ma_hoa(**x).last_hidden_state[:, 0].numpy())   # vector của token đầu câu
    return np.concatenate(ra)                               # mọi câu
D_tr, D_va = vector_dau(tr.sentence[:3000].tolist()), vector_dau(va.sentence.tolist())   # 3000 câu train, cả val
for ten, A, B in (("đầu câu", D_tr, D_va), ("trung bình", V_tr[:3000], V_va)):   # hai cách
    for C in (0.1, 1):                                      # hai mức C
        lr = LogisticRegression(C=C, max_iter=3000).fit(A, tr.sentiment[:3000])   # huấn luyện
        print(ten, C, round(f1_score(va.sentiment, lr.predict(B), average="macro"), 4))   # macro-F1 val
''', "đầu câu 0.1 0.7428\nđầu câu 1 0.7617\ntrung bình 0.1 0.7715\ntrung bình 1 0.7642")

c.ghi(Path(__file__).resolve().parents[2] / "notebooks/ch45_tokenization_pretrained.ipynb")
