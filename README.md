ai-financial-insights/

# AI Financial Insights

An intelligent financial analysis system that automatically categorizes transactions, detects anomalies, and generates actionable insights from financial data.

## Features

- **Data Preparation**: Load and clean financial transaction data
- **Transaction Categorization**: Automatically categorize transactions using keyword matching and semantic similarity
- **Anomaly Detection**: Identify unusual transactions using Isolation Forest
- **Insights Generation**: Generate summary statistics and spending analysis
- **Advanced NLP**: Natural language understanding using transformer models (BERT-based)
  - Intent classification for financial queries
  - Semantic similarity matching
  - Named entity recognition for financial terms
  - Intelligent query routing with fallback support

## Project Structure

```
ai-financial-insights/
├── data/
│   └── sample_statements.csv          # Sample financial data
├── notebooks/
│   └── 01_exploration.ipynb           # Jupyter notebook for data exploration
├── src/
│   ├── data_prep.py                   # Data loading and cleaning
│   ├── categorisation.py              # Transaction categorization
│   ├── anomaly_model.py               # Anomaly detection model
│   ├── insights_engine.py             # Insights generation
│   ├── nlp_router.py                  # NLP query routing (with transformers)
│   ├── advanced_nlp.py                # Advanced transformer-based NLP [NEW]
│   └── app.py                         # Main application
├── tests/
│   ├── test_data_prep.py              # Data prep tests
│   ├── test_anomaly_model.py          # Anomaly model tests
│   └── test_insights_engine.py        # Insights engine tests
├── requirements.txt                   # Python dependencies
└── README.md                          # This file
```

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd ai-financial-insights
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Run the main application:
```bash
python src/app.py
```

### Run tests:
```bash
pytest tests/
```

### Jupyter Notebook:
```bash
jupyter notebook notebooks/01_exploration.ipynb
```

## Module Descriptions

### data_prep.py
Handles data loading, cleaning, and feature engineering.

**Key Functions:**
- `load_data()`: Load CSV financial data
- `clean_data()`: Remove duplicates and handle missing values
- `prepare_features()`: Create engineered features

### categorisation.py
Automatically categorizes transactions based on descriptions.

**Key Classes:**
- `TransactionCategorizer`: Keyword-based transaction categorization

### anomaly_model.py
Detects unusual transactions using machine learning.

**Key Classes:**
- `AnomalyDetector`: Isolation Forest-based anomaly detection

### insights_engine.py
Generates financial insights and statistics.

**Key Classes:**
- `InsightsEngine`: Calculates metrics and generates insights

### nlp_router.py
Routes natural language queries to appropriate analysis methods.

**Key Classes:**
- `QueryRouter`: Routes NLP queries to handlers

### advanced_nlp.py
Advanced transformer-based NLP engine for financial queries.

**Key Classes:**
- `TransformerNLPEngine`: Semantic understanding using transformer models
  - Intent classification (zero-shot)
  - Semantic similarity matching
  - Named entity recognition
  - Transaction categorization by semantic meaning
- `HybridNLPRouter`: Combines transformer models with traditional NLP
  - Intelligent query routing
  - Fallback to keyword matching if transformers unavailable
  - Query summarization and understanding

### app.py
Main application entry point that orchestrates the analysis pipeline.

## Sample Data

- date: Transaction date
- amount: Transaction amount
- description: Transaction description
- category: Assigned category

## Testing

Tests are organized by module and can be run using pytest:

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_data_prep.py

# Run with verbose output
pytest -v tests/
```

## Future Enhancements

- Mobile app support

## License

This project is licensed under the CC BY-NC-ND License.
Modification and commercial use are not permitted.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.
