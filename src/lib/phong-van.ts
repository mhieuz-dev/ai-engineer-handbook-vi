import { getCollection } from 'astro:content';

export interface VongPV {
	ten: string;
	loai: 'hanh-vi' | 'ml' | 'system' | 'product' | 'code';
}

export interface PresetPV {
	id: string;
	ten: string;
	moTa: string;
	nguon: string;
	trongTam: string[];
	vong: VongPV[];
	cau_hoi: {
		'hanh-vi': string[];
		ml: string[];
		system: string[];
		product: string[];
	};
}

export async function taiPreset(): Promise<PresetPV[]> {
	const ds = await getCollection('phongVan');
	const thuTu = ['google', 'meta', 'amazon', 'microsoft', 'nvidia', 'viet-nam', 'startup-genai', 'tu-do'];
	return ds.map((e) => e.data as unknown as PresetPV).sort((a, b) => thuTu.indexOf(a.id) - thuTu.indexOf(b.id));
}
