/** Giải thích lỗi Python hay gặp bằng tiếng Việt, kèm cách sửa ngắn. */

export interface LoiDaHieu {
	loai: string;
	/** Dòng trong đoạn code người học chạy (1-based), null nếu không đọc được. */
	dong: number | null;
	giaiThich: string;
}

/** Lấy số dòng từ traceback của Pyodide; ưu tiên khung gần cuối trong "<exec>" hoặc "<string>". */
export function docDong(message: string): number | null {
	const ds = [...message.matchAll(/File\s+"[^"]*",\s+line\s+(\d+)/g)].map((m) => Number(m[1]));
	return ds.length ? ds[ds.length - 1] : null;
}

const BANG: { mau: RegExp; loai: string; giaiThich: string }[] = [
	{
		mau: /NetworkError|Failed to fetch|importScripts|Failed to load resource|Không tải được Python/i,
		loai: 'kết nối',
		giaiThich: 'Không tải được Python từ CDN. Kiểm tra mạng rồi bấm Chạy lại; nếu mạng chặn CDN thì đổi mạng hoặc dùng notebook trên Colab.',
	},
	{
		mau: /NameError: name '([^']+)' is not defined/,
		loai: 'NameError',
		giaiThich: "Tên biến hoặc hàm chưa được gán ở thời điểm này. Kiểm tra chính tả, dấu hai chấm, và chắc rằng khối gán đã chạy trước. Nếu là hàm của thư viện, nhớ `import` trước khi dùng.",
	},
	{
		mau: /UnboundLocalError: local variable '([^']+)'/,
		loai: 'UnboundLocalError',
		giaiThich: 'Trong hàm, biến được gán ở một nhánh nhưng lại đọc ở nhánh khác. Gán giá trị mặc định ở đầu hàm, hoặc kiểm tra mọi nhánh if/else đều gán biến trước khi dùng.',
	},
	{
		mau: /IndentationError|TabError/,
		loai: 'IndentationError',
		giaiThich: 'Thụt lề sai: Python dùng thụt lề để chia khối. Chọn toàn bộ file rồi thụt lại bằng 4 dấu cách, không trộn tab với dấu cách.',
	},
	{
		mau: /SyntaxError: (.*)/,
		loai: 'SyntaxError',
		giaiThich: 'Câu lệnh không đúng cú pháp. Soi dòng được đánh dấu: thiếu dấu hai chấm sau if/for/def, thiếu ngoặc đóng, hoặc dấu ngoặc không khớp.',
	},
	{
		mau: /IndexError: (list|tuple|string) index out of range/,
		loai: 'IndexError',
		giaiThich: 'Chỉ số vượt quá độ dài. Chỉ số hợp lệ là 0 đến len(xs)-1; muốn lấy phần tử cuối dùng xs[-1]. Kiểm tra lại `range(len(...))` có bị lệch một không.',
	},
	{
		mau: /KeyError: (.*)/,
		loai: 'KeyError',
		giaiThich: "Không có khóa này trong dict. Dùng `d.get(khoa, mac_dinh)` để tránh lỗi, hoặc kiểm tra `if khoa in d` trước khi lấy.",
	},
	{
		mau: /ValueError: (.*)/,
		loai: 'ValueError',
		giaiThich: 'Đúng kiểu dữ liệu nhưng sai giá trị, ví dụ `float("abc")` hay `int("3.5")`. Kiểm tra dữ liệu đầu vào, bỏ khoảng trắng trước khi đổi kiểu.',
	},
	{
		mau: /TypeError: unsupported operand type\(s\)/,
		loai: 'TypeError',
		giaiThich: 'Phép toán giữa hai kiểu không hợp lệ, ví dụ cộng chuỗi với số. Ép kiểu rõ ràng bằng `int(...)`, `float(...)` hoặc `str(...)`.',
	},
	{
		mau: /TypeError: '([^']+)' object is not (callable|subscriptable|iterable)/,
		loai: 'TypeError',
		giaiThich: "Bạn gọi hoặc lấy chỉ số trên một giá trị không phải hàm/danh sách. Kiểm tra biến đó đang giữ gì bằng `print(type(x), x)`.",
	},
	{
		mau: /TypeError: ([^()]+)\(\) (missing|takes) .*positional argument/,
		loai: 'TypeError',
		giaiThich: 'Gọi hàm sai số đối số. Xem lại chữ ký hàm: đếm số tham số bắt buộc và kiểm tra tên tham số khi truyền bằng từ khóa.',
	},
	{
		mau: /AttributeError: '([^']+)' object has no attribute '([^']+)'/,
		loai: 'AttributeError',
		giaiThich: 'Đối tượng không có thuộc tính/phương thức này. Gõ dấu chấm rồi xem gợi ý, hoặc `dir(x)` để liệt kê. Hay gặp khi nhầm list với numpy array (`.shape` chỉ có trên array).',
	},
	{
		mau: /ZeroDivisionError/,
		loai: 'ZeroDivisionError',
		giaiThich: 'Chia cho 0. Kiểm tra mẫu số trước khi chia, hoặc thêm một số rất nhỏ khi chuẩn hóa.',
	},
	{
		mau: /ModuleNotFoundError: No module named '([^']+)'/,
		loai: 'ModuleNotFoundError',
		giaiThich: 'Chưa có thư viện này trong khung code. Một số gói cài bằng `import micropip; await micropip.install("tên-gói")`. Thư viện nặng như torch, transformers, gymnasium thì cần Colab.',
	},
	{
		mau: /FileNotFoundError: .*'([^']+)'/,
		loai: 'FileNotFoundError',
		giaiThich: 'Không tìm thấy tệp. Khung code không thấy ổ đĩa của bạn: muốn dùng dữ liệu thì nạp bằng chuỗi, hoặc tải tệp mẫu của bài. Kiểm tra lại đường dẫn tương đối.',
	},
	{
		mau: /RecursionError: maximum recursion depth/,
		loai: 'RecursionError',
		giaiThich: 'Đệ quy không dừng: thiếu trường hợp cơ sở hoặc trường hợp cơ sở không bao giờ tới. Kiểm tra điều kiện dừng và chắc mỗi lần gọi tiến gần về nó.',
	},
	{
		mau: /AssertionError/,
		loai: 'AssertionError',
		giaiThich: 'Một câu `assert` sai, tức kết quả chưa đúng như bài yêu cầu. Đọc thông điệp ngay sau assert để biết điều kiện nào không đạt.',
	},
	{
		mau: /OverflowError|MemoryError/,
		loai: 'OverflowError',
		giaiThich: 'Số quá lớn hoặc hết bộ nhớ trình duyệt. Giảm kích thước mảng, tránh tạo ma trận quá lớn, hoặc chia nhỏ dữ liệu.',
	},
	{
		mau: /RuntimeError: (.*)/,
		loai: 'RuntimeError',
		giaiThich: 'Lỗi phát sinh lúc chạy. Đọc kỹ dòng thông báo: thường là trạng thái không hợp lệ (ví dụ gọi `.backward()` lần hai trên cùng đồ thị).',
	},
];

export function giaiThichLoi(message: string): LoiDaHieu {
	for (const b of BANG) {
		const m = b.mau.exec(message);
		if (m) {
			let gt = b.giaiThich;
			if (b.loai === 'NameError' && m[1]) gt = `Chưa có tên \`${m[1]}\`. ` + gt;
			if (b.loai === 'KeyError' && m[1]) gt = `Không có khóa ${m[1]}. ` + gt;
			if (b.loai === 'ModuleNotFoundError' && m[1]) gt = `Thiếu gói \`${m[1]}\`. ` + gt;
			return { loai: b.loai, dong: docDong(message), giaiThich: gt };
		}
	}
	const dong = message.trim().split('\n').filter(Boolean).pop() ?? 'Có lỗi khi chạy';
	return { loai: 'Lỗi', dong: docDong(message), giaiThich: `Python báo: ${dong}. Đọc dòng cuối của thông báo để biết loại lỗi, và dòng ngay trên để biết vị trí.` };
}
