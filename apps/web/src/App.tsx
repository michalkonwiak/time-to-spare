import { useEffect, useRef, useState } from 'react';
import type { FormEvent } from 'react';
import { loadDemo, planTrip } from './api/client';
import type {
    CityPack,
    DemoRequest,
    DemoResponse,
    Plan,
    PlanningContext,
} from './api/client';
import {
    duration,
    fixtureTimestamp,
    money,
    noPlanMessages,
    parseBudget,
    time,
} from './format';

type Demo = Awaited<ReturnType<typeof loadDemo>>;

function ClockMark() {
    return (
        <svg aria-hidden="true" viewBox="0 0 40 40" width="40" height="40">
            <circle
                cx="20"
                cy="20"
                r="17"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
            />
            <path
                d="M20 9v12l8 5"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
            />
            <circle cx="20" cy="20" r="2.5" fill="currentColor" />
        </svg>
    );
}

export function App() {
    const [demo, setDemo] = useState<Demo | null>(null);
    const [error, setError] = useState(false);
    const [attempt, setAttempt] = useState(0);
    useEffect(() => {
        const controller = new AbortController();
        loadDemo(controller.signal)
            .then(setDemo)
            .catch(() => {
                if (!controller.signal.aborted) setError(true);
            });
        return () => controller.abort();
    }, [attempt]);

    return (
        <>
            <a className="skip-link" href="#planner">
                Skip to planner
            </a>
            <header className="site-header">
                <a className="brand" href="/" aria-label="Time to Spare home">
                    <ClockMark />
                    <span>
                        time to spare<span className="brand-dot">.</span>
                    </span>
                </a>
                <span className="header-note">
                    A little time. A little adventure.
                </span>
                <span className="demo-badge">INTERACTIVE DEMO</span>
            </header>
            <main>
                <section className="intro" aria-labelledby="intro-title">
                    <div>
                        <p className="eyebrow">THE IN-BETWEEN IS YOURS</p>
                        <h1 id="intro-title">
                            More than
                            <br />
                            time to <em>kill.</em>
                        </h1>
                        <p className="intro-copy">
                            A quiet garden. A coffee around the corner.
                            <br className="desktop-break" /> Find an outing that
                            fits — with time to get back.
                        </p>
                    </div>
                    <div className="ticket" aria-label="Demo scenario">
                        <span className="ticket-label">
                            YOUR WINDOW OF POSSIBILITY
                        </span>
                        <div className="ticket-times">
                            <span>
                                17:40<small>STEP OUT</small>
                            </span>
                            <span className="ticket-arrow" aria-hidden="true">
                                ⟶
                            </span>
                            <span>
                                19:40<small>TRAIN DEPARTURE</small>
                            </span>
                        </div>
                        <div className="ticket-bottom">
                            <span>11 JUN 2030 · WARSAW TIME</span>
                            <span>02h 00m</span>
                        </div>
                        <p>Example times. Adjust them below.</p>
                    </div>
                </section>
                <aside className="demo-notice">
                    <span aria-hidden="true">◉</span>
                    <p>
                        <strong>A small, fictional city.</strong> Places, prices
                        and routes are demo data. This is not a live travel
                        service or navigation tool.
                    </p>
                </aside>
                {demo ? (
                    <Planner demo={demo} />
                ) : (
                    <section
                        id="planner"
                        className="loading-state"
                        aria-live="polite"
                    >
                        {error ? (
                            <>
                                <h2>We couldn’t load the demo.</h2>
                                <p>
                                    Check that the API is running, then try
                                    again.
                                </p>
                                <button
                                    onClick={() => {
                                        setError(false);
                                        setAttempt(attempt + 1);
                                    }}
                                >
                                    Try again
                                </button>
                            </>
                        ) : (
                            <p>Opening your window of possibility…</p>
                        )}
                    </section>
                )}
                <footer>
                    <span>Time well spent, with a little left over.</span>
                    <span>
                        Built around your return time. No location tracking.
                    </span>
                </footer>
            </main>
        </>
    );
}

function Planner({ demo }: { demo: Demo }) {
    const [start, setStart] = useState('17:40');
    const [deadline, setDeadline] = useState('19:40');
    const [budget, setBudget] = useState('45');
    const [walk, setWalk] = useState('60');
    const [pace, setPace] = useState<'standard' | 'relaxed'>('standard');
    const [kind, setKind] = useState<'departure' | 'arrive_by'>('departure');
    const [stepFree, setStepFree] = useState(false);
    const [interests, setInterests] = useState<Array<'walk' | 'food' | 'art'>>([
        'walk',
        'food',
    ]);
    const [response, setResponse] = useState<DemoResponse | null>(null);
    const [pending, setPending] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [selected, setSelected] = useState<number | null>(null);
    const controller = useRef<AbortController | null>(null);
    const results = useRef<HTMLElement | null>(null);
    useEffect(() => () => controller.current?.abort(), []);

    function invalidate() {
        controller.current?.abort();
        controller.current = null;
        setPending(false);
        setResponse(null);
        setError(null);
        setSelected(null);
    }

    async function submit(event: FormEvent<HTMLFormElement>) {
        event.preventDefault();
        invalidate();
        const active = new AbortController();
        controller.current = active;
        try {
            const request: DemoRequest = {
                ...demo.request,
                starts_at: fixtureTimestamp(start),
                deadline: fixtureTimestamp(deadline),
                timezone: 'Europe/Warsaw',
                deadline_type: kind,
                budget_minor: parseBudget(budget),
                max_walk_minutes: Number(walk),
                pace,
                avoid_stairs: stepFree,
                interests,
            };
            setPending(true);
            const data = await planTrip(request, active.signal);
            if (controller.current !== active) return;
            setResponse(data);
            requestAnimationFrame(() => results.current?.focus());
        } catch (caught) {
            if (active.signal.aborted) return;
            setError(
                caught instanceof Error && caught.name !== 'TypeError'
                    ? caught.message
                    : 'We couldn’t reach the planner. Your settings are saved here. Please try again.',
            );
        } finally {
            if (controller.current === active) setPending(false);
        }
    }

    return (
        <div className="workspace" id="planner">
            <section className="form-panel" aria-labelledby="form-title">
                <div className="section-heading">
                    <span className="section-number">01</span>
                    <h2 id="form-title">Make it your time</h2>
                </div>
                <form
                    onSubmit={(event) => {
                        void submit(event);
                    }}
                    onChange={invalidate}
                >
                    <div className="location-box">
                        <span className="field-label">START & RETURN</span>
                        <strong>{demo.catalog.return_point.name}</strong>
                        <span>Same entrance · fictional location</span>
                    </div>
                    <p className="date-note">
                        Tuesday, 11 June 2030 · Europe/Warsaw (UTC+02)
                    </p>
                    <div className="field-grid">
                        <label>
                            Step out at
                            <input
                                type="time"
                                required
                                value={start}
                                onChange={(event) =>
                                    setStart(event.target.value)
                                }
                            />
                        </label>
                        <label>
                            Deadline
                            <input
                                type="time"
                                required
                                value={deadline}
                                onChange={(event) =>
                                    setDeadline(event.target.value)
                                }
                            />
                        </label>
                    </div>
                    <label>
                        What does your deadline mean?
                        <select
                            value={kind}
                            onChange={(event) =>
                                setKind(event.target.value as typeof kind)
                            }
                        >
                            <option value="departure">
                                My train departs then
                            </option>
                            <option value="arrive_by">
                                I need to be at the entrance
                            </option>
                        </select>
                    </label>
                    <div className="buffer-note">
                        {kind === 'departure'
                            ? '20 min station buffer + 10 min extra reserve.'
                            : '10 min extra reserve. No station buffer.'}{' '}
                        These are demo assumptions, not guarantees.
                    </div>
                    <div className="field-grid">
                        <label>
                            Budget (PLN)
                            <input
                                type="text"
                                inputMode="decimal"
                                required
                                value={budget}
                                onChange={(event) =>
                                    setBudget(event.target.value)
                                }
                                aria-describedby="budget-hint"
                            />
                        </label>
                        <label>
                            Walking limit (min)
                            <input
                                type="number"
                                min="0"
                                max="180"
                                step="1"
                                required
                                value={walk}
                                onChange={(event) =>
                                    setWalk(event.target.value)
                                }
                            />
                        </label>
                    </div>
                    <p id="budget-hint" className="field-hint">
                        Zero budget? Free places are included.
                    </p>
                    <label>
                        Your pace
                        <select
                            value={pace}
                            onChange={(event) =>
                                setPace(event.target.value as typeof pace)
                            }
                        >
                            <option value="standard">A comfortable walk</option>
                            <option value="relaxed">Taking it slowly</option>
                        </select>
                    </label>
                    <fieldset>
                        <legend>A little more of…</legend>
                        <div className="interest-options">
                            {(
                                [
                                    ['walk', 'Fresh air'],
                                    ['food', 'Food & coffee'],
                                    ['art', 'Art & culture'],
                                ] as const
                            ).map(([value, label]) => (
                                <label
                                    className={`interest ${interests.includes(value) ? 'active' : ''}`}
                                    key={value}
                                >
                                    <input
                                        type="checkbox"
                                        checked={interests.includes(value)}
                                        onChange={() =>
                                            setInterests(
                                                interests.includes(value)
                                                    ? interests.filter(
                                                          (item) =>
                                                              item !== value,
                                                      )
                                                    : [...interests, value],
                                            )
                                        }
                                    />
                                    <span>{label}</span>
                                </label>
                            ))}
                        </div>
                    </fieldset>
                    <label className="checkbox-label">
                        <input
                            type="checkbox"
                            checked={stepFree}
                            onChange={(event) =>
                                setStepFree(event.target.checked)
                            }
                        />
                        Only verified step-free places and routes
                    </label>
                    {error && (
                        <p role="alert" className="error-message">
                            {error}
                        </p>
                    )}
                    <button
                        className="primary-button"
                        type="submit"
                        disabled={pending}
                    >
                        {pending
                            ? 'Finding what fits…'
                            : 'Find my little adventure'}
                        <span aria-hidden="true">↗</span>
                    </button>
                    {pending && (
                        <button
                            className="text-button"
                            type="button"
                            onClick={invalidate}
                        >
                            Cancel planning
                        </button>
                    )}
                    <p className="submit-note">
                        No sign-up. No live location. Just possibilities.
                    </p>
                </form>
            </section>
            <section
                className="results-panel"
                ref={results}
                tabIndex={-1}
                aria-labelledby="results-title"
                aria-busy={pending}
            >
                <div className="section-heading">
                    <span className="section-number">02</span>
                    <h2 id="results-title">Your time, well spent</h2>
                    {response && (
                        <span className="result-count">
                            {response.result.plans.length} OPTIONS
                        </span>
                    )}
                </div>
                <div aria-live="polite" className="status-line">
                    {pending
                        ? 'Checking visits, walking time and your return…'
                        : response
                          ? `${response.result.plans.length} outings fit your settings.`
                          : 'A few good possibilities, built around your return.'}
                </div>
                {!response && (
                    <div className="empty-state">
                        <div className="clock-art" aria-hidden="true">
                            <span className="clock-orbit orbit-one" />
                            <span className="clock-orbit orbit-two" />
                            <ClockMark />
                            <span className="orbit-label">
                                a little room for more
                            </span>
                        </div>
                        <h3>
                            {pending
                                ? 'A good outing takes a little planning.'
                                : 'What could you do with an hour or two?'}
                        </h3>
                        <p>
                            Tell us what you have in mind. We’ll check the
                            opening hours, cost and time to get back.
                        </p>
                        <div className="empty-pills">
                            <span>1–3 stops</span>
                            <span>Clear costs</span>
                            <span>Room to return</span>
                        </div>
                    </div>
                )}
                {response && response.result.plans.length === 0 && (
                    <div className="empty-state no-plan">
                        <span className="large-symbol" aria-hidden="true">
                            ↶
                        </span>
                        <h3>No outing fits just yet.</h3>
                        <p>
                            {noPlanMessages[response.result.reason ?? ''] ??
                                'Try adjusting your settings. We won’t relax your limits without you.'}
                        </p>
                        <p className="field-hint">
                            Your limits have stayed exactly as you set them.
                        </p>
                    </div>
                )}
                {response &&
                    response.result.plans.map((plan, index) => (
                        <PlanCard
                            key={`${plan.snapshot_id}-${index}`}
                            plan={plan}
                            context={response.context}
                            catalog={demo.catalog}
                            index={index}
                            selected={selected === index}
                            onSelect={() =>
                                setSelected(selected === index ? null : index)
                            }
                        />
                    ))}
            </section>
        </div>
    );
}

function PlanCard({
    plan,
    context,
    catalog,
    index,
    selected,
    onSelect,
}: {
    plan: Plan;
    context: PlanningContext;
    catalog: CityPack;
    index: number;
    selected: boolean;
    onSelect: () => void;
}) {
    const places = new Map(catalog.places.map((place) => [place.id, place]));
    const title = plan.stops
        .map((stop) => places.get(stop.place_id)?.name ?? stop.place_id)
        .join(' + ');
    return (
        <article
            className={`plan-card ${selected ? 'selected' : ''}`}
            aria-labelledby={`plan-title-${index}`}
        >
            <div className="plan-topline">
                <span className="eyebrow">
                    OPTION {String(index + 1).padStart(2, '0')}
                </span>
                <span className="slack-badge">
                    {duration(plan.slack_seconds)} extra slack
                </span>
            </div>
            <h3 id={`plan-title-${index}`}>{title}</h3>
            <div className="plan-metrics">
                <span>
                    <strong>{money(plan.total_cost_minor)}</strong> mandatory
                    cost
                </span>
                <span>
                    <strong>{duration(plan.walk_seconds)}</strong> walking
                </span>
                <span>
                    <strong>{plan.stops.length}</strong> stops
                </span>
            </div>
            <ol className="timeline">
                <li>
                    <span className="timeline-dot" />
                    <time>{time(context.starts_at, context.timezone)}</time>
                    <div>
                        <strong>Step out</strong>
                        <small>{context.return_point_name}</small>
                    </div>
                </li>
                {plan.stops.map((stop) => (
                    <li key={stop.place_id}>
                        <span className="timeline-dot" />
                        <time>{time(stop.starts_at, context.timezone)}</time>
                        <div>
                            <strong>{places.get(stop.place_id)?.name}</strong>
                            <small>
                                Arrive {time(stop.arrival, context.timezone)} ·
                                leave {time(stop.ends_at, context.timezone)}
                            </small>
                            <small>
                                {money(stop.cost_minor)} ·{' '}
                                {duration(
                                    (Date.parse(stop.ends_at) -
                                        Date.parse(stop.starts_at)) /
                                        1000,
                                )}{' '}
                                visit
                            </small>
                        </div>
                    </li>
                ))}
                <li className="return-stop">
                    <span className="timeline-dot" />
                    <time>{time(plan.return_at, context.timezone)}</time>
                    <div>
                        <strong>Back at the entrance</strong>
                        <small>{context.return_point_name}</small>
                    </div>
                </li>
            </ol>
            <div className="return-summary">
                <span>
                    {context.deadline_type === 'departure'
                        ? 'Your entered departure'
                        : 'Your arrival deadline'}
                    <strong>{time(context.deadline, context.timezone)}</strong>
                </span>
                <span>
                    Station buffer
                    <strong>{duration(context.boarding_seconds)}</strong>
                </span>
                <span>
                    Extra reserve
                    <strong>{duration(context.reserve_seconds)}</strong>
                </span>
            </div>
            <details>
                <summary>Timing assumptions & data</summary>
                <p>
                    All times are in {context.timezone}. Planned return must be
                    by {time(context.plan_deadline, context.timezone)}. The
                    entrance deadline before the extra reserve is{' '}
                    {time(context.site_deadline, context.timezone)}.
                </p>
                <p>
                    Walking includes a 15% uncertainty allowance, plus your
                    chosen pace. No live train timetable, queue or weather data
                    is used.
                </p>
                <p>
                    These are fictional sources, not verified real-world
                    information. Fixture valid until{' '}
                    {time(catalog.valid_until, context.timezone)} on 11 June
                    2030.
                </p>
                <ul>
                    {plan.stops.map((stop) => (
                        <li key={stop.place_id}>
                            {places.get(stop.place_id)?.name}:{' '}
                            {stop.evidence_ids.join(', ')}
                        </li>
                    ))}
                </ul>
            </details>
            <button
                className="choose-button"
                type="button"
                aria-pressed={selected}
                onClick={onSelect}
            >
                {selected ? 'Preview selected ✓' : 'Choose this preview'}
                <span aria-hidden="true">→</span>
            </button>
            {selected && (
                <p role="status" className="selection-note">
                    Selected for comparison. This demo does not start a live
                    trip or track your location.
                </p>
            )}
        </article>
    );
}
