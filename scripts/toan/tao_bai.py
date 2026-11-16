"""Sinh 31 bài Toán cho thuật toán vào src/data/toan/.

Chạy: .venv/bin/python scripts/toan/tao_bai.py
Năm module nền + một đồ án toán. Bài code có test; bài chứng minh có lời giải,
chứng minh và rubric tự chấm. Tất cả từ dễ đến khó trong từng module.
"""
from __future__ import annotations

from pathlib import Path

import yaml

GOC = Path(__file__).resolve().parents[2]
RA = GOC / "src" / "data" / "toan"

B: list[dict] = []


def bai(so, ten, module, loai, muc, de, goi_y, loi_giai, chung_minh=None, phuc_tap=None, rubric=None, khung=None, vi_du_test=None, test_an=None, lien_quan=None):
    d = {"so": so, "ten": ten, "module": module, "loai": loai, "muc": muc, "de": de, "goi_y": goi_y, "loi_giai": loi_giai, "lien_quan": lien_quan or []}
    if chung_minh is not None: d["chung_minh"] = chung_minh
    if phuc_tap is not None: d["phuc_tap"] = phuc_tap
    if rubric is not None: d["rubric"] = rubric
    if khung is not None: d["khung"] = khung
    if vi_du_test is not None: d["test_vi_du"] = vi_du_test
    if test_an is not None: d["test_an"] = test_an
    B.append(d)


# ===== Module 1: Độ phức tạp và đệ quy =====
bai(
    1, "Sắp xếp hàm theo tốc độ tăng", "do-phuc-tap", "chung-minh", "de",
    "Sắp các hàm sau từ chậm đến nhanh khi n lớn: `log n`, `n`, `n log n`, `n²`, `2^n`, `n!`.",
    ["So tỉ số hai hàm: nếu tỉ số tiến về 0 thì tử chậm hơn.", "Dùng các giới hạn quen: log n / n → 0, n² / 2^n → 0, 2^n / n! → 0.", "Thứ tự cuối: log n < n < n log n < n² < 2^n < n!."],
    "log n < n < n log n < n² < 2^n < n!.",
    "log n/n→0; n/(n log n)=1/log n→0; n log n/n²=log n/n→0; n²/2^n→0; 2^n/n!→0 vì n! có các thừa số lớn hơn 2.",
    "So sánh bằng giới hạn tỉ số, không dựa vào vài giá trị nhỏ.",
    [{"y": "Xác định đúng 6 hàm", "diem": 3}, {"y": "Dùng tỉ số/giới hạn để so", "diem": 4}, {"y": "Kết luận đúng thứ tự", "diem": 3}],
    lien_quan=[{"ten": "Giải tích cho ML", "trang": "/ai-engineer/ch06-giai-tich/01-dao-ham/"}],
)

bai(
    2, "Truy hồi T(n)=2T(n/2)+n", "do-phuc-tap", "chung-minh", "vua",
    "Giải truy hồi `T(n)=2T(n/2)+n`, `T(1)=1`. Chứng minh `T(n)=O(n log n)`.",
    ["Vẽ cây đệ quy; mỗi mức có tổng bao nhiêu?", "Có bao nhiêu mức trước khi chạm 1?", "Đây là trường hợp 2 của Master theorem."],
    "T(n)=O(n log n).",
    "Cây đệ quy: mức 0 có n, mức 1 có 2·(n/2)=n, …, mức k có n. Có log₂n+1 mức, nên tổng n(log₂n+1)=O(n log n).",
    "O(n log n).",
    [{"y": "Vẽ/giải thích cây đệ quy", "diem": 4}, {"y": "Đếm số mức log n", "diem": 3}, {"y": "Kết luận O(n log n)", "diem": 3}],
    lien_quan=[{"ten": "Độ phức tạp thuật toán", "trang": "/thuat-toan/"}],
)

bai(
    3, "Truy hồi T(n)=T(n-1)+n", "do-phuc-tap", "chung-minh", "de",
    "Giải truy hồi `T(n)=T(n-1)+n`, `T(1)=1`.",
    ["Khai triển từng bước.", "Cộng 1+2+...+n.", "Dùng công thức tổng cấp số cộng."],
    "T(n)=n(n+1)/2=O(n²).",
    "T(n)=n+(n-1)+…+1=n(n+1)/2; chứng minh bằng quy nạp hoặc công thức Gauss.",
    "O(n²).",
    [{"y": "Khai triển đúng", "diem": 4}, {"y": "Tính tổng 1..n", "diem": 4}, {"y": "Kết luận O(n²)", "diem": 2}],
)

bai(
    4, "Mảng động append O(1) khấu hao", "do-phuc-tap", "chung-minh", "vua",
    "Mảng động tăng gấp đôi dung lượng khi đầy. Chứng minh n lần append có tổng chi phí O(n), nên trung bình O(1).",
    ["Đếm số phần tử bị sao chép khi dung lượng là 1,2,4,...,2^k.", "Tổng 1+2+...+2^k < 2n.", "Cộng thêm n lần ghi."],
    "Tổng chi phí O(n), khấu hao O(1) mỗi lần append.",
    "Khi dung lượng 2^i đầy, sao chép 2^i phần tử. Tổng sao chép tới n là 1+2+…+2^k < 2n; cộng n lần ghi được ≤3n=O(n). Chia cho n lần append được O(1) khấu hao.",
    "O(1) khấu hao.",
    [{"y": "Đếm đúng các lần sao chép", "diem": 4}, {"y": "Tính tổng hình học <2n", "diem": 4}, {"y": "Kết luận O(1) khấu hao", "diem": 2}],
)

bai(
    5, "Bộ nhớ merge sort và quicksort", "do-phuc-tap", "chung-minh", "de",
    "So sánh bộ nhớ phụ của merge sort và quicksort bản đệ quy. Khi nào quicksort tốn O(n)?",
    ["Merge sort cần mảng tạm khi trộn.", "Quicksort sắp tại chỗ, nhưng đệ quy chiếm ngăn xếp.", "Trường hợp xấu nhất của quicksort là phân hoạch lệch."],
    "Merge sort O(n); quicksort trung bình O(log n), xấu nhất O(n) do ngăn xếp đệ quy.",
    "Merge sort trộn hai nửa nên cần mảng tạm n. Quicksort đổi chỗ tại chỗ; độ sâu đệ quy trung bình log n, xấu nhất n khi chốt luôn là min/max.",
    "O(n) so với O(log n) trung bình.",
    [{"y": "Nêu bộ nhớ merge sort", "diem": 3}, {"y": "Nêu bộ nhớ quicksort", "diem": 4}, {"y": "Chỉ ra trường hợp xấu nhất", "diem": 3}],
)

bai(
    6, "Đếm số phép so sánh tìm kiếm nhị phân", "do-phuc-tap", "code", "de",
    "Viết `dem_so_sanh(xs, x)` trả về số phép so sánh của tìm kiếm nhị phân trên mảng đã sắp tăng; mảng rỗng trả 0. Mỗi lần so `xs[mid]` với x tính 1.",
    ["Dùng lo/hi và vòng while.", "Tăng biến đếm mỗi lần so sánh.", "Mỗi bước giảm nửa khoảng nên ≤ ceil(log2 n)+1."],
    "def dem_so_sanh(xs, x):\n    lo, hi, dem = 0, len(xs) - 1, 0\n    while lo <= hi:\n        mid = (lo + hi) // 2\n        dem += 1\n        if xs[mid] == x:\n            return dem\n        if xs[mid] < x:\n            lo = mid + 1\n        else:\n            hi = mid - 1\n    return dem",
    "Mỗi bước giảm nửa khoảng nên số so sánh ≤ ceil(log₂ n)+1.",
    "O(log n).",
    khung="def dem_so_sanh(xs, x):\n    # viết code ở đây\n    pass",
    vi_du_test="assert dem_so_sanh([], 1) == 0\nassert dem_so_sanh(list(range(15)), 7) == 1\nassert dem_so_sanh(list(range(15)), 14) <= 5\nassert dem_so_sanh(list(range(15)), 0) <= 5\nprint(\"OK\")",
    test_an="import random\nrng = random.Random(0)\nxs = sorted(rng.sample(range(10000), 1023))\nassert all(dem_so_sanh(xs, xs[i]) <= 11 for i in range(0, 1023, 37))\nprint(\"OK\")",
)

# ===== Module 2: Chứng minh đúng =====
bai(
    7, "Bất biến vòng lặp tìm kiếm nhị phân", "chung-minh", "chung-minh", "de",
    "Phát biểu và chứng minh bất biến vòng lặp của tìm kiếm nhị phân: nếu x có trong mảng thì vị trí của nó luôn nằm trong đoạn [lo, hi].",
    ["Chứng minh ba phần: khởi tạo, duy trì, kết thúc.", "Khi xs[mid] < x, bỏ nửa trái; ngược lại bỏ nửa phải.", "Kết thúc khi lo > hi: đoạn rỗng, x không có."],
    "Bất biến: nếu x có trong xs thì vị trí của nó nằm trong [lo, hi]. Khởi tạo [0, n-1] đúng. Duy trì: nếu xs[mid] < x thì mọi vị trí ≤ mid không thể chứa x, đặt lo = mid+1; nếu xs[mid] > x thì đặt hi = mid-1. Kết thúc: nếu tìm thấy, trả về; nếu lo > hi, đoạn rỗng nên x không có.",
    "Chứng minh bằng bất biến vòng lặp (khởi tạo, duy trì, kết thúc).",
    "O(log n).",
    [{"y": "Phát biểu bất biến đúng", "diem": 3}, {"y": "Chứng minh khởi tạo và duy trì", "diem": 4}, {"y": "Chứng minh kết thúc", "diem": 3}],
    lien_quan=[{"ten": "Tìm kiếm nhị phân", "trang": "/thuat-toan/"}],
)

bai(
    8, "Quy nạp tổng 1..n", "chung-minh", "chung-minh", "de",
    "Chứng minh `1+2+...+n = n(n+1)/2` bằng quy nạp.",
    ["Cơ sở n=1.", "Giả thiết đúng tới n, xét n+1.", "Cộng thêm n+1 và rút gọn."],
    "Cơ sở: n=1, 1=1·2/2. Giả sử đúng tới n. Với n+1: n(n+1)/2+(n+1)=(n+1)(n+2)/2. Vậy đúng với mọi n≥1.",
    "Quy nạp toán học.",
    "O(1) để tính tổng.",
    [{"y": "Cơ sở đúng", "diem": 3}, {"y": "Bước quy nạp đúng", "diem": 5}, {"y": "Kết luận", "diem": 2}],
)

bai(
    9, "Exchange argument cho interval scheduling", "chung-minh", "chung-minh", "vua",
    "Chứng minh tham lam chọn cuộc họp kết thúc sớm nhất cho số cuộc họp không chồng tối đa.",
    ["So nghiệm tham lam với một nghiệm tối ưu.", "Thay cuộc đầu tiên của tối ưu bằng cuộc tham lam.", "Chứng minh thay không làm giảm số cuộc."],
    "Gọi g là cuộc kết thúc sớm nhất, O là nghiệm tối ưu. Nếu O không chứa g, thay cuộc đầu tiên của O bằng g; vì g kết thúc không muộn hơn, các cuộc sau vẫn tương thích, số cuộc không giảm. Lặp lại cho phần còn lại, ta được nghiệm tham lam có cùng số cuộc với O.",
    "Exchange argument.",
    "O(n log n) do sắp xếp.",
    [{"y": "Nêu nghiệm tham lam và tối ưu", "diem": 3}, {"y": "Thay cuộc đầu không giảm số cuộc", "diem": 5}, {"y": "Kết luận tối ưu", "diem": 2}],
)

bai(
    10, "Phản ví dụ tham lam đổi tiền", "chung-minh", "chung-minh", "vua",
    "Cho mệnh giá `[1,3,4]`, số tiền 6. Tham lam chọn đồng lớn nhất trước cho mấy đồng? Tối ưu là mấy? Kết luận gì?",
    ["Tham lam: 4, rồi 1, rồi 1.", "Tối ưu: 3+3.", "Tìm bộ tiền mà tham lam không tối ưu."],
    "Tham lam: 4+1+1 = 3 đồng. Tối ưu: 3+3 = 2 đồng. Vậy tham lam không tối ưu với bộ tiền không chính tắc; cần DP hoặc chứng minh bộ tiền chính tắc.",
    "Phản ví dụ đủ để bác bỏ mệnh đề 'tham lam luôn tối ưu'.",
    "O(số tiền × số mệnh giá) nếu dùng DP.",
    [{"y": "Tính đúng tham lam", "diem": 3}, {"y": "Tính đúng tối ưu", "diem": 4}, {"y": "Kết luận đúng", "diem": 3}],
)

bai(
    11, "Tối ưu con của edit distance", "chung-minh", "chung-minh", "vua",
    "Chứng minh công thức `dp[i][j] = min(dp[i-1][j]+1, dp[i][j-1]+1, dp[i-1][j-1]+(a[i-1]!=b[j-1]))`.",
    ["Xét thao tác cuối cùng để biến tiền tố a[0..i) thành b[0..j).", "Ba thao tác: xoá, chèn, thay/giữ.", "Mỗi thao tác giảm một chỉ số."],
    "Thao tác cuối là xoá a[i-1] → dp[i-1][j]+1; chèn b[j-1] → dp[i][j-1]+1; thay/giữ → dp[i-1][j-1]+(a[i-1]!=b[j-1]). Lấy min. Tối ưu con vì phần còn lại là bài toán nhỏ hơn cùng dạng.",
    "Chứng minh theo thao tác cuối (optimal substructure).",
    "O(n·m) thời gian.",
    [{"y": "Xét đủ ba thao tác cuối", "diem": 4}, {"y": "Lập công thức đúng", "diem": 4}, {"y": "Nêu tối ưu con", "diem": 2}],
)

bai(
    12, "Dijkstra cần cạnh không âm", "chung-minh", "chung-minh", "vua",
    "Cho phản ví dụ Dijkstra sai khi có cạnh âm: A→B=1, A→C=2, C→B=-2. Dijkstra làm gì và đường ngắn nhất thật là gì?",
    ["Dijkstra chốt B khi khoảng cách 1.", "Sau đó xét C=2, cập nhật B=0.", "Vì B đã chốt nên không cập nhật lại."],
    "Dijkstra lấy B với 1 và đánh dấu chốt; sau đó C=2, cập nhật B=0 nhưng B đã chốt nên bỏ qua. Đường thật A→C→B=0. Cạnh âm có thể làm đường đi ngắn hơn sau khi đã chốt, nên Dijkstra chỉ đúng với cạnh không âm.",
    "Phản ví dụ; với cạnh không âm, khi chốt u thì mọi đường khác tới u không thể ngắn hơn.",
    "O((V+E) log V) với heap.",
    [{"y": "Mô tả đúng Dijkstra chốt B", "diem": 3}, {"y": "Chỉ ra đường thật 0", "diem": 4}, {"y": "Kết luận điều kiện không âm", "diem": 3}],
    lien_quan=[{"ten": "BFS/DFS", "trang": "/thuat-toan/"}],
)

# ===== Module 3: Xác suất trong thuật toán =====
bai(
    13, "Kỳ vọng so sánh randomized quicksort", "xac-suat", "chung-minh", "vua",
    "Chứng minh kỳ vọng số so sánh của randomized quicksort là O(n log n).",
    ["Xác suất hai phần tử i<j được so sánh bằng 2/(j-i+1).", "Tổng theo mọi cặp.", "Đưa về tổng harmonic."],
    "E = Σ_{i<j} 2/(j-i+1) = 2Σ_{k=1}^{n-1}(n-k)/k < 2n H_n = O(n log n).",
    "i và j bị so sánh nếu chốt đầu tiên trong đoạn [i,j] là i hoặc j; xác suất 2/(j-i+1). Tổng theo cặp cho O(n log n).",
    "O(n log n) kỳ vọng.",
    [{"y": "Nêu xác suất so sánh cặp", "diem": 4}, {"y": "Lập tổng", "diem": 3}, {"y": "Đưa về harmonic", "diem": 3}],
    lien_quan=[{"ten": "Xác suất và thống kê", "trang": "/ai-engineer/ch07-xac-suat-thong-ke/01-xac-suat-va-mo-phong/"}],
)

bai(
    14, "Hệ số tải bảng băm", "xac-suat", "chung-minh", "de",
    "Bảng băm m ô, n khóa, hệ số tải α=n/m. Chứng minh tìm kiếm trung bình O(1+α) với nối chuỗi.",
    ["Mỗi ô có kỳ vọng n/m khóa.", "Tìm kiếm xem qua 1+α phần tử trung bình.", "Nếu α=O(1) thì O(1)."],
    "Mỗi ô có kỳ vọng α khóa; tìm kiếm trung bình 1+α; với α=O(1) là O(1).",
    "Tính kỳ vọng số khóa mỗi ô; cộng 1 lần so khóa.",
    "O(1+α) trung bình.",
    [{"y": "Nêu kỳ vọng mỗi ô", "diem": 4}, {"y": "Suy ra 1+α", "diem": 4}, {"y": "Kết luận α=O(1)", "diem": 2}],
)

bai(
    15, "Coupon collector", "xac-suat", "chung-minh", "vua",
    "Có n loại coupon, mỗi lần rút đều. Chứng minh kỳ vọng số lần để đủ bộ là n H_n.",
    ["Chia giai đoạn: đã có k loại, xác suất gặp loại mới (n-k)/n.", "Thời gian chờ kỳ vọng là nghịch đảo xác suất.", "Cộng n/(n-k)."],
    "E = Σ_{k=0}^{n-1} n/(n-k) = n Σ_{j=1}^n 1/j = n H_n.",
    "Mỗi giai đoạn là biến hình học với xác suất thành công (n-k)/n; kỳ vọng n/(n-k); cộng lại.",
    "O(n log n) kỳ vọng.",
    [{"y": "Chia giai đoạn đúng", "diem": 4}, {"y": "Kỳ vọng hình học", "diem": 3}, {"y": "Cộng thành nH_n", "diem": 3}],
)

bai(
    16, "Markov và Chebyshev", "xac-suat", "chung-minh", "vua",
    "Phát biểu và chứng minh bất đẳng thức Markov; dùng nó chứng minh Chebyshev.",
    ["Markov: P(X≥a) ≤ E[X]/a với X không âm.", "Chebyshev áp Markov cho (X-μ)².", "P(|X-μ|≥a) = P((X-μ)²≥a²)."],
    "Markov: E[X] = Σ x P(X=x) ≥ a P(X≥a). Chebyshev: P(|X-μ|≥a) = P((X-μ)²≥a²) ≤ E[(X-μ)²]/a² = σ²/a².",
    "Chứng minh trực tiếp từ tổng kỳ vọng.",
    "Không áp dụng cho thuật toán cụ thể.",
    [{"y": "Phát biểu Markov", "diem": 3}, {"y": "Chứng minh Markov", "diem": 3}, {"y": "Suy ra Chebyshev", "diem": 4}],
)

bai(
    17, "Reservoir sampling", "xac-suat", "chung-minh", "kho",
    "Chứng minh reservoir sampling với k=1 chọn mỗi phần tử với xác suất 1/n sau khi đọc n phần tử.",
    ["Quy nạp theo n.", "Khi gặp phần tử thứ n, thay với xác suất 1/n.", "Phần tử cũ sống sót nếu không bị thay."],
    "Sau n bước, mỗi phần tử có xác suất 1/n. Quy nạp: phần tử mới được chọn 1/n; phần tử cũ sống sót với (1-1/n) và trước đó có 1/(n-1), nhân lại 1/n.",
    "Quy nạp; đây là mẫu đều một phần tử.",
    "O(n) thời gian, O(1) bộ nhớ.",
    [{"y": "Nêu quy nạp", "diem": 3}, {"y": "Tính xác suất sống sót", "diem": 5}, {"y": "Kết luận 1/n", "diem": 2}],
)

bai(
    18, "Mô phỏng coupon collector", "xac-suat", "code", "vua",
    "Viết `so_lan_rut(n, seed)` mô phỏng rút đều tới khi đủ n loại; trả về số lần rút. Dùng `random.Random(seed)` để tái lập.",
    ["Dùng set để đếm loại đã gặp.", "Rút tới khi len(set)==n.", "Mỗi lần rút tăng biến đếm."],
    "import random\n\ndef so_lan_rut(n, seed):\n    rng = random.Random(seed)\n    thay = set()\n    dem = 0\n    while len(thay) < n:\n        thay.add(rng.randrange(n))\n        dem += 1\n    return dem",
    "Kỳ vọng n H_n; mô phỏng dùng để kiểm chứng trực giác.",
    "O(n log n) kỳ vọng.",
    khung="import random\n\ndef so_lan_rut(n, seed):\n    # viết code ở đây\n    pass",
    vi_du_test="assert so_lan_rut(1, 0) == 1\nassert so_lan_rut(5, 0) >= 5\nassert so_lan_rut(5, 0) <= 100\nassert so_lan_rut(5, 0) == so_lan_rut(5, 0)\nprint(\"OK\")",
    test_an="for seed in range(5):\n    assert so_lan_rut(10, seed) >= 10\nprint(\"OK\")",
)

# ===== Module 4: Đại số tuyến tính cho ML =====
bai(
    19, "Hạng và nghiệm Ax=b", "dai-so", "chung-minh", "vua",
    "Nêu điều kiện để `Ax=b` có nghiệm, vô nghiệm, vô số nghiệm theo hạng. Ví dụ `A=[[1,2],[2,4]]`, `b=[1,2]` và `b=[1,3]`.",
    ["So rank(A) với rank([A|b]).", "Nếu rank(A)=rank([A|b])=n thì duy nhất.", "Nếu rank < n thì vô số."],
    "Có nghiệm khi rank(A)=rank([A|b]); duy nhất khi rank=n; vô số khi rank<n. A có rank 1; b=[1,2] tương thích nên vô số; b=[1,3] không tương thích nên vô nghiệm.",
    "Định lý Kronecker-Capelli và số ẩn tự do.",
    "O(min(n,m)²·max(n,m)) nếu khử Gauss.",
    [{"y": "Nêu điều kiện có nghiệm", "diem": 4}, {"y": "Nêu điều kiện duy nhất/vô số", "diem": 3}, {"y": "Áp dụng đúng ví dụ", "diem": 3}],
    lien_quan=[{"ten": "Đại số tuyến tính", "trang": "/ai-engineer/ch05-dai-so-tuyen-tinh/03-he-phuong-trinh/"}],
)

bai(
    20, "Bình phương tối thiểu", "dai-so", "chung-minh", "vua",
    "Chứng minh nghiệm bình phương tối thiểu của `Ax≈b` thỏa `A^T A x = A^T b`.",
    ["Cực tiểu ||Ax-b||².", "Đạo hàm theo x: 2A^T(Ax-b).", "Cho gradient bằng 0."],
    "f(x)=||Ax-b||²; ∇f=2A^T(Ax-b); đặt 0 được A^T A x = A^T b. Nếu A^T A khả nghịch thì x=(A^T A)^{-1}A^T b.",
    "Tính gradient của dạng toàn phương và giải phương trình chuẩn.",
    "O(n²m + n³) nếu giải trực tiếp.",
    [{"y": "Lập hàm mất mát", "diem": 2}, {"y": "Tính gradient đúng", "diem": 4}, {"y": "Suy ra phương trình chuẩn", "diem": 4}],
    lien_quan=[{"ten": "Đại số tuyến tính", "trang": "/ai-engineer/ch05-dai-so-tuyen-tinh/03-he-phuong-trinh/"}],
)

bai(
    21, "PCA và trị riêng", "dai-so", "chung-minh", "vua",
    "Chứng minh hướng phương sai lớn nhất của dữ liệu đã chuẩn hóa là vector riêng ứng với trị riêng lớn nhất của ma trận hiệp phương sai.",
    ["Phương sai theo hướng đơn vị u là u^T Σ u.", "Dùng phân tích trị riêng Σ=QΛQ^T.", "Đổi biến v=Q^T u."],
    "Var(u)=u^TΣu. Với Σ=QΛQ^T, đặt v=Q^T u, Var=Σλ_i v_i² ≤ λ_max Σv_i²=λ_max; đạt khi v=e_max, tức u=q_max.",
    "Chặn trên bằng trị riêng lớn nhất; đẳng thức tại vector riêng.",
    "O(d³) nếu phân tích đầy đủ; SVD O(nd²).",
    [{"y": "Viết phương sai theo u", "diem": 3}, {"y": "Dùng trị riêng để chặn", "diem": 5}, {"y": "Kết luận hướng chính", "diem": 2}],
    lien_quan=[{"ten": "Trị riêng", "trang": "/ai-engineer/ch05-dai-so-tuyen-tinh/04-tri-rieng/"}],
)

bai(
    22, "Cosine bất biến với tỉ lệ dương", "dai-so", "chung-minh", "de",
    "Chứng minh `cos(αa,b)=cos(a,b)` với α>0. Nêu khi nào chuẩn hóa làm mất thông tin.",
    ["Tích vô hướng nhân α.", "Chuẩn của αa nhân α.", "Tỉ số không đổi."],
    "Tích vô hướng và chuẩn đều nhân α, nên tỉ số không đổi. Nếu độ lớn có nghĩa (số lần xem, doanh thu) thì chuẩn hóa bỏ mất thông tin; giữ độ lớn thành đặc trưng riêng.",
    "Tính trực tiếp; α dương để không đổi dấu.",
    "O(d).",
    [{"y": "Chứng minh bất biến", "diem": 5}, {"y": "Nêu trường hợp mất thông tin", "diem": 5}],
    lien_quan=[{"ten": "Vector và tích vô hướng", "trang": "/ai-engineer/ch05-dai-so-tuyen-tinh/01-vector/"}],
)

bai(
    23, "PCA bằng SVD", "dai-so", "code", "kho",
    "Viết `pca(X, k)` trả về `(Z, V)`: `Z` là dữ liệu đã chiếu `(n,k)`, `V` là `k` thành phần chính `(k,d)`, dùng SVD sau khi trừ trung bình.",
    ["Trừ trung bình từng cột.", "SVD của Xc.", "Lấy k hàng đầu của V^T và chiếu."],
    "import numpy as np\n\ndef pca(X, k):\n    X = np.asarray(X, dtype=float)\n    Xc = X - X.mean(axis=0)\n    _, _, Vt = np.linalg.svd(Xc, full_matrices=False)\n    V = Vt[:k]\n    return Xc @ V.T, V",
    "SVD Xc=U S V^T; các hàng V^T là hướng chính; chiếu Xc V.",
    "O(n d²) cho SVD gọn.",
    khung="import numpy as np\n\ndef pca(X, k):\n    # viết code ở đây\n    pass",
    vi_du_test="import numpy as np\nX = np.array([[1., 1.], [2., 2.], [3., 3.]])\nZ, V = pca(X, 1)\nassert Z.shape == (3, 1) and V.shape == (1, 2)\nassert np.allclose(Z.mean(0), 0)\nassert abs(abs(V[0, 0]) - abs(V[0, 1])) < 1e-8\nprint(\"OK\")",
    test_an="import numpy as np\nrng = np.random.default_rng(0)\nX = rng.normal(size=(50, 4))\nZ, V = pca(X, 2)\nassert Z.shape == (50, 2) and V.shape == (2, 4)\nassert np.allclose(V @ V.T, np.eye(2), atol=1e-8)\nprint(\"OK\")",
)

bai(
    24, "Số điều kiện", "dai-so", "chung-minh", "kho",
    "Định nghĩa số điều kiện `cond(A)=||A||·||A^{-1}||`. Giải thích vì sao hệ với cond lớn dễ sai; ví dụ `A=[[1,1],[1,1.0001]]`.",
    ["Sai số tương đối của x bị khuếch đại bởi cond(A).", "A gần suy biến thì A^{-1} lớn.", "Ví dụ hai cột gần phụ thuộc."],
    "Với Ax=b, nhiễu δb cho δx/x ≤ cond(A)·δb/b. A gần suy biến, cond lớn, nghiệm nhạy với nhiễu. A=[[1,1],[1,1.0001]] có định thức 1e-4 và cond lớn, nên thay đổi nhỏ ở b làm x đổi mạnh.",
    "Chặn sai số qua chuẩn ma trận.",
    "O(n³) để tính cond chính xác.",
    [{"y": "Định nghĩa cond", "diem": 3}, {"y": "Giải thích khuếch đại sai số", "diem": 4}, {"y": "Áp dụng ví dụ", "diem": 3}],
    lien_quan=[{"ten": "Ma trận và phép biến đổi", "trang": "/ai-engineer/ch05-dai-so-tuyen-tinh/02-ma-tran-la-bien-doi/"}],
)

# ===== Module 5: Tối ưu và hàm lồi =====
bai(
    25, "Kiểm tra hàm lồi", "toi-uu", "chung-minh", "de",
    "Kiểm tra `f(x)=x²`, `g(x)=x³`, `h(x)=|x|` có lồi trên R không; giải thích.",
    ["Dùng đạo hàm bậc hai nếu có.", "Hoặc dùng định nghĩa f(λx+(1-λ)y) ≤ λf(x)+(1-λ)f(y).", "|x| có điểm gãy tại 0 nhưng vẫn lồi."],
    "x² lồi vì f''=2>0. x³ không lồi vì f''=6x đổi dấu. |x| lồi theo định nghĩa (đồ thị nằm dưới dây cung).",
    "Kiểm tra đạo hàm bậc hai hoặc định nghĩa.",
    "Không áp dụng.",
    [{"y": "x² lồi", "diem": 3}, {"y": "x³ không lồi", "diem": 4}, {"y": "|x| lồi", "diem": 3}],
    lien_quan=[{"ten": "Tối ưu hóa", "trang": "/ai-engineer/ch08-toi-uu-hoa/01-gradient-descent/"}],
)

bai(
    26, "GD giảm hàm với bước 1/L", "toi-uu", "chung-minh", "vua",
    "Cho f L-trơn: `f(y) ≤ f(x)+∇f(x)^T(y-x)+(L/2)||y-x||²`. Chứng minh bước `x'=x-(1/L)∇f(x)` làm f giảm ít nhất `(1/(2L))||∇f(x)||²`.",
    ["Thay y=x' vào bất đẳng thức.", "Tính hai hạng tử.", "Cộng lại."],
    "Thay y=x': ∇^T(y-x)=-(1/L)||∇||²; (L/2)||y-x||²=(1/(2L))||∇||². Vậy f(x') ≤ f(x) - (1/(2L))||∇||².",
    "Descent lemma cho hàm L-trơn.",
    "O(1) mỗi bước.",
    [{"y": "Thay bước đúng", "diem": 3}, {"y": "Tính hai hạng tử", "diem": 4}, {"y": "Kết luận giảm", "diem": 3}],
    lien_quan=[{"ten": "Gradient descent", "trang": "/ai-engineer/ch08-toi-uu-hoa/01-gradient-descent/"}],
)

bai(
    27, "Tốc độ hội tụ hàm lồi mạnh", "toi-uu", "chung-minh", "kho",
    "Cho f μ-lồi mạnh, L-trơn. Nêu và chứng minh phác tốc độ `f(x_k)-f* ≤ (1-μ/L)^k (f(x_0)-f*)` với bước 1/L.",
    ["Kết hợp bất đẳng thức giảm và lồi mạnh.", "||∇f||² ≥ 2μ(f-f*).", "Lặp lại."],
    "Từ descent: f_{k+1} ≤ f_k - (1/(2L))||∇f_k||². Lồi mạnh: ||∇f_k||² ≥ 2μ(f_k-f*). Suy ra f_{k+1}-f* ≤ (1-μ/L)(f_k-f*); lặp k lần.",
    "Ghép descent lemma và bất đẳng thức lồi mạnh.",
    "O((L/μ) log(1/ε)) bước để đạt ε.",
    [{"y": "Nêu descent", "diem": 3}, {"y": "Dùng lồi mạnh", "diem": 4}, {"y": "Lặp ra tốc độ", "diem": 3}],
    lien_quan=[{"ten": "Learning rate", "trang": "/ai-engineer/ch08-toi-uu-hoa/02-learning-rate/"}],
)

bai(
    28, "SGD không lệch", "toi-uu", "chung-minh", "vua",
    "Chứng minh gradient mini-batch là ước lượng không lệch của gradient đầy đủ khi lấy mẫu đều.",
    ["Kỳ vọng của trung bình mẫu.", "Tuyến tính của kỳ vọng.", "Mỗi chỉ số được chọn với xác suất 1/n."],
    "E[1/|B| Σ_{i∈B} ∇f_i] = 1/|B| Σ E[∇f_i] = 1/n Σ ∇f_i = ∇f.",
    "Tính kỳ vọng của trung bình; không cần độc lập nếu lấy đều.",
    "O(|B|) mỗi bước.",
    [{"y": "Viết trung bình batch", "diem": 3}, {"y": "Dùng tuyến tính kỳ vọng", "diem": 4}, {"y": "Kết luận không lệch", "diem": 3}],
)

bai(
    29, "KKT bài toán đơn giản", "toi-uu", "chung-minh", "vua",
    "Giải `min x²` với ràng buộc `x≥1` bằng điều kiện KKT.",
    ["Lập Lagrangian L=x²+λ(1-x).", "Đạo hàm theo x: 2x-λ=0.", "Điều kiện bù λ(1-x)=0, λ≥0."],
    "L=x²+λ(1-x). 2x-λ=0; λ(1-x)=0. Nếu x>1 thì λ=0 → x=0, mâu thuẫn x≥1. Vậy x=1, λ=2.",
    "Điều kiện KKT cho bài toán lồi có ràng buộc.",
    "O(1).",
    [{"y": "Lập Lagrangian", "diem": 3}, {"y": "Đạo hàm và bù", "diem": 4}, {"y": "Kết luận x=1, λ=2", "diem": 3}],
)

bai(
    30, "Gradient descent hàm bậc hai", "toi-uu", "code", "de",
    "Viết `gd(A,b,x0,lr,steps)` chạy gradient descent cho `f(x)=1/2 x^T A x - b^T x`, trả về x sau `steps` bước.",
    ["Gradient là Ax-b.", "Cập nhật x = x - lr*(Ax-b).", "Lặp steps lần."],
    "import numpy as np\n\ndef gd(A, b, x0, lr, steps):\n    x = np.asarray(x0, dtype=float).copy()\n    A = np.asarray(A, dtype=float)\n    b = np.asarray(b, dtype=float)\n    for _ in range(steps):\n        x = x - lr * (A @ x - b)\n    return x",
    "Gradient của 1/2 x^T A x - b^T x là Ax-b; hội tụ nếu 0<lr<2/λ_max(A).",
    "O(steps·d²).",
    khung="import numpy as np\n\ndef gd(A, b, x0, lr, steps):\n    # viết code ở đây\n    pass",
    vi_du_test="import numpy as np\nA = np.array([[2., 0.], [0., 2.]])\nb = np.array([2., 4.])\nx = gd(A, b, np.zeros(2), 0.1, 100)\nassert np.allclose(x, [1., 2.], atol=1e-6)\nprint(\"OK\")",
    test_an="import numpy as np\nA = np.array([[4., 1.], [1., 3.]])\nb = np.array([1., 2.])\nx = gd(A, b, np.zeros(2), 0.1, 500)\nassert np.allclose(A @ x, b, atol=1e-6)\nprint(\"OK\")",
)

# ===== Module 6: Đồ án toán =====
bai(
    31, "Đồ án toán: chứng minh một pipeline học máy nhỏ", "do-an", "chung-minh", "kho",
    """Một pipeline: băm `n` người dùng vào `m` ô, lấy top-`k`, giải bình phương tối thiểu, rồi chạy gradient descent. Hãy chứng minh và trả lời 5 phần:

(a) Kỳ vọng va chạm khi băm và độ phức tạp của băm + top-k.
(b) Chứng minh nghiệm bình phương tối thiểu `A^T A x = A^T b`.
(c) Điều kiện gradient descent hội tụ và tốc độ khi hàm lồi mạnh.
(d) Rò rỉ dữ liệu ảnh hưởng thế nào tới đánh giá?
(e) Nêu 2 kiểm tra để tin pipeline trước khi triển khai.""",
    ["Dùng kết quả 5 module.", "Băm: α=n/m; top-k: heap O(n log k).", "Ghép các chứng minh đã học, không cần mới hoàn toàn."],
    """(a) Số cặp va chạm kỳ vọng C(n,2)/m ≈ n²/(2m); băm O(n), top-k bằng heap O(n log k), hoặc O(n + u log u) nếu đếm.
(b) f(x)=||Ax-b||²; ∇f=2A^T(Ax-b); đặt 0 được A^T A x=A^T b; nếu A^T A khả nghịch thì x=(A^T A)^{-1}A^T b.
(c) Với f L-trơn, bước 1/L giảm; nếu μ-lồi mạnh thì f_k-f* ≤ (1-μ/L)^k(f_0-f*); cần 0<lr<2/λ_max.
(d) Nếu chuẩn hóa/thống kê tính trên test hoặc đặc trưng chứa nhãn tương lai, điểm test cao giả tạo; phải chia train/val/test trước khi fit mọi bước.
(e) Kiểm tra bằng golden set và kiểm tra rò rỉ: so điểm trên dữ liệu sạch, kiểm tra từng đặc trưng có sẵn trước thời điểm dự đoán, và chạy kiểm tra gradient trước khi huấn luyện dài.""",
    "Ghép chứng minh của 5 module: xác suất, đại số, tối ưu, quy trình ML.",
    "Tổng hợp; chi phí chính là O(n log k + n d² + bước GD·d²).",
    [{"y": "Phần a: va chạm và độ phức tạp", "diem": 2}, {"y": "Phần b: phương trình chuẩn", "diem": 2}, {"y": "Phần c: điều kiện và tốc độ GD", "diem": 2}, {"y": "Phần d: rò rỉ dữ liệu", "diem": 2}, {"y": "Phần e: hai kiểm tra", "diem": 2}],
    lien_quan=[
        {"ten": "Xác suất", "trang": "/ai-engineer/ch07-xac-suat-thong-ke/01-xac-suat-va-mo-phong/"},
        {"ten": "Đại số tuyến tính", "trang": "/ai-engineer/ch05-dai-so-tuyen-tinh/03-he-phuong-trinh/"},
        {"ten": "Tối ưu hóa", "trang": "/ai-engineer/ch08-toi-uu-hoa/01-gradient-descent/"},
        {"ten": "Đồ án thuật toán", "trang": "/thuat-toan/"},
    ],
)


def main() -> None:
    assert len(B) == 31, len(B)
    so = [b["so"] for b in B]
    assert so == list(range(1, 32)), so
    RA.mkdir(parents=True, exist_ok=True)
    for b in B:
        ten = f"{b['so']:03d}-{b['module']}.yaml"
        with (RA / ten).open("w", encoding="utf-8") as f:
            yaml.safe_dump(b, f, allow_unicode=True, sort_keys=False, width=100)
    print("da ghi", len(B), "bai toan vao", RA)


if __name__ == "__main__":
    main()
