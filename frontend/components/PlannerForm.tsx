'use client';

import { FormEvent, useState } from 'react';

import { api } from '../lib/api';

type TripResult = {
    destination: string;
    match_score: number;
    predicted_cost: number;
    cost_range: [number, number];
    risk_score: number;
    price_prediction: number;
    weather_suitability: number;
    activity_match: number;
    overall_score: number;
    activities: string[];
    itinerary: {
        day: number;
        items: string[];
    }[];
    alternatives: {
        destination: string;
        score: number;
    }[];
};

const initialForm = {
    destination: '',
    days: 5,
    budget: 25000,
    people: 2,
    interests: 'nature,food',
    style: 'balanced',
};

export default function PlannerForm() {
    const [form, setForm] = useState(initialForm);
    const [result, setResult] = useState<TripResult | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    async function submit(event: FormEvent) {
        event.preventDefault();

        setLoading(true);
        setError('');

        try {
            const data = await api(
                '/recommendations/plan',
                {
                    method: 'POST',
                    body: JSON.stringify(form),
                },
            );

            setResult(data);
        } catch (requestError) {
            setError(
                requestError instanceof Error
                    ? requestError.message
                    : 'Unable to analyze the trip.',
            );
        } finally {
            setLoading(false);
        }
    }

    function updateField(
        field: keyof typeof form,
        value: string | number,
    ) {
        setForm((current) => ({
            ...current,
            [field]: value,
        }));
    }

    return (
        <div className="planner-grid">
            <form
                className="card form"
                onSubmit={submit}
            >
                <label>
                    Destination
                    <input
                        value={form.destination}
                        onChange={(event) =>
                            updateField(
                                'destination',
                                event.target.value,
                            )
                        }
                        placeholder="Meghalaya"
                    />
                </label>

                <label>
                    Days
                    <input
                        type="number"
                        min="1"
                        max="30"
                        value={form.days}
                        onChange={(event) =>
                            updateField(
                                'days',
                                Number(event.target.value),
                            )
                        }
                    />
                </label>

                <label>
                    Budget in INR
                    <input
                        type="number"
                        min="1000"
                        value={form.budget}
                        onChange={(event) =>
                            updateField(
                                'budget',
                                Number(event.target.value),
                            )
                        }
                    />
                </label>

                <label>
                    People
                    <input
                        type="number"
                        min="1"
                        max="20"
                        value={form.people}
                        onChange={(event) =>
                            updateField(
                                'people',
                                Number(event.target.value),
                            )
                        }
                    />
                </label>

                <label>
                    Interests
                    <input
                        value={form.interests}
                        onChange={(event) =>
                            updateField(
                                'interests',
                                event.target.value,
                            )
                        }
                        placeholder="nature,food"
                    />
                </label>

                <label>
                    Travel style
                    <select
                        value={form.style}
                        onChange={(event) =>
                            updateField(
                                'style',
                                event.target.value,
                            )
                        }
                    >
                        <option value="budget">
                            Budget
                        </option>
                        <option value="balanced">
                            Balanced
                        </option>
                        <option value="comfort">
                            Comfort
                        </option>
                    </select>
                </label>

                {error && (
                    <p className="error">
                        {error}
                    </p>
                )}

                <button
                    className="button"
                    disabled={loading}
                    type="submit"
                >
                    {loading
                        ? 'Analyzing...'
                        : 'Analyze trip'}
                </button>
            </form>

            {result && (
                <div className="card result">
                    <p className="eyebrow">
                        ML TRIP ANALYSIS
                    </p>

                    <h2>{result.destination}</h2>

                    <div className="metric">
                        <span>Overall score</span>
                        <strong>
                            {result.overall_score}%
                        </strong>
                    </div>

                    <div className="metric">
                        <span>Destination match</span>
                        <strong>
                            {result.match_score}%
                        </strong>
                    </div>

                    <div className="metric">
                        <span>Estimated cost</span>
                        <strong>
                            ₹
                            {Math.round(
                                result.predicted_cost,
                            ).toLocaleString('en-IN')}
                        </strong>
                    </div>

                    <div className="metric">
                        <span>Expected range</span>
                        <strong>
                            ₹
                            {result.cost_range[0].toLocaleString(
                                'en-IN',
                            )}
                            {' - '}
                            ₹
                            {result.cost_range[1].toLocaleString(
                                'en-IN',
                            )}
                        </strong>
                    </div>

                    <div className="metric">
                        <span>Trip risk</span>
                        <strong>
                            {result.risk_score}%
                        </strong>
                    </div>

                    <div className="metric">
                        <span>Weather suitability</span>
                        <strong>
                            {result.weather_suitability}%
                        </strong>
                    </div>

                    <div className="metric">
                        <span>Activity match</span>
                        <strong>
                            {result.activity_match}%
                        </strong>
                    </div>

                    <h3>
                        Recommended activities
                    </h3>

                    <ul>
                        {result.activities.map(
                            (activity) => (
                                <li key={activity}>
                                    {activity}
                                </li>
                            ),
                        )}
                    </ul>

                    <h3>Optimized itinerary</h3>

                    {result.itinerary.map(
                        (day) => (
                            <div
                                className="day"
                                key={day.day}
                            >
                                <strong>
                                    Day {day.day}
                                </strong>

                                <span>
                                    {day.items.join(
                                        ' · ',
                                    )}
                                </span>
                            </div>
                        ),
                    )}

                    <h3>
                        Alternative destinations
                    </h3>

                    <div className="alternatives">
                        {result.alternatives
                            .slice(1)
                            .map((alternative) => (
                                <div
                                    className="metric"
                                    key={
                                        alternative.destination
                                    }
                                >
                                    <span>
                                        {
                                            alternative.destination
                                        }
                                    </span>

                                    <strong>
                                        {
                                            alternative.score
                                        }
                                        %
                                    </strong>
                                </div>
                            ))}
                    </div>
                </div>
            )}
        </div>
    );
}