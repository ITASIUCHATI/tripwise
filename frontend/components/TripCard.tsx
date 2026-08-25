'use client';

type Trip = {
    id: number;
    destination: string;
    days: number;
    budget: number;
    people: number;
    interests: string;
    style: string;
};

type TripCardProps = {
    trip: Trip;
};

export default function TripCard({
    trip,
}: TripCardProps) {
    return (
        <article className="card">
            <p className="eyebrow">
                SAVED TRIP
            </p>

            <h2>{trip.destination}</h2>

            <div className="trip-details">
                <p>
                    <strong>Duration:</strong>{' '}
                    {trip.days} days
                </p>

                <p>
                    <strong>People:</strong>{' '}
                    {trip.people}
                </p>

                <p>
                    <strong>Budget:</strong>{' '}
                    ₹
                    {Math.round(
                        trip.budget,
                    ).toLocaleString('en-IN')}
                </p>

                <p>
                    <strong>Interests:</strong>{' '}
                    {trip.interests}
                </p>

                <p>
                    <strong>Travel style:</strong>{' '}
                    {trip.style}
                </p>
            </div>
        </article>
    );
}