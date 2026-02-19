"""
Integration Guide for Advanced NLP with Transformer Models
===========================================================

This document describes how Advanced NLP using transformer models
has been integrated into the AI Financial Insights project.
"""

# WHAT'S NEW
# ==========

## 1. New Module: advanced_nlp.py
   Location: src/advanced_nlp.py
   
   Classes:
   - TransformerNLPEngine: Uses BERT, BART, and SentenceTransformers
   - HybridNLPRouter: Combines transformers with keyword fallback

   Capabilities:
   ✓ Zero-shot intent classification
   ✓ Semantic similarity matching
   ✓ Named entity recognition
   ✓ Semantic transaction categorization
   ✓ Query summarization

## 2. Updated Module: nlp_router.py
   Now uses TransformerNLPEngine with intelligent fallback
   - Semantic query understanding
   - Better intent classification
   - Entity extraction for parameters

## 3. Enhanced Module: categorisation.py
   Now supports semantic categorization
   - Keyword matching (fast fallback)
   - Transformer-based semantic matching
   - Batch processing support

## 4. Updated Dependencies
   Added:
   - transformers (BERT, BART models)
   - torch (PyTorch backend)
   - sentence-transformers (already present)

# HOW TO USE
# ==========

## Installation
pip install -r requirements.txt

This installs:
- transformers: FB BART, BERT models for NLP tasks
- torch: PyTorch backend for neural networks
- sentence-transformers: Semantic similarity models

## Using Advanced NLP in Code

### 1. Intent Classification
```python
from src.advanced_nlp import TransformerNLPEngine

engine = TransformerNLPEngine()
intent, confidence = engine.classify_intent("Show my spending by category")
# Returns: ("category breakdown", 0.95)
```

### 2. Semantic Similarity
```python
results = engine.find_semantic_similarity(
    "McDonald's",
    ["restaurants", "groceries", "entertainment"]
)
# Returns: [("restaurants", 0.89), ("groceries", 0.12), ...]
```

### 3. Entity Recognition
```python
entities = engine.extract_entities("I spent $150 at Whole Foods")
# Returns: [{'word': '$150', 'entity_group': 'MONEY'}, ...]
```

### 4. Query Routing with Transformers
```python
from src.nlp_router import route_query, get_query_summary

route_type, params = route_query("What are my spending trends?")
# Returns: ("TREND", {"confidence": 0.92, "entities": [...]})

summary = get_query_summary("Show anomalies in my account")
# Returns: "Intent: anomaly detection (confidence: 0.88) | Entities: account"
```

### 5. Transaction Categorization
```python
from src.categorisation import categorise, TransactionCategorizer

# Simple function
category = categorise("Starbucks Coffee")
# Returns: "Restaurants"

# Class-based (for batch processing)
categorizer = TransactionCategorizer(use_advanced_nlp=True)
descriptions = ["McDonald's", "Whole Foods", "Shell Gas"]
categories = categorizer.categorize_batch(descriptions)
# Returns: ["Restaurants", "Groceries", "Fuel"]
```

# ARCHITECTURE
# =============

                 ┌─────────────────────┐
                 │   User Query        │
                 └──────────┬──────────┘
                           │
                ┌──────────▼──────────┐
                │   nlp_router.py     │
                │  (HybridNLPRouter)  │
                └──────────┬──────────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
    ┌──────▼──┐      ┌──────▼──┐     ┌─────▼────┐
    │ Try NLP  │      │ Extract  │     │Try Keywords
    │(Transformers)   │ Entities │     │(Fast)
    └──────┬──┘      └──────┬──┘     └─────┬────┘
           │               │               │
           └───────────────┼───────────────┘
                          │
                    ┌─────▼──────┐
                    │ Final Route │
                    │ + Params    │
                    └─────┬───────┘
                          │
              ┌───────────┴─────────────┐
              │                         │
         ┌────▼────┐      ┌────────────▼────┐
         │Analytics│      │ Categorization  │
         │Engine   │      │Semantics/Fast   │
         └─────────┘      └─────────────────┘

# MODELS USED
# ===========

1. Facebook BART Large MNLI (Zero-shot classification)
   - Papers: "BART: Denoising Sequence-to-Sequence Pre-training"
   - 406M parameters
   - Excellent for intent classification

2. All-MiniLM-L6-v2 (Semantic embeddings)
   - From Sentence-Transformers
   - 22M parameters
   - Fast semantic similarity (384-dim embeddings)

3. DbMD BERT NER (Named entity recognition)
   - English model trained on standard NER datasets
   - Recognizes: MONEY, PERSON, LOCATION, TIME, ORG, etc.

# PERFORMANCE NOTES
# ==================

Lazy Loading: Models load on first use, then cache
GPU Support: Automatically uses GPU if available (cuda:0)
Fallback: Works seamlessly with keywords if transformers unavailable

Approximate Model Sizes:
- BART: ~1.5 GB
- SentenceTransformers: ~90 MB
- BERT NER: ~400 MB
- Total: ~2 GB (downloaded on first use)

# TESTING
# =======

Run the demo:
  python test_advanced_nlp.py

This demonstrates:
1. Intent classification on financial queries
2. Semantic similarity for categorization
3. Named entity recognition
4. Query routing

# BACKWARD COMPATIBILITY
# =======================

All changes are backward compatible:
- Keywords still used as fast path
- Old code still works (just enhanced)
- Graceful fallback if transformers missing
- No breaking changes to existing APIs

# FUTURE ENHANCEMENTS
# ====================

Possible improvements:
- Fine-tune models on financial queries
- Custom financial NER model
- Intent confidence-based routing
- Multi-language support
- Summarization of insights
- Dialogue system for follow-up questions
"""

if __name__ == "__main__":
    print(__doc__)
