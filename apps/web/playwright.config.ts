import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
    testDir: './e2e',
    fullyParallel: true,
    forbidOnly: Boolean(process.env.CI),
    retries: process.env.CI ? 1 : 0,
    workers: 2,
    reporter: 'list',
    use: { baseURL: 'http://127.0.0.1:5174', trace: 'retain-on-failure' },
    projects: [
        { name: 'desktop', use: { ...devices['Desktop Chrome'] } },
        { name: 'mobile', use: { ...devices['Pixel 7'] } },
    ],
    webServer: [
        {
            command:
                'uv run --project ../.. --locked uvicorn time_to_spare.http.app:create_app --factory --host 127.0.0.1 --port 8001',
            url: 'http://127.0.0.1:8001/health/live',
            reuseExistingServer: false,
        },
        {
            command: 'npm run dev -- --port 5174',
            url: 'http://127.0.0.1:5174',
            reuseExistingServer: false,
            env: { API_TARGET: 'http://127.0.0.1:8001' },
        },
    ],
});
