import { describe, it, expect } from 'vitest';
import { readFileSync, readdirSync } from 'node:fs';
import { CHUONG } from '../../src/data/chuong';

interface O {
	cell_type: 'markdown' | 'code' | 'raw';
	source: string[] | string;
}
const nguon = (o: O) => (Array.isArray(o.source) ? o.source.join('') : o.source);
const boChuoi = (d: string) => d.replace(/"(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*'/g, '""');

// Chương 10 có bộ test riêng (notebook.test.ts); các chương khác dựng bằng scripts/notebook/nblib.py.
for (const ch of CHUONG.filter((c) => c.notebook && c.so !== 10)) {
	const nb: { cells: O[] } = JSON.parse(readFileSync(new URL(`../../notebooks/${ch.notebook}`, import.meta.url), 'utf8'));
	const md = nb.cells.filter((o) => o.cell_type === 'markdown').map(nguon);
	const code = nb.cells.filter((o) => o.cell_type === 'code').map(nguon);
	const soTrang = readdirSync(new URL(`../../src/content/docs/${ch.slug}`, import.meta.url)).filter((f) => f.endsWith('.mdx')).length;

	describe(`notebook chương ${ch.so} trình bày cho Colab`, () => {
		it('ô đầu có tiêu đề chương và mục lục trỏ tới đủ các trang của web', () => {
			expect(nguon(nb.cells[0])).toContain(`Chương ${ch.so} · ${ch.ten}`);
			for (let i = 1; i <= soTrang; i++) {
				expect(nguon(nb.cells[0])).toContain(`(#trang-${i})`);
				expect(md.some((s) => s.includes(`id="trang-${i}"`) && s.includes(`## Trang ${i} · `))).toBe(true);
			}
		});

		it('có đáp án ẩn trong <details> cho đủ ba bài tập', () => {
			expect(md.filter((s) => s.includes('<details><summary>Xem đáp án</summary>')).length).toBe(3);
			for (let i = 1; i <= 3; i++) expect(md.some((s) => s.includes(`Bài ${ch.so}.${i}`))).toBe(true);
		});

		it('mỗi ô code có comment tiếng Việt trên ít nhất 80% số dòng', () => {
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
}
