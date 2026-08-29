'use client';

import { FormEvent, useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

import { api, getToken } from '../lib/api';

type TripResult = {
    destination: string;
    days: number;
    people: number;
    interests: string;
    predicted_cost: number;
    per_person_cost: number;
    cost_range: [number, number];
    cost_breakdown: Record<string, number>;
    risk_score: number;
    risk_level: string;
    risks: {
        risk: string;
        severity: string;
        description: string;
    }[];
    best_time: string;
    best_time_note: string;
    places: {
        name: string;
        description: string;
        match_score: number;
        tags: string[];
    }[];
    itinerary: {
        day: number;
        items: string[];
    }[];
    model_explanation: {
        cost: string;
        risk: string;
        places: string;
        best_time: string;
        training_note: string;
    };
};

const initialForm = {
    destination: '',
    days: 5,
    people: 2,
    interests: 'nature,food',
};

function formatMoney(value: number) {
    return `₹${Math.round(value).toLocaleString('en-IN')}`;
}

export default function PlannerForm() {
    const router = useRouter();
    const [form, setForm] = useState(initialForm);
    const [result, setResult] = useState<TripResult | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    useEffect(() => {
        if (!getToken()) {
            router.replace('/login');
        }
    }, [router]);

    async function submit(event: FormEvent) {
        event.preventDefault();
        setLoading(true);
        setError('');
        setResult(null);

        try {
            const data = await api('/recommendations/plan', {
                method: 'POST',
                body: JSON.stringify(form),
            });
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
        setForm((current) => ({ ...current, [field]: value }));
    }

    return (
        <div className="planner-grid planner-grid-wide">
            <form className="card form" onSubmit={submit}>
                <div>
                    <p className="eyebrow">YOUR INPUT</p>
                    <h2 className="form-title">Tell us about the trip</h2>
                    <p className="form-help">
                        No budget or travel style is required. TripWise estimates the budget from your destination, duration, group size and interests.
                    </p>
                </div>

                <label>
                    Destination
                    <input
                        required
                        value={form.destination}
                        onChange={(event) => updateField('destination', event.target.value)}
                        placeholder="Meghalaya"
                    />
                    <small>Try Meghalaya, Manali, Coorg, Goa, Jaipur, Rishikesh, Sikkim or Kerala.</small>
                </label>

                <label>
                    Days
                    <input
                        required
                        type="number"
                        min="1"
                        max="30"
                        value={form.days}
                        onChange={(event) => updateField('days', Number(event.target.value))}
                    />
                </label>

                <label>
                    People
                    <input
                        required
                        type="number"
                        min="1"
                        max="20"
                        value={form.people}
                        onChange={(event) => updateField('people', Number(event.target.value))}
                    />
                </label>

                <label>
                    Interests
                    <input
                        value={form.interests}
                        onChange={(event) => updateField('interests', event.target.value)}
                        placeholder="nature,food,photography"
                    />
                    <small>Comma-separated: nature, adventure, food, culture, peaceful, shopping, beach, photography.</small>
                </label>

                {error && <p className="error">{error}</p>}

                <button className="button" disabled={loading} type="submit">
                    {loading ? 'Analyzing your trip...' : 'Generate Trip Analysis'}
                </button>
            </form>

            {result && (
                <div className="card result">
                    <p className="eyebrow">TRIPWISE ANALYSIS</p>
                    <h2>{result.destination}</h2>
                    <p className="result-subtitle">
                        {result.days} days · {result.people} people · {result.interests}
                    </p>

                    <div className="metric highlight">
                        <span>Estimated total budget</span>
                        <strong>{formatMoney(result.predicted_cost)}</strong>
                    </div>
                    <div className="metric">
                        <span>Estimated per person</span>
                        <strong>{formatMoney(result.per_person_cost)}</strong>
                    </div>
                    <div className="metric">
                        <span>Expected range</span>
                        <strong>{formatMoney(result.cost_range[0])} - {formatMoney(result.cost_range[1])}</strong>
                    </div>

                    <h3>Budget breakdown</h3>
                    <div className="breakdown-grid">
                        {Object.entries(result.cost_breakdown).map(([key, value]) => (
                            <div className="mini-card" key={key}>
                                <span>{key.replace('_', ' ')}</span>
                                <strong>{formatMoney(value)}</strong>
                            </div>
                        ))}
                    </div>

                    <h3>Best time to visit</h3>
                    <div className="info-box">
                        <strong>{result.best_time}</strong>
                        <p>{result.best_time_note}</p>
                    </div>

                    <h3>Travel risks</h3>
                    <div className="risk-summary">
                        <strong>{result.risk_level} risk</strong>
                        <span>{result.risk_score}% overall risk pressure</span>
                    </div>
                    <div className="risk-list">
                        {result.risks.map((risk) => (
                            <div className="risk-item" key={risk.risk}>
                                <div className="risk-heading">
                                    <strong>{risk.risk}</strong>
                                    <span>{risk.severity}</span>
                                </div>
                                <p>{risk.description}</p>
                            </div>
                        ))}
                    </div>

                    <h3>Best places for your interests</h3>
                    <div className="place-list">
                        {result.places.map((place) => (
                            <article className="place-card" key={place.name}>
                                <div className="place-heading">
                                    <h4>{place.name}</h4>
                                    <span>{place.match_score}% match</span>
                                </div>
                                <p>{place.description}</p>
                            </article>
                        ))}
                    </div>

                    <h3>Suggested itinerary</h3>
                    {result.itinerary.map((day) => (
                        <div className="day" key={day.day}>
                            <strong>Day {day.day}</strong>
                            <span>{day.items.join(' · ')}</span>
                        </div>
                    ))}

                    <h3>How the system works</h3>
                    <div className="model-details">
                        <p><strong>Budget:</strong> {result.model_explanation.cost}</p>
                        <p><strong>Risk:</strong> {result.model_explanation.risk}</p>
                        <p><strong>Places:</strong> {result.model_explanation.places}</p>
                        <p><strong>Best time:</strong> {result.model_explanation.best_time}</p>
                        <p><strong>Prototype note:</strong> {result.model_explanation.training_note}</p>
                    </div>
                </div>
            )}
        </div>
    );
}
