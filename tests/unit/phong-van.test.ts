import { describe, it, expect } from 'vitest';
import fs from 'node:fs';
import path from 'node:path';
import YAML from 'yaml';

const THU_MUC = path.resolve('src/data/phong-van');
const PRESET = fs
	.readdirSync(THU_MUC)
	.filter((f) => f.endsWith('.yaml'))
	.map((f) => YAML.parse(fs.readFileSync(path.join(THU_MUC, f), 'utf8')) as Record<string, unknown>);

describe('preset phỏng vấn', () => {
	it('đúng 8 preset, id duy nhất', () => {
		expect(PRESET).toHaveLength(8);
		expect(new Set(PRESET.map((p) => p.id)).size).toBe(8);
	});
	it('mỗi preset có nguồn, trọng tâm, ít nhất 3 vòng và câu hỏi', () => {
		for (const p of PRESET) {
			expect(String(p.nguon).length).toBeGreaterThan(30);
			expect(Array.isArray(p.trongTam) && (p.trongTam as unknown[]).length).toBeGreaterThan(0);
			expect((p.vong as unknown[]).length).toBeGreaterThanOrEqual(3);
			const ch = p.cau_hoi as Record<string, string[]>;
			const tong = Object.values(ch).reduce((s, x) => s + x.length, 0);
			expect(tong).toBeGreaterThan(0);
		}
	});
	it('có preset kiểu Google với vòng code và ML', () => {
		const g = PRESET.find((p) => p.id === 'google')!;
		const loai = (g.vong as { loai: string }[]).map((v) => v.loai);
		expect(loai).toContain('code');
		expect(loai).toContain('ml');
		expect(loai).toContain('system');
	});
});
