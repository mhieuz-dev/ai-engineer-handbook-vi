"""Sinh 40 bài thuật toán tự soạn vào src/data/thuat-toan/.

Chạy: .venv/bin/python scripts/thuat-toan/tao_bai.py
Mỗi bài có đề, ví dụ, ràng buộc, khung hàm, test ví dụ, test ẩn (có bài lớn),
lời giải, độ phức tạp, 3 nấc gợi ý và link dạng tương tự trên LeetCode.
Không cào, không chép đề LeetCode; bối cảnh và test đều viết mới.
"""
from __future__ import annotations

from pathlib import Path

import yaml

GOC = Path(__file__).resolve().parents[2]
RA = GOC / "src" / "data" / "thuat-toan"

DANG = {
    "mang-bang-bam": "Mảng và bảng băm",
    "hai-con-tro": "Hai con trỏ",
    "cua-so-truot": "Cửa sổ trượt",
    "ngan-xep": "Ngăn xếp",
    "tim-kiem-nhi-phan": "Tìm kiếm nhị phân",
    "danh-sach-lien-ket": "Danh sách liên kết",
    "cay": "Cây",
    "do-thi": "Đồ thị BFS/DFS",
    "heap": "Heap",
    "quy-hoach-dong": "Quy hoạch động",
    "quay-lui": "Quay lui",
    "tham-lam": "Tham lam / khoảng",
    "do-an": "Đồ án tốt nghiệp",
}

BAI: list[dict] = []


def bai(so, ten, dang, muc, de, vi_du, rang_buoc, khung, vi_du_test, test_an, loi_giai, phuc_tap, goi_y, tuong_tu):
    BAI.append(
        {
            "so": so,
            "ten": ten,
            "dang": dang,
            "muc": muc,
            "de": de.strip(),
            "vi_du": [{"vao": v, "ra": r} for v, r in vi_du],
            "rang_buoc": rang_buoc,
            "khung": khung.strip("\n"),
            "test_vi_du": vi_du_test.strip("\n"),
            "test_an": test_an.strip("\n"),
            "loi_giai": loi_giai.strip("\n"),
            "phuc_tap": phuc_tap,
            "goi_y": goi_y,
            "tuong_tu": {"ten": tuong_tu[0], "link": tuong_tu[1]},
        }
    )


# 1. Mảng và bảng băm
bai(
    1,
    "Hai đơn hàng đúng mã giảm giá",
    "mang-bang-bam",
    "de",
    """Một sàn thương mại điện tử có danh sách giá trị đơn hàng. Một mã giảm giá chỉ áp dụng khi chọn đúng hai đơn có tổng bằng giá trị mã. Cho `gia` là danh sách số nguyên và `tong`, trả về chỉ số của hai đơn (chỉ số nhỏ trước). Dữ liệu đảm bảo có đúng một cặp.""",
    [("[2, 7, 11, 15], 9", "[0, 1]"), ("[3, 2, 4], 6", "[1, 2]")],
    ["2 ≤ len(gia) ≤ 100 000", "Mỗi đơn có đúng một cặp."],
    """def hai_don(gia, tong):
    # trả về [i, j] với i < j
    pass""",
    """assert hai_don([2, 7, 11, 15], 9) == [0, 1]
assert hai_don([3, 2, 4], 6) == [1, 2]
print("OK")""",
    """gia = list(range(1, 50001)) + [10**9]
tong = 10**9 + 1
kq = hai_don(gia, tong)
assert kq[0] < kq[1] and gia[kq[0]] + gia[kq[1]] == tong
print("OK")""",
    """def hai_don(gia, tong):
    thay = {}
    for j, x in enumerate(gia):
        if tong - x in thay:
            return [thay[tong - x], j]
        thay[x] = j
    return []""",
    "O(n) thời gian, O(n) bộ nhớ.",
    ["Duyệt một lần, với mỗi đơn xem phần bù đã gặp chưa.", "Bảng băm lưu giá trị → chỉ số.", "for j, x: nếu tong-x trong thay thì trả [thay[tong-x], j]; thay[x]=j."],
    ("Two Sum", "https://leetcode.com/problems/two-sum/"),
)

bai(
    2,
    "Món bán chạy nhất trong tuần",
    "mang-bang-bam",
    "de",
    """Bạn có danh sách mã món đã bán trong tuần. Tìm mã xuất hiện nhiều nhất; nếu hòa thì chọn mã nhỏ hơn (theo thứ tự từ điển).""",
    [("[a, b, a, c, b, a]", "a"), ("[x, y, y, x]", "x")],
    ["1 ≤ len(ds) ≤ 100 000"],
    """def mon_ban_chay(ds):
    pass""",
    """assert mon_ban_chay(["a", "b", "a", "c", "b", "a"]) == "a"
assert mon_ban_chay(["x", "y", "y", "x"]) == "x"
print("OK")""",
    """import random
rng = random.Random(0)
ds = [f"m{i%50}" for i in range(20000)]
ds += ["m7"] * 500
rng.shuffle(ds)
assert mon_ban_chay(ds) == "m7"
print("OK")""",
    """from collections import Counter
def mon_ban_chay(ds):
    return min(Counter(ds).items(), key=lambda kv: (-kv[1], kv[0]))[0]""",
    "O(n) thời gian, O(k) bộ nhớ.",
    ["Đếm tần suất bằng dict.", "Khi hòa, so chuỗi để chọn nhỏ hơn.", "Dùng Counter rồi min theo (-đếm, tên)."],
    ("Top K Frequent Elements", "https://leetcode.com/problems/top-k-frequent-elements/"),
)

bai(
    3,
    "Gom đơn theo cùng bộ chữ cái",
    "mang-bang-bam",
    "vua",
    """Mỗi đơn có một mã gồm các chữ cái. Hai mã được coi là cùng nhóm nếu sắp lại chữ cái thì giống nhau. Trả về danh sách các nhóm (mỗi nhóm là danh sách mã). Thứ tự nhóm và thứ tự trong nhóm không quan trọng.""",
    [("[eat, tea, tan, ate, nat, bat]", "[[eat, tea, ate], [tan, nat], [bat]]")],
    ["1 ≤ len(ds) ≤ 20 000", "Mã chỉ gồm chữ thường."],
    """def nhom_don(ds):
    pass""",
    """kq = nhom_don(["eat", "tea", "tan", "ate", "nat", "bat"])
chuan = sorted(sorted(g) for g in kq)
assert chuan == sorted([["ate", "eat", "tea"], ["nat", "tan"], ["bat"]])
print("OK")""",
    """import random
rng = random.Random(1)
ds = ["".join(sorted(rng.sample("abcdef", 5))) for _ in range(5000)]
kq = nhom_don(ds)
assert sum(len(g) for g in kq) == len(ds)
print("OK")""",
    """from collections import defaultdict
def nhom_don(ds):
    nhom = defaultdict(list)
    for s in ds:
        nhom["".join(sorted(s))].append(s)
    return list(nhom.values())""",
    "O(n · k log k) với k là độ dài mã.",
    ["Hai mã cùng nhóm có cùng khóa sau khi sắp chữ.", "Dùng dict khóa → danh sách.", "Với mỗi mã, khóa = ''.join(sorted(s)); thêm vào nhóm."],
    ("Group Anagrams", "https://leetcode.com/problems/group-anagrams/"),
)

bai(
    4,
    "Chuỗi ngày giao hàng liên tiếp",
    "mang-bang-bam",
    "vua",
    """Cho danh sách các ngày giao hàng (số nguyên). Tìm độ dài chuỗi ngày liên tiếp dài nhất, không cần các ngày đứng cạnh nhau trong danh sách.""",
    [("[100, 4, 200, 1, 3, 2]", "4"), ("[0, 3, 7, 2, 5, 8, 4, 6, 0, 1]", "9")],
    ["0 ≤ len(ds) ≤ 100 000"],
    """def chuoi_lien_tiep(ds):
    pass""",
    """assert chuoi_lien_tiep([100, 4, 200, 1, 3, 2]) == 4
assert chuoi_lien_tiep([0, 3, 7, 2, 5, 8, 4, 6, 0, 1]) == 9
assert chuoi_lien_tiep([]) == 0
print("OK")""",
    """import random
rng = random.Random(2)
ds = list(range(-20000, 20001)) + [rng.randint(-30000, 30000) for _ in range(30000)]
assert chuoi_lien_tiep(ds) >= 40001
print("OK")""",
    """def chuoi_lien_tiep(ds):
    s = set(ds)
    dai = 0
    for x in s:
        if x - 1 not in s:
            y = x
            while y + 1 in s:
                y += 1
            dai = max(dai, y - x + 1)
    return dai""",
    "O(n) thời gian, O(n) bộ nhớ.",
    ["Đưa vào set để kiểm tra tồn tại O(1).", "Chỉ bắt đầu đếm từ số không có số liền trước.", "Mỗi phần tử được thăm tối đa hai lần."],
    ("Longest Consecutive Sequence", "https://leetcode.com/problems/longest-consecutive-sequence/"),
)

bai(
    5,
    "Đếm đoạn doanh thu đúng mục tiêu",
    "mang-bang-bam",
    "vua",
    """Cho dãy doanh thu theo ngày (có thể âm do hoàn tiền) và mục tiêu `k`. Đếm số đoạn con liên tiếp có tổng đúng bằng `k`.""",
    [("[1, 1, 1], 2", "2"), ("[1, -1, 0], 0", "3")],
    ["1 ≤ len(ds) ≤ 100 000", "Doanh thu có thể âm."],
    """def dem_doan_tong(ds, k):
    pass""",
    """assert dem_doan_tong([1, 1, 1], 2) == 2
assert dem_doan_tong([1, -1, 0], 0) == 3
print("OK")""",
    """import random
rng = random.Random(3)
ds = [rng.randint(-2, 2) for _ in range(20000)]
assert isinstance(dem_doan_tong(ds, 0), int)
print("OK")""",
    """from collections import defaultdict
def dem_doan_tong(ds, k):
    dem = defaultdict(int)
    dem[0] = 1
    tong = 0
    kq = 0
    for x in ds:
        tong += x
        kq += dem[tong - k]
        dem[tong] += 1
    return kq""",
    "O(n) thời gian, O(n) bộ nhớ.",
    ["Tổng đoạn i..j = tiền tố[j] - tiền tố[i-1].", "Đếm số tiền tố đã gặp bằng tong - k.", "Bảng băm tiền tố → số lần."],
    ("Subarray Sum Equals K", "https://leetcode.com/problems/subarray-sum-equals-k/"),
)

# 2. Hai con trỏ
bai(
    6,
    "Ghép cặp tình nguyện viên theo chiều cao",
    "hai-con-tro",
    "de",
    """Có hai danh sách chiều cao đã sắp tăng. Ghép mỗi cặp một người từ mỗi danh sách sao cho chênh lệch chiều cao nhỏ nhất. Trả về `[cao_a, cao_b]` của cặp tốt nhất; hòa thì chọn cặp có tổng nhỏ hơn.""",
    [("[150, 160, 170], [155, 165]", "[150, 155]")],
    ["1 ≤ len(a), len(b) ≤ 100 000", "Hai danh sách đã sắp tăng."],
    """def ghep_cap(a, b):
    pass""",
    """assert ghep_cap([150, 160, 170], [155, 165]) == [150, 155]
assert ghep_cap([1, 10], [5]) == [1, 5] or ghep_cap([1, 10], [5]) == [10, 5]
print("OK")""",
    """import random
rng = random.Random(4)
a = sorted(rng.sample(range(100000), 20000))
b = sorted(rng.sample(range(100000), 20000))
x, y = ghep_cap(a, b)
assert x in a and y in b
print("OK")""",
    """def ghep_cap(a, b):
    i = j = 0
    tot = None
    while i < len(a) and j < len(b):
        cap = [a[i], b[j]]
        if tot is None or abs(cap[0] - cap[1]) < abs(tot[0] - tot[1]) or (
            abs(cap[0] - cap[1]) == abs(tot[0] - tot[1]) and sum(cap) < sum(tot)
        ):
            tot = cap
        if a[i] < b[j]:
            i += 1
        else:
            j += 1
    return tot""",
    "O(len(a) + len(b)) thời gian.",
    ["Hai danh sách đã sắp nên dùng hai con trỏ.", "Mỗi bước tiến con trỏ ở bên nhỏ hơn.", "Cập nhật cặp tốt nhất trước khi tiến."],
    ("Two Sum II - Input Array Is Sorted", "https://leetcode.com/problems/two-sum-ii-input-array-is-sorted/"),
)

bai(
    7,
    "Xoá mã trùng trong danh sách đã sắp",
    "hai-con-tro",
    "de",
    """Danh sách mã đơn đã sắp tăng. Xoá các mã trùng tại chỗ sao cho mỗi mã còn đúng một lần ở đầu danh sách; trả về số phần tử còn lại `n`. Phần sau `n` không cần quan tâm.""",
    [("[1, 1, 2]", "2")],
    ["0 ≤ len(ds) ≤ 100 000"],
    """def xoa_trung(ds):
    # trả về số phần tử còn lại, sửa ds tại chỗ
    pass""",
    """ds = [1, 1, 2]
n = xoa_trung(ds)
assert n == 2 and ds[:n] == [1, 2]
print("OK")""",
    """ds = [1] * 50000 + [2] * 50000
n = xoa_trung(ds)
assert n == 2 and ds[:n] == [1, 2]
print("OK")""",
    """def xoa_trung(ds):
    if not ds:
        return 0
    n = 1
    for i in range(1, len(ds)):
        if ds[i] != ds[n - 1]:
            ds[n] = ds[i]
            n += 1
    return n""",
    "O(n) thời gian, O(1) bộ nhớ phụ.",
    ["Dùng một con trỏ ghi cho vị trí phần tử khác gần nhất.", "So với phần tử cuối đã ghi, không so với phần tử trước.", "Trả về độ dài mới."],
    ("Remove Duplicates from Sorted Array", "https://leetcode.com/problems/remove-duplicates-from-sorted-array/"),
)

bai(
    8,
    "Bể chứa nước lớn nhất",
    "hai-con-tro",
    "vua",
    """Cho chiều cao các tấm chắn đặt dọc. Chọn hai tấm để giữ được nhiều nước nhất; thể tích = khoảng cách × chiều cao thấp hơn. Trả về thể tích lớn nhất.""",
    [("[1, 8, 6, 2, 5, 4, 8, 3, 7]", "49")],
    ["2 ≤ len(cao) ≤ 100 000"],
    """def chua_nuoc(cao):
    pass""",
    """assert chua_nuoc([1, 8, 6, 2, 5, 4, 8, 3, 7]) == 49
assert chua_nuoc([1, 1]) == 1
print("OK")""",
    """import random
rng = random.Random(5)
cao = [rng.randint(0, 10000) for _ in range(50000)]
assert isinstance(chua_nuoc(cao), int)
print("OK")""",
    """def chua_nuoc(cao):
    i, j = 0, len(cao) - 1
    tot = 0
    while i < j:
        tot = max(tot, (j - i) * min(cao[i], cao[j]))
        if cao[i] < cao[j]:
            i += 1
        else:
            j -= 1
    return tot""",
    "O(n) thời gian, O(1) bộ nhớ.",
    ["Bắt đầu hai đầu, bề rộng lớn nhất.", "Di chuyển bên thấp hơn vì bên đó giới hạn chiều cao.", "Cập nhật diện tích trước khi di chuyển."],
    ("Container With Most Water", "https://leetcode.com/problems/container-with-most-water/"),
)

bai(
    9,
    "Kiểm tra câu phản hồi đối xứng",
    "hai-con-tro",
    "de",
    """Bỏ qua dấu câu, khoảng trắng và phân biệt hoa thường; kiểm tra chuỗi phản hồi có đọc xuôi ngược giống nhau không.""",
    [('"A man, a plan, a canal: Panama"', "true"), ('"xin chào"', "false")],
    ["0 ≤ len(s) ≤ 200 000"],
    """def la_doi_xung(s):
    pass""",
    """assert la_doi_xung("A man, a plan, a canal: Panama") is True
assert la_doi_xung("xin chào") is False
assert la_doi_xung("") is True
print("OK")""",
    """s = ("abc123" * 30000) + "cba321"
assert isinstance(la_doi_xung(s), bool)
print("OK")""",
    """def la_doi_xung(s):
    s = [c.lower() for c in s if c.isalnum()]
    i, j = 0, len(s) - 1
    while i < j:
        if s[i] != s[j]:
            return False
        i += 1
        j -= 1
    return True""",
    "O(n) thời gian, O(n) bộ nhớ (có thể O(1) nếu duyệt tại chỗ).",
    ["Lọc ký tự chữ/số, đưa về chữ thường.", "Hai con trỏ từ hai đầu.", "So từng cặp, khác thì false."],
    ("Valid Palindrome", "https://leetcode.com/problems/valid-palindrome/"),
)

# 3. Cửa sổ trượt
bai(
    10,
    "Đoạn bình luận dài nhất không lặp âm tiết",
    "cua-so-truot",
    "vua",
    """Cho chuỗi các âm tiết (mỗi âm tiết là một ký tự). Tìm độ dài đoạn con liên tiếp dài nhất mà không có âm tiết nào lặp lại.""",
    [('"abcabcbb"', "3"), ('"bbbbb"', "1")],
    ["0 ≤ len(s) ≤ 200 000"],
    """def doan_dai_nhat(s):
    pass""",
    """assert doan_dai_nhat("abcabcbb") == 3
assert doan_dai_nhat("bbbbb") == 1
assert doan_dai_nhat("") == 0
print("OK")""",
    """import string, random
rng = random.Random(6)
s = "".join(rng.choice(string.ascii_letters) for _ in range(50000))
assert isinstance(doan_dai_nhat(s), int)
print("OK")""",
    """def doan_dai_nhat(s):
    thay = {}
    trai = 0
    dai = 0
    for phai, c in enumerate(s):
        if c in thay and thay[c] >= trai:
            trai = thay[c] + 1
        thay[c] = phai
        dai = max(dai, phai - trai + 1)
    return dai""",
    "O(n) thời gian, O(k) bộ nhớ.",
    ["Cửa sổ trượt với vị trí gần nhất của mỗi ký tự.", "Khi gặp ký tự đã có trong cửa sổ, dời trái.", "Cập nhật độ dài sau mỗi bước."],
    ("Longest Substring Without Repeating Characters", "https://leetcode.com/problems/longest-substring-without-repeating-characters/"),
)

bai(
    11,
    "Tổng doanh thu cao nhất trong k ngày",
    "cua-so-truot",
    "de",
    """Cho doanh thu từng ngày và số ngày `k`. Tìm tổng lớn nhất của một đoạn liên tiếp đúng `k` ngày.""",
    [("[2, 1, 5, 1, 3, 2], 3", "9")],
    ["1 ≤ k ≤ len(ds) ≤ 100 000"],
    """def tong_cao_nhat(ds, k):
    pass""",
    """assert tong_cao_nhat([2, 1, 5, 1, 3, 2], 3) == 9
assert tong_cao_nhat([1], 1) == 1
print("OK")""",
    """import random
rng = random.Random(7)
ds = [rng.randint(-100, 100) for _ in range(100000)]
assert isinstance(tong_cao_nhat(ds, 500), int)
print("OK")""",
    """def tong_cao_nhat(ds, k):
    tong = sum(ds[:k])
    tot = tong
    for i in range(k, len(ds)):
        tong += ds[i] - ds[i - k]
        tot = max(tot, tong)
    return tot""",
    "O(n) thời gian, O(1) bộ nhớ phụ.",
    ["Tính tổng cửa sổ đầu.", "Trượt: cộng phần tử mới, trừ phần tử ra.", "Giữ tổng lớn nhất."],
    ("Maximum Average Subarray I", "https://leetcode.com/problems/maximum-average-subarray-i/"),
)

bai(
    12,
    "Đoạn ngắn nhất chứa đủ từ khóa",
    "cua-so-truot",
    "kho",
    """Cho chuỗi văn bản `s` và chuỗi từ khóa `t`. Tìm đoạn con ngắn nhất của `s` chứa đủ mọi ký tự của `t` (kể cả số lần). Không có thì trả về chuỗi rỗng.""",
    [('"ADOBECODEBANC", "ABC"', '"BANC"')],
    ["1 ≤ len(s), len(t) ≤ 100 000"],
    """def doan_ngan_nhat(s, t):
    pass""",
    """assert doan_ngan_nhat("ADOBECODEBANC", "ABC") == "BANC"
assert doan_ngan_nhat("a", "a") == "a"
assert doan_ngan_nhat("a", "aa") == ""
print("OK")""",
    """import random, string
rng = random.Random(8)
s = "".join(rng.choice("abcde") for _ in range(20000))
assert isinstance(doan_ngan_nhat(s, "abcde"), str)
print("OK")""",
    """from collections import Counter
def doan_ngan_nhat(s, t):
    can = Counter(t)
    thieu = len(t)
    trai = 0
    tot = None
    for phai, c in enumerate(s):
        if can[c] > 0:
            thieu -= 1
        can[c] -= 1
        while thieu == 0:
            if tot is None or phai - trai + 1 < len(tot):
                tot = s[trai : phai + 1]
            can[s[trai]] += 1
            if can[s[trai]] > 0:
                thieu += 1
            trai += 1
    return tot or ''""",
    "O(n + m) thời gian.",
    ["Đếm nhu cầu của t.", "Mở rộng phải tới khi đủ, rồi thu trái.", "Ghi đoạn ngắn nhất."],
    ("Minimum Window Substring", "https://leetcode.com/problems/minimum-window-substring/"),
)

bai(
    13,
    "Thay ký tự để đoạn lặp dài nhất",
    "cua-so-truot",
    "vua",
    """Cho chuỗi và số lần thay `k`. Được đổi tối đa `k` ký tự thành ký tự khác; tìm độ dài đoạn con dài nhất có thể toàn một ký tự.""",
    [('"AABABBA", 1', "4")],
    ["1 ≤ len(s) ≤ 100 000"],
    """def thay_dai_nhat(s, k):
    pass""",
    """assert thay_dai_nhat("AABABBA", 1) == 4
assert thay_dai_nhat("AAAA", 2) == 4
print("OK")""",
    """import random, string
rng = random.Random(9)
s = "".join(rng.choice("AB") for _ in range(50000))
assert isinstance(thay_dai_nhat(s, 3), int)
print("OK")""",
    """from collections import Counter
def thay_dai_nhat(s, k):
    dem = Counter()
    trai = 0
    tot = 0
    for phai, c in enumerate(s):
        dem[c] += 1
        while (phai - trai + 1) - max(dem.values()) > k:
            dem[s[trai]] -= 1
            trai += 1
        tot = max(tot, phai - trai + 1)
    return tot""",
    "O(n) thời gian.",
    ["Cửa sổ hợp lệ khi độ dài - tần suất lớn nhất ≤ k.", "Thu trái khi vượt k.", "Ghi độ dài lớn nhất."],
    ("Longest Repeating Character Replacement", "https://leetcode.com/problems/longest-repeating-character-replacement/"),
)

# 4. Ngăn xếp
bai(
    14,
    "Kiểm tra ngoặc trong công thức LaTeX",
    "ngan-xep",
    "de",
    """Cho chuỗi chỉ gồm các ngoặc `()[]{}`. Kiểm tra mọi ngoặc mở đều được đóng đúng thứ tự và đúng loại.""",
    [('"()[]{}"', "true"), ('"(]"', "false")],
    ["0 ≤ len(s) ≤ 200 000"],
    """def ngoac_hop_le(s):
    pass""",
    """assert ngoac_hop_le("()[]{}") is True
assert ngoac_hop_le("(]") is False
assert ngoac_hop_le("([)]") is False
assert ngoac_hop_le("") is True
print("OK")""",
    """s = "(" * 50000 + ")" * 50000
assert ngoac_hop_le(s) is True
print("OK")""",
    """def ngoac_hop_le(s):
    cap = {")": "(", "]": "[", "}": "{"}
    ngan = []
    for c in s:
        if c in "([{":
            ngan.append(c)
        elif c in cap:
            if not ngan or ngan.pop() != cap[c]:
                return False
    return not ngan""",
    "O(n) thời gian, O(n) bộ nhớ.",
    ["Dùng ngăn xếp cho ngoặc mở.", "Ngoặc đóng phải khớp đỉnh.", "Cuối cùng ngăn xếp phải rỗng."],
    ("Valid Parentheses", "https://leetcode.com/problems/valid-parentheses/"),
)

bai(
    15,
    "Giá lớn hơn gần nhất bên phải",
    "ngan-xep",
    "vua",
    """Cho dãy giá sản phẩm. Với mỗi ngày, tìm giá lớn hơn gần nhất về bên phải; không có thì -1.""",
    [("[2, 1, 2, 4, 3]", "[4, 2, 4, -1, -1]")],
    ["1 ≤ len(gia) ≤ 100 000"],
    """def lon_hon_ben_phai(gia):
    pass""",
    """assert lon_hon_ben_phai([2, 1, 2, 4, 3]) == [4, 2, 4, -1, -1]
print("OK")""",
    """import random
rng = random.Random(10)
gia = [rng.randint(0, 10000) for _ in range(50000)]
kq = lon_hon_ben_phai(gia)
assert len(kq) == len(gia)
print("OK")""",
    """def lon_hon_ben_phai(gia):
    kq = [-1] * len(gia)
    ngan = []
    for i, x in enumerate(gia):
        while ngan and gia[ngan[-1]] < x:
            kq[ngan.pop()] = x
        ngan.append(i)
    return kq""",
    "O(n) thời gian.",
    ["Duyệt trái sang phải với ngăn xếp chỉ số giảm dần.", "Khi gặp giá lớn hơn, gán cho các đỉnh nhỏ hơn.", "Đẩy chỉ số hiện tại vào."],
    ("Next Greater Element I", "https://leetcode.com/problems/next-greater-element-i/"),
)

bai(
    16,
    "Ngăn xếp có lấy giá nhỏ nhất",
    "ngan-xep",
    "vua",
    """Cài `MinStack` có `push(x)`, `pop()`, `top()`, `getMin()` đều O(1). `getMin` trả giá nhỏ nhất đang có.""",
    [('push(3), push(1), getMin(), pop(), getMin()', "1, 3")],
    ["Số thao tác ≤ 100 000"],
    """class MinStack:
    def __init__(self):
        pass
    def push(self, x):
        pass
    def pop(self):
        pass
    def top(self):
        pass
    def getMin(self):
        pass""",
    """s = MinStack()
s.push(3); s.push(1); s.push(2)
assert s.getMin() == 1
s.pop()
assert s.top() == 1 and s.getMin() == 1
print("OK")""",
    """import random
rng = random.Random(11)
s = MinStack()
gia = []
for _ in range(20000):
    x = rng.randint(-1000, 1000)
    s.push(x); gia.append(x)
    assert s.getMin() == min(gia)
print("OK")""",
    """class MinStack:
    def __init__(self):
        self.ngan = []
        self.nho = []
    def push(self, x):
        self.ngan.append(x)
        self.nho.append(x if not self.nho else min(x, self.nho[-1]))
    def pop(self):
        self.ngan.pop()
        self.nho.pop()
    def top(self):
        return self.ngan[-1]
    def getMin(self):
        return self.nho[-1]""",
    "O(1) cho mọi thao tác.",
    ["Lưu thêm ngăn xếp giá nhỏ nhất tới từng thời điểm.", "push: nhỏ = min(x, nhỏ trước).", "pop: bỏ cả hai."],
    ("Min Stack", "https://leetcode.com/problems/min-stack/"),
)

# 5. Tìm kiếm nhị phân
bai(
    17,
    "Tìm mã đơn trong danh sách đã sắp",
    "tim-kiem-nhi-phan",
    "de",
    """Cho danh sách mã đơn đã sắp tăng và một mã cần tìm. Trả về chỉ số hoặc -1. Phải chạy trong O(log n).""",
    [("[1, 3, 5, 7], 5", "2"), ("[1, 3, 5], 4", "-1")],
    ["0 ≤ len(ds) ≤ 100 000"],
    """def tim(ds, x):
    pass""",
    """assert tim([1, 3, 5, 7], 5) == 2
assert tim([1, 3, 5], 4) == -1
print("OK")""",
    """ds = list(range(0, 200000, 2))
assert tim(ds, 123456) == 61728
print("OK")""",
    """def tim(ds, x):
    lo, hi = 0, len(ds) - 1
    while lo <= hi:
        giua = (lo + hi) // 2
        if ds[giua] == x:
            return giua
        if ds[giua] < x:
            lo = giua + 1
        else:
            hi = giua - 1
    return -1""",
    "O(log n) thời gian.",
    ["Dùng lo/hi và vòng while.", "So phần tử giữa.", "Thu hẹp nửa chứa x."],
    ("Binary Search", "https://leetcode.com/problems/binary-search/"),
)

bai(
    18,
    "Chèn mã đơn vào đúng vị trí",
    "tim-kiem-nhi-phan",
    "de",
    """Cho danh sách đã sắp và giá trị x. Trả về vị trí chèn để danh sách vẫn sắp (nếu đã có x thì trả vị trí đầu tiên của x).""",
    [("[1, 3, 5, 6], 5", "2"), ("[1, 3, 5, 6], 2", "1")],
    ["0 ≤ len(ds) ≤ 100 000"],
    """def vi_tri_chen(ds, x):
    pass""",
    """assert vi_tri_chen([1, 3, 5, 6], 5) == 2
assert vi_tri_chen([1, 3, 5, 6], 2) == 1
assert vi_tri_chen([1, 3], 4) == 2
print("OK")""",
    """ds = list(range(0, 200000, 2))
assert vi_tri_chen(ds, 123457) == 61729
print("OK")""",
    """def vi_tri_chen(ds, x):
    lo, hi = 0, len(ds)
    while lo < hi:
        giua = (lo + hi) // 2
        if ds[giua] < x:
            lo = giua + 1
        else:
            hi = giua
    return lo""",
    "O(log n) thời gian.",
    ["Tìm vị trí đầu tiên có giá trị ≥ x.", "Dùng khoảng [lo, hi).", "Trả lo."],
    ("Search Insert Position", "https://leetcode.com/problems/search-insert-position/"),
)

bai(
    19,
    "Tìm đỉnh trong dãy tín hiệu",
    "tim-kiem-nhi-phan",
    "vua",
    """Cho dãy tín hiệu mà hai đầu nhỏ hơn phần tử bên trong. Tìm một chỉ số đỉnh (lớn hơn cả hai bên) trong O(log n).""",
    [("[1, 2, 3, 1]", "2")],
    ["1 ≤ len(ds) ≤ 100 000", "Có ít nhất một đỉnh."],
    """def tim_dinh(ds):
    pass""",
    """ds = [1, 2, 3, 1]
i = tim_dinh(ds)
assert ds[i] > ds[i - 1] and ds[i] > ds[i + 1]
print("OK")""",
    """import random
rng = random.Random(12)
ds = sorted(rng.sample(range(100000), 20000)) + sorted(rng.sample(range(100000), 20000), reverse=True)
i = tim_dinh(ds)
assert ds[i] >= ds[i-1] and ds[i] >= ds[i+1]
print("OK")""",
    """def tim_dinh(ds):
    lo, hi = 0, len(ds) - 1
    while lo < hi:
        giua = (lo + hi) // 2
        if ds[giua] < ds[giua + 1]:
            lo = giua + 1
        else:
            hi = giua
    return lo""",
    "O(log n) thời gian.",
    ["So giữa với bên phải để biết đang lên hay xuống.", "Đi về phía dốc lên.", "Khi lo == hi là đỉnh."],
    ("Find Peak Element", "https://leetcode.com/problems/find-peak-element/"),
)

bai(
    20,
    "Chọn tốc độ ăn tối thiểu",
    "tim-kiem-nhi-phan",
    "vua",
    """Có các đống dữ liệu với khối lượng cho trước. Mỗi giờ chọn một đống và ăn tối đa `v` đơn vị; đống còn thì giờ sau ăn tiếp. Tìm `v` nhỏ nhất để ăn hết trong `h` giờ.""",
    [("[3, 6, 7, 11], 8", "4")],
    ["1 ≤ len(dong) ≤ 100 000", "1 ≤ h ≤ 10^9"],
    """def toc_do_nho_nhat(dong, h):
    pass""",
    """assert toc_do_nho_nhat([3, 6, 7, 11], 8) == 4
assert toc_do_nho_nhat([30, 11, 23, 4, 20], 5) == 30
print("OK")""",
    """import random
rng = random.Random(13)
dong = [rng.randint(1, 10**9) for _ in range(20000)]
h = len(dong) + 5000
v = toc_do_nho_nhat(dong, h)
assert sum((x + v - 1) // v for x in dong) <= h
print("OK")""",
    """def toc_do_nho_nhat(dong, h):
    lo, hi = 1, max(dong)
    while lo < hi:
        giua = (lo + hi) // 2
        if sum((x + giua - 1) // giua for x in dong) <= h:
            hi = giua
        else:
            lo = giua + 1
    return lo""",
    "O(n log max) thời gian.",
    ["Số giờ giảm khi tốc độ tăng: tìm nhị phân trên đáp án.", "Hàm kiểm tra: tổng ceil(x/v).", "Tìm v nhỏ nhất thỏa."],
    ("Koko Eating Bananas", "https://leetcode.com/problems/koko-eating-bananas/"),
)

# 6. Danh sách liên kết
bai(
    21,
    "Gộp hai hàng đợi in đã sắp",
    "danh-sach-lien-ket",
    "de",
    """Hai hàng đợi in là hai danh sách liên kết đã sắp tăng. Gộp thành một danh sách đã sắp và trả về đầu danh sách.""",
    [("[1, 2, 4], [1, 3, 4]", "[1, 1, 2, 3, 4, 4]")],
    ["0 ≤ số nút mỗi danh sách ≤ 50 000"],
    """class Nut:
    def __init__(self, gia, tiep=None):
        self.gia = gia
        self.tiep = tiep

def gop(a, b):
    pass""",
    """def tao(xs):
    dau = None
    for x in reversed(xs):
        dau = Nut(x, dau)
    return dau
def ra(n):
    ds = []
    while n:
        ds.append(n.gia); n = n.tiep
    return ds
assert ra(gop(tao([1,2,4]), tao([1,3,4]))) == [1,1,2,3,4,4]
print("OK")""",
    """def tao(xs):
    dau = None
    for x in reversed(xs):
        dau = Nut(x, dau)
    return dau
def ra(n):
    ds = []
    while n:
        ds.append(n.gia); n = n.tiep
    return ds
a = tao(list(range(0, 20000, 2)))
b = tao(list(range(1, 20000, 2)))
assert ra(gop(a, b)) == list(range(20000))
print("OK")""",
    """class Nut:
    def __init__(self, gia, tiep=None):
        self.gia = gia
        self.tiep = tiep

def gop(a, b):
    gia = Nut(0)
    cuoi = gia
    while a and b:
        if a.gia <= b.gia:
            cuoi.tiep, a = a, a.tiep
        else:
            cuoi.tiep, b = b, b.tiep
        cuoi = cuoi.tiep
    cuoi.tiep = a or b
    return gia.tiep""",
    "O(n + m) thời gian.",
    ["Dùng nút giả làm đầu.", "So hai đầu, nối nút nhỏ hơn.", "Cuối cùng nối phần còn lại."],
    ("Merge Two Sorted Lists", "https://leetcode.com/problems/merge-two-sorted-lists/"),
)

bai(
    22,
    "Đảo chiều danh sách đơn",
    "danh-sach-lien-ket",
    "de",
    """Cho đầu danh sách liên kết đơn, đảo chiều và trả về đầu mới.""",
    [("[1, 2, 3]", "[3, 2, 1]")],
    ["0 ≤ số nút ≤ 100 000"],
    """class Nut:
    def __init__(self, gia, tiep=None):
        self.gia = gia
        self.tiep = tiep

def dao(dau):
    pass""",
    """def tao(xs):
    d = None
    for x in reversed(xs): d = Nut(x, d)
    return d
def ra(n):
    ds = []
    while n: ds.append(n.gia); n = n.tiep
    return ds
assert ra(dao(tao([1,2,3]))) == [3,2,1]
print("OK")""",
    """def tao(xs):
    d = None
    for x in reversed(xs): d = Nut(x, d)
    return d
def ra(n):
    ds = []
    while n: ds.append(n.gia); n = n.tiep
    return ds
assert ra(dao(tao(list(range(30000))))) == list(reversed(range(30000)))
print("OK")""",
    """class Nut:
    def __init__(self, gia, tiep=None):
        self.gia = gia
        self.tiep = tiep

def dao(dau):
    truoc = None
    while dau:
        sau = dau.tiep
        dau.tiep = truoc
        truoc, dau = dau, sau
    return truoc""",
    "O(n) thời gian, O(1) bộ nhớ.",
    ["Lưu nút sau trước khi đổi liên kết.", "Trỏ nút hiện tại về trước.", "Tiến cả hai con trỏ."],
    ("Reverse Linked List", "https://leetcode.com/problems/reverse-linked-list/"),
)

bai(
    23,
    "Phát hiện vòng lặp trong nhật ký",
    "danh-sach-lien-ket",
    "vua",
    """Danh sách liên kết có thể bị nối vòng do lỗi ghi log. Kiểm tra xem danh sách có chu trình không, dùng O(1) bộ nhớ phụ.""",
    [("[3, 2, 0, -4] nối đuôi về nút 1", "true")],
    ["0 ≤ số nút ≤ 100 000"],
    """class Nut:
    def __init__(self, gia, tiep=None):
        self.gia = gia
        self.tiep = tiep

def co_vong(dau):
    pass""",
    """a = Nut(1); b = Nut(2); c = Nut(3)
a.tiep = b; b.tiep = c; c.tiep = b
assert co_vong(a) is True
x = Nut(1); y = Nut(2); x.tiep = y
assert co_vong(x) is False
print("OK")""",
    """a = Nut(0); cuoi = a
for i in range(1, 50000):
    cuoi.tiep = Nut(i); cuoi = cuoi.tiep
assert co_vong(a) is False
cuoi.tiep = a
assert co_vong(a) is True
print("OK")""",
    """class Nut:
    def __init__(self, gia, tiep=None):
        self.gia = gia
        self.tiep = tiep

def co_vong(dau):
    cham = nhanh = dau
    while nhanh and nhanh.tiep:
        cham = cham.tiep
        nhanh = nhanh.tiep.tiep
        if cham is nhanh:
            return True
    return False""",
    "O(n) thời gian, O(1) bộ nhớ.",
    ["Dùng hai con trỏ nhanh/chậm.", "Nếu có vòng, nhanh sẽ đuổi kịp chậm.", "Nếu nhanh tới cuối thì không có vòng."],
    ("Linked List Cycle", "https://leetcode.com/problems/linked-list-cycle/"),
)

# 7. Cây
bai(
    24,
    "Độ sâu cây quyết định",
    "cay",
    "de",
    """Cho gốc cây nhị phân biểu diễn các câu hỏi quyết định. Trả về độ sâu lớn nhất (số nút trên đường dài nhất).""",
    [("[3, 9, 20, null, null, 15, 7]", "3")],
    ["0 ≤ số nút ≤ 100 000"],
    """class Nut:
    def __init__(self, gia, trai=None, phai=None):
        self.gia = gia
        self.trai = trai
        self.phai = phai

def do_sau(goc):
    pass""",
    """n = Nut(3, Nut(9), Nut(20, Nut(15), Nut(7)))
assert do_sau(n) == 3
assert do_sau(None) == 0
print("OK")""",
    """goc = Nut(0)
nut = goc
for i in range(1, 20000):
    nut.trai = Nut(i); nut = nut.trai
assert do_sau(goc) == 20000
print("OK")""",
    """class Nut:
    def __init__(self, gia, trai=None, phai=None):
        self.gia = gia
        self.trai = trai
        self.phai = phai

def do_sau(goc):
    if not goc:
        return 0
    ngan = [(goc, 1)]
    tot = 0
    while ngan:
        n, d = ngan.pop()
        tot = max(tot, d)
        if n.trai:
            ngan.append((n.trai, d + 1))
        if n.phai:
            ngan.append((n.phai, d + 1))
    return tot""",
    "O(n) thời gian. Đệ quy sâu 20 000 có thể chạm giới hạn; bản lặp dùng ngăn xếp an toàn hơn.",
    ["Độ sâu = 1 + max(độ sâu trái, phải).", "Gốc rỗng có độ sâu 0.", "Có thể duyệt lặp bằng ngăn xếp."],
    ("Maximum Depth of Binary Tree", "https://leetcode.com/problems/maximum-depth-of-binary-tree/"),
)

bai(
    25,
    "Lật cây thư mục dữ liệu",
    "cay",
    "de",
    """Cho gốc cây nhị phân, đổi chỗ toàn bộ cây con trái và phải, trả về gốc.""",
    [("[4, 2, 7, 1, 3, 6, 9]", "[4, 7, 2, 9, 6, 3, 1]")],
    ["0 ≤ số nút ≤ 100 000"],
    """class Nut:
    def __init__(self, gia, trai=None, phai=None):
        self.gia = gia
        self.trai = trai
        self.phai = phai

def lat(goc):
    pass""",
    """def ra(n):
    if not n: return []
    return [n.gia] + ra(n.trai) + ra(n.phai)
g = Nut(4, Nut(2, Nut(1), Nut(3)), Nut(7, Nut(6), Nut(9)))
assert ra(lat(g)) == [4,7,9,6,2,3,1]
print("OK")""",
    """g = Nut(0); nut = g
for i in range(1, 15000): nut.trai = Nut(i); nut = nut.trai
lat(g)
assert g.trai is None
print("OK")""",
    """class Nut:
    def __init__(self, gia, trai=None, phai=None):
        self.gia = gia
        self.trai = trai
        self.phai = phai

def lat(goc):
    if not goc:
        return None
    ngan = [goc]
    while ngan:
        n = ngan.pop()
        n.trai, n.phai = n.phai, n.trai
        if n.trai:
            ngan.append(n.trai)
        if n.phai:
            ngan.append(n.phai)
    return goc""",
    "O(n) thời gian.",
    ["Đổi hai con của mỗi nút.", "Đệ quy xuống hai bên.", "Trả gốc sau khi đổi."],
    ("Invert Binary Tree", "https://leetcode.com/problems/invert-binary-tree/"),
)

bai(
    26,
    "Kiểm tra cây tìm kiếm nhị phân",
    "cay",
    "vua",
    """Cho gốc cây nhị phân, kiểm tra xem nó có phải cây tìm kiếm nhị phân (trái < gốc < phải, đúng cho mọi nút).""",
    [("[2, 1, 3]", "true"), ("[5, 1, 4, null, null, 3, 6]", "false")],
    ["0 ≤ số nút ≤ 100 000"],
    """class Nut:
    def __init__(self, gia, trai=None, phai=None):
        self.gia = gia
        self.trai = trai
        self.phai = phai

def la_bst(goc):
    pass""",
    """assert la_bst(Nut(2, Nut(1), Nut(3))) is True
assert la_bst(Nut(5, Nut(1), Nut(4, Nut(3), Nut(6)))) is False
print("OK")""",
    """g = Nut(0); nut = g
for i in range(1, 20000): nut.phai = Nut(i); nut = nut.phai
assert la_bst(g) is True
print("OK")""",
    """class Nut:
    def __init__(self, gia, trai=None, phai=None):
        self.gia = gia
        self.trai = trai
        self.phai = phai

def la_bst(goc):
    ngan = []
    truoc = None
    nut = goc
    while ngan or nut:
        while nut:
            ngan.append(nut)
            nut = nut.trai
        nut = ngan.pop()
        if truoc is not None and nut.gia <= truoc:
            return False
        truoc = nut.gia
        nut = nut.phai
    return True""",
    "O(n) thời gian, O(h) bộ nhớ.",
    ["Duyệt giữa (inorder) phải tăng nghiêm ngặt.", "Có thể dùng khoảng (min, max) truyền xuống.", "Cẩn thận nhánh phải của nút nhỏ."],
    ("Validate Binary Search Tree", "https://leetcode.com/problems/validate-binary-search-tree/"),
)

bai(
    27,
    "Duyệt cây theo từng mức",
    "cay",
    "vua",
    """Trả về danh sách các mức của cây nhị phân, mỗi mức là danh sách giá trị từ trái sang phải.""",
    [("[3, 9, 20, null, null, 15, 7]", "[[3], [9, 20], [15, 7]]")],
    ["0 ≤ số nút ≤ 100 000"],
    """class Nut:
    def __init__(self, gia, trai=None, phai=None):
        self.gia = gia
        self.trai = trai
        self.phai = phai

def theo_muc(goc):
    pass""",
    """g = Nut(3, Nut(9), Nut(20, Nut(15), Nut(7)))
assert theo_muc(g) == [[3], [9, 20], [15, 7]]
assert theo_muc(None) == []
print("OK")""",
    """g = Nut(0); nut = g
for i in range(1, 20000): nut.trai = Nut(i); nut = nut.trai
kq = theo_muc(g)
assert len(kq) == 20000
print("OK")""",
    """from collections import deque
class Nut:
    def __init__(self, gia, trai=None, phai=None):
        self.gia = gia
        self.trai = trai
        self.phai = phai

def theo_muc(goc):
    if not goc:
        return []
    kq = []
    hang = deque([goc])
    while hang:
        muc = []
        for _ in range(len(hang)):
            n = hang.popleft()
            muc.append(n.gia)
            if n.trai: hang.append(n.trai)
            if n.phai: hang.append(n.phai)
        kq.append(muc)
    return kq""",
    "O(n) thời gian.",
    ["Dùng hàng đợi BFS.", "Mỗi vòng xử lý đúng số nút của một mức.", "Đưa con vào hàng đợi."],
    ("Binary Tree Level Order Traversal", "https://leetcode.com/problems/binary-tree-level-order-traversal/"),
)

# 8. Đồ thị BFS/DFS
bai(
    28,
    "Robot tìm đường ngắn nhất trong kho",
    "do-thi",
    "vua",
    """Kho là lưới `0` (đi được) và `1` (kệ hàng). Robot đi 4 hướng, từ (0,0) tới (n-1,m-1). Trả về số bước ít nhất hoặc -1.""",
    [("[[0,0,0],[1,1,0],[1,1,0]]", "4")],
    ["1 ≤ n, m ≤ 200"],
    """from collections import deque

def duong_ngan_nhat(luoi):
    pass""",
    """assert duong_ngan_nhat([[0,0,0],[1,1,0],[1,1,0]]) == 4
assert duong_ngan_nhat([[0,1],[1,0]]) == -1
print("OK")""",
    """n = 200
luoi = [[0] * n for _ in range(n)]
assert duong_ngan_nhat(luoi) == 2 * n - 2
print("OK")""",
    """from collections import deque
def duong_ngan_nhat(luoi):
    n, m = len(luoi), len(luoi[0])
    if luoi[0][0] or luoi[-1][-1]:
        return -1
    hang = deque([(0, 0, 0)])
    thay = {(0, 0)}
    while hang:
        x, y, d = hang.popleft()
        if (x, y) == (n - 1, m - 1):
            return d
        for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
            a, b = x + dx, y + dy
            if 0 <= a < n and 0 <= b < m and luoi[a][b] == 0 and (a, b) not in thay:
                thay.add((a, b))
                hang.append((a, b, d + 1))
    return -1""",
    "O(n·m) thời gian.",
    ["BFS cho đường ngắn nhất trên lưới không trọng số.", "Đánh dấu đã thăm khi đưa vào hàng đợi.", "Kiểm tra ô đầu/cuối bị chặn."],
    ("Shortest Path in Binary Matrix", "https://leetcode.com/problems/shortest-path-in-binary-matrix/"),
)

bai(
    29,
    "Đếm ổ dữ liệu rời rạc",
    "do-thi",
    "vua",
    """Lưới `1` là điểm dữ liệu, `0` là trống. Đếm số vùng liên thông 4 hướng của các điểm dữ liệu.""",
    [("[[1,1,0],[1,0,0],[0,0,1]]", "2")],
    ["1 ≤ n, m ≤ 300"],
    """def dem_vung(luoi):
    pass""",
    """assert dem_vung([[1,1,0],[1,0,0],[0,0,1]]) == 2
assert dem_vung([[0]]) == 0
print("OK")""",
    """n = 300
luoi = [[1] * n for _ in range(n)]
assert dem_vung(luoi) == 1
print("OK")""",
    """def dem_vung(luoi):
    n, m = len(luoi), len(luoi[0])
    dem = 0
    for i in range(n):
        for j in range(m):
            if luoi[i][j] != 1:
                continue
            dem += 1
            ngan = [(i, j)]
            luoi[i][j] = 0
            while ngan:
                x, y = ngan.pop()
                for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
                    a, b = x + dx, y + dy
                    if 0 <= a < n and 0 <= b < m and luoi[a][b] == 1:
                        luoi[a][b] = 0
                        ngan.append((a, b))
    return dem""",
    "O(n·m) thời gian.",
    ["Duyệt từng ô, gặp 1 thì tăng đếm.", "DFS/BFS xoá cả vùng.", "Không cần đệ quy, dùng ngăn xếp."],
    ("Number of Islands", "https://leetcode.com/problems/number-of-islands/"),
)

bai(
    30,
    "Kiểm tra thứ tự học các môn",
    "do-thi",
    "vua",
    """Có `n` môn và danh sách cặp `[a, b]` nghĩa là phải học `b` trước `a`. Kiểm tra có thể học hết không (đồ thị không có chu trình).""",
    [("2, [[1,0]]", "true"), ("2, [[1,0],[0,1]]", "false")],
    ["1 ≤ n ≤ 100 000"],
    """def hoc_duoc(n, tien_quyet):
    pass""",
    """assert hoc_duoc(2, [[1,0]]) is True
assert hoc_duoc(2, [[1,0],[0,1]]) is False
print("OK")""",
    """n = 50000
ds = [[i, i-1] for i in range(1, n)]
assert hoc_duoc(n, ds) is True
print("OK")""",
    """from collections import deque
def hoc_duoc(n, tien_quyet):
    ke = [[] for _ in range(n)]
    vao = [0] * n
    for a, b in tien_quyet:
        ke[b].append(a)
        vao[a] += 1
    hang = deque(i for i in range(n) if vao[i] == 0)
    dem = 0
    while hang:
        x = hang.popleft()
        dem += 1
        for y in ke[x]:
            vao[y] -= 1
            if vao[y] == 0:
                hang.append(y)
    return dem == n""",
    "O(n + e) thời gian.",
    ["Đếm bậc vào của từng môn.", "Kahn: bắt đầu từ môn bậc vào 0.", "Nếu duyệt đủ n môn thì không có chu trình."],
    ("Course Schedule", "https://leetcode.com/problems/course-schedule/"),
)

bai(
    31,
    "Thời gian làm lạnh kho hàng",
    "do-thi",
    "kho",
    """Lưới có 0 (trống), 1 (cam tươi), 2 (cam hỏng). Mỗi phút cam hỏng lây 4 hướng. Trả về số phút tới khi không còn cam tươi, hoặc -1 nếu không thể.""",
    [("[[2,1,1],[1,1,0],[0,1,1]]", "4")],
    ["1 ≤ n, m ≤ 200"],
    """from collections import deque

def phut_lanh(luoi):
    pass""",
    """assert phut_lanh([[2,1,1],[1,1,0],[0,1,1]]) == 4
assert phut_lanh([[2,1],[1,1]]) == 2
assert phut_lanh([[2,0,0]]) == 0
print("OK")""",
    """n = 200
luoi = [[2] + [1] * (n - 1) for _ in range(n)]
assert phut_lanh(luoi) >= 0
print("OK")""",
    """from collections import deque
def phut_lanh(luoi):
    n, m = len(luoi), len(luoi[0])
    hang = deque()
    tuoi = 0
    for i in range(n):
        for j in range(m):
            if luoi[i][j] == 2:
                hang.append((i, j, 0))
            elif luoi[i][j] == 1:
                tuoi += 1
    if tuoi == 0:
        return 0
    while hang:
        x, y, p = hang.popleft()
        for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
            a, b = x + dx, y + dy
            if 0 <= a < n and 0 <= b < m and luoi[a][b] == 1:
                luoi[a][b] = 2
                tuoi -= 1
                if tuoi == 0:
                    return p + 1
                hang.append((a, b, p + 1))
    return -1""",
    "O(n·m) thời gian.",
    ["BFS nhiều nguồn từ mọi cam hỏng.", "Đếm số cam tươi còn lại.", "Trả phút khi hết cam tươi."],
    ("Rotting Oranges", "https://leetcode.com/problems/rotting-oranges/"),
)

# 9. Heap
bai(
    32,
    "Top-k từ phổ biến trong phản hồi",
    "heap",
    "vua",
    """Cho danh sách từ và số `k`. Trả về `k` từ xuất hiện nhiều nhất, sắp theo số lần giảm dần; hòa thì theo thứ tự từ điển tăng.""",
    [("[i, love, ai, i, love, coding], 2", "[i, love]")],
    ["1 ≤ k ≤ số từ khác nhau"],
    """import heapq

def top_k(ds, k):
    pass""",
    """assert top_k(["i","love","ai","i","love","coding"], 2) == ["i","love"]
assert top_k(["a","b","a","c","b","a"], 2) == ["a","b"]
print("OK")""",
    """import random, string
rng = random.Random(14)
ds = [rng.choice(string.ascii_lowercase) for _ in range(100000)]
kq = top_k(ds, 5)
assert len(kq) == 5
print("OK")""",
    """from collections import Counter
import heapq
def top_k(ds, k):
    dem = Counter(ds)
    return [x for x in heapq.nsmallest(k, dem, key=lambda x: (-dem[x], x))]""",
    "O(n + u log u) với u là số từ khác nhau.",
    ["Đếm tần suất.", "Dùng heap k phần tử hoặc sắp xếp.", "Khóa (-đếm, từ) để hòa theo từ điển."],
    ("Top K Frequent Words", "https://leetcode.com/problems/top-k-frequent-words/"),
)

bai(
    33,
    "Phần tử lớn thứ k",
    "heap",
    "vua",
    """Cho dãy số và `k`, trả về phần tử lớn thứ `k` (không phải thứ k khác nhau).""",
    [("[3,2,1,5,6,4], 2", "5")],
    ["1 ≤ k ≤ len(ds) ≤ 100 000"],
    """import heapq

def lon_thu_k(ds, k):
    pass""",
    """assert lon_thu_k([3,2,1,5,6,4], 2) == 5
assert lon_thu_k([1], 1) == 1
print("OK")""",
    """import random
rng = random.Random(15)
ds = [rng.randint(-10**9, 10**9) for _ in range(100000)]
assert lon_thu_k(ds, 50000) == sorted(ds, reverse=True)[49999]
print("OK")""",
    """import heapq
def lon_thu_k(ds, k):
    return heapq.nlargest(k, ds)[-1]""",
    "O(n log k) thời gian.",
    ["Giữ heap k phần tử lớn nhất.", "Hoặc quickselect trung bình O(n).", "Đáp án là phần tử nhỏ nhất trong heap k."],
    ("Kth Largest Element in an Array", "https://leetcode.com/problems/kth-largest-element-in-an-array/"),
)

bai(
    34,
    "Gộp k hàng đợi đã sắp",
    "heap",
    "kho",
    """Có `k` danh sách đã sắp. Gộp thành một danh sách đã sắp.""",
    [("[[1,4,5],[1,3,4],[2,6]]", "[1,1,2,3,4,4,5,6]")],
    ["0 ≤ k ≤ 10 000"],
    """import heapq

def gop_k(ds):
    pass""",
    """assert gop_k([[1,4,5],[1,3,4],[2,6]]) == [1,1,2,3,4,4,5,6]
assert gop_k([]) == []
print("OK")""",
    """import random
rng = random.Random(16)
ds = [sorted(rng.randint(0, 10000) for _ in range(1000)) for _ in range(100)]
kq = gop_k(ds)
assert kq == sorted(sum(ds, []))
print("OK")""",
    """import heapq
def gop_k(ds):
    hang = []
    for i, a in enumerate(ds):
        if a:
            heapq.heappush(hang, (a[0], i, 0))
    kq = []
    while hang:
        x, i, j = heapq.heappop(hang)
        kq.append(x)
        if j + 1 < len(ds[i]):
            heapq.heappush(hang, (ds[i][j + 1], i, j + 1))
    return kq""",
    "O(N log k) với N là tổng số phần tử.",
    ["Đưa phần tử đầu của mỗi danh sách vào heap.", "Lấy nhỏ nhất, đẩy phần tử kế của danh sách đó.", "Lặp tới khi heap rỗng."],
    ("Merge k Sorted Lists", "https://leetcode.com/problems/merge-k-sorted-lists/"),
)

# 10. Quy hoạch động
bai(
    35,
    "Số cách leo cầu thang dữ liệu",
    "quy-hoach-dong",
    "de",
    """Mỗi bước leo 1 hoặc 2 bậc. Có bao nhiêu cách leo hết `n` bậc?""",
    [("3", "3")],
    ["1 ≤ n ≤ 45"],
    """def so_cach(n):
    pass""",
    """assert so_cach(3) == 3
assert so_cach(1) == 1
assert so_cach(2) == 2
print("OK")""",
    """assert so_cach(45) == 1836311903
print("OK")""",
    """def so_cach(n):
    a, b = 1, 1
    for _ in range(n):
        a, b = b, a + b
    return a""",
    "O(n) thời gian, O(1) bộ nhớ.",
    ["Cách leo n = cách leo n-1 + cách leo n-2.", "Đây là Fibonacci.", "Giữ hai biến thay vì cả mảng."],
    ("Climbing Stairs", "https://leetcode.com/problems/climbing-stairs/"),
)

bai(
    36,
    "Khoảng cách chỉnh sửa giữa hai từ",
    "quy-hoach-dong",
    "vua",
    """Cho hai từ tiếng Việt đã tách âm tiết (mỗi âm tiết là một đơn vị). Tìm số thao tác chèn/xoá/thay ít nhất để biến từ này thành từ kia.""",
    [('"hoc", "hoc"', "0"), ('"hoc", "hoc_sinh"', "5")],
    ["0 ≤ len(a), len(b) ≤ 500"],
    """def khoang_cach(a, b):
    pass""",
    """assert khoang_cach("hoc", "hoc") == 0
assert khoang_cach("", "abc") == 3
assert khoang_cach("abc", "") == 3
assert khoang_cach("abc", "yabd") == 2
print("OK")""",
    """import random, string
rng = random.Random(17)
a = "".join(rng.choice(string.ascii_lowercase) for _ in range(400))
b = "".join(rng.choice(string.ascii_lowercase) for _ in range(400))
assert isinstance(khoang_cach(a, b), int)
print("OK")""",
    """def khoang_cach(a, b):
    n, m = len(a), len(b)
    truoc = list(range(m + 1))
    for i in range(1, n + 1):
        hien = [i] + [0] * m
        for j in range(1, m + 1):
            hien[j] = min(
                truoc[j] + 1,
                hien[j - 1] + 1,
                truoc[j - 1] + (a[i - 1] != b[j - 1]),
            )
        truoc = hien
    return truoc[m]""",
    "O(n·m) thời gian, O(m) bộ nhớ.",
    ["Bảng dp[i][j] cho tiền tố i, j.", "Ba lựa chọn: xoá, chèn, thay.", "Chỉ cần hàng trước."],
    ("Edit Distance", "https://leetcode.com/problems/edit-distance/"),
)

bai(
    37,
    "Dãy con tăng dài nhất",
    "quy-hoach-dong",
    "vua",
    """Tìm độ dài dãy con tăng nghiêm ngặt dài nhất (không cần liên tiếp).""",
    [("[10,9,2,5,3,7,101,18]", "4")],
    ["1 ≤ len(ds) ≤ 100 000"],
    """import bisect

def lis(ds):
    pass""",
    """assert lis([10,9,2,5,3,7,101,18]) == 4
assert lis([7,7,7]) == 1
print("OK")""",
    """import random
rng = random.Random(18)
ds = list(range(50000))
assert lis(ds) == 50000
print("OK")""",
    """import bisect
def lis(ds):
    duoi = []
    for x in ds:
        i = bisect.bisect_left(duoi, x)
        if i == len(duoi):
            duoi.append(x)
        else:
            duoi[i] = x
    return len(duoi)""",
    "O(n log n) thời gian.",
    ["Giữ mảng đuôi nhỏ nhất cho mỗi độ dài.", "Tìm nhị phân vị trí chèn.", "Độ dài mảng đuôi là đáp án."],
    ("Longest Increasing Subsequence", "https://leetcode.com/problems/longest-increasing-subsequence/"),
)

bai(
    38,
    "Đổi tiền bằng ít xu nhất",
    "quy-hoach-dong",
    "vua",
    """Cho các mệnh giá xu và số tiền cần đổi. Trả về số xu ít nhất, hoặc -1 nếu không đổi được.""",
    [("[1,2,5], 11", "3")],
    ["1 ≤ số tiền ≤ 10 000"],
    """def doi_tien(xu, so_tien):
    pass""",
    """assert doi_tien([1,2,5], 11) == 3
assert doi_tien([2], 3) == -1
print("OK")""",
    """import random
rng = random.Random(19)
xu = [1] + sorted(rng.sample(range(2, 500), 20))
assert isinstance(doi_tien(xu, 10000), int)
print("OK")""",
    """def doi_tien(xu, so_tien):
    vo_cuc = so_tien + 1
    dp = [0] + [vo_cuc] * so_tien
    for x in range(1, so_tien + 1):
        for m in xu:
            if m <= x:
                dp[x] = min(dp[x], dp[x - m] + 1)
    return -1 if dp[so_tien] == vo_cuc else dp[so_tien]""",
    "O(so_tien · số mệnh giá) thời gian.",
    ["dp[x] = số xu ít nhất cho x.", "Thử mọi mệnh giá ≤ x.", "Khởi tạo vô cực, trả -1 nếu không đổi được."],
    ("Coin Change", "https://leetcode.com/problems/coin-change/"),
)

# 11. Quay lui
bai(
    39,
    "Sinh mọi tổ hợp siêu tham số",
    "quay-lui",
    "vua",
    """Cho dict `khong_gian` ánh xạ tên tham số → danh sách giá trị. Sinh mọi tổ hợp (mỗi tham số chọn một giá trị). Trả về list các dict; thứ tự không quan trọng.""",
    [('{"lr": [0.1, 0.01], "batch": [16, 32]}', "4 tổ hợp")],
    ["1 ≤ số tham số ≤ 8", "Mỗi danh sách không rỗng."],
    """def to_hop(khong_gian):
    pass""",
    """kq = to_hop({"lr": [0.1, 0.01], "batch": [16, 32]})
assert len(kq) == 4
assert all(set(x) == {"lr", "batch"} for x in kq)
print("OK")""",
    """kg = {f"p{i}": [0, 1] for i in range(8)}
kq = to_hop(kg)
assert len(kq) == 256
print("OK")""",
    """def to_hop(khong_gian):
    ten = list(khong_gian)
    kq = []
    def lui(i, hien):
        if i == len(ten):
            kq.append(dict(hien))
            return
        for v in khong_gian[ten[i]]:
            hien[ten[i]] = v
            lui(i + 1, hien)
    lui(0, {})
    return kq""",
    "O(số tổ hợp · số tham số) thời gian.",
    ["Đệ quy theo từng tham số.", "Chọn một giá trị rồi sang tham số kế.", "Đủ tham số thì ghi bản sao."],
    ("Combinations", "https://leetcode.com/problems/combinations/"),
)

# 12. Tham lam / khoảng
bai(
    40,
    "Gộp các ca chạy GPU bị chồng giờ",
    "tham-lam",
    "vua",
    """Cho danh sách ca `[bat_dau, ket_thuc]` (giây). Gộp các ca chồng nhau hoặc chạm nhau thành ca lớn hơn, trả về danh sách đã sắp và không chồng.""",
    [("[[1,3],[2,6],[8,10],[15,18]]", "[[1,6],[8,10],[15,18]]")],
    ["0 ≤ số ca ≤ 100 000"],
    """def gop_ca(ca):
    pass""",
    """assert gop_ca([[1,3],[2,6],[8,10],[15,18]]) == [[1,6],[8,10],[15,18]]
assert gop_ca([]) == []
print("OK")""",
    """ca = [[i, i + 3] for i in range(0, 99999, 3)]
kq = gop_ca(ca)
assert kq == [[0, 99999]]
print("OK")""",
    """def gop_ca(ca):
    if not ca:
        return []
    ca = sorted(ca)
    kq = [list(ca[0])]
    for a, b in ca[1:]:
        if a <= kq[-1][1]:
            kq[-1][1] = max(kq[-1][1], b)
        else:
            kq.append([a, b])
    return kq""",
    "O(n log n) thời gian do sắp xếp.",
    ["Sắp theo thời điểm bắt đầu.", "Ca mới chồng/chạm ca cuối thì nới cuối.", "Không thì thêm ca mới."],
    ("Merge Intervals", "https://leetcode.com/problems/merge-intervals/"),
)


# 13. Đồ án tốt nghiệp
bai(
    41,
    "Đồ án tốt nghiệp: hệ thống điều phối kho robot",
    "do-an",
    "kho",
    """Bạn nhận bàn giao một hệ thống điều phối cho kho robot. Dữ liệu gồm danh sách đơn hàng, lưới kho (`0` đi được, `1` kệ hàng) và một gói truy vấn. Viết `dieu_phoi(don_hang, kho, truy_van)` trả về một dict tổng hợp 8 phần, mỗi phần dùng một dạng thuật toán đã học:

1. `cap_giam_gia`: chỉ số `[i, j]` của hai đơn có `gia` cộng lại đúng `truy_van["tong_gia"]` (i < j); không có thì `[]`. Dùng bảng băm.
2. `cua_so_tot_nhat`: tổng `gia` lớn nhất của đúng `truy_van["cua_so"]` đơn liên tiếp; nếu `cua_so` lớn hơn số đơn hoặc ≤ 0 thì `0`. Dùng cửa sổ trượt.
3. `duong_di`: số bước ít nhất từ `(0,0)` tới `(n-1,m-1)` trên lưới, đi 4 hướng; không tới được thì `-1`. Dùng BFS.
4. `top_san_pham`: tối đa `truy_van["top_k"]` tên sản phẩm bán chạy nhất theo tổng `so_luong`, hòa thì theo thứ tự từ điển tăng. Dùng heap hoặc đếm.
5. `ca_gop`: gộp các khoảng giao hàng trong `truy_van["ca"]` chồng nhau hoặc chạm nhau. Dùng tham lam sau khi sắp xếp.
6. `so_cach`: số tập con của `truy_van["trong_luong"]` có tổng không vượt `truy_van["suc_chua"]`, tính cả tập rỗng. Dùng quy hoạch động.
7. `vi_tri_chen`: vị trí chèn `truy_van["gia_tri_chen"]` vào danh sách `gia` đã sắp tăng (vị trí đầu tiên có giá ≥ giá trị chèn). Dùng tìm kiếm nhị phân.
8. `ngoac_hop_le`: kiểm tra `truy_van["mau_ngoac"]` có đóng mở ngoặc đúng loại và đúng thứ tự không. Dùng ngăn xếp.""",
    [
        (
            "5 đơn, lưới 3×3, truy vấn đủ 8 phần (gia 120,180,200,80,150)",
            "{cap_giam_gia: [0,1], cua_so_tot_nhat: 380, duong_di: 4, top_san_pham: [C,B], ca_gop: [[0,50],[60,90]], so_cach: 6, vi_tri_chen: 2, ngoac_hop_le: True}",
        )
    ],
    [
        "1 ≤ số đơn ≤ 100 000; lưới ≤ 200×200; sức chứa ≤ 10 000.",
        "Dữ liệu đúng kiểu; lưới có thể bị chặn hoàn toàn; truy vấn có thể rỗng.",
    ],
    """from collections import deque, Counter
import heapq
import bisect

def dieu_phoi(don_hang, kho, truy_van):
    # 1. cap_giam_gia
    # 2. cua_so_tot_nhat
    # 3. duong_di
    # 4. top_san_pham
    # 5. ca_gop
    # 6. so_cach
    # 7. vi_tri_chen
    # 8. ngoac_hop_le
    return {}""",
    """don_hang = [
    {"ma": "DH1", "gia": 120, "san_pham": "A", "so_luong": 2},
    {"ma": "DH2", "gia": 180, "san_pham": "B", "so_luong": 5},
    {"ma": "DH3", "gia": 200, "san_pham": "A", "so_luong": 3},
    {"ma": "DH4", "gia": 80, "san_pham": "C", "so_luong": 7},
    {"ma": "DH5", "gia": 150, "san_pham": "B", "so_luong": 1},
]
kho = [[0, 0, 0], [1, 1, 0], [0, 0, 0]]
truy_van = {"tong_gia": 300, "cua_so": 2, "top_k": 2, "ca": [[0, 30], [20, 50], [60, 90]], "suc_chua": 10, "trong_luong": [4, 5, 6], "gia_tri_chen": 150, "mau_ngoac": "([{}])"}
kq = dieu_phoi(don_hang, kho, truy_van)
assert kq["cap_giam_gia"] == [0, 1]
assert kq["cua_so_tot_nhat"] == 380
assert kq["duong_di"] == 4
assert kq["top_san_pham"] == ["C", "B"]
assert kq["ca_gop"] == [[0, 50], [60, 90]]
assert kq["so_cach"] == 6
assert kq["vi_tri_chen"] == 2
assert kq["ngoac_hop_le"] is True
print("OK")""",
    """don2 = [
    {"ma": "X", "gia": 10, "san_pham": "A", "so_luong": 1},
    {"ma": "Y", "gia": 20, "san_pham": "A", "so_luong": 2},
    {"ma": "Z", "gia": 30, "san_pham": "B", "so_luong": 2},
]
kho2 = [[0, 1], [0, 0]]
tv2 = {"tong_gia": 100, "cua_so": 5, "top_k": 5, "ca": [[0, 5], [5, 10]], "suc_chua": 0, "trong_luong": [1, 2], "gia_tri_chen": 5, "mau_ngoac": "(]"}
kq2 = dieu_phoi(don2, kho2, tv2)
assert kq2["cap_giam_gia"] == []
assert kq2["cua_so_tot_nhat"] == 0
assert kq2["duong_di"] == 2
assert kq2["top_san_pham"] == ["A", "B"]
assert kq2["ca_gop"] == [[0, 10]]
assert kq2["so_cach"] == 1
assert kq2["vi_tri_chen"] == 0
assert kq2["ngoac_hop_le"] is False
rong = {"tong_gia": 0, "cua_so": 0, "top_k": 0, "ca": [], "suc_chua": 0, "trong_luong": [], "gia_tri_chen": 0, "mau_ngoac": ""}
kq3 = dieu_phoi([], [[1]], rong)
assert kq3["duong_di"] == -1 and kq3["so_cach"] == 1 and kq3["top_san_pham"] == []
print("OK")""",
    """from collections import deque, Counter
import heapq
import bisect

def dieu_phoi(don_hang, kho, truy_van):
    gia = [d["gia"] for d in don_hang]
    # 1. cặp giá bằng bảng băm
    thay = {}
    cap = []
    for i, x in enumerate(gia):
        if truy_van["tong_gia"] - x in thay:
            cap = [thay[truy_van["tong_gia"] - x], i]
            break
        thay[x] = i
    # 2. cửa sổ trượt
    k = truy_van["cua_so"]
    if k <= 0 or k > len(gia):
        cua = 0
    else:
        tong = sum(gia[:k])
        cua = tong
        for i in range(k, len(gia)):
            tong += gia[i] - gia[i - k]
            cua = max(cua, tong)
    # 3. BFS trên lưới
    n, m = len(kho), len(kho[0]) if kho else 0
    duong = -1
    if n and m and not kho[0][0] and not kho[-1][-1]:
        hang = deque([(0, 0, 0)])
        thay_o = {(0, 0)}
        while hang:
            x, y, dd = hang.popleft()
            if (x, y) == (n - 1, m - 1):
                duong = dd
                break
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                a, b = x + dx, y + dy
                if 0 <= a < n and 0 <= b < m and kho[a][b] == 0 and (a, b) not in thay_o:
                    thay_o.add((a, b))
                    hang.append((a, b, dd + 1))
    # 4. top-k bằng đếm + heap
    dem = Counter()
    for d in don_hang:
        dem[d["san_pham"]] += d["so_luong"]
    top = heapq.nsmallest(truy_van["top_k"], dem, key=lambda x: (-dem[x], x)) if truy_van["top_k"] > 0 else []
    # 5. gộp khoảng
    ca = sorted(truy_van["ca"])
    gop = []
    for a, b in ca:
        if gop and a <= gop[-1][1]:
            gop[-1][1] = max(gop[-1][1], b)
        else:
            gop.append([a, b])
    # 6. DP đếm tập con không vượt sức chứa
    C = truy_van["suc_chua"]
    dp = [0] * (C + 1)
    if C >= 0:
        dp[0] = 1
    for x in truy_van["trong_luong"]:
        for s in range(C, x - 1, -1):
            dp[s] += dp[s - x]
    so_cach = sum(dp) if C >= 0 else 0
    # 7. tìm kiếm nhị phân
    vi_tri = bisect.bisect_left(sorted(gia), truy_van["gia_tri_chen"])
    # 8. ngăn xếp kiểm tra ngoặc
    cap_ngoac = {")": "(", "]": "[", "}": "{"}
    ngan = []
    hop = True
    for c in truy_van["mau_ngoac"]:
        if c in "([{":
            ngan.append(c)
        elif c in cap_ngoac:
            if not ngan or ngan.pop() != cap_ngoac[c]:
                hop = False
                break
    if ngan:
        hop = False
    return {
        "cap_giam_gia": cap,
        "cua_so_tot_nhat": cua,
        "duong_di": duong,
        "top_san_pham": top,
        "ca_gop": gop,
        "so_cach": so_cach,
        "vi_tri_chen": vi_tri,
        "ngoac_hop_le": hop,
    }""",
    "O(n log n + n·m + C·|w|) thời gian, O(n + n·m + C) bộ nhớ; n là số đơn, lưới n×m, C sức chứa.",
    [
        "Chia bài toán lớn thành 8 bài con; mỗi bài con là một dạng đã học ở 40 bài trước.",
        "Bảng băm cho cặp giá; cửa sổ trượt; BFS; đếm + heap; sắp xếp khoảng; DP tập con; bisect; ngăn xếp.",
        "Viết hàm phụ cho từng phần, kiểm tra biên (mảng rỗng, lưới bị chặn, sức chứa 0), rồi ghép thành dict.",
    ],
    ("Merge Intervals (một phần của đồ án)", "https://leetcode.com/problems/merge-intervals/"),
)


def main() -> None:
    assert len(BAI) == 41, len(BAI)
    so = [b["so"] for b in BAI]
    assert so == list(range(1, 42)), so
    RA.mkdir(parents=True, exist_ok=True)
    for b in BAI:
        ten = f"{b['so']:03d}-{b['dang']}.yaml"
        with (RA / ten).open("w", encoding="utf-8") as f:
            yaml.safe_dump(b, f, allow_unicode=True, sort_keys=False, width=100)
    print("da ghi", len(BAI), "bai vao", RA)


if __name__ == "__main__":
    main()
