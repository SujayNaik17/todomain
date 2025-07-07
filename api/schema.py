"""
Pydantic models for request and response schemas.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional
from datetime import datetime

class TextInput(BaseModel):
    """Schema for single text input."""
    text: str = Field(
        ..., 
        min_length=1, 
        max_length=10000,
        description="Text to analyze for sentiment",
        example="This product is amazing! I love it so much."
    )
    
    @validator('text')
    def text_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Text cannot be empty or whitespace only')
        return v.strip()

class BatchTextInput(BaseModel):
    """Schema for batch text input."""
    texts: List[str] = Field(
        ..., 
        min_items=1, 
        max_items=100,
        description="List of texts to analyze for sentiment",
        example=[
            "This product is amazing!",
            "Not what I expected.",
            "Decent product for the price."
        ]
    )
    
    @validator('texts')
    def texts_must_not_be_empty(cls, v):
        if not v:
            raise ValueError('Texts list cannot be empty')
        
        # Validate each text
        cleaned_texts = []
        for text in v:
            if not isinstance(text, str):
                raise ValueError('All items must be strings')
            cleaned_text = text.strip()
            if not cleaned_text:
                raise ValueError('Text items cannot be empty or whitespace only')
            cleaned_texts.append(cleaned_text)
        
        return cleaned_texts

class SentimentResponse(BaseModel):
    """Schema for sentiment analysis response."""
    text: str = Field(
        ..., 
        description="Original input text",
        example="This product is amazing! I love it so much."
    )
    sentiment: str = Field(
        ..., 
        description="Predicted sentiment class",
        example="positive"
    )
    confidence: float = Field(
        ..., 
        ge=0.0, 
        le=1.0,
        description="Confidence score for the prediction (0-1)",
        example=0.95
    )
    probabilities: Dict[str, float] = Field(
        ..., 
        description="Probability scores for each sentiment class",
        example={
            "positive": 0.95,
            "negative": 0.03,
            "neutral": 0.02
        }
    )
    
    @validator('probabilities')
    def probabilities_must_sum_to_one(cls, v):
        total = sum(v.values())
        if not (0.99 <= total <= 1.01):  # Allow small floating point errors
            raise ValueError('Probabilities must sum to approximately 1.0')
        return v

class BatchSentimentResponse(BaseModel):
    """Schema for batch sentiment analysis response."""
    results: List[SentimentResponse] = Field(
        ..., 
        description="List of sentiment analysis results",
        min_items=1
    )
    
    class Config:
        schema_extra = {
            "example": {
                "results": [
                    {
                        "text": "This product is amazing!",
                        "sentiment": "positive",
                        "confidence": 0.95,
                        "probabilities": {
                            "positive": 0.95,
                            "negative": 0.03,
                            "neutral": 0.02
                        }
                    },
                    {
                        "text": "Not what I expected.",
                        "sentiment": "negative",
                        "confidence": 0.78,
                        "probabilities": {
                            "positive": 0.12,
                            "negative": 0.78,
                            "neutral": 0.10
                        }
                    }
                ]
            }
        }

class ErrorResponse(BaseModel):
    """Schema for error responses."""
    detail: str = Field(
        ..., 
        description="Error message",
        example="Model not loaded"
    )
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp when the error occurred"
    )
    error_type: Optional[str] = Field(
        None,
        description="Type of error",
        example="ModelNotLoadedError"
    )

class HealthResponse(BaseModel):
    """Schema for health check response."""
    status: str = Field(
        ..., 
        description="Health status",
        example="healthy"
    )
    model_loaded: bool = Field(
        ..., 
        description="Whether the model is loaded",
        example=True
    )
    vectorizer_loaded: bool = Field(
        ..., 
        description="Whether the vectorizer is loaded",
        example=True
    )
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp of the health check"
    )

class ModelStatsResponse(BaseModel):
    """Schema for model statistics response."""
    model_type: str = Field(
        ..., 
        description="Type of the ML model",
        example="MultinomialNB"
    )
    vectorizer_type: str = Field(
        ..., 
        description="Type of the text vectorizer",
        example="TfidfVectorizer"
    )
    classes: List[str] = Field(
        ..., 
        description="List of sentiment classes",
        example=["positive", "negative", "neutral"]
    )
    feature_count: int = Field(
        ..., 
        ge=0,
        description="Number of features in the model",
        example=5000
    )
    status: str = Field(
        ..., 
        description="Model status",
        example="ready"
    )

class APIInfoResponse(BaseModel):
    """Schema for API information response."""
    message: str = Field(
        ..., 
        description="API welcome message",
        example="Sentiment Analysis API"
    )
    version: str = Field(
        ..., 
        description="API version",
        example="1.0.0"
    )
    status: str = Field(
        ..., 
        description="API status",
        example="healthy"
    )
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Current timestamp"
    )
    endpoints: Dict[str, str] = Field(
        ..., 
        description="Available API endpoints",
        example={
            "/predict": "POST - Analyze sentiment of single text",
            "/predict_batch": "POST - Analyze sentiment of multiple texts",
            "/health": "GET - Health check"
        }
    )