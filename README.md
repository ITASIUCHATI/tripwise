# TripWise

TripWise is an ML-powered travel planning application built with Next.js, NestJS, PostgreSQL, FastAPI, and scikit-learn.

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

Users can also create their own account from the login page.

## ML Components

Cost prediction uses a Random Forest regression model using destination, trip duration, number of travelers, and travel style.

Risk prediction uses a Random Forest classification model using duration, group size, travel style, and the ratio between the user's budget and predicted trip cost.

Destination recommendation uses TF-IDF cosine similarity across destination profiles and the user's interests, style, and destination preference.

Weather suitability and itinerary optimization are supporting rule-based components rather than ML predictions.

The current models use generated travel scenarios for a reproducible prototype. Production accuracy would require retraining with real historical travel data.
