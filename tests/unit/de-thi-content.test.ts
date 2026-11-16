import { describe, it, expect } from 'vitest';
import fs from 'node:fs';
import path from 'node:path';
import YAML from 'yaml';

const THU_MUC = path.resolve('src/data/de-thi');
const TEP = fs.readdirSync(THU_MUC).filter((f) => f.endsWith('.yaml')).sort();
const DE = TEP.map((f) => YAML.parse(fs.readFileSync(path.join(THU_MUC, f), 'utf8')) as Record<string, any>);

function trangTonTai(trang: string): boolean {
	const slug = trang.replace(/^\/+|\/+$/g, '');
	const thuMuc = path.resolve('src/content/docs', slug);
	const tep = path.resolve('src/content/docs', `${slug}.mdx`);
	if (fs.existsSync(tep)) return true;
	return fs.existsSync(thuMuc) && fs.readdirSync(thuMuc).some((f) => f.endsWith('.mdx'));
}

describe('ngân hàng đề: cấu trúc và chất lượng', () => {
	it('có Ch0-Ch4 và id câu hỏi không trùng toàn bộ', () => {
		const so = DE.map((d) => d.chuong).sort((a, b) => a - b);
		expect(so.slice(0, 5)).toEqual([0, 1, 2, 3, 4]);
		const ids = DE.flatMap((d) => d.cau_hoi.map((c: { id: string }) => c.id));
		expect(new Set(ids).size).toBe(ids.length);
	});

	it('mỗi khái niệm có link trang tồn tại', () => {
		for (const d of DE) {
			const ids = new Set(d.khai_niem.map((k: { id: string }) => k.id));
			for (const k of d.khai_niem) {
				expect(trangTonTai(k.trang), `${d.chuong} ${k.id} → ${k.trang}`).toBe(true);
			}
			for (const c of d.cau_hoi) {
				expect(Array.isArray(c.khai_niem) && c.khai_niem.length, `${c.id} khai_niem`).toBeTruthy();
				for (const id of c.khai_niem) expect(ids.has(id), `${c.id} trỏ ${id}`).toBe(true);
			}
		}
	});

	it('trắc nghiệm đúng một đáp án, lựa chọn không trùng', () => {
		for (const d of DE) {
			for (const c of d.cau_hoi.filter((x: { loai: string }) => x.loai === 'trac-nghiem')) {
				expect(Array.isArray(c.lua_chon), c.id).toBe(true);
				expect(new Set(c.lua_chon).size, `${c.id} lựa chọn trùng`).toBe(c.lua_chon.length);
				expect(Number.isInteger(c.dap_an) && c.dap_an >= 0 && c.dap_an < c.lua_chon.length, `${c.id} dap_an`).toBe(true);
				expect(String(c.giai_thich).trim().length, `${c.id} giải thích`).toBeGreaterThan(0);
			}
		}
	});

	it('rubric tự luận và nhiệm vụ case cộng đủ 10 điểm', () => {
		for (const d of DE) {
			for (const c of d.cau_hoi) {
				if (c.loai === 'tu-luan') {
					const tong = c.rubric.reduce((s: number, y: { diem: number }) => s + y.diem, 0);
					expect(tong, `${c.id} rubric`).toBe(10);
				}
				if (c.loai === 'case') {
					const tong = c.nhiem_vu.reduce((s: number, y: { diem: number }) => s + y.diem, 0);
					expect(tong, `${c.id} nhiệm vụ`).toBe(10);
					for (const nv of c.nhiem_vu) {
						if (nv.loai === 'code') expect(String(nv.kiem_tra), `${c.id} code`).toContain('OK');
						if (nv.loai === 'tu-luan') expect((nv.rubric ?? []).length, `${c.id} rubric nv`).toBeGreaterThan(0);
					}
				}
			}
		}
	});

	it('bài code có test in OK và lời giải', () => {
		for (const d of DE) {
			for (const c of d.cau_hoi.filter((x: { loai: string }) => x.loai === 'code')) {
				expect(String(c.kiem_tra), `${c.id} kiem_tra`).toContain('OK');
				expect(String(c.khung).trim().length, `${c.id} khung`).toBeGreaterThan(0);
				expect(String(c.loi_giai).trim().length, `${c.id} lời giải`).toBeGreaterThan(0);
				expect(String(c.kiem_tra), `${c.id} code`).toContain('OK');
			}
		}
	});

	it('Ch0-Ch4 đủ 10 trắc nghiệm + 2 tự luận + 1 code + 1 case mỗi chương', () => {
		for (const d of DE.filter((x) => x.chuong <= 4)) {
			const dem = (l: string) => d.cau_hoi.filter((x: { loai: string }) => x.loai === l).length;
			expect({ chuong: d.chuong, tn: dem('trac-nghiem'), tl: dem('tu-luan'), code: dem('code'), case: dem('case') }).toEqual({
				chuong: d.chuong,
				tn: 10,
				tl: 2,
				code: 1,
				case: 1,
			});
		}
	});
});
