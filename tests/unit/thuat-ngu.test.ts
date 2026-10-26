import { describe, it, expect } from 'vitest';
import { readFileSync } from 'node:fs';
import yaml from 'js-yaml';
import { CHUONG } from '../../src/data/chuong';
import { trichIdThuatNgu, dungLinkNguoc, linkHocKy } from '../../src/lib/thuat-ngu';

describe('trichIdThuatNgu', () => {
	it('lấy id theo thứ tự, không trùng', () => {
		const mdx = 'a <Term id="dao-ham">x</Term> b <Term id="mse">y</Term> <Term id="dao-ham">z</Term>';
		expect(trichIdThuatNgu(mdx)).toEqual(['dao-ham', 'mse']);
	});
	it('chấp nhận nháy đơn và khoảng trắng', () => {
		expect(trichIdThuatNgu("<Term  id='gradient' >g</Term>")).toEqual(['gradient']);
	});
	it('không có Term thì trả mảng rỗng', () => {
		expect(trichIdThuatNgu('không có gì')).toEqual([]);
	});
});

describe('dungLinkNguoc', () => {
	it('gom các trang dùng cùng thuật ngữ theo thứ tự đầu vào', () => {
		const map = dungLinkNguoc([
			{ id: 'a/1', title: 'Một', body: '<Term id="mse">m</Term>' },
			{ id: 'a/2', title: 'Hai', body: '<Term id="mse">m</Term> <Term id="gradient">g</Term>' },
		]);
		expect(map.get('mse')).toEqual([{ id: 'a/1', title: 'Một' }, { id: 'a/2', title: 'Hai' }]);
		expect(map.get('gradient')).toEqual([{ id: 'a/2', title: 'Hai' }]);
	});
	it('bỏ qua trang kiem-thu/ để không lộ trang kiểm thử', () => {
		const map = dungLinkNguoc([
			{ id: 'kiem-thu/thanh-phan', title: 'Mẫu', body: '<Term id="dao-ham">x</Term>' },
			{ id: 'a/1', title: 'Một', body: '<Term id="mse">m</Term>' },
		]);
		expect(map.has('dao-ham')).toBe(false);
		expect(map.get('mse')).toHaveLength(1);
	});
});

describe('linkHocKy', () => {
	const ch10 = 'ai-engineer/ch10-hoi-quy-tuyen-tinh';
	it('chương đã xuất bản trỏ tới trang đầu của chương', () => {
		const r = linkHocKy(ch10, [`${ch10}/02-toan`, `${ch10}/01-truc-giac`]);
		expect(r).toEqual({ so: 10, href: `/${ch10}/01-truc-giac/` });
	});
	it('chương chưa xuất bản trỏ /lo-trinh/', () => {
		expect(linkHocKy('ai-engineer/ch06-giai-tich', [])).toEqual({ so: 6, href: '/lo-trinh/' });
	});
	it('đang đọc chính chương đó thì không có link', () => {
		const ids = [`${ch10}/01-truc-giac`];
		expect(linkHocKy(ch10, ids, `/${ch10}/02-toan/`)).toBeUndefined();
		expect(linkHocKy(ch10, ids, `/in/${ch10}/`)).toBeUndefined();
	});
	it('đang đọc chương khác hoặc trang chung thì vẫn có link', () => {
		const ids = [`${ch10}/01-truc-giac`];
		expect(linkHocKy(ch10, ids, '/thuat-ngu/')).toEqual({ so: 10, href: `/${ch10}/01-truc-giac/` });
		expect(linkHocKy('ai-engineer/ch06-giai-tich', ids, `/${ch10}/02-toan/`)).toEqual({ so: 6, href: '/lo-trinh/' });
		expect(linkHocKy('ai-engineer/ch01-python-tu-dau', ids, '/ai-engineer/ch10-hoi-quy-tuyen-tinh/')).toEqual({ so: 1, href: '/lo-trinh/' });
	});
	it('slug lạ trả undefined', () => {
		expect(linkHocKy('khong-co', [])).toBeUndefined();
	});
});

describe('dữ liệu thuat-ngu.yaml', () => {
	it('mọi hocKy đều có trong danh mục chương', () => {
		const muc = yaml.load(readFileSync('src/data/thuat-ngu.yaml', 'utf8')) as { id: string; hocKy?: string }[];
		const slug = new Set(CHUONG.map((c) => c.slug));
		for (const m of muc) if (m.hocKy) expect(slug.has(m.hocKy), `${m.id}: ${m.hocKy}`).toBe(true);
	});
});
