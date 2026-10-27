/** Bề rộng tối thiểu (px) để dựng kệ 3D; hẹp hơn là điện thoại, giữ kệ phẳng. */
export const RONG_3D = 820;

export interface DieuKien3D {
	rong: number;
	giamChuyenDong: boolean;
	/** `(pointer: fine)`: có chuột hoặc bàn di. Máy tính bảng cảm ứng rộng ≥ 820px vẫn giữ kệ phẳng. */
	troChinhXac: boolean;
	/** Có WebGL2. Truyền hàm để chỉ thử tạo context khi các điều kiện rẻ đã đạt. */
	webgl: boolean | (() => boolean);
}

/** Có dựng kệ 3D (tải three) hay giữ kệ phẳng. */
export function du3D(d: DieuKien3D): boolean {
	if (d.rong < RONG_3D || d.giamChuyenDong || !d.troChinhXac) return false;
	return typeof d.webgl === 'function' ? d.webgl() : d.webgl;
}
