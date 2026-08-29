"use client";

import { FormEvent, useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

import { api, getToken } from '../lib/api';

type LocationOption = {
    name: string;
    admin1?: string;
    country?: string;
    country_code?: string;
    latitude: number;
    longitude: number;
    timezone?: string;
    display_name: string;
    correction_score?: number;
};

type TripResult = {
    origin: string;
    origin_display?: string;
    destination: string;
    destination_display?: string;
    destination_input?: string;
    origin_corrected?: boolean;
    destination_corrected?: boolean;
    correction_confidence?: number;
    distance_km: number;
    days: number;
    people: number;
    interests: string;
    predicted_cost: number;
    per_person_cost: number;
    cost_range: [number, number];
    cost_breakdown: Record<string, number>;
    risk_score: number;
    risk_level: string;
    risks: { risk: string; severity: string; description: string }[];
    best_time: string;
    best_time_note: string;
    destination_image?: string | null;
    destination_url?: string | null;
    places: { name: string; description: string; match_score: number; tags: string[]; url?: string | null }[];
    itinerary: { day: number; items: string[] }[];
    model_explanation: { cost: string; risk: string; places: string; best_time: string; training_note: string };
};

const initialForm = {
    origin: '',
    destination: '',
    days: 5,
    people: 2,
    interests: 'nature,food',
};

function formatMoney(value: number) {
    return `₹${Math.round(value).toLocaleString('en-IN')}`;
}

function optionLabel(option: LocationOption) {
    return option.display_name || [option.name, option.admin1, option.country].filter(Boolean).join(', ');
}

export default function PlannerForm() {
    const router = useRouter();
    const [form, setForm] = useState(initialForm);
    const [result, setResult] = useState<TripResult | null>(null);
    const [originOptions, setOriginOptions] = useState<LocationOption[]>([]);
    const [destinationOptions, setDestinationOptions] = useState<LocationOption[]>([]);
    const [originSelection, setOriginSelection] = useState<LocationOption | null>(null);
    const [destinationSelection, setDestinationSelection] = useState<LocationOption | null>(null);
    const [searchingOrigin, setSearchingOrigin] = useState(false);
    const [searchingDestination, setSearchingDestination] = useState(false);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    useEffect(() => {
        if (!getToken()) {
            router.replace('/login');
        }
    }, [router]);

    useEffect(() => {
        const value = form.origin.trim();
        if (value.length < 2 || originSelection?.display_name === value) {
            setOriginOptions([]);
            return;
        }

        const timer = window.setTimeout(async () => {
            setSearchingOrigin(true);
            try {
                const data = await api('/recommendations/destination-options', {
                    method: 'POST',
                    body: JSON.stringify({ destination: value }),
                });
                const options = data.options || [];
                setOriginOptions(options);
                if (options.length === 1 && options[0].name.toLowerCase() === value.toLowerCase()) {
                    setOriginSelection(options[0]);
                }
            } catch {
                setOriginOptions([]);
            } finally {
                setSearchingOrigin(false);
            }
        }, 500);

        return () => window.clearTimeout(timer);
    }, [form.origin, originSelection?.display_name]);

    useEffect(() => {
        const value = form.destination.trim();
        if (value.length < 2 || destinationSelection?.display_name === value) {
            setDestinationOptions([]);
            return;
        }

        const timer = window.setTimeout(async () => {
            setSearchingDestination(true);
            try {
                const data = await api('/recommendations/destination-options', {
                    method: 'POST',
                    body: JSON.stringify({ destination: value }),
                });
                const options = data.options || [];
                setDestinationOptions(options);
                if (options.length === 1 && options[0].name.toLowerCase() === value.toLowerCase()) {
                    setDestinationSelection(options[0]);
                }
            } catch {
                setDestinationOptions([]);
            } finally {
                setSearchingDestination(false);
            }
        }, 500);

        return () => window.clearTimeout(timer);
    }, [form.destination, destinationSelection?.display_name]);

    function updateField(field: keyof typeof form, value: string | number) {
        setForm((current) => ({ ...current, [field]: value }));
        setError('');
        if (field === 'origin') {
            setOriginSelection(null);
            setOriginOptions([]);
        }
        if (field === 'destination') {
            setDestinationSelection(null);
            setDestinationOptions([]);
        }
    }

    function chooseOrigin(option: LocationOption) {
        setOriginSelection(option);
        setForm((current) => ({ ...current, origin: optionLabel(option) }));
        setOriginOptions([]);
    }

    function chooseDestination(option: LocationOption) {
        setDestinationSelection(option);
        setForm((current) => ({ ...current, destination: optionLabel(option) }));
        setDestinationOptions([]);
    }

    async function submit(event: FormEvent) {
        event.preventDefault();
        setLoading(true);
        setError('');
        setResult(null);

        if (!originSelection && originOptions.length > 1) {
            setLoading(false);
            setError('Please choose your starting location from the suggestions.');
            return;
        }

        if (!destinationSelection && destinationOptions.length > 1) {
            setLoading(false);
            setError('Please choose the destination from the suggestions.');
            return;
        }

        try {
            const data = await api('/recommendations/plan', {
                method: 'POST',
                body: JSON.stringify({
                    ...form,
                    origin_selection: originSelection,
                    destination_selection: destinationSelection,
                }),
            });
            setResult(data);
            setOriginOptions([]);
            setDestinationOptions([]);
        } catch (requestError) {
            setError(requestError instanceof Error ? requestError.message : 'Unable to analyze the trip.');
        } finally {
            setLoading(false);
        }
    }

    return (
        <div className="planner-grid planner-grid-wide">
            <form className="card form" onSubmit={submit}>
                <div>
                    <p className="eyebrow">YOUR INPUT</p>
                    <h2 className="form-title">Tell us about the trip</h2>
                    <p className="form-help">
                        Choose your starting point and destination. TripWise uses both locations to estimate travel distance and make the transport part of the budget more realistic.
                    </p>
                </div>

                <label className="destination-field">
                    Starting point
                    <input
                        required
                        value={form.origin}
                        onChange={(event) => updateField('origin', event.target.value)}
                        placeholder="Bhubaneswar, Delhi, Mumbai..."
                    />
                    {searchingOrigin && <small className="suggestion-status">Finding locations...</small>}
                    {originOptions.length > 1 && (
                        <div className="location-popup">
                            <strong>Choose your starting location</strong>
                            {originOptions.map((option, index) => (
                                <button type="button" className="location-option" key={`${option.display_name}-${index}`} onClick={() => chooseOrigin(option)}>
                                    <span>{option.name}</span>
                                    <small>{optionLabel(option)}</small>
                                </button>
                            ))}
                        </div>
                    )}
                    {originOptions.length === 1 && !originSelection && (
                        <button type="button" className="destination-suggestion" onClick={() => chooseOrigin(originOptions[0])}>
                            <span>Use</span>
                            <strong>{optionLabel(originOptions[0])}</strong>
                        </button>
                    )}
                    <small>Start location affects the estimated transport cost.</small>
                </label>

                <label className="destination-field">
                    Destination
                    <input
                        required
                        value={form.destination}
                        onChange={(event) => updateField('destination', event.target.value)}
                        placeholder="Meghalaya, Paris, Tokyo..."
                    />
                    {searchingDestination && <small className="suggestion-status">Finding locations...</small>}
                    {destinationOptions.length > 1 && (
                        <div className="location-popup">
                            <strong>Choose the correct destination</strong>
                            {destinationOptions.map((option, index) => (
                                <button type="button" className="location-option" key={`${option.display_name}-${index}`} onClick={() => chooseDestination(option)}>
                                    <span>{option.name}</span>
                                    <small>{optionLabel(option)}</small>
                                </button>
                            ))}
                        </div>
                    )}
                    {destinationOptions.length === 1 && !destinationSelection && (
                        <button type="button" className="destination-suggestion" onClick={() => chooseDestination(destinationOptions[0])}>
                            <span>Did you mean</span>
                            <strong>{optionLabel(destinationOptions[0])}</strong>
                            <span>?</span>
                        </button>
                    )}
                    <small>TripWise checks the destination live and can suggest a corrected spelling.</small>
                </label>

                <label>
                    Days
                    <input required type="number" min="1" max="30" value={form.days} onChange={(event) => updateField('days', Number(event.target.value))} />
                </label>

                <label>
                    People
                    <input required type="number" min="1" max="20" value={form.people} onChange={(event) => updateField('people', Number(event.target.value))} />
                </label>

                <label>
                    Interests
                    <input value={form.interests} onChange={(event) => updateField('interests', event.target.value)} placeholder="nature,food,photography" />
                    <small>Comma-separated: nature, adventure, food, culture, peaceful, shopping, beach, photography.</small>
                </label>

                {error && <p className="error">{error}</p>}

                <button className="button" disabled={loading} type="submit">
                    {loading ? 'Analyzing destination...' : 'Generate Trip Analysis'}
                </button>
            </form>

            {result && (
                <div className="card result">
                    <p className="eyebrow">TRIPWISE ANALYSIS</p>

                    {(result.origin_corrected || result.destination_corrected) && (
                        <div className="correction-notice">
                            {result.origin_corrected && <>Starting point: <strong>{result.origin_display || result.origin}</strong>. </>}
                            {result.destination_corrected && <>Destination: <strong>{result.destination_display || result.destination}</strong>.</>}
                        </div>
                    )}

                    {result.destination_image && (
                        <img className="destination-hero-image" src={result.destination_image} alt={result.destination_display || result.destination} />
                    )}

                    <div className="analysis-header">
                        <h2>{result.destination}</h2>
                        <p className="result-subtitle">From {result.origin_display || result.origin}</p>
                        {result.destination_display && result.destination_display !== result.destination && <p className="result-subtitle">{result.destination_display}</p>}
                    </div>

                    <p className="result-subtitle">{result.days} days · {result.people} people · {result.interests}</p>

                    <div className="metric">
                        <span>Estimated travel distance</span>
                        <strong>{result.distance_km.toLocaleString('en-IN')} km</strong>
                    </div>
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
                                <div className="risk-heading"><strong>{risk.risk}</strong><span>{risk.severity}</span></div>
                                <p>{risk.description}</p>
                            </div>
                        ))}
                    </div>

                    <h3>Best places for your interests</h3>
                    <div className="place-list">
                        {result.places.map((place) => (
                            <article className="place-card" key={place.name}>
                                <div className="place-heading"><h4>{place.name}</h4><span>{place.match_score}% match</span></div>
                                <p>{place.description}</p>
                            </article>
                        ))}
                    </div>

                    <h3>Suggested itinerary</h3>
                    <div className="itinerary">
                        {result.itinerary.map((day) => (
                            <div className="day" key={day.day}>
                                <strong>Day {day.day}</strong>
                                <div>{day.items.map((item) => <span key={item}>{item}</span>)}</div>
                            </div>
                        ))}
                    </div>

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
