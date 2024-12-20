import { describe, test, expect } from 'vitest';
import config from '../svelte.config.js';

describe('svelte.config.js', () => {
    test('should export a valid configuration object', () => {
        expect(config).toBeDefined();
        expect(typeof config).toBe('object');
        // Add more specific assertions based on your configuration
    });
});