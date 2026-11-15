/**
 * Một hàm máy chủ cho trợ lý học tập, chấm tự luận và (sau này) phỏng vấn.
 * Chạy trên Vercel Edge: Web Request/Response, không cần SDK.
 * Lời nhắc nằm ở đây nên người dùng không sửa được.
 */

export const config = { runtime: 'edge' };

type Loai = 'tro-ly' | 'cham' | 'phong-van';
type Vai = 'user' | 'assistant' | 'system';
interface TinNhan {
	role: Vai;
	content: string;
}

interface YeuCau {
	mode?: Loai;
	messages?: TinNhan[];
	/** Ngữ cảnh ngắn: trang đang mở, đoạn bôi đen, code, lỗi gần nhất. */
	context?: {
		trang?: string;
		tieuDe?: string;
		boiDen?: string;
		code?: string;
		loi?: string;
	};
	/** Dùng cho chấm tự luận: đề, rubric, bài làm. */
	cham?: {
		de?: string;
		rubric?: { y: string; diem: number }[];
		baiLam?: string;
	};
}

const DIEM: Record<Loai, number> = { 'tro-ly': 1, cham: 3, 'phong-van': 15 };
const GIOI_HAN_KHACH = 40;
const GIOI_HAN_DA_DANG_NHAP = 100;
const TRAN_SITE = 1500;
const TOI_DA_CAU = 2000;
const TOI_DA_CODE = 8000;
const TOI_DA_LICH_SU = 12;

const LOI_NHAC_GIA_SU = `Bạn là gia sư AI cho giáo trình tiếng Việt "AI & Robotics" (từ Python tới mô hình ngôn ngữ lớn).
Quy tắc:
- Trả lời ngắn gọn, dễ hiểu, đúng thuật ngữ, có ví dụ cụ thể gắn với bài đang học.
- Không giải hộ bài tập. Khi người học xin đáp án, chỉ gợi ý hướng nghĩ hoặc câu hỏi dẫn dắt.
- Khi chưa chắc, nói rõ chưa chắc, đừng bịa số liệu hay tên tài liệu.
- Cuối câu trả lời, nếu hợp lý, chỉ 1-2 trang liên quan trong giáo trình (dạng /ai-engineer/...) và hỏi ngược lại một câu để người học tự nghĩ.
- Trả lời bằng tiếng Việt, xưng "mình", gọi người học là "bạn".`;

const LOI_NHAC_CHAM = `Bạn là giám khảo chấm bài tự luận cho giáo trình AI. Chấm theo đúng rubric được đưa.
Yêu cầu:
- Chấm từng ý, mỗi ý có điểm đạt (số) và trích dẫn nguyên văn một đoạn trong bài làm làm bằng chứng.
- Bài trống hoặc lạc đề: 0 điểm, ghi rõ lý do.
- Không cộng điểm vượt quá điểm tối đa của ý.
- Chỉ trả về JSON đúng schema, không thêm chữ ngoài JSON:
{"diem": <tổng điểm thang 10>, "y": [{"y": "<tên ý>", "diem": <điểm đạt>, "toiDa": <điểm tối đa>, "trichDan": "<câu trong bài>"}], "nhanXet": "<2-3 câu>"}`;

interface NhaCungCap {
	ten: 'gemini' | 'groq' | 'openrouter';
	khoa: string | undefined;
	model: string;
}

function danhSach(): NhaCungCap[] {
	return [
		{ ten: 'gemini', khoa: process.env.GEMINI_API_KEY, model: process.env.GEMINI_MODEL || 'gemini-2.0-flash' },
		{ ten: 'groq', khoa: process.env.GROQ_API_KEY, model: process.env.GROQ_MODEL || 'llama-3.3-70b-versatile' },
		{
			ten: 'openrouter',
			khoa: process.env.OPENROUTER_API_KEY,
			model: process.env.OPENROUTER_MODEL || 'meta-llama/llama-3.3-70b-instruct:free',
		},
	];
}

function json(body: unknown, status = 200): Response {
	return new Response(JSON.stringify(body), {
		status,
		headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store' },
	});
}

function gioiHanTheoMode(mode: Loai): number {
	return DIEM[mode];
}

/** Ngày theo giờ Việt Nam (UTC+7), dùng làm khóa đếm lượt. */
export function ngayVN(d = new Date()): string {
	const t = new Date(d.getTime() + 7 * 3600_000);
	return t.toISOString().slice(0, 10);
}

export function kiemTraDauVao(body: unknown): { ok: true; du: YeuCau } | { ok: false; loi: string } {
	if (!body || typeof body !== 'object') return { ok: false, loi: 'Thiếu dữ liệu' };
	const b = body as YeuCau;
	const mode = b.mode;
	if (mode !== 'tro-ly' && mode !== 'cham' && mode !== 'phong-van') return { ok: false, loi: 'mode không hợp lệ' };
	if (mode === 'cham') {
		if (!b.cham?.de || !b.cham?.baiLam) return { ok: false, loi: 'Thiếu đề hoặc bài làm' };
		if (b.cham.de.length > TOI_DA_CAU * 2 || b.cham.baiLam.length > TOI_DA_CODE) return { ok: false, loi: 'Bài làm quá dài' };
		if (!Array.isArray(b.cham.rubric) || b.cham.rubric.length === 0 || b.cham.rubric.length > 20) return { ok: false, loi: 'Rubric không hợp lệ' };
		return { ok: true, du: b };
	}
	const msgs = b.messages;
	if (!Array.isArray(msgs) || msgs.length === 0) return { ok: false, loi: 'Thiếu câu hỏi' };
	if (msgs.length > TOI_DA_LICH_SU) return { ok: false, loi: 'Lịch sử quá dài' };
	let tong = 0;
	for (const m of msgs) {
		if (!m || (m.role !== 'user' && m.role !== 'assistant') || typeof m.content !== 'string') return { ok: false, loi: 'Tin nhắn không hợp lệ' };
		tong += m.content.length;
	}
	if (tong > TOI_DA_CAU * TOI_DA_LICH_SU) return { ok: false, loi: 'Câu hỏi quá dài' };
	const c = b.context ?? {};
	if ((c.code ?? '').length > TOI_DA_CODE || (c.boiDen ?? '').length > TOI_DA_CAU || (c.loi ?? '').length > 6000) return { ok: false, loi: 'Ngữ cảnh quá dài' };
	return { ok: true, du: b };
}

/** Kiểm Origin: chỉ nhận yêu cầu từ site và các bản xem trước. */
export function originHopLe(origin: string | null): boolean {
	if (!origin) return false;
	let u: URL;
	try {
		u = new URL(origin);
	} catch {
		return false;
	}
	if (u.hostname === 'localhost' || u.hostname === '127.0.0.1') return true;
	if (u.hostname === 'ai-and-robotics-handbook.vercel.app') return true;
	// Bản preview của Vercel: <hash>-<tài khoản>.vercel.app
	if (u.hostname.endsWith('.vercel.app') && u.hostname.includes('mhieuz-dev')) return true;
	const them = (process.env.ALLOWED_ORIGINS ?? '').split(',').map((x) => x.trim()).filter(Boolean);
	return them.includes(origin);
}

async function bam(s: string): Promise<string> {
	const d = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(s));
	return [...new Uint8Array(d)].slice(0, 12).map((x) => x.toString(16).padStart(2, '0')).join('');
}

interface KetQuaDem {
	ok: boolean;
	con: number;
}

async function demUpstash(khoa: string, diem: number, gioiHan: number): Promise<KetQuaDem> {
	const url = process.env.UPSTASH_REDIS_REST_URL;
	const token = process.env.UPSTASH_REDIS_REST_TOKEN;
	if (!url || !token) return { ok: true, con: Infinity };
	try {
		const r = await fetch(`${url}/pipeline`, {
			method: 'POST',
			headers: { authorization: `Bearer ${token}`, 'content-type': 'application/json' },
			body: JSON.stringify([
				['INCRBY', khoa, String(diem)],
				['EXPIRE', khoa, '172800', 'NX'],
			]),
		});
		if (!r.ok) return { ok: true, con: Infinity };
		const kq = (await r.json()) as { result: number }[];
		const daDung = Number(kq?.[0]?.result ?? 0);
		return { ok: daDung <= gioiHan, con: Math.max(0, gioiHan - daDung) };
	} catch {
		return { ok: true, con: Infinity };
	}
}

async function kiemLuot(ip: string, mode: Loai): Promise<{ ok: boolean; con: number; tong: boolean }> {
	const ngay = ngayVN();
	const id = await bam(ip);
	const khach = await demUpstash(`ai:g:${id}:${ngay}`, gioiHanTheoMode(mode), GIOI_HAN_KHACH);
	if (!khach.ok) return { ok: false, con: 0, tong: false };
	const tong = await demUpstash(`ai:site:${ngay}`, gioiHanTheoMode(mode), TRAN_SITE);
	return { ok: tong.ok, con: khach.con, tong: tong.ok };
}

interface KqNhaCungCap {
	text: string;
	ten: string;
}

async function goiGemini(n: NhaCungCap, system: string, messages: TinNhan[]): Promise<string> {
	const contents = messages.map((m) => ({ role: m.role === 'assistant' ? 'model' : 'user', parts: [{ text: m.content }] }));
	const r = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${encodeURIComponent(n.model)}:generateContent?key=${encodeURIComponent(n.khoa!)}`, {
		method: 'POST',
		headers: { 'content-type': 'application/json' },
		body: JSON.stringify({
			system_instruction: { parts: [{ text: system }] },
			contents,
			generationConfig: { temperature: 0.4, maxOutputTokens: 1200 },
		}),
	});
	if (!r.ok) throw new Error(`gemini ${r.status}`);
	const d = (await r.json()) as { candidates?: { content?: { parts?: { text?: string }[] } }[] };
	const text = d.candidates?.[0]?.content?.parts?.map((p) => p.text ?? '').join('') ?? '';
	if (!text) throw new Error('gemini rỗng');
	return text;
}

async function goiOpenAICompat(n: NhaCungCap, system: string, messages: TinNhan[]): Promise<string> {
	const url = n.ten === 'groq' ? 'https://api.groq.com/openai/v1/chat/completions' : 'https://openrouter.ai/api/v1/chat/completions';
	const header: Record<string, string> = { 'content-type': 'application/json', authorization: `Bearer ${n.khoa}` };
	if (n.ten === 'openrouter') {
		header['http-referer'] = 'https://ai-and-robotics-handbook.vercel.app';
		header['x-title'] = 'AI & Robotics Handbook';
	}
	const r = await fetch(url, {
		method: 'POST',
		headers: header,
		body: JSON.stringify({
			model: n.model,
			temperature: 0.4,
			max_tokens: 1200,
			messages: [{ role: 'system', content: system }, ...messages.map((m) => ({ role: m.role, content: m.content }))],
		}),
	});
	if (!r.ok) throw new Error(`${n.ten} ${r.status}`);
	const d = (await r.json()) as { choices?: { message?: { content?: string } }[] };
	const text = d.choices?.[0]?.message?.content ?? '';
	if (!text) throw new Error(`${n.ten} rỗng`);
	return text;
}

async function goiMot(n: NhaCungCap, system: string, messages: TinNhan[]): Promise<string> {
	return n.ten === 'gemini' ? goiGemini(n, system, messages) : goiOpenAICompat(n, system, messages);
}

/** Thử lần lượt các nhà cung cấp free; cái nào lỗi/hết lượt thì sang cái kế. */
export async function goiAI(system: string, messages: TinNhan[]): Promise<KqNhaCungCap> {
	for (const n of danhSach()) {
		if (!n.khoa) continue;
		try {
			const text = await goiMot(n, system, messages);
			return { text, ten: n.ten };
		} catch {
			/* sang nhà cung cấp kế */
		}
	}
	throw new Error('het-nha-cung-cap');
}

function dungNguCanh(c: YeuCau['context']): string {
	if (!c) return '';
	const phan: string[] = [];
	if (c.tieuDe) phan.push(`Trang đang mở: ${c.tieuDe}`);
	if (c.trang) phan.push(`Đường dẫn: ${c.trang}`);
	if (c.boiDen) phan.push(`Đoạn người học bôi đen:\n"""${c.boiDen}"""`);
	if (c.code) phan.push(`Code trong khung:\n\`\`\`python\n${c.code}\n\`\`\``);
	if (c.loi) phan.push(`Lỗi gần nhất:\n${c.loi}`);
	return phan.length ? `\n\nNgữ cảnh hiện tại:\n${phan.join('\n')}` : '';
}

function tinNhanCham(b: NonNullable<YeuCau['cham']>): TinNhan[] {
	const rubric = (b.rubric ?? []).map((y, i) => `${i + 1}. ${y.y} (${y.diem} điểm)`).join('\n');
	return [
		{
			role: 'user',
			content: `Đề bài:\n${b.de}\n\nRubric (tổng 10 điểm):\n${rubric}\n\nBài làm của học viên:\n"""${b.baiLam}"""\n\nHãy chấm theo đúng schema JSON đã nêu.`,
		},
	];
}

export default async function handler(req: Request): Promise<Response> {
	if (req.method !== 'POST') return json({ loi: 'Chỉ nhận POST' }, 405);
	if (!originHopLe(req.headers.get('origin'))) return json({ loi: 'Nguồn gọi không hợp lệ' }, 403);

	let body: unknown;
	try {
		body = await req.json();
	} catch {
		return json({ loi: 'JSON không hợp lệ' }, 400);
	}
	const kiem = kiemTraDauVao(body);
	if (!('du' in kiem)) return json({ loi: kiem.loi }, 400);
	const du = kiem.du;
	const mode = du.mode!;

	const ip = (req.headers.get('x-forwarded-for') ?? '').split(',')[0].trim() || 'khong-ro';
	const luot = await kiemLuot(ip, mode);
	if (!luot.ok) {
		return json(
			{
				loi: 'het-luot',
				thongBao: luot.tong
					? 'Hết lượt AI miễn phí hôm nay. Mai quay lại, hoặc dán key riêng của bạn để dùng không giới hạn.'
					: 'Cả site đã dùng hết lượt AI miễn phí hôm nay. Mai quay lại nhé.',
			},
			429,
		);
	}

	if (process.env.AI_MOCK === '1') {
		const text =
			mode === 'cham'
				? JSON.stringify({ diem: 7, y: [], nhanXet: 'Chế độ thử: chưa gọi nhà cung cấp thật.' })
				: 'Đây là câu trả lời thử của trợ lý. Máy chủ đang chạy ở chế độ AI_MOCK.';
		return json({ text, nhaCungCap: 'mock', con: luot.con });
	}

	const system = mode === 'cham' ? LOI_NHAC_CHAM : LOI_NHAC_GIA_SU;
	const messages: TinNhan[] = mode === 'cham' ? tinNhanCham(du.cham!) : [...(du.messages ?? [])];
	if (mode === 'tro-ly') {
		const nc = dungNguCanh(du.context);
		if (nc && messages.length) messages[messages.length - 1] = { ...messages[messages.length - 1], content: messages[messages.length - 1].content + nc };
	}

	try {
		const kq = await goiAI(system, messages);
		if (mode === 'cham') {
			try {
				const j = JSON.parse(kq.text.replace(/^```json\s*|```$/g, '').trim());
				return json({ cham: j, nhaCungCap: kq.ten, con: luot.con });
			} catch {
				return json({ text: kq.text, nhaCungCap: kq.ten, con: luot.con });
			}
		}
		return json({ text: kq.text, nhaCungCap: kq.ten, con: luot.con });
	} catch {
		return json({ loi: 'het-nha-cung-cap', thongBao: 'Các nhà cung cấp AI free đang quá tải hoặc hết lượt. Thử lại sau ít phút, hoặc dán key riêng.' }, 503);
	}
}
