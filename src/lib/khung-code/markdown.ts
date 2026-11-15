/** Dựng Markdown nhỏ cho câu trả lời trợ lý: mã code, đậm/nghiêng, liên kết, danh sách, KaTeX. */

function thoat(s: string): string {
	return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

/**
 * Trả về HTML an toàn: mọi chữ do mô hình sinh ra đều được thoát trước,
 * chỉ các thẻ do hàm này tạo mới được đưa vào.
 */
export async function thanhHtml(md: string): Promise<string> {
	const khoi: string[] = [];
	const noiTuyen: string[] = [];
	const toan: string[] = [];

	let s = md.replace(/```(\w*)\n([\s\S]*?)```/g, (_m, _lang, code: string) => {
		khoi.push(code);
		return `\u0000K${khoi.length - 1}\u0000`;
	});
	s = s.replace(/`([^`\n]+)`/g, (_m, code: string) => {
		noiTuyen.push(code);
		return `\u0000C${noiTuyen.length - 1}\u0000`;
	});
	s = s.replace(/\$\$([\s\S]+?)\$\$/g, (_m, tex: string) => {
		toan.push(tex);
		return `\u0000T${toan.length - 1}\u0000`;
	});
	s = s.replace(/\$([^$\n]+?)\$/g, (_m, tex: string) => {
		toan.push(tex);
		return `\u0000T${toan.length - 1}\u0000`;
	});

	s = thoat(s);
	s = s.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
	s = s.replace(/(^|[^*])\*([^*\n]+)\*/g, '$1<em>$2</em>');
	s = s.replace(/\[([^\]]+)\]\((https?:\/\/[^)\s]+|\/[^)\s]*)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');

	const ra: string[] = [];
	let ds: 'ul' | 'ol' | null = null;
	for (const dong of s.split('\n')) {
		const t = dong.trimEnd();
		const ul = /^\s*[-*]\s+(.*)$/.exec(t);
		const ol = /^\s*\d+\.\s+(.*)$/.exec(t);
		if (ul || ol) {
			const loai = ul ? 'ul' : 'ol';
			if (ds !== loai) {
				if (ds) ra.push(`</${ds}>`);
				ra.push(`<${loai}>`);
				ds = loai;
			}
			ra.push(`<li>${(ul?.[1] ?? ol?.[1]) ?? ''}</li>`);
			continue;
		}
		if (ds) {
			ra.push(`</${ds}>`);
			ds = null;
		}
		if (!t.trim()) continue;
		const h = /^(#{1,4})\s+(.*)$/.exec(t);
		if (h) {
			const n = Math.min(h[1].length + 2, 6);
			ra.push(`<h${n}>${h[2]}</h${n}>`);
		} else {
			ra.push(`<p>${t}</p>`);
		}
	}
	if (ds) ra.push(`</${ds}>`);
	let html = ra.join('\n');

	html = html.replace(/\u0000C(\d+)\u0000/g, (_m, i: string) => `<code>${thoat(noiTuyen[Number(i)])}</code>`);
	html = html.replace(
		/\u0000K(\d+)\u0000/g,
		(_m, i: string) =>
			`<div class="kc-md-khoi"><pre><code>${thoat(khoi[Number(i)])}</code></pre><button type="button" class="kc-md-dua">Đưa vào khung code</button></div>`,
	);

	if (toan.length) {
		try {
			const katex = (await import('katex')).default;
			html = html.replace(/\u0000T(\d+)\u0000/g, (_m, i: string) => {
				try {
					return katex.renderToString(toan[Number(i)], { throwOnError: false, displayMode: false });
				} catch {
					return `<code>${thoat(toan[Number(i)])}</code>`;
				}
			});
		} catch {
			html = html.replace(/\u0000T(\d+)\u0000/g, (_m, i: string) => `<code>${thoat(toan[Number(i)])}</code>`);
		}
	}

	return html;
}
