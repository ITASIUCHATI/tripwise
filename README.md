# TripWise

TripWise is an ML-powered travel planning application built with Next.js, NestJS, PostgreSQL, FastAPI and scikit-learn.

## Current planner flow

The user only enters:

- Destination
- Number of days
- Number of people
- Interests

TripWise then generates:

- ML-estimated total budget and per-person budget
- Expected cost range and budget breakdown
- Overall travel-risk score and a list of destination-specific risks
- Best time to visit and the reason
- Places to visit ranked against the user's interests, with descriptions
- A day-by-day suggested itinerary
- An explanation of which component produced each result

Images are intentionally left for the next iteration so the core ML flow stays stable first.

## Architecture

Frontend: Vercel
Backend: Render
ML service: Render
Database: PostgreSQL

## Authentication

TripWise uses JWT authentication. Each account can access only its own saved trips and dashboard statistics.

Demo login:

Email: demo@tripwise.app
Password: TripWise@123

## ML components

Cost prediction uses a Random Forest regression model trained on generated travel scenarios using destination, days, people and interest signals.

Risk prediction uses a Random Forest classification model using destination, duration, group size and interest signals. Destination-specific risk descriptions are supplied from the travel knowledge catalog so the user sees the individual risks rather than only one number.

Place recommendation uses TF-IDF cosine similarity over destination-specific place descriptions and tags against the user's interests.

Best-time guidance and the supporting itinerary are knowledge/rule-based components rather than ML predictions.

The current models are a reproducible prototype. Production accuracy would require real historical travel-cost, incident and tourism data.
