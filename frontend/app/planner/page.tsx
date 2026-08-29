import PlannerForm from '../../components/PlannerForm';

export default function PlannerPage() {
    return (
        <main className="page">
            <div className="section-head">
                <p className="eyebrow">TRIP PLANNER</p>
                <h1>Plan smarter with TripWise</h1>
                <p>Enter only your destination, trip duration, group size and interests. TripWise estimates your budget, identifies travel risks, finds the best time to visit and ranks places worth seeing.</p>
            </div>
            <PlannerForm />
        </main>
    );
}
