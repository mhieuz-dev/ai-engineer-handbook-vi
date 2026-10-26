import { describe, it, expect } from 'vitest';
import { dsCuonSach } from '../../src/lib/ke-sach/du-lieu';
import { NHANH, PHAN, CHUONG, chuongDaXuatBan, cauHinhSidebar } from '../../src/data/chuong';

describe('kệ sách: dữ liệu hai cuốn', () => {
	it('đúng thứ tự AI Engineer rồi Robotics', () => {
		expect(dsCuonSach().map((s) => s.id)).toEqual(['ai-engineer', 'robotics']);
	});
	it('AI Engineer lấy số chương và trang đầu từ catalog', () => {
		const [ai] = dsCuonSach();
		expect(ai.ten).toBe('AI Engineer');
		expect(ai.tongChuong).toBe(65);
		expect(ai.tongChuong).toBe(CHUONG.length);
		expect(ai.daViet).toBe(1);
		expect(ai.daViet).toBe(chuongDaXuatBan().length);
		expect(ai.href).toBe('/ai-engineer/ch10-hoi-quy-tuyen-tinh/01-truc-giac/');
		expect(ai.sapCo).toBe(false);
	});
	it('Robotics là sách sắp có, không có link', () => {
		const [, rb] = dsCuonSach();
		expect(rb.ten).toBe('Robotics');
		expect(rb.sapCo).toBe(true);
		expect(rb.href).toBeNull();
		expect(rb.tongChuong).toBeNull();
		expect(rb.daViet).toBe(0);
	});
	it('ảnh bìa tùy chọn: hiện chưa có ảnh nào, bìa vẽ bằng canvas', () => {
		for (const s of dsCuonSach()) {
			expect(s).toHaveProperty('anhBia');
			expect(s.anhBia).toBeUndefined();
		}
	});
	it('màu bìa và chữ là mã hex', () => {
		for (const s of dsCuonSach()) {
			expect(s.mauBia).toMatch(/^#[0-9A-Fa-f]{6}$/);
			expect(s.mauChu).toMatch(/^#[0-9A-Fa-f]{6}$/);
		}
	});
});

describe('Robotics trong catalog không đổi sidebar', () => {
	it('NHANH có Robotics nhưng Robotics chưa có Phần nào', () => {
		expect(NHANH.map((n) => n.id)).toEqual(['ai-engineer', 'robotics']);
		expect(PHAN.filter((p) => p.nhanh === 'robotics')).toHaveLength(0);
	});
	it('cấu hình sidebar vẫn chỉ một nhánh AI Engineer', () => {
		expect(cauHinhSidebar().map((n) => n.label)).toEqual(['AI Engineer']);
	});
});
