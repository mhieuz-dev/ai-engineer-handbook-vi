/** Gọi máy chủ AI của site, hoặc gọi thẳng nhà cung cấp nếu người học dán key riêng. */
import { layIdToken } from '../firebase';

export type NhaCungCap = 'gemini' | 'groq' | 'openrouter';

export interface KhoaRieng {
	nhaCungCap: NhaCungCap;
	khoa: string;
	model: string;
}

export interface NguCanh {
	trang?: string;
	tieuDe?: string;
	boiDen?: string;
	code?: string;
	loi?: string;
}

export interface TinNhan {
	role: 'user' | 'assistant';
	content: string;
}

export interface TraLoi {
	text?: string;
	cham?: unknown;
	nhaCungCap?: string;
	con?: number;
	loi?: string;
	thongBao?: string;
}

const KHOA_KEY = 'air-ai-key-v1';

export const MODEL_GOI_Y: Record<NhaCungCap, string> = {
	gemini: 'gemini-2.0-flash',
	groq: 'llama-3.3-70b-versatile',
	openrouter: 'meta-llama/llama-3.3-70b-instruct:free',
};

export function docKhoaRieng(): KhoaRieng | null {
	try {
		const o = JSON.parse(localStorage.getItem(KHOA_KEY) ?? 'null');
		if (!o || typeof o.khoa !== 'string' || !['gemini', 'groq', 'openrouter'].includes(o.nhaCungCap)) return null;
		return { nhaCungCap: o.nhaCungCap, khoa: o.khoa, model: typeof o.model === 'string' && o.model ? o.model : MODEL_GOI_Y[o.nhaCungCap as NhaCungCap] };
	} catch {
		return null;
	}
}

export function luuKhoaRieng(k: KhoaRieng): void {
	try {
		localStorage.setItem(KHOA_KEY, JSON.stringify(k));
	} catch {
		/* chặn storage: bỏ qua */
	}
}

export function xoaKhoaRieng(): void {
	try {
		localStorage.removeItem(KHOA_KEY);
	} catch {
		/* bỏ qua */
	}
}

const LOI_NHAC_GIA_SU =
	'Bạn là gia sư AI cho giáo trình tiếng Việt "AI & Robotics". Trả lời ngắn, có ví dụ, đúng thuật ngữ. ' +
	'Không giải hộ bài tập; chỉ gợi ý hướng nghĩ. Khi chưa chắc thì nói rõ. Cuối câu trả lời hỏi ngược lại một câu.';

async function goiGemini(k: KhoaRieng, messages: TinNhan[], nguCanh: string): Promise<string> {
	const contents = messages.map((m) => ({ role: m.role === 'assistant' ? 'model' : 'user', parts: [{ text: m.content }] }));
	if (nguCanh) contents[contents.length - 1].parts[0].text += nguCanh;
	const r = await fetch(
		`https://generativelanguage.googleapis.com/v1beta/models/${encodeURIComponent(k.model)}:generateContent?key=${encodeURIComponent(k.khoa)}`,
		{
			method: 'POST',
			headers: { 'content-type': 'application/json' },
			body: JSON.stringify({ system_instruction: { parts: [{ text: LOI_NHAC_GIA_SU }] }, contents, generationConfig: { temperature: 0.4, maxOutputTokens: 1200 } }),
		},
	);
	if (!r.ok) throw new Error(`Gemini ${r.status}`);
	const d = (await r.json()) as { candidates?: { content?: { parts?: { text?: string }[] } }[] };
	const text = d.candidates?.[0]?.content?.parts?.map((p) => p.text ?? '').join('') ?? '';
	if (!text) throw new Error('Gemini trả về rỗng');
	return text;
}

async function goiOpenRouter(k: KhoaRieng, messages: TinNhan[], nguCanh: string): Promise<string> {
	const msgs = messages.map((m) => ({ role: m.role, content: m.content }));
	if (nguCanh) msgs[msgs.length - 1].content += nguCanh;
	const r = await fetch('https://openrouter.ai/api/v1/chat/completions', {
		method: 'POST',
		headers: {
			'content-type': 'application/json',
			authorization: `Bearer ${k.khoa}`,
			'http-referer': location.origin,
			'x-title': 'AI & Robotics Handbook',
		},
		body: JSON.stringify({ model: k.model, temperature: 0.4, max_tokens: 1200, messages: [{ role: 'system', content: LOI_NHAC_GIA_SU }, ...msgs] }),
	});
	if (!r.ok) throw new Error(`OpenRouter ${r.status}`);
	const d = (await r.json()) as { choices?: { message?: { content?: string } }[] };
	const text = d.choices?.[0]?.message?.content ?? '';
	if (!text) throw new Error('OpenRouter trả về rỗng');
	return text;
}

function nguCanhThanhChu(c: NguCanh | undefined): string {
	if (!c) return '';
	const phan: string[] = [];
	if (c.tieuDe) phan.push(`Trang đang mở: ${c.tieuDe}`);
	if (c.boiDen) phan.push(`Đoạn bôi đen:\n"""${c.boiDen}"""`);
	if (c.code) phan.push(`Code trong khung:\n\`\`\`python\n${c.code}\n\`\`\``);
	if (c.loi) phan.push(`Lỗi gần nhất:\n${c.loi}`);
	return phan.length ? `\n\nNgữ cảnh:\n${phan.join('\n')}` : '';
}

export interface YeuCauHoi {
	messages: TinNhan[];
	context?: NguCanh;
}

export async function hoiTroLy({ messages, context }: YeuCauHoi): Promise<TraLoi> {
	const khoa = docKhoaRieng();
	if (khoa) {
		if (khoa.nhaCungCap === 'groq') {
			return {
				loi: 'groq-cors',
				thongBao: 'Groq thường chặn gọi thẳng từ trình duyệt. Hãy dùng key Gemini hoặc OpenRouter cho key riêng, hoặc xoá key để dùng lượt miễn phí của site.',
			};
		}
		try {
			const nc = nguCanhThanhChu(context);
			const text = khoa.nhaCungCap === 'gemini' ? await goiGemini(khoa, messages, nc) : await goiOpenRouter(khoa, messages, nc);
			return { text, nhaCungCap: `${khoa.nhaCungCap} (key riêng)` };
		} catch (e) {
			return { loi: 'key-rieng', thongBao: `Key riêng không dùng được: ${e instanceof Error ? e.message : String(e)}. Kiểm tra lại key và tên model.` };
		}
	}

	try {
		const header: Record<string, string> = { 'content-type': 'application/json' };
		const token = await layIdToken();
		if (token) header.authorization = `Bearer ${token}`;
		const r = await fetch('/api/ai', {
			method: 'POST',
			headers: header,
			body: JSON.stringify({ mode: 'tro-ly', messages, context }),
		});
		if (r.status === 429) {
			const d = (await r.json()) as TraLoi;
			return { loi: 'het-luot', thongBao: d.thongBao ?? 'Hết lượt AI miễn phí hôm nay.' };
		}
		if (!r.ok) {
			const d = (await r.json().catch(() => ({}))) as TraLoi;
			return { loi: 'may-chu', thongBao: d.thongBao ?? 'Máy chủ AI chưa sẵn sàng.' };
		}
		return (await r.json()) as TraLoi;
	} catch {
		return { loi: 'mang', thongBao: 'Không kết nối được máy chủ AI. Kiểm tra mạng rồi thử lại.' };
	}
}

export interface ChamKetQua {
	diem: number;
	y?: { y: string; diem: number; toiDa?: number; trichDan?: string }[];
	nhanXet?: string;
}

/** Chấm một bài tự luận theo rubric; trả null khi máy chủ AI không sẵn sàng. */
export async function chamBai(de: string, rubric: { y: string; diem: number }[], baiLam: string): Promise<ChamKetQua | null> {
	const header: Record<string, string> = { 'content-type': 'application/json' };
	const token = await layIdToken();
	if (token) header.authorization = `Bearer ${token}`;
	try {
		const r = await fetch('/api/ai', {
			method: 'POST',
			headers: header,
			body: JSON.stringify({ mode: 'cham', cham: { de, rubric, baiLam } }),
		});
		if (!r.ok) return null;
		const d = (await r.json()) as { cham?: ChamKetQua };
		const c = d.cham;
		if (!c) return null;
		let diem = typeof c.diem === 'number' ? c.diem : null;
		if (diem === null && Array.isArray(c.y)) {
			const toiDa = c.y.reduce((s, x) => s + (x.toiDa ?? 0), 0) || rubric.reduce((s, x) => s + x.diem, 0);
			const dat = c.y.reduce((s, x) => s + (x.diem ?? 0), 0);
			diem = toiDa ? (dat / toiDa) * 10 : 0;
		}
		if (diem === null) return null;
		return { ...c, diem };
	} catch {
		return null;
	}
}
