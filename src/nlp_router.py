"""
NLP Query Routing Module

Routes user queries to appropriate analysis handlers using intelligent keyword matching
and query understanding. Handles ANY user query gracefully by searching actual transaction data.
"""

from typing import Tuple, Dict, List, Optional
import re
import pandas as pd

# Define routing patterns with weights
ROUTING_PATTERNS = {
    "CATEGORY": {
        "keywords": ["category", "breakdown", "spending by", "expenses by", "spent on", "how much on", "spend on"],
        "weight": 10
    },
    "ANOMALIES": {
        "keywords": ["anomal", "unusual", "odd", "suspicious", "strange", "weird", "outlier", "abnormal"],
        "weight": 10
    },
    "HEALTH": {
        "keywords": ["health", "score", "financial health", "health score", "financial well", "well-being"],
        "weight": 10
    },
    "TREND": {
        "keywords": ["trend", "over time", "change", "increase", "decrease", "growth", "pattern", "history"],
        "weight": 8
    },
    "SUMMARY": {
        "keywords": ["total", "overview", "summary", "all spending", "all transactions", "everything"],
        "weight": 5
    },
    "SEARCH": {
        "keywords": ["find", "look", "show", "list", "what", "where", "tell me about"],
        "weight": 3
    },
}

def extract_category_from_dataframe(query: str, df: pd.DataFrame) -> Optional[str]:
    """
    Extract category from query by matching against actual dataframe categories.
    Supports partial matching and fuzzy matching.
    
    :param query: User query
    :param df: Transaction dataframe with 'category' column
    :return: Matching category or None
    """
    if "category" not in df.columns or df.empty:
        return None
    
    import difflib
    q_lower = query.lower()
    actual_categories = [str(cat) for cat in df["category"].unique() if isinstance(cat, str)]

    # Try exact match
    for cat in actual_categories:
        if cat.lower() in q_lower or cat.lower() == q_lower:
            return cat

    # Try partial match (substring)
    for cat in actual_categories:
        if cat.lower() in q_lower:
            return cat

    # Try reverse match (category name is part of query)
    for cat in actual_categories:
        if cat.lower() in q_lower or any(word in q_lower for word in cat.lower().split()):
            return cat

    # Try fuzzy match using difflib
    words = [w for w in q_lower.split() if len(w) > 2]
    for word in words:
        matches = difflib.get_close_matches(word, [cat.lower() for cat in actual_categories], n=1, cutoff=0.7)
        if matches:
            # Return the original category with the closest match
            for cat in actual_categories:
                if cat.lower() == matches[0]:
                    return cat

    return None

def extract_merchant_from_query(query: str, df: pd.DataFrame) -> Optional[str]:
    """
    Extract merchant/description keywords from query.
    Searches actual transaction descriptions with flexible matching.
    
    :param query: User query
    :param df: Transaction dataframe
    :return: Matched description value or None
    """
    import difflib
    if df.empty:
        return None

    q_lower = query.lower()

    # Remove common transaction words first
    ignore_words = {"transaction", "transactions", "spending", "spent", "show", "tell"}
    query_terms = [w.strip('.,!?') for w in q_lower.split() if w.lower() not in ignore_words and len(w) >= 2]

    if not query_terms:
        return None

    # Search in ALL columns (including category, type, etc.)
    all_columns = df.columns.tolist()

    import re
    for term in query_terms:
        term_lower = term.lower()

        # Try to find exact or partial match in any column
        for col in all_columns:
            if col not in df.columns:
                continue
            try:
                col_values = df[col].dropna().astype(str).unique()
                for value in col_values:
                    value_lower = str(value).lower().strip()
                    if (
                        term_lower == value_lower or                   # exact match
                        term_lower in value_lower or                   # substring
                        value_lower in term_lower or                   # reverse
                        value_lower.startswith(term_lower) or          # startswith
                        term_lower.startswith(value_lower) or          # reverse
                        any(term_lower in word or word in term_lower for word in value_lower.split())
                    ):
                        return str(value)
                # Fuzzy match using difflib if no direct match
                matches = difflib.get_close_matches(term_lower, [str(v).lower() for v in col_values], n=1, cutoff=0.7)
                if matches:
                    # Return the original value with the closest match
                    for value in col_values:
                        if str(value).lower() == matches[0]:
                            return str(value)
            except:
                continue

    return None

def extract_amount_range(query: str) -> Optional[Tuple[float, float]]:
    """
    Extract amount range from query (e.g., "over 100", "less than 50").
    
    :param query: User query
    :return: Tuple of (min_amount, max_amount) or None
    """
    q_lower = query.lower()
    
    # Match patterns like "over 100", "more than 50", "less than 100"
    patterns = [
        (r"over\s+£?(\d+(?:\.\d{2})?)", lambda m: float(m.group(1))),
        (r"more than\s+£?(\d+(?:\.\d{2})?)", lambda m: float(m.group(1))),
        (r"greater than\s+£?(\d+(?:\.\d{2})?)", lambda m: float(m.group(1))),
        (r"less than\s+£?(\d+(?:\.\d{2})?)", lambda m: (0, float(m.group(1)))),
        (r"under\s+£?(\d+(?:\.\d{2})?)", lambda m: (0, float(m.group(1)))),
        (r"between\s+£?(\d+(?:\.\d{2})?)\s+and\s+£?(\d+(?:\.\d{2})?)", 
         lambda m: (float(m.group(1)), float(m.group(2)))),
    ]
    
    for pattern, converter in patterns:
        match = re.search(pattern, q_lower)
        if match:
            result = converter(match)
            if isinstance(result, tuple):
                return result
            else:
                return (result, float('inf'))
    
    return None

def extract_search_terms(query: str) -> List[str]:
    """
    Extract meaningful search terms from a query.
    Removes common words and returns searchable keywords.
    
    :param query: User query
    :return: List of search terms
    """
    # Remove common words that don't help searching
    stop_words = {
        "how", "much", "can", "i", "me", "my", "the", "a", "an", "and", "or", "but", "is", "are", "was", "were",
        "in", "on", "at", "to", "of", "for", "from", "by", "with", "about", "what", "where", "when", "why", "which",
        "do", "did", "does", "show", "tell", "give", "find", "list", "search",
        "transaction", "transactions", "spending", "spent", "cost", "price", "amount", "have", "has", "had",
        "money", "payment", "payments", "bills", "bill", "account", "accounts", "made", "during", "month", "day"
    }
    
    # Split query into words and get meaningful terms (min 2 chars now)
    words = query.lower().split()
    terms = [w.strip('.,!?') for w in words if w.lower() not in stop_words and len(w) >= 2]
    
    return terms

def search_transactions(query: str, df: pd.DataFrame) -> Optional[pd.DataFrame]:
    """
    Intelligently search transactions using query terms.
    Searches across description, category, and other relevant columns.
    
    :param query: User query
    :param df: Transaction dataframe
    :return: Filtered dataframe or None
    """
    if df.empty:
        return None
    
    search_terms = extract_search_terms(query)
    if not search_terms:
        return None
    
    # Create search mask
    mask = pd.Series([False] * len(df), index=df.index)
    
    # Search in multiple columns
    search_columns = ["description", "merchant", "name", "category", "type"]
    
    import re
    for term in search_terms:
        for col in search_columns:
            if col in df.columns:
                col_mask = df[col].astype(str).str.contains(re.escape(term), case=False, na=False)
                mask = mask | col_mask
    
    result = df[mask]
    return result if len(result) > 0 else None

def route_query(query: str, df: Optional[pd.DataFrame] = None) -> Tuple[str, Dict]:
    """
    Route a user query to the appropriate analysis handler.
    Intelligently handles ANY query by finding the best matching intent
    and searching actual transaction data.
    
    :param query: User query text
    :param df: Optional dataframe for dynamic searching
    :return: Tuple of (route_type, parameters)
    """
    if not query or not query.strip():
        return "SUMMARY", {}
    
    q_lower = query.lower()
    
    # Extract parameters
    params = {
        "query": query,
    }
    
    # PRIORITY 1: If dataframe is provided, try to extract dynamic parameters FIRST
    # These take priority over keyword-based routing
    if df is not None and not df.empty:
        # Try to extract category from actual dataframe
        category = extract_category_from_dataframe(query, df)
        if category:
            params["category"] = category
            return "CATEGORY", params
        
        # Try to extract merchant/description - THIS IS PRIORITY
        merchant = extract_merchant_from_query(query, df)
        if merchant:
            params["merchant"] = merchant
            # Check for amount range too
            amount_range = extract_amount_range(query)
            if amount_range:
                params["amount_min"] = amount_range[0]
                params["amount_max"] = amount_range[1]
            return "SEARCH", params
        
        # Try to extract amount range (even without merchant)
        amount_range = extract_amount_range(query)
        if amount_range:
            params["amount_min"] = amount_range[0]
            params["amount_max"] = amount_range[1]
            return "SEARCH", params
        
        # ONLY try fuzzy search if no merchant/category/amount was extracted
        # AND the query is not a single word (single words should not fuzzy match)
        query_words = [w for w in query.split() if w.lower() not in 
                      {"transaction", "transactions", "spending", "spent", "show", "tell"}]
        
        if len(query_words) > 1:  # Only fuzzy search for multi-word queries
            search_result = search_transactions(query, df)
            if search_result is not None and len(search_result) > 0 and len(search_result) < len(df) * 0.5:
                # Only use fuzzy search if it returns < 50% of data (not everything)
                params["search_result"] = search_result
                params["is_fuzzy_search"] = True
                return "SEARCH", params
    
    # PRIORITY 2: Check for specific intent keywords
    route_scores = {}
    
    for route_type, config in ROUTING_PATTERNS.items():
        keywords = config["keywords"]
        weight = config.get("weight", 1)
        
        # Count keyword matches
        match_count = sum(1 for kw in keywords if kw in q_lower)
        
        if match_count > 0:
            route_scores[route_type] = match_count * weight
    
    # If no specific route matched, use heuristics
    if not route_scores:
        # Check for amount/number queries (likely category)
        if any(word in q_lower for word in ["how much", "total", "amount", "cost", "price", "spent"]):
            route_scores["SUMMARY"] = 5
        # Check for comparison queries (likely trend)
        elif any(word in q_lower for word in ["compare", "versus", "vs", "better", "worse"]):
            route_scores["TREND"] = 5
        # Default: Try to search the query as a free-form term
        else:
            route_scores["SUMMARY"] = 1
    
    # Get best matching route
    best_route = max(route_scores, key=route_scores.get) if route_scores else "SUMMARY"
    params["route_score"] = route_scores.get(best_route, 0)
    
    return best_route, params

def get_query_summary(query: str) -> str:
    """
    Get a summary of what was understood from the query.
    
    :param query: User query text
    :return: Summary string
    """
    route_type, params = route_query(query)
    return f"Understood: {route_type}"

def analyze_query(query: str, df: Optional[pd.DataFrame] = None) -> Dict:
    """
    Provide detailed analysis of the query for logging/debugging.
    
    :param query: User query text
    :param df: Optional dataframe for analysis
    :return: Analysis dictionary
    """
    route_type, params = route_query(query, df)
    
    analysis = {
        "route_type": route_type,
        "parameters": params,
        "query_length": len(query),
    }
    
    return analysis