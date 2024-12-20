import { TextEncoder, TextDecoder } from 'util';

// Set TextEncoder and TextDecoder on the global scope unconditionally
globalThis.TextEncoder = TextEncoder;
globalThis.TextDecoder = TextDecoder;

// Optional: Extend Jest matchers if using @testing-library/jest-dom
import '@testing-library/jest-dom';

// ...existing code...