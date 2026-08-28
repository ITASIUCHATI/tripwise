'use client';

import {
    useEffect,
    useState,
} from 'react';

import TripCard from '../../components/TripCard';
import { api, getToken } from '../../lib/api';
import { useRouter } from 'next/navigation';

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
    const router = useRouter();
    const [trips, setTrips] = useState<Trip[]>([]);
    const [error, setError] = useState('');

    useEffect(() => {
        if (!getToken()) {
            router.replace('/login');
            return;
        }

        api('/trips')
            .then(setTrips)
            .catch(() =>
                setError(
                    'Unable to load saved trips.',
                ),
            );
    }, [router]);

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