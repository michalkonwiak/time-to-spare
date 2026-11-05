import { describe, expect, it } from 'vitest';
import { duration, fixtureTimestamp, parseBudget, time } from './format';

describe('money input', () => {
    it('preserves cents without floating point rounding', () => {
        expect(parseBudget('0.29')).toBe(29);
        expect(parseBudget('45.5')).toBe(4550);
        expect(parseBudget('0')).toBe(0);
        expect(parseBudget('1000')).toBe(100000);
    });
    it.each(['-1', '1.234', '1000.01', 'Infinity', '', '1e2'])(
        'rejects %s',
        (input) => {
            expect(() => parseBudget(input)).toThrow();
        },
    );
});

it('uses Warsaw time regardless of the browser timezone', () => {
    expect(time('2030-06-11T15:40:00Z', 'Europe/Warsaw')).toBe('17:40:00');
    expect(fixtureTimestamp('19:40')).toBe('2030-06-11T19:40:00+02:00');
    expect(() => fixtureTimestamp('24:00')).toThrow();
});

it('does not round return slack upward', () => {
    expect(duration(59)).toBe('0m 59s');
    expect(duration(423)).toBe('7m 3s');
});
