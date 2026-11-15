import { getCollection } from 'astro:content';
import type { DeThi } from './de-thi-logic';

/** Đọc ngân hàng đề đã kiểm bằng schema của content collection. Chỉ chạy lúc build. */
export async function taiDeThi(): Promise<DeThi[]> {
	const ds = await getCollection('deThi');
	return ds.map((e) => e.data as unknown as DeThi).sort((a, b) => a.chuong - b.chuong);
}
