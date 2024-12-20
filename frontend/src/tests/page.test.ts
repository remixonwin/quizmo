import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/svelte';
import Page from '../routes/+page.svelte';

describe('Page Component', () => {
  it('renders the page correctly', () => {
    const { getByText } = render(Page);
    expect(getByText('Welcome to SvelteKit')).toBeInTheDocument();

    // Use a function matcher to handle split text
    expect(getByText((content, element) => {
      const hasText = (node) => node.textContent === 'Visit svelte.dev/docs/kit to read the documentation';
      const nodeHasText = hasText(element);
      const childrenDontHaveText = Array.from(element?.children || []).every(child => !hasText(child));
      return nodeHasText && childrenDontHaveText;
    })).toBeInTheDocument();
  });
});
