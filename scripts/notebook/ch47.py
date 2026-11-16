"""Dựng notebooks/ch47_llm_hoat_dong.ipynb: python3 scripts/notebook/ch47.py"""
from pathlib import Path
from nblib import Chuong, code, khung

c = Chuong(47, "LLM hoạt động thế nào", "ch47-llm-hoat-dong",
           "Mở một LLM thật (Qwen2.5-0.5B) trên CPU, xem phân phối token tiếp theo và perplexity, tự viết vòng sinh văn bản với tham lam, nhiệt độ, top-p, rồi so mô hình gốc với mô hình chỉ dẫn.",
           ["Đọc cấu hình một LLM thật và tokenizer của nó.",
            "Lấy phân phối token tiếp theo, tính perplexity.",
            "Tự viết vòng sinh văn bản; thấy bịa đặt và lặp vòng.",
            "Hiểu khuôn hội thoại và khác biệt giữa bản gốc và bản chỉ dẫn."],
           [("LLM là gì", "01-llm-la-gi"), ("Đoán token tiếp theo", "02-doan-token-tiep-theo"),
            ("Sinh văn bản", "03-sinh-van-ban"), ("Mô hình gốc và mô hình chỉ dẫn", "04-goc-va-instruct"),
            ("Bài tập", "05-bai-tap")],
           thoi_gian="khoảng 6 phút trên CPU, chưa kể tải hai mô hình (khoảng 2 GB, một lần)")

c.mo_trang(1, "Tải Qwen2.5-0.5B (khoảng 1 GB), đọc cấu hình, đo tokenizer trên UIT-VSFC.")
c.cells.append(code('''
!pip install -q pyarrow transformers                         # đọc parquet, mô hình Hugging Face
'''))
c.o('''
import math                                                 # hàm mũ
import os                                                   # đường dẫn
import time                                                 # đo thời gian
import urllib.request                                       # tải tệp
import numpy as np                                          # mảng
import pandas as pd                                         # bảng
import torch                                                # PyTorch
from transformers import AutoTokenizer, AutoModelForCausalLM   # tokenizer, mô hình đoán token tiếp theo
torch.set_num_threads(4)                                    # 4 luồng
R_GOC = "060db6499f32faf8b98477b0a26969ef7d8b9987"          # ghim phiên bản
tok = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-0.5B", revision=R_GOC)   # tokenizer
llm = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-0.5B", revision=R_GOC, dtype=torch.float32).eval()   # bản gốc
c = llm.config                                              # cấu hình
print(sum(p.numel() for p in llm.parameters()), len(tok))   # số tham số, số token
print(c.num_hidden_layers, c.hidden_size, c.num_attention_heads, c.num_key_value_heads,
      c.intermediate_size, c.max_position_embeddings, c.vocab_size)   # khối, d, đầu query, đầu key-value, lớp ẩn, ngữ cảnh, từ điển
''', '494032768 151665\n24 896 14 2 4864 32768 151936')
c.o('''
URL = "https://huggingface.co/api/datasets/uitnlp/vietnamese_students_feedback/parquet/default/{}/0.parquet"   # UIT-VSFC
THU_MUC = os.path.expanduser("~/.cache/vsfc")               # lưu tạm
def tai(phan):                                              # tải một lần
    os.makedirs(THU_MUC, exist_ok=True)                     # tạo thư mục
    tep = os.path.join(THU_MUC, phan + ".parquet")          # đường dẫn
    if not os.path.exists(tep):                             # chưa có thì tải
        urllib.request.urlretrieve(URL.format(phan), tep)   # tải về
    return pd.read_parquet(tep)                             # đọc
va = tai("validation")                                      # val
print(round(np.mean([len(tok.tokenize(s)) for s in va.sentence]), 2))   # token trung bình mỗi câu
cau = "Thầy giảng dạy rất nhiệt tình, slide đầy đủ."         # câu thử của Chương 45
print(len(tok.tokenize(cau)), [tok.convert_tokens_to_string([t]) for t in tok.tokenize(cau)])   # số token, từng token
''', "15.51\n12 ['Th', 'ầy', ' giảng', ' dạy', ' rất', ' nhiệt', ' tình', ',', ' slide', ' đầy', ' đủ', '.']",
    khung("doc", ["15,51 token mỗi câu, so với 49,77 của GPT-2 ở Chương 45: gần như mỗi âm tiết một token."]))

c.mo_trang(2, "Phân phối token tiếp theo và perplexity (vài giây).")
c.o('''
def tiep_theo(van_ban, k=8):                                # k token tiếp theo có xác suất cao nhất
    x = tok(van_ban, return_tensors="pt")                   # mã hóa
    with torch.no_grad():                                   # không cần gradient
        p = llm(**x).logits[0, -1].softmax(-1)              # phân phối cho token ngay sau văn bản
    xs, ids = p.topk(k)                                     # k token tốt nhất
    return p, [(tok.decode(i), round(v.item(), 3)) for v, i in zip(xs, ids)]   # phân phối, danh sách
for van_ban in ["Thủ đô của Việt Nam là", "Hôm nay trời mưa nên em"]:   # hai đoạn mở đầu
    print(van_ban, tiep_theo(van_ban)[1])                   # top 8
p, _ = tiep_theo("Thủ đô của Việt Nam là")                  # phân phối đầy đủ
for w in [" Hà", " thành"]:                                 # hai token đáng xem
    i = tok.encode(w)[0]                                    # chỉ số token
    print(repr(w), round(p[i].item(), 4), int((p > p[i]).sum()) + 1)   # xác suất và thứ hạng
''', "Thủ đô của Việt Nam là [(' một', 0.136), (' nơi', 0.13), (' gì', 0.115), (' thành', 0.108), (' thủ', 0.09), (' __', 0.02), (' địa', 0.017), (' đất', 0.013)]\nHôm nay trời mưa nên em [(' đi', 0.144), (' không', 0.078), (' đã', 0.036), (' m', 0.025), (' về', 0.019), (' sẽ', 0.018), (' phải', 0.017), (' lại', 0.016)]\n' Hà' 0.0062 14\n' thành' 0.108 4")
c.o('''
import random                                               # xáo trộn
def perplexity(van_ban):                                    # e mũ cross-entropy trung bình mỗi token
    ids = tok(van_ban, return_tensors="pt")["input_ids"]    # mã hóa
    with torch.no_grad():                                   # không cần gradient
        return round(math.exp(llm(ids, labels=ids).loss.item()), 1)   # mô hình tự dịch nhãn một vị trí
cau = "Thầy giảng dạy rất nhiệt tình và luôn giúp đỡ sinh viên."   # câu tự nhiên
tu = cau[:-1].split()                                       # các từ
random.seed(0)                                              # xáo cố định
random.shuffle(tu)                                          # xáo trộn
xao = " ".join(tu) + "."                                    # câu xáo
print(perplexity(cau), cau)                                 # câu tự nhiên
print(perplexity(xao), xao)                                 # câu xáo
''', '31.6 Thầy giảng dạy rất nhiệt tình và luôn giúp đỡ sinh viên.\n3654.4 giảng đỡ giúp tình sinh dạy rất luôn nhiệt Thầy viên và.',
    khung("doc", ["Cùng các từ, xáo trộn thì perplexity tăng khoảng 115 lần."]))

c.mo_trang(3, "Vòng sinh văn bản tự viết: tham lam, nhiệt độ, top-p (khoảng nửa phút).")
c.o('''
def sinh(van_ban, so_token=30, T=0.0, top_p=1.0, seed=0):   # sinh so_token token
    g = torch.Generator().manual_seed(seed)                 # ngẫu nhiên cố định
    ids = tok(van_ban, return_tensors="pt")["input_ids"]    # đoạn mở đầu
    for _ in range(so_token):                               # mỗi bước một token
        with torch.no_grad():                               # không cần gradient
            lg = llm(ids).logits[0, -1]                     # chỉ cần vị trí cuối
        if T == 0:                                          # tham lam
            j = lg.argmax()                                 # token xác suất cao nhất
        else:                                               # lấy mẫu
            p = (lg / T).softmax(-1)                        # nhiệt độ
            if top_p < 1:                                   # top-p
                xs, thu_tu = p.sort(descending=True)        # sắp giảm dần
                giu = xs.cumsum(0) - xs < top_p             # giữ token cho tới khi tổng vừa vượt top_p
                p = torch.zeros_like(p).scatter(0, thu_tu[giu], xs[giu])   # bỏ cái đuôi
                p = p / p.sum()                             # chuẩn hóa lại
            j = torch.multinomial(p, 1, generator=g)[0]     # rút một token
        ids = torch.cat([ids, j.view(1, 1)], 1)             # nối rồi đoán tiếp
    return tok.decode(ids[0])                               # văn bản
t0 = time.time()                                            # đo thời gian
print(repr(sinh("Thủ đô của Việt Nam là thành phố")))       # tham lam
print(repr(sinh("Trường đại học tốt nhất để học trí tuệ nhân tạo là")))   # tham lam
print(time.time() - t0 < 120)                               # dưới 2 phút
''', "'Thủ đô của Việt Nam là thành phố lớn nhất thế giới, với hơn 200 triệu dân, 100 triệu người dân ở đây. Trong đó, có '\n'Trường đại học tốt nhất để học trí tuệ nhân tạo là gì? - Tin tức - Trường đại học tốt nhất để học trí tuệ nhân tạo là gì?\\nTrường đại học tốt nhất để học trí'\nTrue",
    khung("doc", ["Câu đầu trôi chảy và bịa hoàn toàn; câu sau lặp vòng."]))
c.o('''
for T in (0.7, 1.0, 1.5):                                   # ba nhiệt độ
    print(T, repr(sinh("Hôm nay trời mưa nên em", T=T)))    # cùng seed
print("top-p 0.9", repr(sinh("Hôm nay trời mưa nên em", T=1.0, top_p=0.9)))   # cắt đuôi
''', "0.7 'Hôm nay trời mưa nên em rất thích đi bơi. Thấy em làm vậy em cảm thấy rất tự hào, vì em đã tự mình làm điều này, mình cũng'\n1.0 'Hôm nay trời mưa nên em họ tập không bầm bầm ở tối. Yêu Em hiện tại em Thiếu Ngọc mới bị kiểu kiểu chuyện như thế này, sao'\n1.5 'Hôm nay trời mưa nên em họ ta không憩 mùa愈旺 ởpellier啦 //AsVip一期 Aw lined da chorus perché ultimo contest headline serfs Fo_literals each Ausb'\ntop-p 0.9 'Hôm nay trời mưa nên em họ tập không bọc luôn có ở thì làm gì em yêu tôi thấy em ho một đôi mắt bị mèo che thấy đâu nè\\n'")

c.mo_trang(4, "Bản Instruct (tải thêm khoảng 1 GB), khuôn hội thoại, hỏi cả hai bản.")
c.o('''
R_CD = "7ae557604adf67be50417f59c2c2f167def9a775"           # ghim phiên bản
tok_cd = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-0.5B-Instruct", revision=R_CD)   # tokenizer kèm khuôn hội thoại
llm_cd = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-0.5B-Instruct", revision=R_CD, dtype=torch.float32).eval()   # bản chỉ dẫn
hoi = "Thủ đô của Việt Nam là gì?"                         # câu hỏi
khuon = tok_cd.apply_chat_template([{"role": "user", "content": hoi}], tokenize=False, add_generation_prompt=True)   # bọc trong khuôn
print(khuon)                                                # xem khuôn
''', '<|im_start|>system\nYou are Qwen, created by Alibaba Cloud. You are a helpful assistant.<|im_end|>\n<|im_start|>user\nThủ đô của Việt Nam là gì?<|im_end|>\n<|im_start|>assistant')
c.o('''
HET = tok_cd.convert_tokens_to_ids("<|im_end|>")           # token kết thúc lượt nói
def tra_loi(mo_hinh, van_ban, so_token=40):                 # sinh tham lam, dừng ở token kết thúc
    ids = tok_cd(van_ban, return_tensors="pt")["input_ids"] # mã hóa
    n0 = ids.shape[1]                                       # độ dài đoạn đầu
    for _ in range(so_token):                               # mỗi bước
        with torch.no_grad():                               # không cần gradient
            j = mo_hinh(ids).logits[0, -1].argmax()         # tham lam
        ids = torch.cat([ids, j.view(1, 1)], 1)             # nối
        if j.item() in (HET, tok_cd.eos_token_id):          # mô hình tự kết thúc lượt nói
            break                                           # dừng
    return tok_cd.decode(ids[0, n0:])                       # chỉ phần mô hình viết
print("gốc, hỏi thẳng:   ", repr(tra_loi(llm, hoi)))        # bản gốc, không khuôn
print("chỉ dẫn, có khuôn:", repr(tra_loi(llm_cd, khuon)))   # bản chỉ dẫn, có khuôn
print("gốc, có khuôn:    ", repr(tra_loi(llm, khuon)))      # bản gốc, có khuôn
''', "gốc, hỏi thẳng:    ' - Tin tức - 24h.vn\\nThủ đô của Việt Nam là gì?\\nThủ đô của Việt Nam là gì? 24h.vn\\nThủ đô của Việt Nam'\nchỉ dẫn, có khuôn: 'Thủ đô của Việt Nam là Hà Nội.<|im_end|>'\ngốc, có khuôn:     'Thủ đô của Việt Nam là Hà Nội.acco\\nacco\\nBạn có thể sử dụng các công cụ để tìm kiếm thông tin về thủ đô của Việt Nam.acco\\nacco\\nBạn có'",
    khung("doc", ["Bản gốc có khuôn cũng trả lời đúng Hà Nội nhưng không biết dừng: kiến thức đến từ tiền huấn luyện, bước chỉ dẫn dạy hình thức."]))

c.mo_trang(5, "Ba bài tập. Đoán trước, rồi mới mở đáp án.")
c.bai("47.1", "Đếm tham số bằng tay", "Từ cấu hình, đếm số tham số của Qwen2.5-0.5B và phần trăm của bảng vector token.",
      "Mỗi khối 14 912 384, tổng khớp đúng 494 032 768; bảng vector token chiếm 27,6%. Code ở ô ngay dưới.")
c.o('''
d, f, V, L, dk = 896, 4864, 151936, 24, 64                  # cấu hình
kv = 2 * dk                                                 # 2 đầu key, value dùng chung cho 14 đầu query
moi_khoi = (d * d + d) + 2 * (d * kv + kv) + d * d + 3 * d * f + 2 * d   # query, key và value, đầu ra, SwiGLU, hai RMSNorm
tong = L * moi_khoi + V * d + d                             # + bảng vector token + RMSNorm cuối
print(moi_khoi, tong, tong == sum(p.numel() for p in llm.parameters()), round(100 * V * d / tong, 1))   # khớp không, % bảng token
''', '14912384 494032768 True 27.6')
c.bai("47.2", "Phân loại cảm xúc không cần huấn luyện", "So log xác suất của Tích cực và Tiêu cực; ngưỡng 0, rồi ngưỡng chọn trên 100 câu có nhãn.",
      "Ngưỡng 0: 52,5%, mô hình lệch hẳn về Tiêu cực. Ngưỡng chọn trên 100 câu khác: 81%. Code ở ô ngay dưới (khoảng 3 phút).")
c.o('''
def log_xs(khuon, tra_loi):                                 # tổng log xác suất của tra_loi khi đứng sau khuon
    a = tok_cd(khuon, return_tensors="pt")["input_ids"]     # câu lệnh
    b = tok_cd(tra_loi, return_tensors="pt")["input_ids"]   # câu trả lời
    ids = torch.cat([a, b], 1)                              # nối
    with torch.no_grad():                                   # không cần gradient
        lp = llm_cd(ids).logits[0, :-1].log_softmax(-1)     # log xác suất ở mọi vị trí
    vt = torch.arange(a.shape[1] - 1, ids.shape[1] - 1)     # vị trí đoán từng token của tra_loi
    return lp[vt, ids[0, a.shape[1]:]].sum().item()         # cộng lại
def diem(s):                                                # điểm tích cực trừ tiêu cực
    k = tok_cd.apply_chat_template([{"role": "user", "content": f'Cảm xúc của câu sau là tích cực hay tiêu cực? "{s}"'}],
                                   tokenize=False, add_generation_prompt=True)   # câu lệnh trong khuôn
    return log_xs(k, "Tích cực") - log_xs(k, "Tiêu cực")    # hiệu log xác suất
hai_lop = va[va.sentiment != 1]                             # bỏ trung tính
chon, do = hai_lop.iloc[:100], hai_lop.iloc[100:300]        # 100 câu để chọn ngưỡng, 200 câu để đo
d_chon = np.array([diem(s) for s in chon.sentence])         # điểm 100 câu chọn
d_do = np.array([diem(s) for s in do.sentence])             # điểm 200 câu đo
y_chon, y_do = chon.sentiment.values == 2, do.sentiment.values == 2   # nhãn tích cực
print(np.bincount(do.sentiment, minlength=3), (d_do > 0).sum(), ((d_do > 0) == y_do).mean())   # phân bố nhãn, số câu đoán tích cực, độ chính xác
nguong = max(sorted(d_chon), key=lambda t: ((d_chon > t) == y_chon).mean())   # ngưỡng tốt nhất trên 100 câu chọn
print(round(nguong, 2), ((d_do > nguong) == y_do).mean())   # ngưỡng, độ chính xác trên 200 câu đo
''', '[ 90   0 110] 17 0.525\n-0.82 0.81')
c.bai("47.3", "Vì sao tham lam hay lặp", "Tỷ lệ bộ ba token khác nhau trong 100 token sinh bằng tham lam và bằng top-p 0,9, nhiệt độ 0,7.",
      "27,6% so với 79,6%: tham lam lặp gần ba phần tư văn bản. Code ở ô ngay dưới (khoảng 1 phút).")
c.o('''
def ty_le_khac(van_ban, mo_dau):                            # tỷ lệ bộ ba token khác nhau
    ids = tok(van_ban)["input_ids"][len(tok(mo_dau)["input_ids"]):]   # chỉ phần được sinh
    ba = list(zip(ids, ids[1:], ids[2:]))                   # các bộ ba
    return round(len(set(ba)) / len(ba), 3)                 # khác nhau trên tổng
md = "Trường đại học tốt nhất để học trí tuệ nhân tạo là"   # đoạn mở đầu
print("tham lam", ty_le_khac(sinh(md, so_token=100), md))   # tham lam
print("top-p 0.9, T 0.7", ty_le_khac(sinh(md, so_token=100, T=0.7, top_p=0.9), md))   # lấy mẫu
''', 'tham lam 0.276\ntop-p 0.9, T 0.7 0.796')

c.ghi(Path(__file__).resolve().parents[2] / "notebooks/ch47_llm_hoat_dong.ipynb")
