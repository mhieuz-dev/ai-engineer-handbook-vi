// Vẽ hai bìa sách kiểu vẽ tay bằng Rough.js, ghi ra SVG tĩnh trong public/hinh/bia/.
// Chạy lúc soạn: `node scripts/bia/ve-bia.mjs`. Hạt ngẫu nhiên cố định nên chạy lại cho đúng file cũ.
// Chữ được chuyển thành path bằng opentype.js (đọc font @fontsource), nên SVG không cần tải font nào.
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { gzipSync } from 'node:zlib';
import { createRequire } from 'node:module';
import opentype from 'opentype.js';
import sharp from 'sharp';

const require = createRequire(import.meta.url);
const rough = require('roughjs');

const NM = 'node_modules/@fontsource';
const taiFont = (tep) => opentype.parse(readFileSync(`${NM}/${tep}`).buffer);
const boFont = (goi, ten, kieu) => ['latin', 'latin-ext', 'vietnamese'].map((s) => taiFont(`${goi}/files/${ten}-${s}-${kieu}.woff`));
const FONT_DAM = boFont('be-vietnam-pro', 'be-vietnam-pro', '800-normal');
const FONT_VUA = boFont('be-vietnam-pro', 'be-vietnam-pro', '600-normal');
const FONT_TAY = boFont('patrick-hand', 'patrick-hand', '400-normal');

const W = 600;
const H = 900;

/* ---------- Tiện ích chung ---------- */

/** Làm tròn số trong path data còn 1 chữ số thập phân: file nhỏ đi nhiều, mắt không thấy khác. */
const gon = (d) =>
	d
		.replace(/-?\d*\.\d+(e-?\d+)?/g, (n) => {
			const r = Math.round(Number(n) * 10) / 10;
			return Object.is(r, -0) ? '0' : String(r);
		})
		.replace(/\s+/g, ' ')
		.replace(/ ?([MLCQZmlcqz]) ?/g, '$1')
		.replace(/ -/g, '-')
		.trim();

const so = (n) => String(Math.round(n * 10) / 10);

/** Ngẫu nhiên có hạt giống (LCG), dùng cho mọi thứ ngoài Rough.js. */
function ngauNhien(hat) {
	let s = hat >>> 0;
	return () => (s = (s * 1664525 + 1013904223) >>> 0) / 4294967296;
}

/** Đường cong mượt qua các điểm (Catmull-Rom → Bézier bậc ba). */
function muot(diem, kin = false) {
	const p = diem;
	const n = p.length;
	const lay = (i) => (kin ? p[(i + n) % n] : p[Math.max(0, Math.min(n - 1, i))]);
	let d = `M${so(p[0][0])} ${so(p[0][1])}`;
	const het = kin ? n : n - 1;
	for (let i = 0; i < het; i++) {
		const [p0, p1, p2, p3] = [lay(i - 1), lay(i), lay(i + 1), lay(i + 2)];
		const c1 = [p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6];
		const c2 = [p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6];
		d += `C${so(c1[0])} ${so(c1[1])} ${so(c2[0])} ${so(c2[1])} ${so(p2[0])} ${so(p2[1])}`;
	}
	return kin ? d + 'Z' : d;
}

/** Vùng kín từ hai đường cong mượt nối nhau bằng đoạn thẳng (không bị cong lố ở chỗ nối như `muot(..., true)`). */
const noi = (a, b) => `${muot(a)}L${muot(b).slice(1)}Z`;

/** Bộ vẽ một bìa: gom các nét Rough.js thành chuỗi SVG, mỗi hình một hạt giống riêng, cố định. */
class Bia {
	constructor(hat) {
		this.g = rough.generator();
		this.hat = hat;
		this.dem = 0;
		this.phan = [];
	}
	tho(s) {
		this.phan.push(s);
	}
	/** Một hình Rough.js; `bao` là thuộc tính thêm cho nhóm (opacity, filter...). */
	ve(loai, args, tuyChon = {}, bao = '') {
		const opts = { roughness: 1.4, bowing: 1, strokeWidth: 2, seed: this.hat + ++this.dem, ...tuyChon };
		const hinh = this.g[loai](...args, opts);
		let s = '';
		for (const p of this.g.toPaths(hinh)) {
			const net = p.stroke && p.stroke !== 'none' ? ` stroke="${p.stroke}" stroke-width="${so(p.strokeWidth)}"` : '';
			s += `<path${p.fill && p.fill !== 'none' ? ` fill="${p.fill}"` : ''}${net} d="${gon(p.d)}"/>`;
		}
		this.tho(bao ? `<g ${bao}>${s}</g>` : s);
	}
	/** Gói các nét vẽ trong `ham` vào một nhóm `<g ...>`. */
	nhom(bao, ham) {
		this.tho(`<g ${bao}>`);
		ham();
		this.tho('</g>');
	}
	svg(nen) {
		let than = this.phan.join('');
		// Gộp các nét liền nhau cùng màu, cùng độ dày (chỉ nét, không tô) thành một path: file nhỏ đi đáng kể.
		const gop = /<path( stroke="[^"]+" stroke-width="[^"]+") d="([^"]*)"\/><path\1 d="([^"]*)"\/>/g;
		for (let truoc = ''; truoc !== than; ) (truoc = than), (than = than.replace(gop, '<path$1 d="$2$3"/>'));
		return (
			`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${H}" width="${W}" height="${H}">` +
			`<defs>${nen}</defs>` +
			`<g fill="none" stroke-linecap="round" stroke-linejoin="round">${than}</g></svg>`
		);
	}
}

/** Tự ghi path data từ lệnh của opentype.js: `toPathData()` của bản 2.0 đôi khi in ra `NaN` (vd `QNaN 850.1`). */
function lenhPath(lenh) {
	return lenh
		.map((c) =>
			c.type === 'Z'
				? 'Z'
				: c.type + (c.type === 'C' ? [c.x1, c.y1, c.x2, c.y2, c.x, c.y] : c.type === 'Q' ? [c.x1, c.y1, c.x, c.y] : [c.x, c.y]).map(so).join(' '),
		)
		.join('');
}

/** Chuỗi chữ → path data. Mỗi ký tự lấy từ subset font đầu tiên có glyph đó (latin, latin-ext, vietnamese). */
function chu(text, x, y, co, fonts, gian = 0, canh = 'trai') {
	const kyTu = [...text.normalize('NFC')];
	const chon = kyTu.map((k) => {
		const f = fonts.find((f) => f.charToGlyphIndex(k) > 0) ?? fonts[0];
		return { f, g: f.charToGlyph(k) };
	});
	const doRong = () => {
		let w = 0;
		chon.forEach(({ f, g }, i) => {
			w += (g.advanceWidth * co) / f.unitsPerEm + (i < chon.length - 1 ? gian : 0);
			const sau = chon[i + 1];
			if (sau && sau.f === f) w += (f.getKerningValue(g, sau.g) * co) / f.unitsPerEm;
		});
		return w;
	};
	const rong = doRong();
	let cx = canh === 'giua' ? x - rong / 2 : canh === 'phai' ? x - rong : x;
	let d = '';
	chon.forEach(({ f, g }, i) => {
		d += lenhPath(g.getPath(cx, y, co).commands);
		cx += (g.advanceWidth * co) / f.unitsPerEm + gian;
		const sau = chon[i + 1];
		if (sau && sau.f === f) cx += (f.getKerningValue(g, sau.g) * co) / f.unitsPerEm;
	});
	return { d: gon(d), rong };
}

/** Rãnh bản lề gần gáy, như bìa cứng thật. */
const banLe = (toi, sang) =>
	`<path d="M0 0H22V${H}H0Z" fill="${toi}" opacity=".18"/><path d="M30 0V${H}" stroke="${toi}" stroke-width="3" opacity=".35"/><path d="M33.5 0V${H}" stroke="${sang}" stroke-width="1.5" opacity=".35"/>`;

/* ---------- Đầu nhìn nghiêng (dùng chung cho hai bìa, hướng sang phải ở toạ độ gốc) ---------- */

// Toạ độ gốc: đỉnh đầu y = 0, cằm y ≈ 240, gáy x ≈ 12, chóp mũi x ≈ 224.
const MAT_NGHIENG = [
	[105, 0], [150, 8], [183, 32], [199, 64], [204, 96], [200, 112], [205, 128], [216, 150], [224, 164],
	[214, 172], [206, 175], [210, 187], [203, 194], [208, 202], [202, 212], [205, 226], [195, 239],
	[170, 244], [142, 236], [118, 216], [92, 210], [62, 206], [34, 182], [16, 142], [12, 96], [26, 48], [60, 13],
];

function bienDoi(diem, { x, y, ti, lat = false }) {
	return diem.map(([a, b]) => [x + (lat ? -a : a) * ti, y + b * ti]);
}

/* ---------- Bìa AI Engineer ---------- */

function biaAi() {
	const b = new Bia(2610);
	const rnd = ngauNhien(2610);
	const nen =
		'<linearGradient id="n" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0E1A2B"/><stop offset="1" stop-color="#0E2233"/></linearGradient>' +
		'<radialGradient id="q" cx="0.66" cy="0.36" r="0.42"><stop offset="0" stop-color="#2F7FD8" stop-opacity=".55"/><stop offset=".55" stop-color="#1D5BA6" stop-opacity=".14"/><stop offset="1" stop-color="#0E2233" stop-opacity="0"/></radialGradient>' +
		'<filter id="s" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="2.4" result="m"/><feMerge><feMergeNode in="m"/><feMergeNode in="SourceGraphic"/></feMerge></filter>' +
		'<linearGradient id="f" x1="0" y1="0" x2="0" y2="900" gradientUnits="userSpaceOnUse"><stop offset=".56" stop-color="#fff"/><stop offset=".655" stop-color="#000"/></linearGradient>' +
		`<mask id="m" maskUnits="userSpaceOnUse" x="0" y="0" width="${W}" height="${H}"><rect width="${W}" height="${H}" fill="url(#f)"/></mask>`;
	b.tho(`<rect width="${W}" height="${H}" fill="url(#n)"/><rect width="${W}" height="${H}" fill="url(#q)"/>`);

	// Bụi sao li ti.
	let sao = '';
	for (let i = 0; i < 46; i++) sao += `<circle cx="${so(40 + rnd() * 540)}" cy="${so(20 + rnd() * 560)}" r="${so(0.6 + rnd() * 1.1)}"/>`;
	b.tho(`<g fill="#9ED0FF" opacity=".35">${sao}</g>`);

	// Quả cầu mạng nơ-ron.
	const C = { x: 392, y: 318, R: 172 };
	const N = 78;
	const nut = [];
	const [ax, ay] = [0.42, 0.5];
	for (let i = 0; i < N; i++) {
		const yy = 1 - (2 * (i + 0.5)) / N;
		const r = Math.sqrt(1 - yy * yy);
		const th = i * 2.399963 + (rnd() - 0.5) * 0.25;
		let [x, y, z] = [Math.cos(th) * r, yy, Math.sin(th) * r];
		[y, z] = [y * Math.cos(ax) - z * Math.sin(ax), y * Math.sin(ax) + z * Math.cos(ax)];
		[x, z] = [x * Math.cos(ay) + z * Math.sin(ay), -x * Math.sin(ay) + z * Math.cos(ay)];
		nut.push({ x, y, z, X: C.x + C.R * x, Y: C.y - C.R * y });
	}
	const canh = new Set();
	nut.forEach((a, i) => {
		const gan = nut
			.map((c, j) => [j, (a.x - c.x) ** 2 + (a.y - c.y) ** 2 + (a.z - c.z) ** 2])
			.filter(([j]) => j !== i)
			.sort((p, q) => p[1] - q[1])
			.slice(0, 3);
		for (const [j] of gan) canh.add(i < j ? `${i}-${j}` : `${j}-${i}`);
	});
	// Vòng cầu và kinh tuyến mờ.
	b.ve('circle', [C.x, C.y, C.R * 2], { stroke: '#4FA8FF', strokeWidth: 1.6, roughness: 1.2 }, 'opacity=".55"');
	for (const k of [0.36, 0.72]) b.ve('ellipse', [C.x, C.y, C.R * 2 * k, C.R * 2], { stroke: '#4FA8FF', strokeWidth: 1, roughness: 1.1 }, 'opacity=".22"');
	b.ve('ellipse', [C.x, C.y, C.R * 2, C.R * 0.7], { stroke: '#4FA8FF', strokeWidth: 1, roughness: 1.1 }, 'opacity=".22"');
	const sau = [];
	const truoc = [];
	for (const k of canh) {
		const [i, j] = k.split('-').map(Number);
		((nut[i].z + nut[j].z) / 2 > 0 ? truoc : sau).push([nut[i], nut[j]]);
	}
	let s = '';
	for (const [p, q] of sau) s += `M${so(p.X)} ${so(p.Y)}L${so(q.X)} ${so(q.Y)}`;
	b.tho(`<path d="${s}" stroke="#4FA8FF" stroke-width=".8" fill="none" opacity=".3"/>`);
	let nho = '';
	for (const n of nut) if (n.z <= 0) nho += `<circle cx="${so(n.X)}" cy="${so(n.Y)}" r="${so(1.6 + n.z)}"/>`;
	b.tho(`<g fill="#9ED0FF" opacity=".45">${nho}</g>`);
	b.nhom('filter="url(#s)"', () => {
		b.nhom('opacity=".85"', () => {
			for (const [p, q] of truoc) b.ve('line', [p.X, p.Y, q.X, q.Y], { stroke: '#4FA8FF', strokeWidth: 1.2, roughness: 0.9 });
		});
		// Nút phía trước: chấm tròn sáng; nút gần nhất có thêm vòng bút chì.
		let lon = '';
		for (const n of nut) if (n.z > 0) lon += `<circle cx="${so(n.X)}" cy="${so(n.Y)}" r="${so(2.6 + n.z * 3.4)}"/>`;
		b.tho(`<g fill="#9ED0FF" stroke="#E4F2FF" stroke-width="1">${lon}</g>`);
		for (const n of nut) if (n.z > 0.7) b.ve('circle', [n.X, n.Y, 14 + n.z * 6], { stroke: '#9ED0FF', strokeWidth: 0.9, roughness: 0.9, disableMultiStroke: true });
	});

	// Người máy nhìn nghiêng, hướng về quả cầu: đầu, cổ, vai mờ dần xuống phía tiêu đề.
	const T = { x: 44, y: 176, ti: 1.24 };
	const P = (x, y) => bienDoi([[x, y]], T)[0];
	const L = (ds) => bienDoi(ds, T);
	const NEN = '#10243A';
	const vienSang = { stroke: '#EEF5FC', strokeWidth: 2.3, roughness: 1.25 };
	const net = { stroke: '#DCE8F4', strokeWidth: 1.4, roughness: 1.1 };
	const gach = { stroke: 'none', fill: '#9ED0FF', fillStyle: 'hachure', hachureGap: 6.5, hachureAngle: -48, fillWeight: 0.8, roughness: 1.2 };
	b.nhom('mask="url(#m)"', () => {
		const co = L([[88, 200], [150, 232], [150, 300], [90, 300]]);
		b.tho(`<path d="M${co.map((p) => p.map(so).join(' ')).join('L')}Z" fill="${NEN}"/>`);
		b.ve('polygon', [co], { ...net, fill: '#9ED0FF', fillStyle: 'hachure', hachureGap: 6, hachureAngle: -50, fillWeight: 0.7 });
		for (const yy of [244, 266]) b.ve('path', [muot(L([[88, yy], [120, yy + 8], [150, yy + 4]]))], net);
		const lung = [[90, 268], [56, 288], [12, 304], [-20, 330], [-34, 390]];
		const nguc = [[250, 390], [236, 342], [204, 314], [166, 300], [150, 280]];
		b.tho(`<path d="${noi(L(lung), L(nguc))}" fill="${NEN}"/>`);
		b.ve('path', [muot(L([[90, 268], [56, 288], [12, 304], [-20, 330], [-34, 390], [60, 390], [70, 330], [40, 296]]), true)], gach, 'opacity=".3"');
		b.ve('path', [muot(L(lung))], vienSang);
		b.ve('path', [muot(L(nguc))], vienSang);
		// Vòng cổ áo và nắp vai.
		b.ve('path', [muot(L([[90, 270], [118, 290], [152, 282]]))], net);
		b.ve('path', [muot(L([[30, 300], [84, 306], [116, 334], [124, 390]]))], net);
		b.ve('path', [muot(L([[166, 304], [178, 340], [182, 390]]))], net);
	});
	// Đầu: che phần quả cầu phía sau rồi vẽ viền.
	const vien = muot(L(MAT_NGHIENG), true);
	b.tho(`<path d="${vien}" fill="${NEN}"/>`);
	// Bóng khối: gạch chéo nhạt ở nửa sau hộp sọ.
	b.ve('path', [muot(L([[105, 0], [118, 50], [108, 110], [96, 160], [92, 210], [62, 206], [34, 182], [16, 142], [12, 96], [26, 48], [60, 13]]), true)], gach, 'opacity=".2"');
	// Mặt hắt ánh xanh từ quả cầu.
	const mat = [[172, 24], [150, 70], [140, 112], [138, 160], [146, 205], [162, 241], ...MAT_NGHIENG.slice(2, 17).reverse()];
	b.ve('path', [muot(L(mat), true)], { ...gach, fill: '#4FA8FF', hachureAngle: 62, hachureGap: 5.5 }, 'opacity=".42"');
	b.ve('path', [vien], vienSang);
	// Đường nối các mảnh vỏ.
	b.ve('path', [muot(L([[172, 24], [150, 70], [140, 112], [138, 160], [146, 205], [162, 241]]))], net);
	b.ve('path', [muot(L([[118, 3], [110, 52], [100, 106]]))], net);
	b.ve('path', [muot(L([[92, 170], [114, 200], [140, 236]]))], net);
	b.ve('path', [muot(L([[203, 194], [190, 196]]))], { ...net, strokeWidth: 1.2 });
	// Tai: đĩa tròn hai lớp.
	b.ve('circle', [...P(96, 136), 56 * T.ti], { ...vienSang, strokeWidth: 2, fill: NEN, fillStyle: 'solid', roughness: 1 });
	b.ve('circle', [...P(96, 136), 28 * T.ti], { stroke: '#9ED0FF', strokeWidth: 1.6, roughness: 0.9 });
	// Mắt sáng xanh và vòng tròn ở thái dương, nối ra quả cầu.
	b.nhom('filter="url(#s)"', () => {
		b.ve('path', [muot(L([[180, 113], [191, 109], [199, 114], [190, 118]]), true)], { stroke: '#9ED0FF', strokeWidth: 1.8, fill: '#4FA8FF', fillStyle: 'solid', roughness: 0.5 });
		b.ve('path', [muot(L([[176, 104], [190, 100], [201, 104]]))], { ...net, strokeWidth: 1.2 });
		const tt = P(170, 84);
		b.ve('circle', [...tt, 24], { stroke: '#9ED0FF', strokeWidth: 1.8, roughness: 0.7 });
		b.ve('circle', [...tt, 11], { stroke: '#CFE8FF', strokeWidth: 1, fill: '#4FA8FF', fillStyle: 'solid', roughness: 0.5 });
		// Bốn nút gần nhất phía trước mặt, quanh tầm thái dương.
		const toi = nut
			.filter((n) => n.z > 0 && n.X > 330 && Math.abs(n.Y - tt[1]) < 110)
			.sort((p, q) => p.X - q.X)
			.slice(0, 4);
		b.nhom('opacity=".7"', () => {
			for (const n of toi) b.ve('curve', [[[tt[0] + 12, tt[1]], [(tt[0] + n.X) / 2, (tt[1] + n.Y) / 2 - 18], [n.X, n.Y]]], { stroke: '#9ED0FF', strokeWidth: 1, roughness: 0.6, disableMultiStroke: true });
		});
	});

	// Chữ.
	const nhan = chu('HỌC · HIỂU · LÀM', 50, 74, 15, FONT_VUA, 4.2);
	b.tho(`<path d="${nhan.d}" fill="#9ED0FF"/>`);
	const ai = chu('AI', 42, 732, 142, FONT_DAM, 2);
	b.tho(`<path d="${ai.d}" fill="#FFFFFF"/>`);
	// Con trỏ dòng lệnh màu cam ngay sau chữ AI.
	b.ve('rectangle', [42 + ai.rong + 20, 712, 42, 20], { stroke: '#E07A1F', strokeWidth: 1.5, fill: '#E07A1F', fillStyle: 'solid', roughness: 0.8 });
	const kySu = chu('ENGINEER', 48, 792, 62, FONT_DAM, 3);
	b.tho(`<path d="${kySu.d}" fill="#4FA8FF"/>`);
	const phu = chu('Từ Python đến mô hình ngôn ngữ lớn', 50, 832, 27, FONT_TAY, 0.4);
	b.tho(`<path d="${phu.d}" fill="#DCE8F4"/>`);
	b.ve('line', [50, 852, 552, 852], { stroke: '#4FA8FF', strokeWidth: 1, roughness: 0.6, disableMultiStroke: true }, 'opacity=".45"');
	const nhanh = chu('AI & ROBOTICS', 50, 880, 12, FONT_VUA, 3.4);
	b.tho(`<path d="${nhanh.d}" fill="#9ED0FF" opacity=".8"/>`);
	const tg = chu('Mhz', 552, 882, 25, FONT_TAY, 0.6, 'phai');
	b.tho(`<path d="${tg.d}" fill="#FFFFFF"/>`);
	b.tho(banLe('#000', '#9ED0FF'));
	return b.svg(nen);
}

/* ---------- Bìa Robotics ---------- */

/** Bánh răng: đường viền có răng hình thang quanh tâm (x, y). */
function banhRang(x, y, rNgoai, rTrong, soRang, lech = 0) {
	const diem = [];
	for (let i = 0; i < soRang; i++) {
		const a = lech + (i / soRang) * Math.PI * 2;
		const buoc = (Math.PI * 2) / soRang;
		for (const [t, r] of [[0, rTrong], [0.18, rNgoai], [0.5, rNgoai], [0.68, rTrong]]) {
			const g = a + t * buoc;
			diem.push([x + Math.cos(g) * r, y + Math.sin(g) * r]);
		}
	}
	return `M${diem.map((p) => p.map(so).join(' ')).join('L')}Z`;
}

function biaRobotics() {
	const b = new Bia(2611);
	const nen =
		'<linearGradient id="n" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#E6EAEB"/><stop offset="1" stop-color="#D9DEE0"/></linearGradient>' +
		'<radialGradient id="q" cx="0.62" cy="0.38" r="0.5"><stop offset="0" stop-color="#FFFFFF" stop-opacity=".8"/><stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/></radialGradient>' +
		'<filter id="b" x="-10%" y="-10%" width="120%" height="120%"><feDropShadow dx="3" dy="3" stdDeviation="2.5" flood-color="#7D8A92" flood-opacity=".45"/></filter>' +
		'<filter id="r" x="-10%" y="-10%" width="130%" height="130%"><feDropShadow dx="-8" dy="10" stdDeviation="9" flood-color="#5B6770" flood-opacity=".22"/></filter>';
	b.tho(`<rect width="${W}" height="${H}" fill="url(#n)"/><rect width="${W}" height="${H}" fill="url(#q)"/>`);

	// Tiêu đề dọc ở mép trái, đọc từ dưới lên.
	const td = chu('ROBOTICS', 0, 0, 150, FONT_DAM, 4);
	const x0 = 168;
	const y0 = (H + td.rong) / 2;
	b.tho(`<path d="${td.d}" fill="#FFFFFF" filter="url(#b)" transform="translate(${x0} ${so(y0)}) rotate(-90)"/>`);

	// Người máy nhìn nghiêng sang trái: vai, cổ, đầu; hộp sọ phía sau mở ra lộ bánh răng và dây.
	const T = { x: 548, y: 158, ti: 1.42, lat: true };
	const P = (x, y) => bienDoi([[x, y]], T)[0];
	const L = (ds) => bienDoi(ds, T);
	const vienDam = { stroke: '#46525B', strokeWidth: 2.2, roughness: 1.3 };
	const trang = '#F7F9F9';
	const bong = { stroke: 'none', fill: '#8E9AA2', fillStyle: 'hachure', hachureGap: 6, hachureAngle: 40, fillWeight: 0.9, roughness: 1.3 };

	// Cả người máy đổ một bóng mềm lên nền.
	b.tho('<g filter="url(#r)">');
	// Cổ: trụ kim loại có khớp, dây chạy dọc rồi chui vào thân.
	const co = L([[84, 196], [150, 228], [152, 300], [82, 300]]);
	b.tho(`<path d="M${co.map((p) => p.map(so).join(' ')).join('L')}Z" fill="#C9D0D4"/>`);
	b.ve('polygon', [co], { ...vienDam, fill: '#6F7C85', fillStyle: 'hachure', hachureGap: 5, hachureAngle: -40, fillWeight: 0.8 });
	for (const yy of [246, 272]) b.ve('path', [muot(L([[82, yy], [116, yy + 10], [151, yy + 4]]))], { ...vienDam, strokeWidth: 1.6 });
	b.ve('path', [muot(L([[118, 230], [126, 270], [122, 310]]))], { stroke: '#E07A1F', strokeWidth: 3, roughness: 1 });
	b.ve('path', [muot(L([[100, 226], [94, 270], [100, 310]]))], { stroke: '#2E4A62', strokeWidth: 3, roughness: 1 });
	// Vai và ngực: vỏ trắng bóng, nắp vai tròn, khớp vai.
	const lung = [[86, 262], [52, 286], [10, 306], [-30, 340], [-52, 420], [-62, 530]];
	const nguc = [[262, 530], [250, 440], [232, 370], [200, 322], [166, 304], [150, 282]];
	b.tho(`<path d="${noi(L(lung), L(nguc))}" fill="${trang}"/>`);
	b.ve('path', [muot(L([[86, 262], [52, 286], [10, 306], [-30, 340], [-52, 420], [-62, 530], [110, 530], [134, 460], [140, 400], [120, 334], [70, 302]]), true)], bong, 'opacity=".5"');
	b.ve('path', [muot(L(lung))], vienDam);
	b.ve('path', [muot(L(nguc))], vienDam);
	b.ve('path', [muot(L([[4, 310], [70, 300], [124, 330], [146, 400], [138, 470], [118, 530]]))], { ...vienDam, strokeWidth: 1.8 });
	b.ve('path', [muot(L([[168, 308], [188, 360], [194, 440], [204, 530]]))], { ...vienDam, strokeWidth: 1.5 });
	b.ve('path', [muot(L([[84, 270], [118, 290], [152, 284]]))], { ...vienDam, strokeWidth: 1.8 });
	b.ve('circle', [...P(70, 366), 44 * T.ti], { ...vienDam, strokeWidth: 1.8, fill: '#E3E8EA', fillStyle: 'solid' });
	b.ve('circle', [...P(70, 366), 20 * T.ti], { ...vienDam, strokeWidth: 1.4, fill: '#8E9AA2', fillStyle: 'hachure', hachureGap: 4 });
	// Ánh bóng trên nắp vai.
	b.ve('path', [muot(L([[20, 320], [66, 312], [104, 330]]))], { stroke: '#FFFFFF', strokeWidth: 4, roughness: 0.8 });

	// Đầu.
	const dau = L(MAT_NGHIENG);
	const vien = muot(dau, true);
	b.tho(`<path d="${vien}" fill="${trang}"/>`);
	// Bóng dưới hàm và sau gáy.
	b.ve('path', [muot(L([[96, 166], [130, 200], [168, 240], [142, 236], [118, 216], [92, 210], [62, 206], [40, 186]]), true)], { ...bong }, 'opacity=".55"');
	// Khoang sọ mở: viền cắt chéo từ trán ra sau gáy.
	const khoang = L([[150, 8], [160, 40], [150, 72], [118, 96], [80, 118], [40, 134], [14, 132], [12, 96], [26, 48], [60, 13], [105, 0]]);
	const kVien = muot(khoang, true);
	b.tho(`<path d="${kVien}" fill="#3C4850"/>`);
	b.ve('path', [kVien], { stroke: 'none', fill: '#22292E', fillStyle: 'cross-hatch', hachureGap: 7, fillWeight: 0.7, roughness: 1.4 }, 'opacity=".6"');
	// Bánh răng trong khoang.
	const rang = [
		[...P(56, 72), 34, 27, 12, 0.1, '#D7DDE0'],
		[...P(104, 46), 22, 17, 9, 0.3, '#B9C2C7'],
		[...P(122, 82), 15, 11, 8, 0.0, '#E07A1F'],
		[...P(30, 108), 18, 13, 8, 0.2, '#B9C2C7'],
	];
	for (const [x, y, ro, ri, n, l, mau] of rang) {
		b.ve('path', [banhRang(x, y, ro * T.ti, ri * T.ti, n, l)], { stroke: '#2A3238', strokeWidth: 1.6, fill: mau, fillStyle: 'solid', roughness: 0.7 });
		b.ve('circle', [x, y, ri * T.ti * 0.9], { stroke: '#2A3238', strokeWidth: 1.4, roughness: 0.6 });
		b.ve('circle', [x, y, ri * T.ti * 0.32], { stroke: '#2A3238', strokeWidth: 1.2, fill: '#2A3238', fillStyle: 'solid', roughness: 0.5 });
	}
	// Dây lộ ra từ khoang, chạy xuống gáy.
	const day = [
		['#E07A1F', [[40, 120], [24, 150], [40, 190], [86, 214]]],
		['#2E4A62', [[64, 112], [48, 150], [62, 186], [96, 212]]],
		['#2A3238', [[78, 112], [66, 150], [78, 192], [110, 214]]],
	];
	for (const [mau, ds] of day) b.ve('curve', [L(ds)], { stroke: mau, strokeWidth: 3, roughness: 1 });
	// Vành cắt của vỏ.
	b.ve('path', [muot(L([[150, 8], [160, 40], [150, 72], [118, 96], [80, 118], [40, 134], [14, 132]]))], { ...vienDam, strokeWidth: 3 });
	b.ve('path', [vien], vienDam);
	// Mảnh vỏ mặt, tai, mắt.
	b.ve('path', [muot(L([[160, 40], [156, 90], [148, 150], [152, 205], [164, 241]]))], { ...vienDam, strokeWidth: 1.5 });
	b.ve('path', [muot(L([[96, 170], [118, 200], [142, 236]]))], { ...vienDam, strokeWidth: 1.5 });
	b.ve('circle', [...P(98, 146), 50 * T.ti], { ...vienDam, fill: trang, fillStyle: 'solid' });
	b.ve('circle', [...P(98, 146), 26 * T.ti], { ...vienDam, strokeWidth: 1.5, fill: '#B9C2C7', fillStyle: 'hachure', hachureGap: 4 });
	b.ve('path', [muot(L([[178, 113], [190, 108], [199, 114], [189, 119]]), true)], { stroke: '#2A3238', strokeWidth: 1.8, fill: '#2A3238', fillStyle: 'solid', roughness: 0.6 });
	// Ánh bóng trên trán.
	b.ve('path', [muot(L([[176, 52], [188, 72], [193, 92]]))], { stroke: '#FFFFFF', strokeWidth: 4, roughness: 0.8 });

	b.tho('</g>');

	// Dải chéo "SẮP CÓ" ở góc trên phải.
	b.tho('<g transform="translate(600 0) rotate(45)">');
	b.ve('rectangle', [-170, 100, 340, 46], { stroke: '#B85F12', strokeWidth: 1.6, fill: '#E07A1F', fillStyle: 'solid', roughness: 1 });
	const sc = chu('SẮP CÓ', 0, 132, 24, FONT_DAM, 4, 'giua');
	b.tho(`<path d="${sc.d}" fill="#FFFFFF"/></g>`);

	// Chữ nhỏ.
	const nhan = chu('AI & ROBOTICS', 196, 74, 15, FONT_VUA, 4.2);
	b.tho(`<path d="${nhan.d}" fill="#5B6770"/>`);
	const phu = chu('Nhánh thứ hai, đang được soạn', 196, 104, 25, FONT_TAY, 0.4);
	b.tho(`<path d="${phu.d}" fill="#46525B"/>`);
	const tg = chu('Mhz', 552, 872, 26, FONT_TAY, 0.6, 'phai');
	b.tho(`<path d="${tg.d}" fill="#46525B"/>`);
	b.tho(banLe('#5B6770', '#FFFFFF'));
	return b.svg(nen);
}

/* ---------- Ghi file ---------- */

mkdirSync('public/hinh/bia', { recursive: true });
/** Ảnh nhỏ cho kệ phẳng trên điện thoại (SVG chỉ dành cho cảnh 3D). Bản 2x 720x1080 nặng 33-36 KB (quá 25 KB) nên chỉ làm 1x. */
const WEBP = [['', 360, 540, 62]];
for (const [ten, ve] of [['ai-engineer', biaAi], ['robotics', biaRobotics]]) {
	const svg = ve();
	writeFileSync(`public/hinh/bia/${ten}.svg`, svg);
	console.log(`${ten}.svg: ${svg.length} B, gzip ${gzipSync(svg, { level: 9 }).length} B`);
	for (const [hau, rong, cao, chatLuong] of WEBP) {
		const webp = await sharp(Buffer.from(svg), { density: (72 * rong) / W }).resize(rong, cao).webp({ quality: chatLuong, effort: 6 }).toBuffer();
		writeFileSync(`public/hinh/bia/${ten}${hau}.webp`, webp);
		console.log(`${ten}${hau}.webp: ${rong}x${cao}, ${webp.length} B`);
	}
}
