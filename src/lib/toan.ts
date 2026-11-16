import { getCollection } from 'astro:content';
import type { BaiToan } from './toan-dang';

export { MODULE_TOAN, THU_TU_MODULE } from './toan-dang';
export type { BaiToan } from './toan-dang';

export async function taiBaiToan(): Promise<BaiToan[]> {
	const ds = await getCollection('toan');
	return ds.map((e) => e.data as unknown as BaiToan).sort((a, b) => a.so - b.so);
}
