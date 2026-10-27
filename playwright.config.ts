import { defineConfig } from '@playwright/test';

export default defineConfig({
	testDir: 'tests/e2e',
	webServer: {
		command: 'npm run build && npm run preview -- --port 4399 --ignore-lock',
		url: 'http://localhost:4399',
		reuseExistingServer: true,
		timeout: 180_000,
	},
	use: { baseURL: 'http://localhost:4399' },
	projects: [
		{ name: 'desktop', use: { viewport: { width: 1280, height: 800 } } },
		{ name: 'mobile', use: { viewport: { width: 375, height: 812 }, hasTouch: true, isMobile: true } },
	],
});
