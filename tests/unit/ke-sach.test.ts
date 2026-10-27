import { describe, it, expect, vi } from 'vitest';
import { readFileSync, statSync } from 'node:fs';
import { join } from 'node:path';
import { gzipSync } from 'node:zlib';
import { dsCuonSach } from '../../src/lib/ke-sach/du-lieu';
import { du3D } from '../../src/lib/ke-sach/cong-3d';
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
		expect(ai.daViet).toBe(2);
		expect(ai.daViet).toBe(chuongDaXuatBan().length);
		expect(ai.href).toBe('/ai-engineer/ch01-python-tu-dau/01-bien-va-kieu/');
		expect(ai.sapCo).toBe(false);
	});
	it('mỗi cuốn có moTa một câu cho bảng thông tin', () => {
		const [ai, rb] = dsCuonSach();
		expect(ai.moTa).toBe('Từ Python cơ bản đến Machine Learning, Deep Learning và mô hình ngôn ngữ lớn, hiểu tận gốc từng thuật toán.');
		expect(rb.moTa).toBe('Toán robot, điều khiển, phần cứng, ROS 2 và sim-to-real. Nhánh này đang được soạn.');
	});
	it('Robotics là sách sắp có, không có link', () => {
		const [, rb] = dsCuonSach();
		expect(rb.ten).toBe('Robotics');
		expect(rb.sapCo).toBe(true);
		expect(rb.href).toBeNull();
		expect(rb.tongChuong).toBeNull();
		expect(rb.daViet).toBe(0);
	});
	it('ảnh bìa vẽ tay: mỗi cuốn trỏ đúng file SVG trong public/', () => {
		expect(dsCuonSach().map((s) => s.anhBia)).toEqual(['/hinh/bia/ai-engineer.svg', '/hinh/bia/robotics.svg']);
	});
	it('ảnh bìa nhỏ cho kệ phẳng: đúng đường dẫn WebP, mỗi file ≤ 15 KB', () => {
		const ds = dsCuonSach();
		expect(ds.map((s) => s.anhBiaNho)).toEqual(['/hinh/bia/ai-engineer.webp', '/hinh/bia/robotics.webp']);
		for (const s of ds) expect(statSync(join(process.cwd(), 'public', s.anhBiaNho!)).size).toBeLessThanOrEqual(15 * 1024);
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

describe('bìa SVG tĩnh trong public/hinh/bia', () => {
	for (const ten of ['ai-engineer', 'robotics']) {
		const duongDan = `public/hinh/bia/${ten}.svg`;
		it(`${ten}.svg: tồn tại, ≤ 120 KB, khung 600x900, không phụ thuộc gì bên ngoài`, () => {
			const kichThuoc = statSync(duongDan).size;
			expect(kichThuoc).toBeGreaterThan(5_000);
			expect(kichThuoc).toBeLessThanOrEqual(120 * 1024);
			const svg = readFileSync(duongDan, 'utf8');
			expect(gzipSync(svg).length).toBeLessThan(kichThuoc);
			expect(svg).toMatch(/^<svg [^>]*viewBox="0 0 600 900"/);
			expect(svg).toContain('xmlns="http://www.w3.org/2000/svg"');
			// Ngoài namespace bắt buộc của SVG, không có URL nào: không ảnh ngoài, không font web.
			expect(svg.replace('xmlns="http://www.w3.org/2000/svg"', '')).not.toMatch(/http/i);
			expect(svg).not.toMatch(/<image|<text|@font-face|<script|<!--|<metadata/);
			expect(svg).not.toContain('NaN');
		});
	}
});

describe('cổng tải kệ 3D', () => {
	const du = { rong: 1280, giamChuyenDong: false, troChinhXac: true, webgl: true };
	it('máy tính có chuột, đủ rộng, có WebGL2 thì dựng 3D', () => {
		expect(du3D(du)).toBe(true);
		expect(du3D({ ...du, rong: 820 })).toBe(true);
	});
	it('thiếu một điều kiện thì giữ kệ phẳng', () => {
		expect(du3D({ ...du, rong: 819 })).toBe(false);
		expect(du3D({ ...du, giamChuyenDong: true })).toBe(false);
		expect(du3D({ ...du, troChinhXac: false })).toBe(false); // máy tính bảng cảm ứng ≥ 820px
		expect(du3D({ ...du, webgl: false })).toBe(false);
	});
	it('chỉ thử WebGL khi các điều kiện rẻ đã đạt', () => {
		const thu = vi.fn(() => true);
		expect(du3D({ ...du, troChinhXac: false, webgl: thu })).toBe(false);
		expect(du3D({ ...du, rong: 375, webgl: thu })).toBe(false);
		expect(thu).not.toHaveBeenCalled();
		expect(du3D({ ...du, webgl: thu })).toBe(true);
		expect(thu).toHaveBeenCalledTimes(1);
		expect(du3D({ ...du, webgl: () => false })).toBe(false);
	});
});
