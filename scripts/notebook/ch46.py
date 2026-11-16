"""Dựng notebooks/ch46_fine_tune_phobert.ipynb: python3 scripts/notebook/ch46.py"""
from pathlib import Path
from nblib import Chuong, code, khung

c = Chuong(46, "Fine-tune PhoBERT", "ch46-fine-tune-phobert",
           "Tinh chỉnh PhoBERT cho phân loại cảm xúc UIT-VSFC bằng vòng huấn luyện PyTorch tự viết, so với mọi mô hình trước, rồi nhìn vào bên trong mô hình đã tinh chỉnh.",
           ["Hiểu tinh chỉnh khác trích đặc trưng và học từ đầu thế nào.",
            "Tự viết vòng tinh chỉnh: tốc độ học nhỏ, khởi động dần, cắt gradient.",
            "Đánh giá trung thực trên test, đọc kết quả theo từng lớp và các câu sai.",
            "Đo lớp nào thay đổi và vector của tốt, tệ trước và sau tinh chỉnh."],
           [("Tinh chỉnh là gì", "01-tinh-chinh-la-gi"), ("Vòng huấn luyện", "02-vong-huan-luyen"),
            ("Kết quả và so sánh", "03-ket-qua"), ("Bên trong mô hình đã tinh chỉnh", "04-ben-trong-mo-hinh"),
            ("Bài tập", "05-bai-tap")],
           thoi_gian="khoảng 1 giờ trên CPU (40 phút ở trang 2); chọn GPU trong Colab sẽ nhanh hơn nhiều")

c.mo_trang(1, "Lắp đầu phân loại lên PhoBERT, mã hóa dữ liệu, xem mô hình trước khi học.")
c.cells.append(code('''
!pip install -q pyarrow underthesea transformers            # đọc parquet, tách từ tiếng Việt, mô hình Hugging Face
'''))
c.o('''
import copy                                                 # sao chép trọng số
import os                                                   # đường dẫn, biến môi trường
import time                                                 # đo thời gian
import urllib.request                                       # tải tệp
os.environ["DISABLE_SAFETENSORS_CONVERSION"] = "1"          # không tải thêm bản chuyển đổi 540 MB (Chương 45)
import numpy as np                                          # mảng
import pandas as pd                                         # bảng
import torch                                                # PyTorch
import torch.nn.functional as F                             # hàm loss
from sklearn.metrics import accuracy_score, f1_score        # thước đo
from transformers import AutoTokenizer, AutoModelForSequenceClassification   # tokenizer, mô hình có đầu phân loại
from underthesea import word_tokenize                       # tách từ
torch.set_num_threads(4)                                    # 4 luồng (nhanh hơn 8 trên máy viết sách)
R = "01daacda68afe13d83023d16ec647239e344a1e6"              # phiên bản PhoBERT đã ghim
pho = AutoTokenizer.from_pretrained("vinai/phobert-base", revision=R)   # tokenizer
torch.manual_seed(0)                                        # đầu phân loại khởi tạo cố định
goc = AutoModelForSequenceClassification.from_pretrained("vinai/phobert-base", revision=R, num_labels=3)   # thân PhoBERT + đầu mới
print(goc.classifier)                                       # cấu trúc đầu phân loại
print(sum(p.numel() for p in goc.parameters()), sum(p.numel() for p in goc.classifier.parameters()))   # tổng tham số, tham số của đầu
''', 'RobertaClassificationHead(\n  (dense): Linear(in_features=768, out_features=768, bias=True)\n  (dropout): Dropout(p=0.1, inplace=False)\n  (out_proj): Linear(in_features=768, out_features=3, bias=True)\n)\n135000579 592899')
c.o('''
URL = "https://huggingface.co/api/datasets/uitnlp/vietnamese_students_feedback/parquet/default/{}/0.parquet"   # UIT-VSFC
THU_MUC = os.path.expanduser("~/.cache/vsfc")               # lưu tạm
def tai(phan):                                              # tải một lần
    os.makedirs(THU_MUC, exist_ok=True)                     # tạo thư mục
    tep = os.path.join(THU_MUC, phan + ".parquet")          # đường dẫn
    if not os.path.exists(tep):                             # chưa có thì tải
        urllib.request.urlretrieve(URL.format(phan), tep)   # tải về
    return pd.read_parquet(tep)                             # đọc
tr, va, te = tai("train"), tai("validation"), tai("test")   # ba phần
ma_hoa = lambda ds: [pho(word_tokenize(s, format="text"), truncation=True, max_length=64)["input_ids"] for s in ds.sentence]   # tách từ rồi mã hóa
I_tr, I_va, I_te = ma_hoa(tr), ma_hoa(va), ma_hoa(te)       # chỉ số token của ba phần
y_tr, y_va, y_te = torch.tensor(tr.sentiment.values), va.sentiment.values, te.sentiment.values   # nhãn
def du_doan(m, I, lo=128):                                  # dự đoán cả một tập
    m.eval()                                                # tắt dropout
    ra = []                                                 # kết quả từng lô
    with torch.no_grad():                                   # không cần gradient
        for k in range(0, len(I), lo):                      # lô 128
            x = pho.pad({"input_ids": I[k:k + lo]}, return_tensors="pt")   # đệm lô, kèm mặt nạ
            ra.append(m(**x).logits.argmax(-1))             # lớp có điểm cao nhất
    return torch.cat(ra).numpy()                            # mọi câu
def cham(y, p):                                             # độ chính xác, macro-F1
    return round(accuracy_score(y, p), 4), round(f1_score(y, p, average="macro"), 4)   # hai thước đo
p0 = du_doan(goc, I_va)                                     # mô hình chưa học
print(cham(y_va, p0), np.bincount(p0, minlength=3), np.bincount(y_va))   # thước đo, số câu đoán mỗi lớp, số câu thật mỗi lớp
''', '(0.0701, 0.0626) [  27 1456  100] [705  73 805]',
    khung("doc", ["Chưa học: đoán 1456/1583 câu là trung tính, lớp hiếm nhất, nên chỉ đúng 7%."]))

c.mo_trang(2, "Vòng tinh chỉnh tự viết, 3 epoch (khoảng 40 phút trên CPU).")
c.o('''
from transformers import get_linear_schedule_with_warmup    # lịch khởi động dần rồi giảm tuyến tính
def tinh_chinh(I, y, lr=2e-5, so_epoch=3, lo=32, seed=0):   # tinh chỉnh từ PhoBERT gốc
    torch.manual_seed(seed)                                 # khởi tạo đầu và thứ tự lô cố định
    m = AutoModelForSequenceClassification.from_pretrained("vinai/phobert-base", revision=R, num_labels=3)   # bản mới
    opt = torch.optim.AdamW(m.parameters(), lr=lr, weight_decay=0.01, fused=True)   # fused: lặp lại được trên CPU
    so_buoc = so_epoch * ((len(I) + lo - 1) // lo)          # tổng số lô
    lich = get_linear_schedule_with_warmup(opt, int(0.1 * so_buoc), so_buoc)   # khởi động 10% số bước
    tot, ban_tot = -1, None                                 # bản tốt nhất
    for ep in range(1, so_epoch + 1):                       # mỗi epoch
        m.train()                                           # bật dropout
        thu_tu = torch.randperm(len(I))                     # xáo trộn
        tong = 0.0                                          # tổng loss
        for k in range(0, len(I), lo):                      # lô 32
            idx = thu_tu[k:k + lo]                          # chỉ số
            x = pho.pad({"input_ids": [I[i] for i in idx]}, return_tensors="pt")   # đệm lô
            loss = F.cross_entropy(m(**x).logits, y[idx])   # loss
            opt.zero_grad()                                 # xóa gradient
            loss.backward()                                 # lượt ngược
            torch.nn.utils.clip_grad_norm_(m.parameters(), 1.0)   # cắt gradient
            opt.step()                                      # cập nhật
            lich.step()                                     # lịch tốc độ học theo từng lô
            tong += loss.item() * len(idx)                  # cộng loss
        acc, f1 = cham(y_va, du_doan(m, I_va))              # đo val
        print(ep, round(tong / len(I), 4), acc, f1)         # epoch, loss train, độ chính xác, macro-F1
        if f1 > tot:                                        # tốt hơn
            tot, ban_tot = f1, copy.deepcopy(m.state_dict())   # sao chép thật, không phải tham chiếu
    m.load_state_dict(ban_tot)                              # giữ bản có macro-F1 val cao nhất
    return m                                                # mô hình đã tinh chỉnh
t0 = time.time()                                            # đo thời gian
tc = tinh_chinh(I_tr, y_tr)                                 # tinh chỉnh trên toàn bộ train
print(round(time.time() - t0) < 7200)                       # dưới 2 giờ
''', '1 0.3922 0.9431 0.8319\n2 0.1773 0.9476 0.8492\n3 0.1323 0.9526 0.8507\nTrue',
    khung("doc", ["Macro-F1 val 0,832 ngay sau epoch 1, đã hơn mọi mô hình trước (SVM cân bằng 0,801); bản giữ lại là epoch 3, 95,26% / 0,851."]))

c.mo_trang(3, "Đo test một lần, theo từng lớp, và đọc các câu sai.")
c.o('''
from sklearn.metrics import classification_report, confusion_matrix   # báo cáo theo lớp, ma trận nhầm lẫn
p_te = du_doan(tc, I_te)                                    # đo test một lần
print(cham(y_te, p_te))                                     # độ chính xác, macro-F1
print(classification_report(y_te, p_te, target_names=["tiêu cực", "trung tính", "tích cực"], digits=3))   # từng lớp
print(confusion_matrix(y_te, p_te))                         # hàng: nhãn đúng, cột: nhãn đoán
''', '(0.9394, 0.8235)\n              precision    recall  f1-score   support\n\n    tiêu cực      0.946     0.972     0.959      1409\n  trung tính      0.735     0.449     0.558       167\n    tích cực      0.946     0.962     0.954      1590\n\n    accuracy                          0.939      3166\n   macro avg      0.876     0.794     0.823      3166\nweighted avg      0.935     0.939     0.935      3166\n\n[[1369   12   28]\n [  33   75   59]\n [  45   15 1530]]',
    khung("doc", ["Test 93,94% / 0,823, hơn SVM của Chương 41 (89,67% / 0,753). Lớp trung tính vẫn yếu: F1 0,558."]))
c.o('''
ten = ["tiêu cực", "trung tính", "tích cực"]                # tên lớp
sai = np.flatnonzero(p_te != y_te)                          # các câu đoán sai
print(len(sai))                                             # số câu sai
for i in sai[:8]:                                           # tám câu đầu
    print(ten[y_te[i]], "->", ten[p_te[i]], "|", te.sentence[i])   # nhãn đúng, nhãn đoán, câu
''', '192\ntích cực -> trung tính | tính điểm thi đua các nhóm .\ntích cực -> tiêu cực | trong trường macbook thầy số hai thì không có máy nào số một .\ntrung tính -> tích cực | môn học này giúp chúng em hiểu ra những vấn đề cơ bản .\ntích cực -> tiêu cực | phần lớn chỉ là lý thuyết và bài tập .\ntrung tính -> tích cực | như vậy tụi em sẽ định hướng tốt hơn và tập trung vào những thứ cần thiết .\ntiêu cực -> tích cực | thêm hoạt động của sinh viên , giúp sinh viên chủ động hơn .\ntích cực -> trung tính | giảng bài xúc tích .\ntrung tính -> tích cực | ví dụ phù hợp với nội dung kiến thức , hướng dẫn chi tiết .')

c.mo_trang(4, "Độ thay đổi của từng lớp và vector của tốt, tệ (vài giây).")
c.o('''
truoc = dict(goc.named_parameters())                        # trọng số trước tinh chỉnh (cùng seed với tinh_chinh)
def doi(tien_to):                                           # % thay đổi tương đối của mọi tham số có tên bắt đầu bằng tien_to
    tu = sum(((p - truoc[n]) ** 2).sum().item() for n, p in tc.named_parameters() if n.startswith(tien_to))   # bình phương độ dời
    mau = sum((truoc[n] ** 2).sum().item() for n, p in tc.named_parameters() if n.startswith(tien_to))   # bình phương độ lớn ban đầu
    return round(100 * (tu / mau) ** 0.5, 3)                # tỷ số, phần trăm
phan = ["roberta.embeddings."] + [f"roberta.encoder.layer.{i}." for i in range(12)] + ["classifier."]   # 14 phần
muc_doi = [doi(t) for t in phan]                            # mức đổi của từng phần
print(muc_doi)                                              # vector từ, khối 0 tới 11, đầu phân loại
''', '[0.127, 0.664, 0.652, 0.651, 0.684, 0.694, 0.715, 0.718, 0.712, 0.767, 0.803, 0.814, 1.02, 4.525]',
    khung("doc", ["Phần thân đổi chưa tới 1,1%, khối sâu đổi nhiều hơn khối nông; chỉ đầu phân loại ngẫu nhiên đổi 4,5% (hình 46.1 trên web)."]))
c.o('''
def vector_tu(m, cau, tu):                                  # vector lớp cuối tại vị trí của từ tu trong câu
    x = pho(cau, return_tensors="pt")                       # mã hóa
    vt = pho.convert_ids_to_tokens(x["input_ids"][0]).index(tu)   # vị trí của từ
    m.eval()                                                # tắt dropout
    with torch.no_grad():                                   # không cần gradient
        return m.roberta(**x).last_hidden_state[0, vt]      # vector 768 chiều
for a, b, khung_cau in [("tốt", "tệ", "thầy dạy rất {} ."), ("hay", "dở", "môn học này {} ."), ("tốt", "hay", "thầy dạy rất {} .")]:   # hai cặp trái nghĩa, một cặp gần nghĩa
    cos = [round(F.cosine_similarity(vector_tu(m, khung_cau.format(a), a), vector_tu(m, khung_cau.format(b), b), dim=0).item(), 3) for m in (goc, tc)]   # trước, sau
    print(a, b, cos)                                        # cosine trước và sau tinh chỉnh
''', 'tốt tệ [0.605, -0.049]\nhay dở [0.565, -0.137]\ntốt hay [0.612, 0.992]',
    khung("doc", ["Trước tinh chỉnh, tốt và tệ gần nhau như tốt và hay; sau tinh chỉnh, cặp trái nghĩa gần vuông góc, cặp gần nghĩa gần trùng nhau."]))

c.mo_trang(5, "Ba bài tập. Đoán trước, rồi mới mở đáp án. Hai bài đầu huấn luyện thật, mỗi bài vài phút.")
c.bai("46.1", "Tốc độ học quá lớn", "Tinh chỉnh 2000 câu train đầu tiên, 1 epoch, với tốc độ học 1e-3 và 2e-5.",
      "1e-3 sụp về đoán mọi câu là tiêu cực (44,54%, macro-F1 0,205); 2e-5 đạt 88,57% / 0,604. Code ở ô ngay dưới.")
c.o('''
for lr in (1e-3, 2e-5):                                     # hai tốc độ học
    print("lr", lr)                                         # đang thử
    _ = tinh_chinh(I_tr[:2000], y_tr[:2000], lr=lr, so_epoch=1)   # 2000 câu, 1 epoch
''', 'lr 0.001\n1 0.8889 0.4454 0.2054\nlr 2e-05\n1 0.7241 0.8857 0.604')
c.bai("46.2", "Khi chỉ có 500 câu có nhãn", "Trên 500 câu train đầu tiên, so tinh chỉnh (hai seed) với PhoBERT đóng băng cộng hồi quy logistic.",
      "Trích đặc trưng thắng: 0,606 so với 0,593 và 0,580; hai seed lệch nhau 1,9 điểm độ chính xác. Code ở ô ngay dưới.")
c.o('''
from sklearn.linear_model import LogisticRegression         # hồi quy logistic
def vector_tb(m, I, lo=128):                                # trung bình vector các token, mô hình đóng băng
    ra = []                                                 # kết quả từng lô
    with torch.no_grad():                                   # không cần gradient
        for k in range(0, len(I), lo):                      # lô 128
            x = pho.pad({"input_ids": I[k:k + lo]}, return_tensors="pt")   # đệm lô
            h = m(**x).last_hidden_state                    # vector các token
            mk = x["attention_mask"][..., None]             # 1 ở token thật
            ra.append(((h * mk).sum(1) / mk.sum(1)).numpy())   # trung bình các token thật
    return np.concatenate(ra)                               # mọi câu
goc.eval()                                                  # tắt dropout
lr_dt = LogisticRegression(C=0.1, max_iter=3000).fit(vector_tb(goc.roberta, I_tr[:500]), y_tr[:500].numpy())   # trích đặc trưng
print("đóng băng", cham(y_va, lr_dt.predict(vector_tb(goc.roberta, I_va))))   # đo val
for seed in (0, 1):                                         # hai seed
    m500 = tinh_chinh(I_tr[:500], y_tr[:500], seed=seed)    # tinh chỉnh trên 500 câu
    print("tinh chỉnh, seed", seed, cham(y_va, du_doan(m500, I_va)))   # đo val
''', 'đóng băng (0.8888, 0.6064)\n1 0.9496 0.7896 0.5354\n2 0.6758 0.8503 0.58\n3 0.5633 0.8692 0.593\ntinh chỉnh, seed 0 (0.8692, 0.593)\n1 0.9154 0.7922 0.5399\n2 0.7177 0.8389 0.5723\n3 0.6322 0.8503 0.58\ntinh chỉnh, seed 1 (0.8503, 0.58)')
c.bai("46.3", "Bộ nhớ để tinh chỉnh", "Trọng số, gradient và hai trung bình động của AdamW, số thực 4 byte: bao nhiêu GB cho PhoBERT và cho mô hình 7 tỷ tham số?",
      "2,16 GB và 112 GB, chưa kể giá trị trung gian. Code ở ô ngay dưới.")
c.o('''
for ten, n in (("PhoBERT", sum(p.numel() for p in goc.parameters())), ("7 tỷ", 7e9)):   # hai mô hình
    print(ten, round(n * 4 * 4 / 1e9, 2), "GB")             # 4 bản mỗi tham số, 4 byte mỗi số
''', 'PhoBERT 2.16 GB\n7 tỷ 112.0 GB')

c.ghi(Path(__file__).resolve().parents[2] / "notebooks/ch46_fine_tune_phobert.ipynb")
