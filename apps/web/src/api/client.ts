import createClient from 'openapi-fetch';
import type { components, paths } from './schema';

export type DemoRequest = components['schemas']['DemoRequest'];
export type DemoResponse = components['schemas']['DemoResponse'];
export type CityPack = components['schemas']['CityPack'];
export type Plan = components['schemas']['Plan'];
export type PlanningContext = components['schemas']['PlanningContext'];

const client = createClient<paths>({ baseUrl: '' });

export async function loadDemo(signal: AbortSignal) {
    const [request, catalog] = await Promise.all([
        client.GET('/api/v1/demo/request', { signal }),
        client.GET('/api/v1/demo/catalog', { signal }),
    ]);
    if (!request.data || !catalog.data) {
        throw new Error('The demo could not be loaded. Please try again.');
    }
    return { request: request.data, catalog: catalog.data };
}

export async function planTrip(
    body: DemoRequest,
    signal: AbortSignal,
): Promise<DemoResponse> {
    const result = await client.POST('/api/v1/demo/plan', { body, signal });
    if (!result.data) {
        if (result.response.status === 422) {
            throw new Error(
                'Check your times: the return deadline must be later than the start.',
            );
        }
        throw new Error(
            'Planning is unavailable. Your settings are still here; please try again.',
        );
    }
    return result.data;
}
