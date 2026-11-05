export function money(minor: number): string {
    return new Intl.NumberFormat('en-GB', {
        style: 'currency',
        currency: 'PLN',
    }).format(minor / 100);
}

export function parseBudget(value: string): number {
    if (!/^\d{1,4}(\.\d{1,2})?$/.test(value)) {
        throw new Error(
            'Enter a budget from 0 to 1,000 PLN, with at most two decimal places.',
        );
    }
    const [whole = '0', fraction = ''] = value.split('.');
    const minor = Number(whole) * 100 + Number(fraction.padEnd(2, '0'));
    if (minor > 100_000) throw new Error('The demo budget limit is 1,000 PLN.');
    return minor;
}

export function time(value: string, timezone: string): string {
    return new Intl.DateTimeFormat('en-GB', {
        timeZone: timezone,
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false,
    }).format(new Date(value));
}

export function duration(seconds: number): string {
    const minutes = Math.floor(seconds / 60);
    const remainder = seconds % 60;
    return remainder ? `${minutes}m ${remainder}s` : `${minutes} min`;
}

// This UI is explicitly restricted to one fixture date, whose Warsaw offset is +02:00.
// Real citypack dates require timezone-aware input conversion, including DST folds.
export function fixtureTimestamp(clock: string): string {
    if (!/^([01]\d|2[0-3]):[0-5]\d$/.test(clock))
        throw new Error('Enter a valid time.');
    return `2030-06-11T${clock}:00+02:00`;
}

export const noPlanMessages: Record<string, string> = {
    INSUFFICIENT_TIME:
        'There is not enough time after the return buffers. Try a later deadline.',
    START_IN_PAST: 'This demo starts at 17:40. Choose that time or later.',
    SNAPSHOT_EXPIRED: 'The fixture data has expired for this start time.',
    RETURN_UNREACHABLE: 'There is no verified return route for these settings.',
    ACCESSIBILITY_UNVERIFIED: 'A step-free return route could not be verified.',
    NO_FEASIBLE_PLAN:
        'No outing fits all your settings. Try allowing more walking or more time. A zero budget still allows free places.',
};
