"""
Demo script to test the Advanced NLP Engine
"""

import sys
import os

# Fix encoding for Windows
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from src.advanced_nlp import TransformerNLPEngine, HybridNLPRouter

def demo_transformer_nlp():
    """Demo the transformer-based NLP engine."""
    print("\n" + "="*60)
    print("ADVANCED NLP ENGINE DEMO")
    print("="*60)
    
    try:
        engine = TransformerNLPEngine()
        
        # Test 1: Intent Classification
        print("\n[TEST 1] Intent Classification (Zero-Shot)")
        print("-" * 60)
        test_queries = [
            "Show me my spending by category",
            "Are there any unusual transactions?",
            "What's my financial health score?",
            "How has my spending changed over time?"
        ]
        
        for query in test_queries:
            intent, confidence = engine.classify_intent(query)
            print(f"Query: '{query}'")
            print(f"  Intent: {intent} (confidence: {confidence:.2f})\n")
        
        # Test 2: Semantic Similarity
        print("\n[TEST 2] Semantic Similarity Matching")
        print("-" * 60)
        descriptions = [
            "McDonald's",
            "Whole Foods",
            "Shell Gas Station",
            "Netflix",
            "Google Play"
        ]
        
        candidates = ["restaurants", "groceries", "fuel", "entertainment", "services"]
        
        for desc in descriptions:
            results = engine.find_semantic_similarity(desc, candidates)
            top_match = results[0]
            print(f"'{desc}' -> '{top_match[0]}' (similarity: {top_match[1]:.2f})")
        
        # Test 3: Transaction Categorization
        print("\n[TEST 3] Transaction Categorization")
        print("-" * 60)
        transactions = [
            "Starbucks Coffee",
            "Uber Trip",
            "CVS Pharmacy",
            "Amazon",
            "Electric Company"
        ]
        
        for trans in transactions:
            category = engine.categorize_transaction_description(trans)
            print(f"'{trans}' -> Category: {category}")
        
        # Test 4: Named Entity Recognition
        print("\n[TEST 4] Named Entity Recognition")
        print("-" * 60)
        test_text = "I spent $150 at Whole Foods yesterday and another $45 at Shell gas station"
        entities = engine.extract_entities(test_text)
        if entities:
            print(f"Text: '{test_text}'")
            print("Entities found:")
            for entity in entities:
                print(f"  - {entity['word']} ({entity['entity_group']})")
        
    except ImportError as e:
        print(f"[ERROR] Transformers not installed: {e}")
        print("Install with: pip install transformers torch")

def demo_hybrid_router():
    """Demo the hybrid NLP router."""
    print("\n" + "="*60)
    print("HYBRID NLP ROUTER DEMO")
    print("="*60)
    
    router = HybridNLPRouter()
    
    test_queries = [
        "What are my spending habits?",
        "Show me anomalies in my transactions",
        "How healthy is my financial situation?",
        "Give me a category breakdown of my spending",
        "Show trends in my expenses",
        "Help me budget better",
        "I need to understand my account",
    ]
    
    print("\nQuery Routing Results:")
    print("-" * 60)
    
    for query in test_queries:
        route_type, params = router.route_query(query)
        summary = router.get_query_summary(query)
        
        print(f"\nQuery: '{query}'")
        print(f"  Route: {route_type}")
        print(f"  Summary: {summary}")
        if params:
            print(f"  Params: {params}")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("ADVANCED NLP INTEGRATION TEST")
    print("="*60)
    
    # Run demos
    demo_transformer_nlp()
    demo_hybrid_router()
    
    print("\n" + "="*60)
    print("DEMO COMPLETE")
    print("="*60)
