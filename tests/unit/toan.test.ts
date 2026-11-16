import { describe, it, expect } from 'vitest';
import fs from 'node:fs';
import path from 'node:path';
import YAML from 'yaml';

const THU_MUC = path.resolve('src/data/toan');
const TEP = fs.readdirSync(THU_MUC).filter((f) => f.endsWith('.yaml')).sort();
const BAI = TEP.map((f) => YAML.parse(fs.readFileSync(path.join(THU_MUC, f), 'utf8')) as Record<string, any>);

function trangTonTai(trang: string): boolean {
	const slug = trang.replace(/^\/+|\/+$/g, '');
	if (fs.existsSync(path.resolve('src/content/docs', `${slug}.mdx`))) return true;
	const dir = path.resolve('src/content/docs', slug);
	return fs.existsSync(dir) && fs.readdirSync(dir).some((f) => f.endsWith('.mdx'));
}

describe('toán cho thuật toán', () => {
	it('đúng 31 bài, số 1..31, tên tệp theo số', () => {
		expect(BAI).toHaveLength(31);
		expect(BAI.map((b) => b.so)).toEqual(Array.from({ length: 31 }, (_, i) => i + 1));
		expect(TEP.map((f) => Number(f.slice(0, 3)))).toEqual(Array.from({ length: 31 }, (_, i) => i + 1));
	});

	it('đủ 6 module, mỗi module có bài, đồ án ở cuối', () => {
		const dem = new Map<string, number>();
		for (const b of BAI) dem.set(b.module, (dem.get(b.module) ?? 0) + 1);
		expect([...dem.keys()].sort()).toEqual(['chung-minh', 'dai-so', 'do-an', 'do-phuc-tap', 'toi-uu', 'xac-suat']);
		expect(dem.get('do-an')).toBe(1);
		const cap = BAI.find((b) => b.so === 31)!;
		expect(cap.module).toBe('do-an');
		expect(cap.muc).toBe('kho');
		expect(cap.rubric).toHaveLength(5);
		expect(cap.rubric.reduce((s: number, y: { diem: number }) => s + y.diem, 0)).toBe(10);
	});

	it('mỗi bài đủ 3 gợi ý, lời giải; bài chứng minh có chứng minh và rubric 10', () => {
		for (const b of BAI) {
			expect(b.goi_y, `${b.so} gợi ý`).toHaveLength(3);
			expect(String(b.loi_giai).trim().length, `${b.so} lời giải`).toBeGreaterThan(0);
			if (b.loai === 'chung-minh') {
				expect(String(b.chung_minh ?? '').trim().length, `${b.so} chứng minh`).toBeGreaterThan(0);
				if (b.rubric) {
					const tong = b.rubric.reduce((s: number, y: { diem: number }) => s + y.diem, 0);
					expect(tong, `${b.so} rubric`).toBe(10);
				}
			} else {
				expect(String(b.khung ?? '').trim().length, `${b.so} khung`).toBeGreaterThan(0);
				expect(String(b.test_vi_du ?? ''), `${b.so} test ví dụ`).toContain('OK');
				expect(String(b.test_an ?? ''), `${b.so} test ẩn`).toContain('OK');
			}
		}
	});

	it('link liên quan tồn tại', () => {
		for (const b of BAI) {
			for (const x of b.lien_quan ?? []) {
				expect(trangTonTai(x.trang), `${b.so} → ${x.trang}`).toBe(true);
			}
		}
	});
});
