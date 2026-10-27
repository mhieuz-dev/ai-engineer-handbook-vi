/**
 * Cảnh 3D của kệ sách ở trang chủ. Chỉ được nạp bằng `import()` động từ KeSach.astro (máy tính, có WebGL,
 * không giảm chuyển động, kệ sắp vào màn hình). Vẽ theo yêu cầu: không có vòng lặp chạy nền, chỉ vẽ khi
 * có gì đó đang chuyển động, dừng hẳn khi kệ ra khỏi màn hình.
 */
import {
	BoxGeometry,
	CanvasTexture,
	DirectionalLight,
	Group,
	HemisphereLight,
	Mesh,
	MeshBasicMaterial,
	MeshStandardMaterial,
	NeutralToneMapping,
	PerspectiveCamera,
	PlaneGeometry,
	Raycaster,
	RepeatWrapping,
	Scene,
	SRGBColorSpace,
	Vector2,
	WebGLRenderer,
	type BufferGeometry,
	type Material,
	type Object3D,
	type Texture,
} from 'three';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';
import type { CuonSach } from './du-lieu';

export interface KeSach3D {
	huy(): void;
	/** Rút sách ra, mở bìa và giữ nguyên đó. Trả về false nếu cảnh chưa sẵn sàng. */
	chon(id: CuonSach['id']): boolean;
	/** Đóng bìa và đẩy cuốn đang mở về kệ. */
	dong(): void;
	/** Làm nổi một cuốn (rê chuột hoặc focus vào thẻ chọn); null để bỏ. */
	danhDau(id: CuonSach['id'] | null): void;
}

const FONT = '"Be Vietnam Pro", system-ui, sans-serif';
const GOC_XOAY = (25 * Math.PI) / 180;
const NHO_RA = 0.15;
const RUT_RA = 0.62;
const MO_BIA = -1.95;

// Kích thước (đơn vị cảnh): một ngăn kệ đủ cho hai cuốn.
const KE = { rong: 3.55, cao: 2.3, sau: 1.0, van: 0.1, hong: 0.11, chan: 0.28 };
const SACH = { rong: 1.24, cao: 1.86 }; // đúng tỉ lệ 2:3 của ảnh bìa SVG

/* ---------- Kết cấu vẽ bằng canvas ---------- */

function taoCanvas(w: number, h: number): [HTMLCanvasElement, CanvasRenderingContext2D] {
	const cv = document.createElement('canvas');
	cv.width = w;
	cv.height = h;
	return [cv, cv.getContext('2d')!];
}

/** Ảnh bìa SVG vẽ lại lên canvas 1024x1536: dùng SVG làm texture trực tiếp chỉ có 600x900 điểm ảnh, bị nhòe. */
function taiBia(url: string): Promise<HTMLCanvasElement | null> {
	return new Promise((xong) => {
		const anh = new Image();
		anh.onload = () => {
			const [cv, g] = taoCanvas(1024, 1536);
			g.drawImage(anh, 0, 0, cv.width, cv.height);
			xong(cv);
		};
		anh.onerror = () => xong(null);
		anh.src = url;
	});
}

function kieuSRGB(t: Texture, anisotropy: number): Texture {
	t.colorSpace = SRGBColorSpace;
	t.anisotropy = anisotropy;
	return t;
}

/** Ngẫu nhiên có hạt giống: cùng một kệ ở mọi lần tải. */
function ngauNhien(hat: number) {
	let s = hat >>> 0;
	return () => ((s = (s * 1664525 + 1013904223) >>> 0) / 4294967296);
}

/** Vân gỗ: nền màu gỗ, các thớ dài lượn nhẹ, đậm nhạt xen kẽ. `toi` thêm bóng góc (ván hậu). */
function vanGo(mau: string, hat: number, toi = false): HTMLCanvasElement {
	const [cv, g] = taoCanvas(1024, 512);
	const r = ngauNhien(hat);
	g.fillStyle = mau;
	g.fillRect(0, 0, 1024, 512);
	for (let i = 0; i < 150; i++) {
		const y0 = r() * 512;
		const bien = 2 + r() * 6;
		const pha = r() * Math.PI * 2;
		g.strokeStyle = r() < 0.55 ? `rgba(40,20,8,${0.05 + r() * 0.12})` : `rgba(255,225,180,${0.03 + r() * 0.07})`;
		g.lineWidth = 0.6 + r() * 2.4;
		g.beginPath();
		for (let x = 0; x <= 1024; x += 16) {
			const y = y0 + Math.sin(x / (90 + r() * 4) + pha) * bien;
			if (x === 0) g.moveTo(x, y);
			else g.lineTo(x, y);
		}
		g.stroke();
	}
	if (toi) {
		// Ánh sáng khó lọt vào góc ngăn kệ: tối dần ở mép trên và hai bên.
		const tren = g.createLinearGradient(0, 0, 0, 512);
		tren.addColorStop(0, 'rgba(20,10,4,0.55)');
		tren.addColorStop(0.35, 'rgba(20,10,4,0.08)');
		tren.addColorStop(1, 'rgba(20,10,4,0.18)');
		g.fillStyle = tren;
		g.fillRect(0, 0, 1024, 512);
		for (const [x0, x1] of [[0, 160], [1024, 864]]) {
			const ben = g.createLinearGradient(x0, 0, x1, 0);
			ben.addColorStop(0, 'rgba(20,10,4,0.45)');
			ben.addColorStop(1, 'rgba(20,10,4,0)');
			g.fillStyle = ben;
			g.fillRect(Math.min(x0, x1), 0, 160, 512);
		}
	}
	return cv;
}

/** Bóng mềm hình elip (bóng giả thay cho shadow map). */
function bongMem(): HTMLCanvasElement {
	const [cv, g] = taoCanvas(128, 128);
	const grad = g.createRadialGradient(64, 64, 0, 64, 64, 64);
	grad.addColorStop(0, 'rgba(0,0,0,0.85)');
	grad.addColorStop(0.45, 'rgba(0,0,0,0.45)');
	grad.addColorStop(1, 'rgba(0,0,0,0)');
	g.fillStyle = grad;
	g.fillRect(0, 0, 128, 128);
	return cv;
}

/** Mép giấy: nền kem với các vạch trang mảnh. */
function mepGiay(): HTMLCanvasElement {
	const [cv, g] = taoCanvas(256, 64);
	const r = ngauNhien(7);
	g.fillStyle = '#efe6d2';
	g.fillRect(0, 0, 256, 64);
	for (let x = 0; x < 256; x += 2) {
		g.fillStyle = `rgba(120,95,60,${0.05 + r() * 0.12})`;
		g.fillRect(x, 0, 1, 64);
	}
	return cv;
}

const W = 600;
const H = Math.round((W * SACH.cao) / SACH.rong);

/** Rãnh bản lề gần gáy của bìa cứng. */
function banLe(g: CanvasRenderingContext2D, toi: string, sang: string) {
	g.fillStyle = toi;
	g.fillRect(30, 0, 5, H);
	g.fillStyle = sang;
	g.fillRect(36, 0, 2, H);
}

function chuGian(g: CanvasRenderingContext2D, chu: string, x: number, y: number, gian: number) {
	let cx = x;
	for (const k of chu) {
		g.fillText(k, cx, y);
		cx += g.measureText(k).width + gian;
	}
}

function biaAiEngineer(s: CuonSach): HTMLCanvasElement {
	const [cv, g] = taoCanvas(W, H);
	const nen = g.createLinearGradient(0, 0, W, H);
	nen.addColorStop(0, '#0b1a29');
	nen.addColorStop(1, s.mauBia);
	g.fillStyle = nen;
	g.fillRect(0, 0, W, H);

	// Quả cầu mạng nơ-ron phát sáng.
	const cx = W * 0.6;
	const cy = H * 0.36;
	const R = W * 0.3;
	const hao = g.createRadialGradient(cx, cy, 0, cx, cy, R * 1.6);
	hao.addColorStop(0, 'rgba(70,160,255,0.42)');
	hao.addColorStop(0.5, 'rgba(40,110,210,0.14)');
	hao.addColorStop(1, 'rgba(20,60,140,0)');
	g.fillStyle = hao;
	g.fillRect(0, 0, W, H);

	const r = ngauNhien(2026);
	const diem: { x: number; y: number; z: number }[] = [];
	for (let i = 0; i < 64; i++) {
		// Phân bố đều trên mặt cầu (xoắn Fibonacci) rồi nghiêng nhẹ.
		const y = 1 - (i / 63) * 2;
		const rr = Math.sqrt(1 - y * y);
		const t = i * 2.39996 + r() * 0.15;
		const x = Math.cos(t) * rr;
		const z = Math.sin(t) * rr;
		diem.push({ x: cx + x * R, y: cy + (y * 0.94 + z * 0.12) * R, z });
	}
	g.lineCap = 'round';
	for (let i = 0; i < diem.length; i++) {
		for (let j = i + 1; j < diem.length; j++) {
			const a = diem[i];
			const b = diem[j];
			const d = Math.hypot(a.x - b.x, a.y - b.y);
			if (d > R * 0.42) continue;
			const sau = (a.z + b.z + 2) / 4; // 0 phía sau, 1 phía trước
			g.strokeStyle = `rgba(130,200,255,${0.1 + sau * 0.45})`;
			g.lineWidth = 0.8 + sau * 1.2;
			g.beginPath();
			g.moveTo(a.x, a.y);
			g.lineTo(b.x, b.y);
			g.stroke();
		}
	}
	for (const p of diem) {
		const sau = (p.z + 1) / 2;
		g.shadowColor = 'rgba(120,200,255,0.9)';
		g.shadowBlur = 6 + sau * 10;
		g.fillStyle = `rgba(${200 + sau * 55},${230 + sau * 25},255,${0.35 + sau * 0.65})`;
		g.beginPath();
		g.arc(p.x, p.y, 1.6 + sau * 3, 0, Math.PI * 2);
		g.fill();
	}
	g.shadowBlur = 0;
	// Vành quỹ đạo.
	g.strokeStyle = 'rgba(140,205,255,0.35)';
	g.lineWidth = 1.5;
	g.beginPath();
	g.ellipse(cx, cy, R * 1.28, R * 0.36, -0.32, 0, Math.PI * 2);
	g.stroke();

	banLe(g, 'rgba(0,0,0,0.35)', 'rgba(255,255,255,0.08)');

	const le = 64;
	g.textBaseline = 'alphabetic';
	g.fillStyle = 'rgba(160,210,255,0.75)';
	g.font = `600 19px ${FONT}`;
	chuGian(g, 'AI & ROBOTICS  ·  NHÁNH 1', le, 72, 3);

	g.fillStyle = '#E07A1F';
	g.fillRect(le, H * 0.665, 64, 7);
	g.fillStyle = '#ffffff';
	g.font = `800 150px ${FONT}`;
	g.fillText('AI', le - 6, H * 0.665 + 150);
	g.fillStyle = '#8ec9ff';
	g.font = `800 70px ${FONT}`;
	chuGian(g, 'ENGINEER', le - 2, H * 0.665 + 228, 4);
	g.fillStyle = 'rgba(236,244,252,0.82)';
	g.font = `400 25px ${FONT}`;
	g.fillText(s.phuDe, le, H * 0.665 + 278);
	g.fillStyle = 'rgba(160,210,255,0.6)';
	g.font = `600 18px ${FONT}`;
	chuGian(g, 'MHZ', W - 96, 72, 4);
	return cv;
}

function biaRobotics(s: CuonSach): HTMLCanvasElement {
	const [cv, g] = taoCanvas(W, H);
	const nen = g.createLinearGradient(0, 0, W * 0.4, H);
	nen.addColorStop(0, '#eef0f2');
	nen.addColorStop(1, '#c9ced3');
	g.fillStyle = nen;
	g.fillRect(0, 0, W, H);
	const sang = g.createRadialGradient(W * 0.66, H * 0.42, 0, W * 0.66, H * 0.42, W * 0.6);
	sang.addColorStop(0, 'rgba(255,255,255,0.85)');
	sang.addColorStop(1, 'rgba(255,255,255,0)');
	g.fillStyle = sang;
	g.fillRect(0, 0, W, H);

	// Họa tiết cơ khí: bánh răng và một cánh tay robot cách điệu, trắng bạc.
	const gx = W * 0.66;
	const gy = H * 0.4;
	const banhRang = (x: number, y: number, rr: number, rang: number, nghieng: number) => {
		g.beginPath();
		for (let i = 0; i < rang * 2; i++) {
			const a = nghieng + (i * Math.PI) / rang;
			const rad = i % 2 === 0 ? rr : rr * 0.86;
			const a2 = a + Math.PI / rang;
			g.lineTo(x + Math.cos(a) * rad, y + Math.sin(a) * rad);
			g.lineTo(x + Math.cos(a2) * rad, y + Math.sin(a2) * rad);
		}
		g.closePath();
		g.fill();
		g.stroke();
		g.beginPath();
		g.arc(x, y, rr * 0.32, 0, Math.PI * 2);
		g.stroke();
	};
	g.shadowColor = 'rgba(60,70,80,0.28)';
	g.shadowBlur = 18;
	g.shadowOffsetY = 6;
	g.fillStyle = 'rgba(255,255,255,0.9)';
	g.strokeStyle = 'rgba(150,160,170,0.7)';
	g.lineWidth = 2;
	banhRang(gx, gy, W * 0.2, 14, 0.1);
	banhRang(gx + W * 0.17, gy + W * 0.25, W * 0.1, 9, 0.3);
	// Cánh tay: ba khâu, khớp tròn.
	const khop: [number, number][] = [
		[W * 0.42, H * 0.82],
		[W * 0.5, H * 0.62],
		[W * 0.74, H * 0.6],
		[W * 0.84, H * 0.68],
	];
	g.lineCap = 'round';
	for (let i = 0; i < khop.length - 1; i++) {
		g.strokeStyle = 'rgba(255,255,255,0.95)';
		g.lineWidth = 26 - i * 6;
		g.beginPath();
		g.moveTo(...khop[i]);
		g.lineTo(...khop[i + 1]);
		g.stroke();
	}
	g.shadowBlur = 0;
	g.shadowOffsetY = 0;
	for (const [x, y] of khop) {
		g.fillStyle = '#ffffff';
		g.strokeStyle = 'rgba(120,130,140,0.8)';
		g.lineWidth = 2;
		g.beginPath();
		g.arc(x, y, 13, 0, Math.PI * 2);
		g.fill();
		g.stroke();
	}

	banLe(g, 'rgba(60,70,80,0.18)', 'rgba(255,255,255,0.6)');

	// Tên sách dọc bên trái, đọc từ dưới lên.
	g.save();
	g.translate(176, H - 60);
	g.rotate(-Math.PI / 2);
	g.fillStyle = s.mauChu;
	g.font = `800 132px ${FONT}`;
	g.textBaseline = 'alphabetic';
	chuGian(g, 'ROBOTICS', 0, 0, 6);
	g.restore();

	g.fillStyle = '#4a5560';
	g.font = `600 19px ${FONT}`;
	chuGian(g, 'AI & ROBOTICS  ·  NHÁNH 2', 214, H - 112, 3);
	g.font = `400 24px ${FONT}`;
	g.fillStyle = '#3b4650';
	g.fillText(s.phuDe, 214, H - 66);

	// Dải "SẮP CÓ" chéo góc trên phải.
	g.save();
	g.translate(W - 112, 112);
	g.rotate(Math.PI / 4);
	g.fillStyle = '#E07A1F';
	g.shadowColor = 'rgba(0,0,0,0.25)';
	g.shadowBlur = 10;
	g.fillRect(-190, -26, 380, 52);
	g.shadowBlur = 0;
	g.fillStyle = '#ffffff';
	g.font = `800 24px ${FONT}`;
	g.textAlign = 'center';
	g.textBaseline = 'middle';
	g.fillText('SẮP CÓ', 0, 2);
	g.restore();
	return cv;
}

/** Trang đầu lộ ra khi mở bìa. */
function trangDau(s: CuonSach): HTMLCanvasElement {
	const [cv, g] = taoCanvas(W, H);
	g.fillStyle = '#f4ecdb';
	g.fillRect(0, 0, W, H);
	g.strokeStyle = 'rgba(31,95,139,0.35)';
	g.lineWidth = 2;
	g.strokeRect(46, 46, W - 92, H - 92);
	g.textAlign = 'center';
	g.fillStyle = '#1F5F8B';
	g.font = `800 64px ${FONT}`;
	g.fillText(s.ten.toUpperCase(), W / 2, H * 0.42);
	g.fillStyle = '#E07A1F';
	g.fillRect(W / 2 - 32, H * 0.42 + 30, 64, 5);
	g.fillStyle = '#5b5346';
	g.font = `400 26px ${FONT}`;
	g.fillText(s.phuDe, W / 2, H * 0.42 + 90);
	g.fillStyle = '#1F5F8B';
	g.font = `600 28px ${FONT}`;
	g.fillText('Bắt đầu đọc →', W / 2, H * 0.78);
	return cv;
}

/* ---------- Dựng cảnh ---------- */

interface Cuon {
	s: CuonSach;
	nhom: Group;
	banLeBia: Group;
	z0: number;
	nho: number;
	nhoDich: number;
	mo: number;
	moDich: number;
	lac: number; // thời điểm bắt đầu lắc, 0 nếu không lắc
}

export function dungKe(goc: HTMLElement, sach: CuonSach[], khiChon: (s: CuonSach) => void): KeSach3D {
	let daHuy = false;
	let sanSang = false;
	let renderer: WebGLRenderer | null = null;
	let raf = 0;
	let dangThay = true;
	let soKhung = 0;
	let tLan = 0;
	let dangChon = false;
	const donDep: (() => void)[] = [];

	const scene = new Scene();
	const camera = new PerspectiveCamera(26, 2, 0.1, 50);
	const ke = new Group();
	scene.add(ke);
	const cuon: Cuon[] = [];
	let xoay = 0;
	let xoayDich = 0;
	let rePhai: Cuon | null = null;
	let danhDauNgoai: Cuon | null = null;

	function veMotKhung(t: number) {
		raf = 0;
		if (!renderer || daHuy) return;
		const dt = tLan ? Math.min((t - tLan) / 1000, 0.05) : 1 / 60;
		tLan = t;
		const k = 1 - Math.exp(-dt * 12);
		let conDong = false;
		const tien = (a: number, b: number) => {
			const d = b - a;
			if (Math.abs(d) < 1e-4) return b;
			conDong = true;
			return a + d * k;
		};
		xoay = tien(xoay, xoayDich);
		ke.rotation.y = xoay;
		for (const c of cuon) {
			c.nho = tien(c.nho, c.nhoDich);
			c.mo = tien(c.mo, c.moDich);
			c.nhom.position.z = c.z0 + c.nho;
			c.banLeBia.rotation.y = c.mo;
			if (c.lac) {
				const tt = (t - c.lac) / 1000;
				if (tt < 0.7) {
					c.nhom.rotation.z = Math.sin(tt * 34) * 0.045 * Math.exp(-tt * 5);
					conDong = true;
				} else {
					c.nhom.rotation.z = 0;
					c.lac = 0;
				}
			}
		}
		renderer.render(scene, camera);
		goc.dataset.nho = Math.max(...cuon.map((c) => c.nho)).toFixed(2);
		goc.dataset.frames = String(++soKhung);
		if (conDong) yeuCauVe();
		else tLan = 0;
	}

	function yeuCauVe() {
		if (!raf && dangThay && renderer && !daHuy) raf = requestAnimationFrame(veMotKhung);
	}

	function capNhatNho() {
		let doi = false;
		for (const c of cuon) {
			if (dangChon && c.nhoDich === RUT_RA) continue;
			const dich = c === rePhai || c === danhDauNgoai ? NHO_RA : 0;
			if (dich !== c.nhoDich) (c.nhoDich = dich), (doi = true);
		}
		if (doi) yeuCauVe();
	}

	let dangMo: Cuon | null = null;
	let choId: CuonSach['id'] | null = null;

	function chon(id: CuonSach['id']): boolean {
		if (!sanSang) {
			choId = id; // cảnh chưa dựng xong: rút sách ngay khi sẵn sàng
			return false;
		}
		const c = cuon.find((x) => x.s.id === id);
		if (!c) return false;
		if (dangMo && dangMo !== c) dong();
		dangMo = c;
		dangChon = true;
		c.nhoDich = RUT_RA;
		c.moDich = MO_BIA;
		xoayDich = 0;
		yeuCauVe();
		return true;
	}

	function dong() {
		choId = null;
		const c = dangMo;
		if (!c) return;
		dangMo = null;
		dangChon = false;
		c.moDich = 0;
		c.nhoDich = 0;
		capNhatNho();
		yeuCauVe();
	}

	function danhDau(id: CuonSach['id'] | null) {
		danhDauNgoai = cuon.find((c) => c.s.id === id) ?? null;
		capNhatNho();
	}

	function huy() {
		if (daHuy) return;
		daHuy = true;
		if (raf) cancelAnimationFrame(raf);
		for (const f of donDep) f();
		const daXoa = new Set<unknown>();
		scene.traverse((o: Object3D) => {
			const m = o as Mesh;
			if (!m.isMesh) return;
			const g = m.geometry as BufferGeometry;
			if (!daXoa.has(g)) (daXoa.add(g), g.dispose());
			for (const mat of ([] as Material[]).concat(m.material)) {
				if (daXoa.has(mat)) continue;
				daXoa.add(mat);
				const map = (mat as MeshStandardMaterial).map;
				if (map && !daXoa.has(map)) (daXoa.add(map), map.dispose());
				mat.dispose();
			}
		});
		if (renderer) {
			// Trả context WebGL ngay, không chờ bộ dọn rác (trình duyệt giới hạn số context cùng lúc).
			renderer.forceContextLoss();
			renderer.dispose();
			renderer.domElement.remove();
			renderer = null;
		}
		goc.dataset.trangThai = 'phang';
	}

	async function khoiDong() {
		// Ảnh bìa tải song song với font; lỗi thì dùng bìa vẽ bằng canvas.
		const choBia = Promise.all(sach.map((s) => (s.anhBia ? taiBia(s.anhBia) : null)));
		// Chữ trên bìa cần Be Vietnam Pro đã tải (kể cả bộ ký tự có dấu) trước khi vẽ canvas.
		try {
			await Promise.all([
				document.fonts.load(`800 80px ${FONT}`, 'AI ENGINEER ROBOTICS SẮP CÓ'),
				document.fonts.load(`600 20px ${FONT}`, 'AI & ROBOTICS · NHÁNH Bắt đầu đọc →'),
				document.fonts.load(`400 25px ${FONT}`, sach.map((s) => s.phuDe).join(' ')),
			]);
			await document.fonts.ready;
		} catch {
			/* vẫn vẽ bằng font dự phòng */
		}
		const biaSvg = await choBia;
		if (daHuy) return;

		const r = new WebGLRenderer({ antialias: true, alpha: true, powerPreference: 'low-power' });
		renderer = r;
		r.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.5));
		r.outputColorSpace = SRGBColorSpace;
		r.toneMapping = NeutralToneMapping;
		r.toneMappingExposure = 1.05;
		const aniso = Math.min(4, r.capabilities.getMaxAnisotropy());

		// Ánh sáng: trời ấm + một nguồn chính chéo từ trên trái.
		scene.add(new HemisphereLight(0xfff3e0, 0x5a4030, 1.3));
		const den = new DirectionalLight(0xfff0dc, 2.8);
		den.position.set(-3.5, 6, 6);
		scene.add(den);

		// Kệ gỗ.
		const tGo = kieuSRGB(new CanvasTexture(vanGo('#5f3d25', 11)), aniso);
		tGo.wrapS = tGo.wrapT = RepeatWrapping;
		const go = new MeshStandardMaterial({ map: tGo, color: 0xffffff, roughness: 0.55, metalness: 0 });
		const tHau = kieuSRGB(new CanvasTexture(vanGo('#8c6849', 23, true)), aniso);
		const hau = new MeshStandardMaterial({ map: tHau, roughness: 0.8 });
		const R = 0.035;
		const ngoaiRong = KE.rong + KE.hong * 2;
		const tamVan = (w: number, h: number, d: number, x: number, y: number, z: number) => {
			const m = new Mesh(new RoundedBoxGeometry(w, h, d, 3, R), go);
			m.position.set(x, y, z);
			ke.add(m);
		};
		tamVan(KE.rong + 0.02, KE.van, KE.sau, 0, -KE.van / 2, 0);
		tamVan(ngoaiRong + 0.08, KE.van, KE.sau + 0.06, 0, KE.cao + KE.van / 2, 0.01);
		for (const sx of [-1, 1]) tamVan(KE.hong, KE.cao + KE.chan, KE.sau, sx * (KE.rong / 2 + KE.hong / 2), (KE.cao - KE.chan) / 2, 0);
		// Thanh chân trước, lùi vào trong.
		tamVan(KE.rong, KE.chan - KE.van, 0.06, 0, -KE.van - (KE.chan - KE.van) / 2, KE.sau / 2 - 0.1);
		const vanHau = new Mesh(new PlaneGeometry(KE.rong + 0.1, KE.cao + 0.05), hau);
		vanHau.position.set(0, KE.cao / 2, -KE.sau / 2 + 0.03);
		ke.add(vanHau);

		// Bóng giả.
		const tBong = new CanvasTexture(bongMem());
		const bong = (w: number, d: number, x: number, y: number, z: number, opacity: number, dung = false) => {
			const m = new Mesh(new PlaneGeometry(w, d), new MeshBasicMaterial({ map: tBong, transparent: true, depthWrite: false, opacity }));
			if (!dung) m.rotation.x = -Math.PI / 2;
			m.position.set(x, y, z);
			ke.add(m);
			return m;
		};
		bong(ngoaiRong + 1.2, KE.sau + 1.1, 0, -KE.chan - 0.001, 0.05, 0.55);

		// Sách.
		const tGiay = kieuSRGB(new CanvasTexture(mepGiay()), aniso);
		const tGiayTren = tGiay.clone();
		tGiayTren.center.set(0.5, 0.5);
		tGiayTren.rotation = Math.PI / 2;
		const giay = new MeshStandardMaterial({ map: tGiay, roughness: 0.9 });
		const giayTren = new MeshStandardMaterial({ map: tGiayTren, roughness: 0.9 });
		const giayTrang = new MeshStandardMaterial({ color: 0xf2ead8, roughness: 0.9 });

		const viTri = [
			{ x: -0.8, quay: 0.06, day: 0.34 },
			{ x: 0.82, quay: -0.08, day: 0.28 },
		];
		sach.forEach((s, i) => {
			const vt = viTri[i] ?? { x: 0, quay: 0, day: 0.3 };
			const { rong: w, cao: h } = SACH;
			const d = vt.day;
			const bia = 0.028;
			const nhom = new Group();
			nhom.userData.id = s.id;
			const z0 = -0.08;
			nhom.position.set(vt.x, 0, z0);
			nhom.rotation.y = vt.quay;

			const veBia = biaSvg[i] ?? (s.id === 'robotics' ? biaRobotics(s) : biaAiEngineer(s));
			const matBia = new MeshStandardMaterial({ map: kieuSRGB(new CanvasTexture(veBia), aniso), roughness: 0.42 });
			const vo = new MeshStandardMaterial({ color: s.mauBia, roughness: 0.5 });

			// Chỉ sách mở được mới cần vẽ trang đầu.
			const matTrangDau = s.sapCo ? giayTrang : new MeshStandardMaterial({ map: kieuSRGB(new CanvasTexture(trangDau(s)), aniso), roughness: 0.9 });
			const ruot = new Mesh(new BoxGeometry(w - 0.06, h - 0.07, d - bia * 2), [giay, giayTrang, giayTren, giayTren, matTrangDau, giayTrang]);
			ruot.position.set(0.0, h / 2, 0);
			const biaSau = new Mesh(new BoxGeometry(w, h, bia), vo);
			biaSau.position.set(0, h / 2, -d / 2 + bia / 2);
			const gay = new Mesh(new RoundedBoxGeometry(0.06, h, d, 2, 0.025), vo);
			gay.position.set(-w / 2 + 0.02, h / 2, 0);
			const banLeBia = new Group();
			banLeBia.position.set(-w / 2, h / 2, d / 2 - bia / 2);
			const biaTruoc = new Mesh(new BoxGeometry(w, h, bia), [vo, vo, vo, vo, matBia, giayTrang]);
			biaTruoc.position.x = w / 2;
			banLeBia.add(biaTruoc);
			nhom.add(ruot, biaSau, gay, banLeBia);
			ke.add(nhom);

			// Bóng tiếp xúc dưới chân sách và bóng đổ lên ván hậu.
			bong(w + 0.35, d + 0.45, vt.x, 0.002, z0, 0.5);
			bong(w + 0.6, h * 0.95, vt.x + 0.22, h * 0.5, -KE.sau / 2 + 0.035, 0.32, true);

			cuon.push({ s, nhom, banLeBia, z0, nho: 0, nhoDich: 0, mo: 0, moDich: 0, lac: 0 });
		});

		// Khung hình: vừa cả kệ ở mọi tỉ lệ khung.
		const tamY = (KE.cao - KE.chan) / 2 + 0.05;
		const canhCamera = () => {
			const rect = goc.getBoundingClientRect();
			const w = Math.max(1, rect.width);
			const h = Math.max(1, rect.height);
			r.setSize(w, h, false);
			camera.aspect = w / h;
			const tanV = Math.tan((camera.fov * Math.PI) / 360);
			const canRong = ngoaiRong + 0.55;
			const canCao = KE.cao + KE.chan + KE.van + 0.7;
			const xa = Math.max(canCao / 2 / tanV, canRong / 2 / (tanV * camera.aspect)) + KE.sau / 2;
			const nang = 0.16;
			camera.position.set(0, tamY + Math.sin(nang) * xa, Math.cos(nang) * xa);
			camera.lookAt(0, tamY, 0);
			camera.updateProjectionMatrix();
			yeuCauVe();
		};

		const cv = r.domElement;
		cv.setAttribute('aria-hidden', 'true');
		cv.className = 'canvas-3d';
		goc.appendChild(cv);
		canhCamera();

		const ro = new ResizeObserver(canhCamera);
		ro.observe(goc);
		const io = new IntersectionObserver((e) => {
			dangThay = e.some((x) => x.isIntersecting);
			if (dangThay) yeuCauVe();
			else if (raf) (cancelAnimationFrame(raf), (raf = 0), (tLan = 0));
		});
		io.observe(goc);
		donDep.push(() => (ro.disconnect(), io.disconnect()));

		// Chuột: rê để làm nổi, kéo để xoay kệ, bấm để chọn.
		const ray = new Raycaster();
		const ndc = new Vector2();
		const trungSach = (e: PointerEvent): Cuon | null => {
			const b = cv.getBoundingClientRect();
			ndc.set(((e.clientX - b.left) / b.width) * 2 - 1, -((e.clientY - b.top) / b.height) * 2 + 1);
			ray.setFromCamera(ndc, camera);
			const hit = ray.intersectObjects(cuon.map((c) => c.nhom), true)[0];
			let o: Object3D | null = hit?.object ?? null;
			while (o && !o.userData.id) o = o.parent;
			return cuon.find((c) => c.nhom === o) ?? null;
		};
		let keo: { x: number; xoay: number; da: boolean; id: number } | null = null;
		const xuong = (e: PointerEvent) => {
			if (e.button !== 0) return;
			keo = { x: e.clientX, xoay: xoayDich, da: false, id: e.pointerId };
		};
		const di = (e: PointerEvent) => {
			if (keo && keo.id === e.pointerId) {
				const dx = e.clientX - keo.x;
				if (!keo.da && Math.abs(dx) > 4) {
					keo.da = true;
					cv.setPointerCapture(e.pointerId);
					cv.style.cursor = 'grabbing';
				}
				if (keo.da) {
					xoayDich = Math.max(-GOC_XOAY, Math.min(GOC_XOAY, keo.xoay + dx * 0.006));
					yeuCauVe();
					return;
				}
			}
			const c = trungSach(e);
			if (c !== rePhai) {
				rePhai = c;
				cv.style.cursor = c ? 'pointer' : 'grab';
				capNhatNho();
			}
		};
		const len = (e: PointerEvent) => {
			const k = keo;
			keo = null;
			if (!k || k.id !== e.pointerId) return;
			if (k.da) {
				cv.releasePointerCapture(e.pointerId);
				cv.style.cursor = 'grab';
				return;
			}
			const c = trungSach(e);
			if (c && chon(c.s.id)) khiChon(c.s);
		};
		const roi = () => {
			if (keo?.da) return;
			rePhai = null;
			capNhatNho();
		};
		cv.addEventListener('pointerdown', xuong);
		cv.addEventListener('pointermove', di);
		cv.addEventListener('pointerup', len);
		cv.addEventListener('pointercancel', len);
		cv.addEventListener('pointerleave', roi);
		cv.style.cursor = 'grab';
		donDep.push(() => {
			cv.removeEventListener('pointerdown', xuong);
			cv.removeEventListener('pointermove', di);
			cv.removeEventListener('pointerup', len);
			cv.removeEventListener('pointercancel', len);
			cv.removeEventListener('pointerleave', roi);
		});

		// Khung đầu tiên vẽ đồng bộ để canvas không hiện trống.
		veMotKhung(performance.now());
		sanSang = true;
		goc.dataset.trangThai = 'san-sang';
		if (choId) chon(choId);
	}

	khoiDong().catch(() => {
		// Không tạo được WebGL hoặc lỗi khác: giữ bản phẳng.
		huy();
	});

	return { huy, chon, dong, danhDau };
}
