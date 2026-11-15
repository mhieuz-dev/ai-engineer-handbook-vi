import { describe, it, expect } from 'vitest';
import { thanhHtml } from '../../src/lib/khung-code/markdown';

describe('markdown câu trả lời trợ lý', () => {
	it('thoát HTML lạ, không cho chạy script', async () => {
		const h = await thanhHtml('<script>alert(1)</script> và <b>x</b>');
		expect(h).not.toContain('<script>');
		expect(h).not.toContain('<b>x</b>');
		expect(h).toContain('&lt;script&gt;');
	});
	it('đậm, nghiêng, code dòng, liên kết', async () => {
		const h = await thanhHtml('**đậm** và *nghiêng* và `np.array` và [trang](/ai-engineer/ch01-python-tu-dau/)');
		expect(h).toContain('<strong>đậm</strong>');
		expect(h).toContain('<em>nghiêng</em>');
		expect(h).toContain('<code>np.array</code>');
		expect(h).toContain('href="/ai-engineer/ch01-python-tu-dau/"');
	});
	it('khối code có nút đưa vào khung', async () => {
		const h = await thanhHtml('```python\nprint(1)\n```');
		expect(h).toContain('kc-md-khoi');
		expect(h).toContain('Đưa vào khung code');
		expect(h).toContain('print(1)');
	});
	it('danh sách và tiêu đề', async () => {
		const h = await thanhHtml('## Mục\n- một\n- hai\n1. ba');
		expect(h).toContain('<h4>Mục</h4>');
		expect(h).toContain('<ul>');
		expect(h).toContain('<li>một</li>');
		expect(h).toContain('<ol>');
	});
	it('công thức $...$ thành KaTeX', async () => {
		const h = await thanhHtml('Ta có $E=mc^2$ đẹp.');
		expect(h).toContain('katex');
	});
});
