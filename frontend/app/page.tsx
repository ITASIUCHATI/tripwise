import Link from 'next/link';

export default function Home() {
    return (
        <main className="hero">
            <div className="hero-card">
                <p className="eyebrow">
                    TRAVEL INTELLIGENCE
                </p>

                <h1>
                    Plan smarter with TripWise.
                </h1>

                <p>
                    ML-powered recommendations,
                    cost prediction, risk analysis,
                    and itinerary optimization in
                    one travel workspace.
                </p>

                <Link
                    className="button"
                    href="/login"
                >
                    Plan a trip
                </Link>
            </div>
        </main>
    );
}