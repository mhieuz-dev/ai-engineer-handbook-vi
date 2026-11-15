/** Điều khiển khung code nổi: mở/đóng, chạy Pyodide, thử ngay, lưu nháp, trợ lý. */
import { giaiThichLoi, type LoiDaHieu } from './loi';
import { soOutput } from './so-output';
import { MayChay } from './chay';
import type { TrinhSoan } from './editor';

const KHOA_NHAP = 'air-khung-code-v1';
const MA_MAU = '# Gõ code Python ở đây rồi bấm Chạy (Ctrl+Enter).\nprint("Xin chào!")\n';

interface Khoi {
	figure: HTMLElement;
	pre: HTMLPreElement;
	ma: string;
	output: string | null;
	tieuDe: string;
	canColab: boolean;
	laPip: boolean;
	nut?: HTMLButtonElement;
}

function tachDong(pre: HTMLElement): string {
	const dong = pre.querySelectorAll('.ec-line');
	if (dong.length) return [...dong].map((e) => e.textContent ?? '').join('\n');
	return pre.textContent ?? '';
}

function timOutput(figure: HTMLElement): string | null {
	let n = figure.parentElement?.nextElementSibling;
	while (n) {
		if (n.matches('.expressive-code')) {
			const f2 = n.querySelector('figure');
			const tieuDe = f2?.querySelector('.title')?.textContent?.trim();
			if (tieuDe === 'Output') {
				const pre = f2?.querySelector('pre');
				return pre ? tachDong(pre as HTMLElement) : null;
			}
			return null;
		}
		n = n.nextElementSibling;
	}
	return null;
}

function canColab(ma: string): boolean {
	return (
		/^\s*(?:import|from)\s+(torch|torchvision|torchaudio|transformers|gymnasium|stable_baselines3|sentence_transformers|datasets|huggingface_hub|accelerate|peft|trl)\b/m.test(ma) ||
		/\btorch\./.test(ma) ||
		/\btransformers\./.test(ma) ||
		/\bfrom_pretrained\s*\(/.test(ma)
	);
}

export function khoiTaoKhungCode(): void {
	const panel = document.getElementById('kc-panel') as HTMLElement | null;
	const nutMo = document.querySelector<HTMLButtonElement>('.kc-nut');
	if (!panel || !nutMo) return;
	// Đưa ra body để không bị ngữ cảnh xếp lớp của main/khung nội dung cắt mất.
	document.body.append(nutMo, panel);

	const $ = <T extends HTMLElement>(s: string) => panel.querySelector<T>(s)!;
	const el = {
		editor: $('.kc-editor'),
		code: $<HTMLElement>('.kc-code'),
		troLy: $<HTMLElement>('.kc-troly'),
		out: $<HTMLElement>('.kc-out'),
		hinh: $<HTMLElement>('.kc-hinh'),
		kqTen: $<HTMLElement>('.kc-kq-ten'),
		kqNhan: $<HTMLElement>('.kc-kq-nhan'),
		trangThai: $<HTMLElement>('.kc-trang-thai'),
		chay: $<HTMLButtonElement>('.kc-chay'),
		dung: $<HTMLButtonElement>('.kc-dung'),
		undo: $<HTMLButtonElement>('.kc-undo'),
		redo: $<HTMLButtonElement>('.kc-redo'),
		khoiPhuc: $<HTMLButtonElement>('.kc-khoi-phuc'),
		dong: $<HTMLButtonElement>('.kc-dong'),
		keo: $<HTMLElement>('.kc-keo'),
		tlNoi: $<HTMLElement>('.kc-tl-tra-loi'),
		tlCau: $<HTMLTextAreaElement>('.kc-tl-cau'),
		tlForm: $<HTMLFormElement>('.kc-tl-form'),
	};

	const may = new MayChay();
	const slug = location.pathname;
	let trinhSoan: TrinhSoan | null = null;
	let maGoc = '';
	let dangChay = false;
	let thuNgay: { k: Khoi; chunks: string[] } | null = null;
	let henNhap: number | undefined;
	let loiGanNhat: LoiDaHieu | null = null;
	let dongCuoiIn = '';

	const trangThai = (s: string) => {
		el.trangThai.textContent = s;
	};

	const docNhap = (): Record<string, string> => {
		try {
			const o = JSON.parse(localStorage.getItem(KHOA_NHAP) ?? '{}');
			return o && typeof o === 'object' && !Array.isArray(o) ? o : {};
		} catch {
			return {};
		}
	};
	const luuNhap = (ma: string) => {
		window.clearTimeout(henNhap);
		henNhap = window.setTimeout(() => {
			try {
				const o = docNhap();
				o[slug] = ma;
				localStorage.setItem(KHOA_NHAP, JSON.stringify(o));
			} catch {
				/* trình duyệt chặn: bỏ qua */
			}
		}, 400);
	};

	const tab = (ten: 'code' | 'tro-ly') => {
		panel.querySelectorAll<HTMLButtonElement>('.kc-tab').forEach((b) => {
			const chon = b.dataset.tab === ten;
			b.classList.toggle('dang-chon', chon);
			b.setAttribute('aria-selected', String(chon));
		});
		el.code.hidden = ten !== 'code';
		el.troLy.hidden = ten !== 'tro-ly';
	};

	const veHinh = (ds: string[]) => {
		el.hinh.replaceChildren(
			...ds.map((b64) => {
				const img = document.createElement('img');
				img.src = `data:image/png;base64,${b64}`;
				img.alt = 'Hình do code vẽ ra';
				return img;
			}),
		);
	};

	const ganTroLy = (loi: LoiDaHieu) => {
		loiGanNhat = loi;
		if (!el.tlNoi.textContent?.trim()) {
			el.tlNoi.innerHTML = '';
			const p = document.createElement('p');
			p.textContent = `Lỗi gần nhất là ${loi.loai}${loi.dong ? ` ở dòng ${loi.dong}` : ''}. ${loi.giaiThich}`;
			el.tlNoi.append(p);
		}
	};

	const chay = async (chunks?: string[], soHien?: number, laThuNgay = false) => {
		if (!trinhSoan || dangChay) return;
		const ds = chunks ?? [trinhSoan.lay()];
		const hien = soHien ?? ds.length - 1;
		dangChay = true;
		el.chay.hidden = true;
		el.dung.hidden = false;
		el.out.textContent = '';
		el.hinh.replaceChildren();
		el.kqTen.textContent = 'Đang chạy...';
		el.kqNhan.textContent = '';
		el.kqNhan.className = 'kc-kq-nhan';
		trinhSoan.danhDauLoi(null);
		loiGanNhat = null;
		trangThai(may.sanSang ? 'Đang chạy...' : 'Đang tải Python (lần đầu hơi lâu)...');
		let daIn = '';
		let loi = '';
		const baoLau = window.setTimeout(() => {
			if (dangChay) trangThai('Chạy lâu hơn 30 giây. Bấm Dừng nếu không muốn chờ.');
		}, 30000);
		try {
			await may.nap();
			await may.chay(ds, (m) => {
				if (typeof m.i === 'number' && m.i !== hien) return;
				if (m.loai === 'stdout' || m.loai === 'stderr') {
					daIn += m.s ?? '';
					el.out.textContent = daIn;
					dongCuoiIn = daIn;
				} else if (m.loai === 'hinh' && m.hinh) {
					veHinh(m.hinh);
				} else if (m.loai === 'loi') {
					loi = m.message ?? '';
				}
			});
		} catch (e) {
			loi = e instanceof Error ? e.message : String(e);
		}
		window.clearTimeout(baoLau);
		dangChay = false;
		if (!daCaiJedi && may.sanSang) {
			daCaiJedi = true;
			may.caiJedi().catch(() => {});
		}
		el.chay.hidden = false;
		el.dung.hidden = true;
		if (loi) {
			const g = giaiThichLoi(loi);
			if (g.dong != null) trinhSoan.danhDauLoi(g.dong);
			el.out.textContent = daIn ? `${daIn}\n\n${loi}` : loi;
			el.kqTen.textContent = `Lỗi ${g.loai}`;
			el.kqNhan.textContent = g.dong ? `dòng ${g.dong}` : '';
			el.kqNhan.className = 'kc-kq-nhan kc-loi';
			trangThai(`Lỗi ${g.loai}`);
			ganTroLy(g);
		} else {
			el.kqTen.textContent = 'Xong';
			el.kqNhan.textContent = '';
			el.kqNhan.className = 'kc-kq-nhan';
			trangThai('Xong');
			if (laThuNgay && thuNgay) soSanh(thuNgay.k, daIn);
		}
	};

	const soSanh = (k: Khoi, ra: string) => {
		if (k.output == null) {
			el.kqNhan.textContent = 'Không có Output để so';
			return;
		}
		const kq = soOutput(ra, k.output);
		if (kq.khop) {
			el.kqNhan.textContent = '✔ Khớp Output';
			el.kqNhan.className = 'kc-kq-nhan kc-khop';
			k.nut?.classList.add('kc-dat');
		} else {
			el.kqNhan.textContent = `Khác Output (${kq.lech.length} dòng)`;
			el.kqNhan.className = 'kc-kq-nhan kc-khac';
			el.out.textContent = `${ra}\n\n--- Output của bài ---\n${k.output}`;
		}
	};

	let daCaiJedi = false;
	const baoDamPython = () => {
		if (may.sanSang) return;
		trangThai('Đang tải Python (lần đầu hơi lâu)...');
		may
			.nap()
			.then(() => trangThai('Sẵn sàng'))
			.catch(() => trangThai('Không tải được Python, kiểm tra mạng rồi thử lại'));
	};

	const mo = async (ma?: string) => {
		panel.hidden = false;
		nutMo.setAttribute('aria-expanded', 'true');
		if (!trinhSoan) {
			trangThai('Đang tải trình soạn...');
			const { taoTrinhSoan } = await import('./editor');
			const nhap = docNhap();
			const banDau = ma ?? nhap[slug] ?? MA_MAU;
			maGoc = ma ?? (nhap[slug] ? '' : MA_MAU);
			trinhSoan = await taoTrinhSoan(
				el.editor,
				banDau,
				(code, line, col) => may.goiY(code, line, col),
				(s) => luuNhap(s),
				() => void chay(),
			);
			trangThai('Sẵn sàng');
		} else if (ma !== undefined) {
			trinhSoan.dat(ma);
			maGoc = ma;
		}
		tab('code');
		baoDamPython();
		trinhSoan?.view.focus();
	};

	const dong = () => {
		panel.hidden = true;
		nutMo.setAttribute('aria-expanded', 'false');
		nutMo.focus({ preventScroll: true });
	};

	nutMo.addEventListener('click', () => {
		if (panel.hidden) void mo();
		else dong();
	});
	el.dong.addEventListener('click', dong);
	el.chay.addEventListener('click', () => void chay());
	el.dung.addEventListener('click', () => {
		may.huy();
		dangChay = false;
		el.chay.hidden = false;
		el.dung.hidden = true;
		trangThai('Đã dừng');
	});
	el.undo.addEventListener('click', () => trinhSoan?.undo());
	el.redo.addEventListener('click', () => trinhSoan?.redo());
	el.khoiPhuc.addEventListener('click', () => {
		if (!trinhSoan) return;
		trinhSoan.dat(maGoc || MA_MAU);
		luuNhap(maGoc || MA_MAU);
		trangThai('Đã khôi phục code gốc');
	});
	panel.querySelectorAll<HTMLButtonElement>('.kc-tab').forEach((b) => {
		b.addEventListener('click', () => tab(b.dataset.tab === 'tro-ly' ? 'tro-ly' : 'code'));
	});
	document.addEventListener('keydown', (e) => {
		if (e.key === 'Escape' && !panel.hidden && !document.querySelector('dialog[open]')) dong();
	});

	// Kéo góc trên trái để đổi kích thước trên máy tính.
	el.keo.addEventListener('pointerdown', (e) => {
		if (e.button !== 0) return;
		const r = panel.getBoundingClientRect();
		const { clientX: x0, clientY: y0 } = e;
		panel.setPointerCapture(e.pointerId);
		const move = (ev: PointerEvent) => {
			const w = Math.max(360, Math.min(window.innerWidth - 24, r.width - (ev.clientX - x0)));
			const h = Math.max(300, Math.min(window.innerHeight - 24, r.height - (ev.clientY - y0)));
			panel.style.width = `${w}px`;
			panel.style.height = `${h}px`;
		};
		const up = () => {
			window.removeEventListener('pointermove', move);
			window.removeEventListener('pointerup', up);
		};
		window.addEventListener('pointermove', move);
		window.addEventListener('pointerup', up);
	});

	// Gắn nút vào từng khối code của bài.
	const figures = [...document.querySelectorAll<HTMLElement>('main .expressive-code figure')];
	const khoi: Khoi[] = [];
	for (const figure of figures) {
		const pre = figure.querySelector<HTMLPreElement>('pre[data-language="python"]');
		if (!pre) continue;
		const tieuDe = figure.querySelector('.title')?.textContent?.trim() ?? '';
		const ma = tachDong(pre);
		khoi.push({
			figure,
			pre,
			ma,
			output: timOutput(figure),
			tieuDe,
			canColab: canColab(ma),
			laPip: /^\s*!/.test(ma),
		});
	}

	const ganNut = (k: Khoi) => {
		if (k.figure.dataset.kcGan) return;
		k.figure.dataset.kcGan = '1';
		const nut = document.createElement('button');
		nut.type = 'button';
		nut.className = 'kc-thu-ngay';
		if (k.tieuDe === 'Đề bài') {
			nut.textContent = 'Mở trong khung code';
			nut.classList.add('kc-mo-code');
			nut.addEventListener('click', () => void mo(k.ma));
		} else if (k.canColab) {
			nut.textContent = 'Cần Colab';
			nut.classList.add('kc-can-colab');
			nut.disabled = true;
			nut.title = 'Khối này cần PyTorch/Transformers; khung code trên web không chạy được, mở notebook trong Colab.';
		} else if (k.laPip) {
			return;
		} else {
			nut.textContent = '▶ Thử ngay';
			nut.addEventListener('click', () => void moVaThu(k));
		}
		const hang = document.createElement('div');
		hang.className = 'kc-hang-nut';
		hang.appendChild(nut);
		const vo = k.figure.closest('.expressive-code') ?? k.figure;
		vo.before(hang);
		k.nut = nut;
	};
	khoi.forEach(ganNut);

	const moVaThu = async (k: Khoi) => {
		const viTri = khoi.indexOf(k);
		const truoc = khoi.slice(0, viTri);
		const chunks = [...truoc.filter((x) => !x.canColab && !x.laPip && x.tieuDe !== 'Đề bài').map((x) => x.ma), k.ma];
		thuNgay = { k, chunks };
		await mo(k.ma);
		tab('code');
		await chay(chunks, chunks.length - 1, true);
	};

	// Trợ lý: bản cục bộ (chưa gọi máy chủ AI). GĐ sau sẽ thay bằng lời gọi máy chủ.
	const tomTat = () => {
		const dau = [...document.querySelectorAll<HTMLElement>('main .sl-markdown-content h2')]
			.map((h) => h.textContent?.trim())
			.filter(Boolean)
			.slice(0, 8);
		return dau.length ? `Trang này có các mục: ${dau.join(' · ')}.` : 'Trang này chưa có tiêu đề mục nào.';
	};
	const hoiNguoc = () => {
		const dau = [...document.querySelectorAll<HTMLElement>('main .sl-markdown-content h2')]
			.map((h) => h.textContent?.trim())
			.filter(Boolean)
			.slice(0, 3);
		if (!dau.length) return 'Thử tự hỏi: khái niệm chính của trang này là gì, nó dùng khi nào, và nó hỏng ra sao?';
		return `Thử trả lời: ${dau.map((t, i) => `(${i + 1}) ${t} là gì và cho một ví dụ?`).join(' ')}`;
	};
	const traLoi = (viec: string) => {
		if (viec === 'loi') {
			if (!loiGanNhat) return 'Chưa có lỗi nào. Chạy một khối code rồi quay lại đây.';
			return `Lỗi ${loiGanNhat.loai}${loiGanNhat.dong ? ` ở dòng ${loiGanNhat.dong}` : ''}: ${loiGanNhat.giaiThich}`;
		}
		if (viec === 'bai') return 'Mở phần Bài tập cuối trang, chọn một bài, rồi bấm "Mở trong khung code" để thử. Trợ lý không đưa đáp án, chỉ gợi ý hướng nghĩ.';
		if (viec === 'tom-tat') return tomTat();
		if (viec === 'hoi-nguoc') return hoiNguoc();
		return '';
	};
	panel.querySelectorAll<HTMLButtonElement>('.kc-tl-nhanh').forEach((b) => {
		b.addEventListener('click', () => {
			el.tlNoi.textContent = traLoi(b.dataset.viec ?? '');
		});
	});
	el.tlForm.addEventListener('submit', (e) => {
		e.preventDefault();
		const cau = el.tlCau.value.trim();
		if (!cau) return;
		el.tlNoi.textContent = `Câu hỏi: ${cau}\n\nTrợ lý AI sẽ trả lời khi máy chủ AI được bật. Trong lúc đó, thử đọc lại mục liên quan và chạy một khối code nhỏ.`;
	});
}
