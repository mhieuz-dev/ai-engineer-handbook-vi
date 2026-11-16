import { describe, it, expect } from 'vitest';
import fs from 'node:fs';
import path from 'node:path';
import YAML from 'yaml';
import { LO_TRINH } from '../../src/lib/thuat-toan-dang';

const THU_MUC = path.resolve('src/data/thuat-toan');
const TEP = fs.readdirSync(THU_MUC).filter((f) => f.endsWith('.yaml')).sort();
const BAI = TEP.map((f) => YAML.parse(fs.readFileSync(path.join(THU_MUC, f), 'utf8')) as Record<string, unknown>);

describe('ngân hàng bài thuật toán', () => {
	it('đúng 41 bài, số 1..41, tên tệp theo số', () => {
		expect(BAI).toHaveLength(41);
		expect(BAI.map((b) => b.so)).toEqual(Array.from({ length: 41 }, (_, i) => i + 1));
		expect(TEP.map((f) => Number(f.slice(0, 3)))).toEqual(Array.from({ length: 41 }, (_, i) => i + 1));
	});
	it('mỗi bài đủ trường, 3 gợi ý, có test in OK', () => {
		for (const b of BAI) {
			for (const k of ['ten', 'dang', 'muc', 'de', 'khung', 'test_vi_du', 'test_an', 'loi_giai', 'phuc_tap', 'tuong_tu']) {
				expect(b[k], `${b.so} thiếu ${k}`).toBeTruthy();
			}
			expect(b.goi_y, `${b.so} gợi ý`).toHaveLength(3);
			expect(String(b.test_vi_du)).toContain('OK');
			expect(String(b.test_an)).toContain('OK');
		}
	});
	it('link tương tự đều là LeetCode https', () => {
		for (const b of BAI) {
			const link = (b.tuong_tu as { link: string }).link;
			expect(link).toMatch(/^https:\/\/leetcode\.com\/problems\/[a-z0-9-]+\/$/);
		}
	});
	it('13 dạng đều có bài, đồ án ở cuối', () => {
		const dang = new Set(BAI.map((b) => b.dang));
		expect(dang.size).toBe(13);
		const cap = BAI.find((b) => b.so === 41)!;
		expect(cap.dang).toBe('do-an');
		expect(cap.muc).toBe('kho');
		expect(String(cap.test_an)).toContain('OK');
		expect(String(cap.de)).toContain('8 phần');
	});
	it('lộ trình dễ đến khó phủ đủ 41 bài, đồ án cuối', () => {
		expect(LO_TRINH).toHaveLength(41);
		expect([...LO_TRINH].sort((a, b) => a - b)).toEqual(Array.from({ length: 41 }, (_, i) => i + 1));
		expect(LO_TRINH[LO_TRINH.length - 1]).toBe(41);
	});
});
