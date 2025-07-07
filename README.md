# Sentiment Classification Project

A comprehensive machine learning project for sentiment analysis of product reviews. This project includes data scraping, preprocessing, model training, and a RESTful API for real-time sentiment prediction.

## Project Structure

```
sentiment-classification/
│
├── README.md                   # Project documentation
├── requirements.txt            # Python dependencies
│
├── data/
│   ├── raw/                   # Raw scraped reviews
│   │   └── reviews_raw.csv
│   └── processed/             # Cleaned & labeled data
│       └── reviews_clean.csv
│
├── scraping/
│   ├── scraper.py             # Python script to scrape reviews
│   └── utils.py               # Helper functions for scraping
│
├── notebooks/
│   ├── 1_preprocessing.ipynb   # Data cleaning, labeling
│   ├── 2_training.ipynb        # Model training, evaluation
│   └── 3_api_colab.ipynb       # Colab notebook to run API
│
├── model/
│   ├── sentiment_model.pkl     # Trained ML model
│   └── vectorizer.pkl          # TF-IDF vectorizer
│
└── api/
    ├── app.py                  # FastAPI application
    └── schema.py               # Request/response models
```

## Features

- **Data Scraping**: Automated web scraping for product reviews
- **Data Preprocessing**: Text cleaning, tokenization, and labeling
- **Machine Learning**: Multiple ML models with hyperparameter tuning
- **API Service**: RESTful API for real-time sentiment prediction
- **Jupyter Notebooks**: Interactive development and analysis
- **Google Colab Support**: Cloud-based training and deployment

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Data Collection

Run the scraping script to collect reviews:

```bash
python scraping/scraper.py
```

### 3. Data Preprocessing

Open and run the preprocessing notebook:

```bash
jupyter notebook notebooks/1_preprocessing.ipynb
```

### 4. Model Training

Train the sentiment analysis model:

```bash
jupyter notebook notebooks/2_training.ipynb
```

### 5. Start the API

Launch the FastAPI server:

```bash
cd api
python app.py
```

The API will be available at `http://localhost:8000`

## API Usage

### Single Prediction

```bash
curl -X POST "http://localhost:8000/predict" \
     -H "Content-Type: application/json" \
     -d '{"text": "This product is amazing!"}'
```

### Batch Prediction

```bash
curl -X POST "http://localhost:8000/predict_batch" \
     -H "Content-Type: application/json" \
     -d '{"texts": ["Great product!", "Poor quality", "Average item"]}'
```

### Interactive Documentation

Visit `http://localhost:8000/docs` for interactive API documentation.

## Model Performance

The trained model achieves:
- **Accuracy**: ~85% on test data
- **Classes**: Positive, Negative, Neutral
- **Features**: TF-IDF vectorization with n-grams
- **Algorithm**: Multinomial Naive Bayes (best performing)

## Google Colab Integration

Use the provided Colab notebook for cloud-based training and deployment:

1. Open `notebooks/3_api_colab.ipynb` in Google Colab
2. Install dependencies and mount Google Drive
3. Load your data and train the model
4. Deploy the API with ngrok for external access

## Development

### Adding New Features

1. **New Data Sources**: Extend `scraping/scraper.py`
2. **Preprocessing Steps**: Modify `notebooks/1_preprocessing.ipynb`
3. **Model Algorithms**: Add to `notebooks/2_training.ipynb`
4. **API Endpoints**: Extend `api/app.py` and `api/schema.py`

### Testing

```bash
# Test the scraper
python -m pytest scraping/

# Test the API
python -m pytest api/

# Run all tests
python -m pytest
```

## Data Sources

Currently supports scraping from:
- E-commerce product pages
- Review websites
- Social media platforms

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions and support, please open an issue on GitHub or contact the development team.
