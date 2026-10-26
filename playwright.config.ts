import { defineConfig } from '@playwright/test';

export default defineConfig({
	testDir: 'tests/e2e',
	webServer: {
		command: 'npm run build && npm run preview -- --port 4321 --ignore-lock',
		url: 'http://localhost:4321',
		reuseExistingServer: true,
		timeout: 180_000,
	},
	use: { baseURL: 'http://localhost:4321' },
	projects: [
		{ name: 'desktop', use: { viewport: { width: 1280, height: 800 } } },
		{ name: 'mobile', use: { viewport: { width: 375, height: 812 } } },
	],
});
