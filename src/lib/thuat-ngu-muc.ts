/** Chữ cái để nhóm thuật ngữ: bỏ dấu, đ → d, chữ hoa; ký tự không phải A-Z thành '#'. */
export function chuCai(ten: string): string {
	const c = ten
		.normalize('NFD')
		.replace(/\p{M}/gu, '')
		.replace(/đ/gi, 'd')
		.charAt(0)
		.toUpperCase();
	return /^[A-Z]$/.test(c) ? c : '#';
}

/** Chuẩn hoá chuỗi để tìm không dấu, không phân biệt hoa thường. */
export function chuanHoaTim(s: string): string {
	return s
		.normalize('NFD')
		.replace(/\p{M}/gu, '')
		.replace(/đ/gi, 'd')
		.toLowerCase()
		.replace(/\s+/g, ' ')
		.trim();
}

export const BANG_CHU_CAI = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('');
