// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';
import sitemap from '@astrojs/sitemap';
import { unified } from '@astrojs/markdown-remark';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import { cauHinhSidebar } from './src/data/chuong.ts';

// https://astro.build/config
export default defineConfig({
	site: 'https://ai-and-robotics.vercel.app',
	markdown: {
		processor: unified({ remarkPlugins: [remarkMath], rehypePlugins: [rehypeKatex] }),
	},
	// Vite 8 dùng rolldown: giữ chú thích @license (three.js MIT) ở đầu chunk JS đã nén.
	vite: { build: { rolldownOptions: { output: { comments: { legal: true } } } } },
	integrations: [
		// Tự khai báo sitemap (Starlight sẽ bỏ qua bản của nó) để loại trang in PDF và trang mẫu cho e2e.
		sitemap({ filter: (url) => !/^\/(in|kiem-thu)\//.test(new URL(url).pathname) }),
		starlight({
			title: 'AI & Robotics',
			defaultLocale: 'root',
			locales: { root: { label: 'Tiếng Việt', lang: 'vi' } },
			sidebar: cauHinhSidebar(),
			components: {
				SocialIcons: './src/components/overrides/SocialIcons.astro',
				Sidebar: './src/components/overrides/Sidebar.astro',
				Pagination: './src/components/overrides/Pagination.astro',
				PageTitle: './src/components/overrides/PageTitle.astro',
				TableOfContents: './src/components/overrides/TableOfContents.astro',
			},
			customCss: [
				'@fontsource/be-vietnam-pro/400.css',
				'@fontsource/be-vietnam-pro/600.css',
				'@fontsource/be-vietnam-pro/800.css',
				'@fontsource/lora/400.css',
				'@fontsource/lora/400-italic.css',
				'@fontsource/lora/600.css',
				'@fontsource/jetbrains-mono/400.css',
				'./src/styles/theme.css',
				'katex/dist/katex.min.css',
			],
		}),
	],
});
