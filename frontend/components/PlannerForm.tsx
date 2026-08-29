'use client';

import { FormEvent, useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

import { api, getToken } from '../lib/api';

type TripResult = {
    destination: string;
    destination_display?: string;
    destination_input?: string;
    destination_corrected?: boolean;
    correction_confidence?: number;
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
        image?: string | null;
        url?: string | null;
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
    const [destinationSuggestion, setDestinationSuggestion] = useState('');
    const [suggestionLoading, setSuggestionLoading] = useState(false);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    useEffect(() => {
        if (!getToken()) {
            router.replace('/login');
        }
    }, [router]);

    async function checkDestination() {
        const destination = form.destination.trim();
        if (destination.length < 2) {
            setDestinationSuggestion('');
            return;
        }

        setSuggestionLoading(true);

        try {
            const data = await api('/recommendations/suggest-destination', {
                method: 'POST',
                body: JSON.stringify({ destination }),
            });

            setDestinationSuggestion(data.suggestion || '');
        } catch {
            setDestinationSuggestion('');
        } finally {
            setSuggestionLoading(false);
        }
    }

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
            setDestinationSuggestion('');
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
        if (field === 'destination') {
            setDestinationSuggestion('');
        }
    }

    function useSuggestion() {
        if (!destinationSuggestion) {
            return;
        }

        updateField('destination', destinationSuggestion);
        setDestinationSuggestion('');
    }

    return (
        <div className="planner-grid planner-grid-wide">
            <form className="card form" onSubmit={submit}>
                <div>
                    <p className="eyebrow">YOUR INPUT</p>

                    <h2 className="form-title">
                        Tell us about the trip
                    </h2>

                    <p className="form-help">
                        Enter a destination, trip duration, group size and interests. TripWise retrieves destination information dynamically instead of limiting you to a fixed destination list.
                    </p>
                </div>

                <label className="destination-field">
                    Destination

                    <input
                        required
                        value={form.destination}
                        onChange={(event) =>
                            updateField(
                                'destination',
                                event.target.value,
                            )
                        }
                        onBlur={checkDestination}
                        placeholder="Meghalaya, Paris, Tokyo..."
                    />

                    {suggestionLoading && (
                        <small className="suggestion-status">
                            Checking destination...
                        </small>
                    )}

                    {destinationSuggestion && (
                        <button
                            type="button"
                            className="destination-suggestion"
                            onClick={useSuggestion}
                        >
                            <span>Did you mean</span>
                            <strong>{destinationSuggestion}</strong>
                            <span>?</span>
                        </button>
                    )}

                    <small>
                        You can enter a city, region or country. TripWise will resolve the destination dynamically.
                    </small>
                </label>

                <label>
                    Days

                    <input
                        required
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
                    People

                    <input
                        required
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
                        placeholder="nature,food,photography"
                    />

                    <small>
                        Comma-separated: nature, adventure, food, culture, peaceful, shopping, beach, photography.
                    </small>
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
                        ? 'Analyzing destination...'
                        : 'Generate Trip Analysis'}
                </button>
            </form>

            {result && (
                <div className="card result">
                    <p className="eyebrow">
                        TRIPWISE ANALYSIS
                    </p>

                    {result.destination_corrected && (
                        <div className="correction-notice">
                            We interpreted “{result.destination_input}” as <strong>{result.destination}</strong>.
                        </div>
                    )}

                    <div className="analysis-header">
                        <h2>{result.destination}</h2>
                        {result.destination_display &&
                            result.destination_display !== result.destination && (
                                <p className="result-subtitle">
                                    {result.destination_display}
                                </p>
                            )}
                    </div>

                    <p className="result-subtitle">
                        {result.days} days · {result.people}{' '}
                        people · {result.interests}
                    </p>

                    <div className="metric highlight">
                        <span>
                            Estimated total budget
                        </span>

                        <strong>
                            {formatMoney(
                                result.predicted_cost,
                            )}
                        </strong>
                    </div>

                    <div className="metric">
                        <span>
                            Estimated per person
                        </span>

                        <strong>
                            {formatMoney(
                                result.per_person_cost,
                            )}
                        </strong>
                    </div>

                    <div className="metric">
                        <span>Expected range</span>

                        <strong>
                            {formatMoney(
                                result.cost_range[0],
                            )}{' '}
                            -{' '}
                            {formatMoney(
                                result.cost_range[1],
                            )}
                        </strong>
                    </div>

                    <h3>Budget breakdown</h3>

                    <div className="breakdown-grid">
                        {Object.entries(
                            result.cost_breakdown,
                        ).map(([key, value]) => (
                            <div
                                className="mini-card"
                                key={key}
                            >
                                <span>
                                    {key.replace('_', ' ')}
                                </span>

                                <strong>
                                    {formatMoney(value)}
                                </strong>
                            </div>
                        ))}
                    </div>

                    <h3>Best time to visit</h3>

                    <div className="info-box">
                        <strong>
                            {result.best_time}
                        </strong>

                        <p>
                            {result.best_time_note}
                        </p>
                    </div>

                    <h3>Travel risks</h3>

                    <div className="risk-summary">
                        <strong>
                            {result.risk_level} risk
                        </strong>

                        <span>
                            {result.risk_score}% overall
                            risk pressure
                        </span>
                    </div>

                    <div className="risk-list">
                        {result.risks.map((risk) => (
                            <div
                                className="risk-item"
                                key={risk.risk}
                            >
                                <div className="risk-heading">
                                    <strong>
                                        {risk.risk}
                                    </strong>

                                    <span>
                                        {risk.severity}
                                    </span>
                                </div>

                                <p>
                                    {risk.description}
                                </p>
                            </div>
                        ))}
                    </div>

                    <h3>
                        Best places for your interests
                    </h3>

                    <div className="place-list">
                        {result.places.map((place) => (
                            <article
                                className="place-card"
                                key={place.name}
                            >
                                {place.image && (
                                    <img
                                        className="place-image"
                                        src={place.image}
                                        alt={place.name}
                                        loading="lazy"
                                    />
                                )}

                                <div className="place-heading">
                                    <h4>
                                        {place.name}
                                    </h4>

                                    <span>
                                        {place.match_score}%
                                        match
                                    </span>
                                </div>

                                <p>
                                    {place.description}
                                </p>
                            </article>
                        ))}
                    </div>

                    <h3>Suggested itinerary</h3>

                    <div className="itinerary">
                        {result.itinerary.map((day) => (
                            <div
                                className="day"
                                key={day.day}
                            >
                                <strong>
                                    Day {day.day}
                                </strong>

                                <div>
                                    {day.items.map((item) => (
                                        <span key={item}>
                                            {item}
                                        </span>
                                    ))}
                                </div>
                            </div>
                        ))}
                    </div>

                    <h3>How the system works</h3>

                    <div className="model-details">
                        <p>
                            <strong>
                                Budget:
                            </strong>{' '}
                            {result.model_explanation.cost}
                        </p>

                        <p>
                            <strong>
                                Risk:
                            </strong>{' '}
                            {result.model_explanation.risk}
                        </p>

                        <p>
                            <strong>
                                Places:
                            </strong>{' '}
                            {result.model_explanation.places}
                        </p>

                        <p>
                            <strong>
                                Best time:
                            </strong>{' '}
                            {result.model_explanation.best_time}
                        </p>

                        <p>
                            <strong>
                                Prototype note:
                            </strong>{' '}
                            {result.model_explanation.training_note}
                        </p>
                    </div>
                </div>
            )}
        </div>
    );
}
