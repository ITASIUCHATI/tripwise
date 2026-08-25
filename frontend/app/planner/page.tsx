import PlannerForm from '../../components/PlannerForm';

export default function PlannerPage() {
    return (
        <main className="page">
            <div className="section-head">
                <p className="eyebrow">
                    TRIP PLANNER
                </p>

                <h1>Build your trip</h1>

                <p>
                    Give TripWise your preferences
                    and let the ML service score
                    destinations, cost, risk,
                    activities, and itinerary.
                </p>
            </div>

            <PlannerForm />
        </main>
    );
}