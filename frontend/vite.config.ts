import { defineConfig } from 'vite';
import { svelte } from '@sveltejs/vite-plugin-svelte';
import { coverage } from '@vitest/coverage-v8';

export default defineConfig({
  plugins: [svelte()],
  test: {
    environment: 'jsdom', // Use 'jsdom' for DOM-related tests
    setupFiles: './tests/setupVitest.js',
    globals: true,
    coverage: {
      enabled: true,
      reporter: ['text', 'json', 'html']
    },
  },
});
