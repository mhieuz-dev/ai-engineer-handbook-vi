// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';
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
	integrations: [
		starlight({
			title: 'AI & Robotics',
			defaultLocale: 'root',
			locales: { root: { label: 'Tiếng Việt', lang: 'vi' } },
			social: [{ icon: 'github', label: 'GitHub', href: 'https://github.com/mhieuz-dev/ai-engineer-handbook-vi' }],
			sidebar: cauHinhSidebar(),
			components: { Sidebar: './src/components/overrides/Sidebar.astro' },
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
