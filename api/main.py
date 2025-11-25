"""FastAPI application for house price prediction."""

import datetime
from contextlib import asynccontextmanager
from typing import Dict

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field, field_validator

from ames_house_price_prediction.core.service import PredictionService

# Global service instance
prediction_service: PredictionService = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load the prediction service on startup."""
    global prediction_service
    try:
        prediction_service = PredictionService.from_files()
    except Exception as e:
        raise RuntimeError(f"Failed to load prediction service: {e}")

    yield

    # Cleanup on shutdown
    prediction_service = None


app = FastAPI(
    title="House Price Quoting Service",
    description="A simple API to get a quote based on house characteristics.",
    version="0.2.0",
    lifespan=lifespan,
)


class HouseFeatures(BaseModel):
    """Input model for house features."""

    LotArea: float = Field(
        ..., gt=0, description="Lot size in square feet", examples=[8450]
    )
    YearBuilt: int = Field(
        ...,
        ge=1800,
        le=datetime.datetime.now().year,
        description="Original construction date",
        examples=[2003],
    )
    YearRemodAdd: int = Field(
        ...,
        ge=1800,
        le=datetime.datetime.now().year,
        description="Remodel date (same as construction date if no remodeling or additions)",
        examples=[2003],
    )
    OverallQual: int = Field(
        ...,
        ge=1,
        le=10,
        description="Overall material and finish quality (1-10)",
        examples=[7],
    )
    OverallCond: int = Field(
        ..., ge=1, le=10, description="Overall condition rating (1-10)", examples=[5]
    )

    @field_validator("YearRemodAdd")
    @classmethod
    def validate_remodel_year(cls, v: int, info) -> int:
        """Validate that remodel year is not before build year."""
        if "YearBuilt" in info.data and v < info.data["YearBuilt"]:
            raise ValueError("YearRemodAdd cannot be before YearBuilt")
        return v


class PredictionResponse(BaseModel):
    """Response model for price prediction."""

    predicted_price: float = Field(
        ..., description="Predicted house sale price in USD", examples=[208500.0]
    )
    input_features: Dict = Field(..., description="Input features used for prediction")


@app.get("/", summary="Health check")
def root() -> Dict[str, str]:
    """Check if the API is running."""
    return {"status": "healthy", "message": "House Price Quoting Service is running"}


@app.get(
    "/quote/",
    response_model=PredictionResponse,
    summary="Get house price quote",
    description="Get a price prediction based on house characteristics",
)
async def quote(
    LotArea: float,
    YearBuilt: int,
    YearRemodAdd: int,
    OverallQual: int,
    OverallCond: int,
) -> PredictionResponse:
    """Get a house price prediction.

    Args:
        LotArea: Lot size in square feet
        YearBuilt: Original construction date
        YearRemodAdd: Remodel date
        OverallQual: Overall quality (1-10)
        OverallCond: Overall condition (1-10)

    Returns:
        Predicted house price

    Raises:
        HTTPException: If prediction fails
    """
    try:
        # Validate input using Pydantic model
        features = HouseFeatures(
            LotArea=LotArea,
            YearBuilt=YearBuilt,
            YearRemodAdd=YearRemodAdd,
            OverallQual=OverallQual,
            OverallCond=OverallCond,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid input: {str(e)}",
        )

    try:
        # Make prediction
        predicted_price = prediction_service.predict_single(
            LotArea=features.LotArea,
            YearBuilt=features.YearBuilt,
            YearRemodAdd=features.YearRemodAdd,
            YrSold=datetime.datetime.now().year,
            OverallQual=features.OverallQual,
            OverallCond=features.OverallCond,
        )

        return PredictionResponse(
            predicted_price=predicted_price, input_features=features.model_dump()
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}",
        )


@app.post(
    "/quote/",
    response_model=PredictionResponse,
    summary="Get house price quote (POST)",
    description="Get a price prediction based on house characteristics using POST request",
)
async def quote_post(features: HouseFeatures) -> PredictionResponse:
    """Get a house price prediction using POST request.

    Args:
        features: House features as JSON body

    Returns:
        Predicted house price

    Raises:
        HTTPException: If prediction fails
    """
    try:
        predicted_price = prediction_service.predict_single(
            LotArea=features.LotArea,
            YearBuilt=features.YearBuilt,
            YearRemodAdd=features.YearRemodAdd,
            YrSold=datetime.datetime.now().year,
            OverallQual=features.OverallQual,
            OverallCond=features.OverallCond,
        )

        return PredictionResponse(
            predicted_price=predicted_price, input_features=features.model_dump()
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}",
        )
