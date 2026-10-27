import { describe, it, expect } from 'vitest';
import { readFileSync } from 'node:fs';

interface O {
	cell_type: 'markdown' | 'code' | 'raw';
	source: string[] | string;
	outputs?: unknown[];
}
const nb: { cells: O[]; metadata: Record<string, unknown> } = JSON.parse(
	readFileSync(new URL('../../notebooks/ch10_hoi_quy_tuyen_tinh.ipynb', import.meta.url), 'utf8'),
);
const nguon = (o: O) => (Array.isArray(o.source) ? o.source.join('') : o.source);
const md = nb.cells.filter((o) => o.cell_type === 'markdown').map(nguon);
const code = nb.cells.filter((o) => o.cell_type === 'code').map(nguon);

describe('notebook chương 10 trình bày cho Colab', () => {
	it('ô đầu là markdown có tiêu đề chương', () => {
		expect(nb.cells[0].cell_type).toBe('markdown');
		expect(nguon(nb.cells[0])).toContain('Chương 10 · Hồi quy tuyến tính');
	});

	it('mục lục trỏ tới đủ 6 phần, mỗi phần có mỏ neo', () => {
		for (let i = 1; i <= 6; i++) {
			expect(nguon(nb.cells[0])).toContain(`(#trang-${i})`);
			expect(md.some((s) => s.includes(`id="trang-${i}"`) && s.includes(`## Trang ${i} · `))).toBe(true);
		}
	});

	it('không có code inline dài quá 40 ký tự trong ô markdown (output dài phải nằm trong khối code riêng)', () => {
		const dai: string[] = [];
		for (const s of md) {
			const ngoaiKhoi = s.replace(/```[\s\S]*?```/g, '');
			for (const m of ngoaiKhoi.matchAll(/`([^`\n]+)`/g)) if (m[1].length > 40) dai.push(m[1]);
			for (const m of ngoaiKhoi.matchAll(/<code[^>]*>([\s\S]*?)<\/code>/g)) if (m[1].length > 40) dai.push(m[1]);
		}
		expect(dai).toEqual([]);
	});

	it('có đáp án ẩn trong <details> và đủ ba bài tập', () => {
		expect(md.filter((s) => s.includes('<details><summary>Xem đáp án</summary>')).length).toBeGreaterThanOrEqual(3);
		for (const bai of ['10.1', '10.2', '10.3']) expect(md.some((s) => s.includes(`Bài ${bai}`))).toBe(true);
		expect(md.join('\n')).toContain('1{,}54375');
	});

	it('có đủ bốn loại khung màu như trang web, chữ trong khung đặt màu rõ ràng', () => {
		const tatCa = md.join('\n');
		for (const [mau, nhan] of [
			['#E07A1F', 'VÌ SAO LẠI LÀ'],
			['#2E8B57', 'ĐỌC KẾT QUẢ'],
			['#C0392B', 'LỖI HAY GẶP'],
			['#1F5F8B', 'TRỰC GIÁC'],
		]) {
			expect(tatCa).toContain(`border-left:6px solid ${mau}`);
			expect(tatCa).toContain(nhan);
		}
		for (const m of tatCa.matchAll(/<div style="border-left:[^"]*"/g)) expect(m[0]).toContain('color:#2b2b2b');
	});

	it('mỗi ô code có comment tiếng Việt trên ít nhất 80% số dòng', () => {
		for (const s of code) {
			const dong = s.split('\n').filter((d) => d.trim() && !/^[\s)\]}]+$/.test(d));
			const coComment = dong.filter((d) => d.includes('#')).length;
			expect(coComment / dong.length, s.slice(0, 60)).toBeGreaterThanOrEqual(0.8);
		}
	});

	it('lưu không kèm output, không ghi tên công cụ sinh nội dung', () => {
		for (const o of nb.cells.filter((x) => x.cell_type === 'code')) expect(o.outputs).toEqual([]);
		expect(JSON.stringify(nb)).not.toMatch(/claude|anthropic|chatgpt|openai/i);
		expect(JSON.stringify(nb)).not.toMatch(/[—–]/);
	});
});
