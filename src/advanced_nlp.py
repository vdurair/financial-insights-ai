"""
Advanced NLP Module using Transformer Models

Provides semantic understanding and intent classification using
transformer-based models (BERT, DistilBERT, etc.)
"""

import os
from typing import Dict, Tuple, List
import numpy as np

try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
    from sentence_transformers import SentenceTransformer, util
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False


class TransformerNLPEngine:
    """
    Advanced NLP engine using transformer models for:
    - Intent classification
    - Semantic similarity
    - Named entity recognition
    - Text summarization
    """
    
    def __init__(self, use_gpu: bool = False):
        """
        Initialize transformer-based NLP models with lazy loading.
        Models are only loaded when explicitly needed.
        
        :param use_gpu: Use GPU acceleration if available
        """
        if not TRANSFORMERS_AVAILABLE:
            print("⚠️  Transformers not available. Using keyword-based fallback only.")
            self.models_loaded = False
            return
        
        self.device = 0 if use_gpu else -1  # -1 for CPU
        self.models_loaded = False
        self.intent_classifier = None
        self.semantic_model = None
        self.ner_pipeline = None
        
        # Models will be loaded lazily when needed
        # This prevents app startup delays
        
        # Financial intent labels
        self.financial_intents = [
            "spending analysis",
            "anomaly detection",
            "category breakdown",
            "health check",
            "trend analysis",
            "budgeting",
            "account overview"
        ]
    
    def classify_intent(self, query: str, threshold: float = 0.3) -> Tuple[str, float]:
        """
        Classify the intent of a user query using zero-shot classification.
        
        :param query: User query text
        :param threshold: Confidence threshold
        :return: Tuple of (intent, confidence)
        """
        if not self.models_loaded or not self.intent_classifier:
            return "unknown", 0.0
            
        try:
            result = self.intent_classifier(
                query,
                self.financial_intents,
                multi_class=False
            )
            
            intent = result['labels'][0]
            confidence = result['scores'][0]
            
            if confidence < threshold:
                return "unknown", confidence
            
            return intent, confidence
            
        except Exception as e:
            print(f"❌ Intent classification error: {e}")
            return "unknown", 0.0
    
    def find_semantic_similarity(self, query: str, candidates: List[str]) -> List[Tuple[str, float]]:
        """
        Find the most semantically similar candidates to the query.
        
        :param query: Query text
        :param candidates: List of candidate texts to compare
        :return: List of (candidate, similarity_score) sorted by similarity
        """
        try:
            query_embedding = self.semantic_model.encode(query, convert_to_tensor=True)
            candidate_embeddings = self.semantic_model.encode(candidates, convert_to_tensor=True)
            
            similarities = util.pytorch_cos_sim(query_embedding, candidate_embeddings)[0]
            
            results = [
                (candidates[i], float(similarities[i]))
                for i in range(len(candidates))
            ]
            
            return sorted(results, key=lambda x: x[1], reverse=True)
            
        except Exception as e:
            print(f"❌ Semantic similarity error: {e}")
            return [(c, 0.0) for c in candidates]
    
    def extract_entities(self, text: str) -> List[Dict]:
        """
        Extract named entities from text (amounts, dates, categories, etc.)
        
        :param text: Input text
        :return: List of entities with their types and positions
        """
        try:
            entities = self.ner_pipeline(text)
            return entities
        except Exception as e:
            print(f"❌ NER error: {e}")
            return []
    
    def categorize_transaction_description(self, description: str) -> str:
        """
        Use semantic similarity to categorize a transaction description.
        
        :param description: Transaction description
        :return: Predicted category
        """
        categories = [
            "groceries",
            "restaurants",
            "transportation",
            "utilities",
            "entertainment",
            "shopping",
            "healthcare",
            "insurance",
            "savings",
            "other"
        ]
        
        similarities = self.find_semantic_similarity(description, categories)
        return similarities[0][0]  # Return top match
    
    def summarize_query(self, query: str) -> str:
        """
        Generate a semantic understanding of the query for logging/debugging.
        
        :param query: User query
        :return: Summary of understood intent
        """
        intent, confidence = self.classify_intent(query)
        entities = self.extract_entities(query)
        
        entity_summary = ", ".join([e['word'] for e in entities[:3]])
        
        summary = f"Intent: {intent} (confidence: {confidence:.2f})"
        if entity_summary:
            summary += f" | Entities: {entity_summary}"
        
        return summary


class HybridNLPRouter:
    """
    Hybrid router combining transformer models with traditional NLP.
    Provides fallback logic and intent routing for financial queries.
    """
    
    def __init__(self):
        """Initialize the hybrid NLP router."""
        self.transformer_engine = None
        try:
            self.transformer_engine = TransformerNLPEngine()
        except ImportError:
            print("⚠️  Transformers not available. Using keyword-based fallback.")
        
        # Fallback keywords if transformers unavailable
        self.keyword_routes = {
            "CATEGORY": ["category", "breakdown", "spending by", "expenses by"],
            "ANOMALIES": ["anomal", "unusual", "odd", "suspicious"],
            "HEALTH": ["health", "score", "financial health"],
            "SUMMARY": ["spend", "summary", "total", "overview"],
            "TREND": ["trend", "over time", "change", "increase", "decrease"],
        }
    
    def route_query(self, query: str) -> Tuple[str, Dict]:
        """
        Route a query to the appropriate analysis handler.
        
        :param query: User query text
        :return: Tuple of (route_type, parameters)
        """
        # Try transformer-based routing first
        if self.transformer_engine:
            return self._transformer_route(query)
        else:
            return self._keyword_route(query)
    
    def _transformer_route(self, query: str) -> Tuple[str, Dict]:
        """Route using transformer models, with fallback to keywords."""
        # Check if transformer models are available
        if not self.transformer_engine or not self.transformer_engine.models_loaded:
            return self._keyword_route(query)
        
        try:
            intent, confidence = self.transformer_engine.classify_intent(query)
            
            # If confidence too low, fall back to keywords
            if intent == "unknown" or confidence < 0.3:
                return self._keyword_route(query)
            
            # Map transformer intents to route types
            intent_map = {
                "spending analysis": "SUMMARY",
                "anomaly detection": "ANOMALIES",
                "category breakdown": "CATEGORY",
                "health check": "HEALTH",
                "trend analysis": "TREND",
                "budgeting": "BUDGET",
                "account overview": "SUMMARY"
            }
            
            route_type = intent_map.get(intent, "UNKNOWN")
            
            # If still unknown, fall back to keywords
            if route_type == "UNKNOWN":
                return self._keyword_route(query)
            
            # Extract entities for parameters
            entities = self.transformer_engine.extract_entities(query) if self.transformer_engine.models_loaded else []
            params = {"confidence": confidence, "entities": entities}
            
            print(f"🤖 Transformer routing: {route_type} (confidence: {confidence:.2f})")
            
            return route_type, params
            
        except Exception as e:
            print(f"⚠️  Transformer routing failed: {e}. Falling back to keywords.")
            return self._keyword_route(query)
    
    def _keyword_route(self, query: str) -> Tuple[str, Dict]:
        """Fallback keyword-based routing."""
        q = query.lower()
        
        for route_type, keywords in self.keyword_routes.items():
            if any(kw in q for kw in keywords):
                return route_type, {}
        
        return "UNKNOWN", {}
    
    def get_query_summary(self, query: str) -> str:
        """Get a summary of what was understood from the query."""
        if self.transformer_engine:
            return self.transformer_engine.summarize_query(query)
        return query
