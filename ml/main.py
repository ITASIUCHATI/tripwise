from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from predict import plan_trip
from recommend import resolve_destination, search_destination_options

app = FastAPI(title="TripWise ML Service", version="4.0.0")


class TripRequest(BaseModel):
    origin: str = Field(min_length=1)
    destination: str = Field(min_length=1)
    days: int = Field(default=5, ge=1, le=30)
    people: int = Field(default=2, ge=1, le=20)
    interests: str = "nature,food"
    origin_selection: dict | None = None
    destination_selection: dict | None = None


class DestinationSuggestionRequest(BaseModel):
    destination: str = Field(min_length=1)


@app.get("/health")
def health():
    return {"status": "ok", "service": "TripWise ML", "version": "4.0.0"}


@app.post("/suggest-destination")
def destination_suggestion(request: DestinationSuggestionRequest):
    try:
        options = search_destination_options(request.destination)
        if not options:
            raise ValueError("I could not identify this destination. Check the spelling and try again.")
        best = options[0]
        return {
            "suggestion": best["name"] if best["name"].lower() != request.destination.strip().lower() else None,
            "confidence": best.get("correction_score", 100),
            "options": options,
        }
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=502, detail="Destination intelligence service is temporarily unavailable.") from error


@app.post("/destination-options")
def destination_options(request: DestinationSuggestionRequest):
    try:
        options = search_destination_options(request.destination)
        return {"query": request.destination.strip(), "options": options}
    except Exception as error:
        raise HTTPException(status_code=502, detail="Destination intelligence service is temporarily unavailable.") from error


@app.post("/plan")
def plan(request: TripRequest):
    try:
        return plan_trip(request.model_dump())
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=502, detail="Unable to retrieve live destination information right now. Please try again.") from error
