import Link from 'next/link';

export default function Home() {
    return (
        <main className="hero">
            <div className="hero-card">
                <p className="eyebrow">TRAVEL INTELLIGENCE</p>
                <h1>Plan smarter with TripWise.</h1>
                <p>ML-powered recommendations, route-aware cost prediction, risk analysis, best-time guidance and itinerary planning in one travel workspace.</p>
                <div className="hero-actions">
                    <Link className="button" href="/login?mode=login">Sign in</Link>
                    <Link className="secondary-button" href="/login?mode=register">Create account</Link>
                </div>
            </div>
        </main>
    );
}
