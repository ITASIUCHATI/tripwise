from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from predict import plan_trip
from recommend import resolve_destination

app = FastAPI(
    title="TripWise ML Service",
    version="3.0.0",
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
        "version": "3.0.0",
    }


@app.post("/suggest-destination")
def destination_suggestion(request: DestinationSuggestionRequest):
    try:
        resolved = resolve_destination(request.destination)
        if not resolved.get("corrected"):
            return {"suggestion": None}
        return {
            "suggestion": resolved["name"],
            "confidence": resolved.get("correction_confidence", 0),
        }
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(
            status_code=502,
            detail="Destination intelligence service is temporarily unavailable.",
        ) from error


@app.post("/plan")
def plan(request: TripRequest):
    try:
        return plan_trip(request.model_dump())
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(
            status_code=502,
            detail="Unable to retrieve live destination information right now. Please try again.",
        ) from error
