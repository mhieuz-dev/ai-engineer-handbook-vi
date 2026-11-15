/** So kết quả chạy với khối Output của bài: số thực dung sai 1e-6, còn lại so từng ký tự. */

export interface DongLech {
	dong: number;
	mong: string;
	ra: string;
}

export interface KetQuaSo {
	khop: boolean;
	lech: DongLech[];
	/** Số dòng hai bên cùng có và cùng khớp. */
	khopDong: number;
}

const SO = /^[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?$/;

function khopToken(a: string, b: string): boolean {
	if (a === b) return true;
	if (SO.test(a) && SO.test(b)) {
		const x = Number(a);
		const y = Number(b);
		return Math.abs(x - y) <= 1e-6 * Math.max(1, Math.abs(x), Math.abs(y));
	}
	return false;
}

function khopDongMot(a: string, b: string): boolean {
	const ta = a.trim().split(/\s+/).filter(Boolean);
	const tb = b.trim().split(/\s+/).filter(Boolean);
	if (ta.length !== tb.length) return false;
	for (let i = 0; i < ta.length; i++) if (!khopToken(ta[i], tb[i])) return false;
	return true;
}

export function soOutput(ra: string, mong: string): KetQuaSo {
	const a = ra.replace(/\r\n/g, '\n').replace(/\s+$/, '').split('\n');
	const b = mong.replace(/\r\n/g, '\n').replace(/\s+$/, '').split('\n');
	const lech: DongLech[] = [];
	let khopDong = 0;
	const n = Math.max(a.length, b.length);
	for (let i = 0; i < n; i++) {
		const x = a[i] ?? '';
		const y = b[i] ?? '';
		if (x === '' && y === '') continue;
		if (khopDongMot(x, y)) khopDong++;
		else lech.push({ dong: i + 1, mong: y, ra: x });
	}
	return { khop: lech.length === 0, lech, khopDong };
}
