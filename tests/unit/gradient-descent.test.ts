import { describe, it, expect } from 'vitest';
import { chayGD } from '../../src/lib/gradient-descent';

const x = [1, 2, 3, 4];
const y = [2, 4, 5, 7];

describe('chayGD', () => {
	it('lr 0,05: MSE đầu 23,5, bước 1 và bước 40 khớp bản chạy Python', () => {
		const m = chayGD(x, y, 0.05, 40);
		expect(m).toHaveLength(40);
		expect(m[0]).toBe(23.5);
		expect(m[1]).toBeCloseTo(0.6884375, 7);
		expect(m[39]).toBeCloseTo(0.0500808146, 8);
	});
	it('lr 0,135 phát nổ: MSE tăng mỗi bước', () => {
		const m = chayGD(x, y, 0.135, 4);
		[23.5, 36.95958438, 58.14467124, 91.48951859].forEach((v, i) => expect(m[i]).toBeCloseTo(v, 6));
	});
	it('lr 0,005 còn chậm sau 40 bước', () => {
		expect(chayGD(x, y, 0.005, 40)[39]).toBeCloseTo(0.0763161901, 8);
	});
});
