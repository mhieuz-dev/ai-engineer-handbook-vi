// Gradient descent cho y = w·x + b, w = b = 0 ban đầu. Trả về MSE đo trước mỗi lần cập nhật.
export function chayGD(x: number[], y: number[], lr: number, soBuoc: number): number[] {
	const n = x.length;
	let w = 0;
	let b = 0;
	const mse: number[] = [];
	for (let k = 0; k < soBuoc; k++) {
		const e = x.map((xi, i) => y[i] - (w * xi + b));
		mse.push(e.reduce((s, v) => s + v * v, 0) / n);
		const gw = (-2 / n) * e.reduce((s, v, i) => s + v * x[i], 0);
		const gb = (-2 / n) * e.reduce((s, v) => s + v, 0);
		w -= lr * gw;
		b -= lr * gb;
	}
	return mse;
}
