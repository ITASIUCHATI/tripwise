# TripWise

TripWise is an ML-powered travel planning application built with Next.js, NestJS, PostgreSQL, FastAPI and scikit-learn.

## Current planning flow

The planner asks only for:

- Destination
- Number of days
- Number of people
- Interests

The application does not depend on a fixed destination list.

## Dynamic destination intelligence

When a user submits a destination, the ML service resolves it dynamically using external destination data sources. This allows inputs such as:

- Meghalaya
- Sikkim
- Paris
- Tokyo
- Darjeeling
- Kyoto
- Any other destination that can be resolved by the live sources

A misspelled destination can also produce a machine-assisted correction suggestion. The frontend does not maintain a hard-coded destination list.

## What the ML service returns

For a resolved destination, TripWise generates:

- Estimated total budget
- Per-person budget
- Budget range
- Budget breakdown
- Overall risk score and potential travel risks
- Best time to visit using historical weather patterns
- Places discovered dynamically from Wikimedia and ranked against interests using TF-IDF similarity
- Place descriptions and available images
- A day-by-day itinerary

## ML architecture

The system uses a hybrid approach:

1. Destination resolution is performed dynamically from live geocoding and Wikimedia search data.
2. Destination summaries and attraction pages are retrieved at request time.
3. TF-IDF cosine similarity ranks live attraction information against user interests.
4. A Random Forest regressor estimates a prototype trip budget from trip and climate features.
5. A Random Forest classifier estimates overall risk pressure from trip and climate features.
6. Historical weather data is used to calculate a data-driven recommended travel window.
7. The itinerary optimizer converts ranked places into a day-by-day plan.

The budget and risk models are reproducible prototype models trained on generated scenarios. They are not live hotel, flight or booking prices.

## External data sources

The ML service uses public APIs from Open-Meteo for geocoding and historical weather information and Wikimedia for destination and attraction information.

No destination needs to be manually added to `ml/recommend.py`.

## Local development

### Backend

```text
cd backend
npm install
npx prisma generate
npm run start:dev
```

### ML service

```text
cd ml
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```

### Frontend

```text
cd frontend
npm install
npm run dev
```

## Environment variables

Backend:

```text
DATABASE_URL=
JWT_SECRET=
ML_SERVICE_URL=http://localhost:8000
OPENAI_API_KEY=
```

Frontend:

```text
NEXT_PUBLIC_API_URL=http://localhost:3001
```

For production, set `ML_SERVICE_URL` on the NestJS service to the public URL of the deployed FastAPI ML service and set `NEXT_PUBLIC_API_URL` on the Vercel frontend to the public NestJS backend URL.
