import { describe, it, expect } from 'vitest';
import { readFileSync } from 'node:fs';

interface O {
	cell_type: 'markdown' | 'code' | 'raw';
	source: string[] | string;
}
const nb: { cells: O[] } = JSON.parse(readFileSync(new URL('../../notebooks/ch01_python_tu_dau.ipynb', import.meta.url), 'utf8'));
const nguon = (o: O) => (Array.isArray(o.source) ? o.source.join('') : o.source);
const md = nb.cells.filter((o) => o.cell_type === 'markdown').map(nguon);
const code = nb.cells.filter((o) => o.cell_type === 'code').map(nguon);

describe('notebook chương 1 trình bày cho Colab', () => {
	it('ô đầu có tiêu đề chương và mục lục trỏ tới đủ 5 phần', () => {
		expect(nguon(nb.cells[0])).toContain('Chương 1 · Python từ đầu');
		for (let i = 1; i <= 5; i++) {
			expect(nguon(nb.cells[0])).toContain(`(#trang-${i})`);
			expect(md.some((s) => s.includes(`id="trang-${i}"`) && s.includes(`## Trang ${i} · `))).toBe(true);
		}
	});

	it('có đáp án ẩn trong <details> cho đủ ba bài tập', () => {
		expect(md.filter((s) => s.includes('<details><summary>Xem đáp án</summary>')).length).toBe(3);
		for (const bai of ['1.1', '1.2', '1.3']) expect(md.some((s) => s.includes(`Bài ${bai}`))).toBe(true);
	});

	it('mỗi ô code có comment tiếng Việt trên ít nhất 80% số dòng', () => {
		const boChuoi = (d: string) => d.replace(/"(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*'/g, '""');
		for (const s of code) {
			const dong = s.split('\n').filter((d) => d.trim() && !/^[\s)\]}]+$/.test(d));
			const coComment = dong.filter((d) => boChuoi(d).includes('#')).length;
			expect(coComment / dong.length, s.slice(0, 60)).toBeGreaterThanOrEqual(0.8);
		}
	});

	it('mỗi ô code có một khối "Output mong đợi" ngay sau', () => {
		nb.cells.forEach((o, i) => {
			if (o.cell_type !== 'code') return;
			expect(nguon(nb.cells[i + 1]), nguon(o).slice(0, 60)).toMatch(/^Output mong đợi[^\n]*:\n+```text\n/);
		});
	});

	it('chữ trong khung đặt màu rõ ràng', () => {
		for (const m of md.join('\n').matchAll(/<div style="border-left:[^"]*"/g)) expect(m[0]).toContain('color:#2b2b2b');
	});
});
