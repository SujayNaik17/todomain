"""
FastAPI application for sentiment analysis.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import joblib
import pandas as pd
import numpy as np
from typing import List, Dict
import logging
import os
from datetime import datetime
import uvicorn

from schema import TextInput, BatchTextInput, SentimentResponse, BatchSentimentResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Sentiment Analysis API",
    description="API for analyzing sentiment of text reviews using machine learning",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for model and vectorizer
model = None
vectorizer = None

def load_model():
    """Load the trained model and vectorizer."""
    global model, vectorizer
    
    try:
        model_path = os.path.join("model", "sentiment_model.pkl")
        vectorizer_path = os.path.join("model", "vectorizer.pkl")
        
        if os.path.exists(model_path) and os.path.exists(vectorizer_path):
            model = joblib.load(model_path)
            vectorizer = joblib.load(vectorizer_path)
            logger.info("Model and vectorizer loaded successfully!")
        else:
            logger.warning("Model files not found. Using demo mode.")
            # For demo purposes, create a simple model
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.naive_bayes import MultinomialNB
            
            # Sample data for demo
            sample_texts = ["good product", "bad quality", "average item"]
            sample_labels = ["positive", "negative", "neutral"]
            
            vectorizer = TfidfVectorizer(max_features=1000)
            X = vectorizer.fit_transform(sample_texts)
            model = MultinomialNB()
            model.fit(X, sample_labels)
            
            logger.info("Demo model created and loaded!")
            
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        raise

def preprocess_text(text: str) -> str:
    """Preprocess text for model input."""
    if not text:
        return ""
    
    import re
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove special characters and digits
    text = re.sub(r'[^a-zA-Z\\s]', '', text)
    
    # Remove extra whitespace
    text = re.sub(r'\\s+', ' ', text).strip()
    
    return text

@app.on_event("startup")
async def startup_event():
    """Initialize the application."""
    logger.info("Starting Sentiment Analysis API...")
    load_model()
    logger.info("API is ready to serve requests!")

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Sentiment Analysis API",
        "version": "1.0.0",
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "/predict": "POST - Analyze sentiment of single text",
            "/predict_batch": "POST - Analyze sentiment of multiple texts",
            "/health": "GET - Health check",
            "/docs": "GET - Interactive API documentation",
            "/redoc": "GET - ReDoc API documentation"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "vectorizer_loaded": vectorizer is not None,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/predict", response_model=SentimentResponse)
async def predict_sentiment(input_data: TextInput):
    """
    Predict sentiment for a single text.
    
    Args:
        input_data: TextInput object containing the text to analyze
        
    Returns:
        SentimentResponse: Prediction results with sentiment, confidence, and probabilities
    """
    try:
        if model is None or vectorizer is None:
            raise HTTPException(status_code=503, detail="Model not loaded")
        
        # Preprocess the text
        processed_text = preprocess_text(input_data.text)
        
        if not processed_text:
            raise HTTPException(status_code=400, detail="Text is empty after preprocessing")
        
        # Vectorize the text
        text_vector = vectorizer.transform([processed_text])
        
        # Make prediction
        prediction = model.predict(text_vector)[0]
        probabilities = model.predict_proba(text_vector)[0]
        
        # Get confidence score (highest probability)
        confidence = float(max(probabilities))
        
        # Create probabilities dictionary
        prob_dict = {}
        for i, class_label in enumerate(model.classes_):
            prob_dict[class_label] = float(probabilities[i])
        
        logger.info(f"Prediction made for text: '{input_data.text}' -> {prediction}")
        
        return SentimentResponse(
            text=input_data.text,
            sentiment=prediction,
            confidence=confidence,
            probabilities=prob_dict
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing text: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing text: {str(e)}")

@app.post("/predict_batch", response_model=BatchSentimentResponse)
async def predict_sentiment_batch(input_data: BatchTextInput):
    """
    Predict sentiment for multiple texts.
    
    Args:
        input_data: BatchTextInput object containing list of texts to analyze
        
    Returns:
        BatchSentimentResponse: List of prediction results
    """
    try:
        if model is None or vectorizer is None:
            raise HTTPException(status_code=503, detail="Model not loaded")
        
        if not input_data.texts:
            raise HTTPException(status_code=400, detail="No texts provided")
        
        if len(input_data.texts) > 100:  # Limit batch size
            raise HTTPException(status_code=400, detail="Batch size too large (max 100)")
        
        results = []
        
        for text in input_data.texts:
            # Preprocess the text
            processed_text = preprocess_text(text)
            
            if not processed_text:
                # Handle empty text
                results.append(SentimentResponse(
                    text=text,
                    sentiment="neutral",
                    confidence=0.5,
                    probabilities={"positive": 0.33, "negative": 0.33, "neutral": 0.34}
                ))
                continue
            
            # Vectorize the text
            text_vector = vectorizer.transform([processed_text])
            
            # Make prediction
            prediction = model.predict(text_vector)[0]
            probabilities = model.predict_proba(text_vector)[0]
            
            # Get confidence score
            confidence = float(max(probabilities))
            
            # Create probabilities dictionary
            prob_dict = {}
            for i, class_label in enumerate(model.classes_):
                prob_dict[class_label] = float(probabilities[i])
            
            results.append(SentimentResponse(
                text=text,
                sentiment=prediction,
                confidence=confidence,
                probabilities=prob_dict
            ))
        
        logger.info(f"Batch prediction completed for {len(input_data.texts)} texts")
        
        return BatchSentimentResponse(results=results)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing batch: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing batch: {str(e)}")

@app.get("/stats")
async def get_model_stats():
    """Get model statistics and information."""
    try:
        if model is None or vectorizer is None:
            return {"status": "Model not loaded"}
        
        stats = {
            "model_type": type(model).__name__,
            "vectorizer_type": type(vectorizer).__name__,
            "classes": list(model.classes_) if hasattr(model, 'classes_') else [],
            "feature_count": len(vectorizer.vocabulary_) if hasattr(vectorizer, 'vocabulary_') else 0,
            "status": "ready"
        }
        
        return stats
    
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")

if __name__ == "__main__":
    # Run the application
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )