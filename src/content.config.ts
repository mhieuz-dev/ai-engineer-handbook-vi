import { defineCollection } from 'astro:content';
import { z } from 'astro/zod';
import { file, glob } from 'astro/loaders';
import { docsLoader } from '@astrojs/starlight/loaders';
import { docsSchema } from '@astrojs/starlight/schema';

const mucDo = z.enum(['de', 'vua', 'kho']).default('vua');
const khaiNiem = z.array(z.string()).default([]);

const tracNghiem = z.object({
	loai: z.literal('trac-nghiem'),
	id: z.string(),
	khai_niem: khaiNiem,
	muc: mucDo,
	diem: z.number().default(1),
	de: z.string(),
	lua_chon: z.array(z.string()).min(2),
	dap_an: z.number().int().min(0),
	giai_thich: z.string(),
});

const tuLuan = z.object({
	loai: z.literal('tu-luan'),
	id: z.string(),
	khai_niem: khaiNiem,
	muc: mucDo,
	diem: z.number().default(10),
	de: z.string(),
	rubric: z.array(z.object({ y: z.string(), diem: z.number() })).min(1),
	tra_loi_mau: z.string(),
});

const code = z.object({
	loai: z.literal('code'),
	id: z.string(),
	khai_niem: khaiNiem,
	muc: mucDo,
	diem: z.number().default(3),
	de: z.string(),
	khung: z.string(),
	kiem_tra: z.string(),
	loi_giai: z.string(),
});

const nhiemVu = z.discriminatedUnion('loai', [
	z.object({ loai: z.literal('code'), de: z.string(), diem: z.number(), kiem_tra: z.string() }),
	z.object({
		loai: z.literal('tu-luan'),
		de: z.string(),
		diem: z.number(),
		rubric: z.array(z.object({ y: z.string(), diem: z.number() })).min(1),
	}),
]);

const caseThi = z.object({
	loai: z.literal('case'),
	id: z.string(),
	khai_niem: khaiNiem,
	muc: mucDo,
	diem: z.number().default(10),
	boi_canh: z.string(),
	du_lieu: z.array(z.string()).default([]),
	bay: z.array(z.string()).default([]),
	nhiem_vu: z.array(nhiemVu).min(1),
	dap_an_mau: z.string(),
});

const deThi = defineCollection({
	loader: glob({ pattern: '**/*.yaml', base: './src/data/de-thi' }),
	schema: z.object({
		chuong: z.number().int().min(0),
		ten: z.string(),
		khai_niem: z.array(z.object({ id: z.string(), ten: z.string(), trang: z.string() })).min(1),
		cau_hoi: z.array(z.discriminatedUnion('loai', [tracNghiem, tuLuan, code, caseThi])).min(1),
	}),
});

export const collections = {
	docs: defineCollection({ loader: docsLoader(), schema: docsSchema() }),
	thuatNgu: defineCollection({
		loader: file('src/data/thuat-ngu.yaml'),
		schema: z.object({
			id: z.string(),
			ten: z.string(),
			tenTiengAnh: z.string().optional(),
			giaiThich: z.string(),
			hocKy: z.string().optional(),
		}),
	}),
	deThi: deThi,
};
