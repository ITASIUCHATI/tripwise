from fastapi import FastAPI
from pydantic import BaseModel, Field

from predict import plan_trip


app = FastAPI(
    title="TripWise ML Service",
    version="1.0.0"
)


class TripRequest(BaseModel):
    destination: str = ""
    days: int = Field(
        default=5,
        ge=1,
        le=30
    )
    budget: float = Field(
        default=25000,
        gt=0
    )
    people: int = Field(
        default=2,
        ge=1,
        le=20
    )
    interests: str = "nature,food"
    style: str = "balanced"


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "TripWise ML"
    }


@app.post("/plan")
def plan(request: TripRequest):
    return plan_trip(
        request.model_dump()
    )