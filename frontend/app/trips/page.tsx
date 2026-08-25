'use client';

import {
    useEffect,
    useState,
} from 'react';

import TripCard from '../../components/TripCard';
import { api } from '../../lib/api';

type Trip = {
    id: number;
    destination: string;
    days: number;
    budget: number;
    people: number;
    interests: string;
    style: string;
};

export default function TripsPage() {
    const [trips, setTrips] = useState<Trip[]>([]);
    const [error, setError] = useState('');

    useEffect(() => {
        api('/trips')
            .then(setTrips)
            .catch(() =>
                setError(
                    'Unable to load saved trips.',
                ),
            );
    }, []);

    return (
        <main className="page">
            <div className="section-head">
                <p className="eyebrow">
                    SAVED TRIPS
                </p>

                <h1>Your trips</h1>

                <p>
                    View the travel plans you have
                    created with TripWise.
                </p>
            </div>

            {error && (
                <div className="card error">
                    {error}
                </div>
            )}

            <div className="grid">
                {trips.map((trip) => (
                    <TripCard
                        key={trip.id}
                        trip={trip}
                    />
                ))}

                {!trips.length && !error && (
                    <div className="card">
                        <p>
                            No saved trips yet.
                            Create one from the
                            planner.
                        </p>
                    </div>
                )}
            </div>
        </main>
    );
}