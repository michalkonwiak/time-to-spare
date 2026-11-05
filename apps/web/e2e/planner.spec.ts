import { expect, test } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test('plans an outing, exposes buffers and clears stale results when edited', async ({
    page,
}) => {
    await page.goto('/');
    await expect(
        page.getByRole('heading', { name: 'Make it your time' }),
    ).toBeVisible();
    await page
        .getByRole('button', { name: 'Find my little adventure' })
        .click();
    const cards = page.getByRole('article');
    await expect(cards).toHaveCount(3);
    await expect(cards.first()).toContainText('Demo garden');
    await expect(cards.first()).toContainText('Station buffer');
    await expect(cards.first()).toContainText('20 min');
    await expect(cards.first()).toContainText('19:40:00');
    await cards
        .first()
        .getByRole('button', { name: 'Choose this preview' })
        .click();
    await expect(cards.first().getByRole('status')).toContainText(
        'does not start a live trip',
    );
    await page.getByLabel('Budget (PLN)').fill('0');
    await expect(cards).toHaveCount(0);
    await page
        .getByRole('button', { name: 'Find my little adventure' })
        .click();
    await expect(cards).toHaveCount(1);
    await expect(cards.first()).toContainText('PLN');
    await expect(cards.first()).not.toContainText('Demo cafe');
});

test('handles no-plan and invalid-time results without relaxing limits', async ({
    page,
}) => {
    await page.goto('/');
    await page.getByLabel('Deadline', { exact: true }).fill('18:00');
    await page
        .getByRole('button', { name: 'Find my little adventure' })
        .click();
    await expect(page.getByText('No outing fits just yet.')).toBeVisible();
    await expect(
        page.getByText('Your limits have stayed exactly as you set them.'),
    ).toBeVisible();
    await page.getByLabel('Deadline', { exact: true }).fill('17:00');
    await page
        .getByRole('button', { name: 'Find my little adventure' })
        .click();
    await expect(page.getByRole('alert')).toContainText('later than the start');
});

test('keeps inputs on network failure and supports retry', async ({ page }) => {
    await page.goto('/');
    await page.getByLabel('Budget (PLN)').fill('30');
    await page.route('**/api/v1/demo/plan', (route) => route.abort());
    await page
        .getByRole('button', { name: 'Find my little adventure' })
        .click();
    await expect(page.getByRole('alert')).toContainText('couldn’t reach');
    await expect(page.getByLabel('Budget (PLN)')).toHaveValue('30');
    await page.unroute('**/api/v1/demo/plan');
    await page
        .getByRole('button', { name: 'Find my little adventure' })
        .click();
    await expect(page.getByRole('article').first()).toBeVisible();
});

test('does not render a response for inputs edited during a request', async ({
    page,
}) => {
    await page.goto('/');
    let release: (() => void) | undefined;
    const gate = new Promise<void>((resolve) => {
        release = resolve;
    });
    await page.route('**/api/v1/demo/plan', async (route) => {
        await gate;
        try {
            await route.continue();
        } catch {
            /* The edited request is intentionally aborted. */
        }
    });
    await page
        .getByRole('button', { name: 'Find my little adventure' })
        .click();
    await expect(
        page.getByRole('button', { name: 'Cancel planning' }),
    ).toBeVisible();
    await page.getByLabel('Budget (PLN)').fill('0');
    release?.();
    await expect(page.getByRole('article')).toHaveCount(0);
    await expect(
        page.getByRole('button', { name: 'Find my little adventure' }),
    ).toBeEnabled();
});

test('supports keyboard flow, accessible results and narrow screens', async ({
    page,
}) => {
    await page.goto('/');
    await page.getByLabel('Budget (PLN)').fill('45');
    const submit = page.getByRole('button', {
        name: 'Find my little adventure',
    });
    await submit.focus();
    await page.keyboard.press('Enter');
    await expect(page.getByRole('article').first()).toBeVisible();
    expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
    const overflow = await page.evaluate(
        () => document.documentElement.scrollWidth > window.innerWidth,
    );
    expect(overflow).toBe(false);
    await page.screenshot({
        path: `test-results/planner-${test.info().project.name}.png`,
        fullPage: true,
    });
});

test('recovers from a failed catalog load', async ({ page }) => {
    await page.route('**/api/v1/demo/catalog', (route) => route.abort());
    await page.goto('/');
    await expect(
        page.getByRole('heading', { name: 'We couldn’t load the demo.' }),
    ).toBeVisible();
    await page.unroute('**/api/v1/demo/catalog');
    await page.getByRole('button', { name: 'Try again' }).click();
    await expect(page.getByLabel('Budget (PLN)')).toBeVisible();
});

test('arrival deadlines omit the boarding buffer and step-free excludes unverified places', async ({
    page,
}) => {
    await page.goto('/');
    await page
        .getByLabel('What does your deadline mean?')
        .selectOption('arrive_by');
    await page.getByLabel('Only verified step-free places and routes').check();
    await page
        .getByRole('button', { name: 'Find my little adventure' })
        .click();
    const first = page.getByRole('article').first();
    await expect(first).toContainText('Your arrival deadline');
    await expect(first).toContainText('0 min');
    await expect(
        page.getByRole('article').filter({ hasText: 'Demo gallery' }),
    ).toHaveCount(0);
});
