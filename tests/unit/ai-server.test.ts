import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { kiemTraDauVao, originHopLe, ngayVN, goiAI } from '../../api/ai';

describe('kiểm tra đầu vào máy chủ AI', () => {
	it('nhận câu hỏi trợ lý hợp lệ', () => {
		const kq = kiemTraDauVao({ mode: 'tro-ly', messages: [{ role: 'user', content: 'Vì sao cần chuẩn hóa?' }] });
		expect(kq.ok).toBe(true);
	});
	it('từ chối mode lạ, thiếu câu hỏi, lịch sử quá dài', () => {
		expect(kiemTraDauVao({ mode: 'x' }).ok).toBe(false);
		expect(kiemTraDauVao({ mode: 'tro-ly', messages: [] }).ok).toBe(false);
		expect(kiemTraDauVao({ mode: 'tro-ly', messages: Array.from({ length: 13 }, () => ({ role: 'user', content: 'x' })) }).ok).toBe(false);
	});
	it('giới hạn độ dài code và đoạn bôi đen', () => {
		const dai = 'x'.repeat(9000);
		expect(kiemTraDauVao({ mode: 'tro-ly', messages: [{ role: 'user', content: 'hỏi' }], context: { code: dai } }).ok).toBe(false);
	});
	it('phỏng vấn cần lịch sử hợp lệ', () => {
		const ok = kiemTraDauVao({
			mode: 'phong-van',
			phongVan: { lichSu: [{ vong: 'Sàng lọc', cauHoi: 'Kể về dự án', traLoi: 'Em làm...' }] },
		});
		expect(ok.ok).toBe(true);
		expect(kiemTraDauVao({ mode: 'phong-van', phongVan: { lichSu: [] } }).ok).toBe(false);
		expect(kiemTraDauVao({ mode: 'phong-van', phongVan: { lichSu: [{ vong: 'x', cauHoi: 1, traLoi: 'y' }] } }).ok).toBe(false);
	});
	it('chấm tự luận cần đề, bài làm và rubric', () => {
		expect(kiemTraDauVao({ mode: 'cham', cham: { de: 'đề', baiLam: 'bài' } }).ok).toBe(false);
		const kq = kiemTraDauVao({ mode: 'cham', cham: { de: 'đề', baiLam: 'bài', rubric: [{ y: 'ý 1', diem: 10 }] } });
		expect(kq.ok).toBe(true);
	});
});

describe('kiểm Origin', () => {
	it('nhận site, localhost và bản preview của mình', () => {
		expect(originHopLe('https://ai-and-robotics-handbook.vercel.app')).toBe(true);
		expect(originHopLe('http://localhost:4399')).toBe(true);
		expect(originHopLe('https://abc-mhieuz-dev.vercel.app')).toBe(true);
	});
	it('từ chối site lạ và origin rỗng', () => {
		expect(originHopLe('https://evil.example')).toBe(false);
		expect(originHopLe(null)).toBe(false);
		expect(originHopLe('không-phải-url')).toBe(false);
	});
});

describe('ngày Việt Nam', () => {
	it('20:00 UTC đã sang ngày mới ở UTC+7', () => {
		expect(ngayVN(new Date('2026-11-15T20:00:00Z'))).toBe('2026-11-16');
		expect(ngayVN(new Date('2026-11-15T10:00:00Z'))).toBe('2026-11-15');
	});
});

describe('chuyển nhà cung cấp khi một cái lỗi', () => {
	const khoa = ['GEMINI_API_KEY', 'GROQ_API_KEY', 'OPENROUTER_API_KEY'] as const;
	const goc = Object.fromEntries(khoa.map((k) => [k, process.env[k]]));
	beforeEach(() => {
		process.env.GEMINI_API_KEY = 'g';
		process.env.GROQ_API_KEY = 'q';
		delete process.env.OPENROUTER_API_KEY;
	});
	afterEach(() => {
		for (const k of khoa) {
			if (goc[k] === undefined) delete process.env[k];
			else process.env[k] = goc[k];
		}
		vi.restoreAllMocks();
	});

	it('Gemini 429 thì chuyển sang Groq', async () => {
		const goi = vi.fn(async (url: string) => {
			if (String(url).includes('generativelanguage')) return new Response('hết lượt', { status: 429 });
			return new Response(JSON.stringify({ choices: [{ message: { content: 'trả lời từ groq' } }] }), { status: 200 });
		});
		vi.stubGlobal('fetch', goi);
		const kq = await goiAI('system', [{ role: 'user', content: 'hỏi' }]);
		expect(kq.ten).toBe('groq');
		expect(kq.text).toBe('trả lời từ groq');
		expect(goi).toHaveBeenCalledTimes(2);
	});

	it('không có key nào thì báo hết nhà cung cấp', async () => {
		delete process.env.GEMINI_API_KEY;
		delete process.env.GROQ_API_KEY;
		await expect(goiAI('system', [{ role: 'user', content: 'hỏi' }])).rejects.toThrow('het-nha-cung-cap');
	});
});
