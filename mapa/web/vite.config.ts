import adapter from '@sveltejs/adapter-node';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vitest/config';

export default defineConfig({
	plugins: [
		sveltekit({
			compilerOptions: {
				// Runes en todo el proyecto, salvo librerías de terceros.
				runes: ({ filename }) => (filename.includes('node_modules') ? undefined : true)
			},
			adapter: adapter()
		})
	],
	test: { include: ['src/**/*.test.ts'] }
});
