import { describe, it, expect } from 'vitest';
import { someFunction } from '../lib/index';

describe('lib/index', () => {
  it('should correctly execute someFunction', () => {
    const result = someFunction('test input');
    expect(result).toBe('Processed test input');
  });
});
