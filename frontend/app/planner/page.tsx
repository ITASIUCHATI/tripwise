import PlannerForm from '../../components/PlannerForm';

export default function PlannerPage() {
    return (
        <main className="page">
            <div className="section-head">
                <p className="eyebrow">TRIP PLANNER</p>
                <h1>Plan smarter with TripWise</h1>
                <p>Choose where your trip starts, your destination, trip duration, group size and interests. TripWise uses the route distance to improve the transport estimate, then analyzes risks, best time to visit and places worth seeing.</p>
            </div>
            <PlannerForm />
        </main>
    );
}
