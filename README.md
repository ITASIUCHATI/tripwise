# TripWise

TripWise is a full-stack travel intelligence platform using machine learning for destination and activity recommendation, trip cost prediction, price prediction, risk scoring, weather suitability, and itinerary optimization. An LLM layer turns structured predictions into natural-language travel advice.

## Stack

Frontend: Next.js, React, TypeScript
Backend: NestJS, Prisma, PostgreSQL
ML: Python, FastAPI, scikit-learn
AI: OpenAI API

## Structure

- frontend: web application
- backend: API and database layer
- ml: prediction and recommendation service

## Local setup

Create a PostgreSQL database named `tripwise`.

Copy `.env.example` into `.env` and update the values.

Start the ML service from `ml` with a Python virtual environment and install `requirements.txt`.

Start the backend after installing dependencies and generating Prisma Client.

Start the frontend after installing dependencies.

The frontend uses `NEXT_PUBLIC_API_URL` to reach the backend.
