from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from predict import plan_trip
from recommend import suggest_destination


app = FastAPI(
    title="TripWise ML Service",
    version="2.1.0",
)


class TripRequest(BaseModel):
    destination: str = Field(min_length=1)
    days: int = Field(default=5, ge=1, le=30)
    people: int = Field(default=2, ge=1, le=20)
    interests: str = "nature,food"


class DestinationSuggestionRequest(BaseModel):
    destination: str = Field(min_length=1)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "TripWise ML",
    }


@app.post("/suggest-destination")
def destination_suggestion(
    request: DestinationSuggestionRequest,
):
    try:
        suggestion = suggest_destination(
            request.destination,
        )

        return {
            "suggestion": suggestion,
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail="Unable to generate destination suggestion.",
        ) from error


@app.post("/plan")
def plan(request: TripRequest):
    try:
        return plan_trip(request.model_dump())

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error