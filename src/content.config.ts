import { defineCollection } from 'astro:content';
import { z } from 'astro/zod';
import { file } from 'astro/loaders';
import { docsLoader } from '@astrojs/starlight/loaders';
import { docsSchema } from '@astrojs/starlight/schema';

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
};
