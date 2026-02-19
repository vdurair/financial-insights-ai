"""
Transaction Categorization Module

Categorizes financial transactions using both keyword matching
and advanced transformer-based semantic analysis.
"""

from typing import Optional

# Try to import advanced NLP (graceful fallback if not available)
try:
    from advanced_nlp import TransformerNLPEngine
    # Disable advanced NLP to use simple keyword-based categorization only
    ADVANCED_NLP_AVAILABLE = False
except ImportError:
    ADVANCED_NLP_AVAILABLE = False

# Keyword-based category map (fallback)
CATEGORY_MAP = {
    "TESCO": "Groceries",
    "ASDA": "Groceries",
    "MORRISONS": "Groceries",
    "SAINSBURY": "Groceries",
    "WHOLE FOODS": "Groceries",
    "SAFEWAY": "Groceries",
    "TRADER JOE": "Groceries",
    "KROGER": "Groceries",
    
    "UBER": "Transport",
    "LYFT": "Transport",
    "TAXI": "Transport",
    "AMTRAK": "Transport",
    "DELTA": "Transport",
    "UNITED": "Transport",
    
    "SHELL": "Fuel",
    "BP": "Fuel",
    "CHEVRON": "Fuel",
    "EXXON": "Fuel",
    "MOBIL": "Fuel",
    
    "AMAZON": "Shopping",
    "EBAY": "Shopping",
    "TARGET": "Shopping",
    "WALMART": "Shopping",
    "CVS": "Shopping",
    "WALGREENS": "Shopping",
    
    "NETFLIX": "Entertainment",
    "SPOTIFY": "Entertainment",
    "HULU": "Entertainment",
    "DISNEY": "Entertainment",
    "MOVIE": "Entertainment",
    "CINEMA": "Entertainment",
    
    "STARBUCKS": "Restaurants",
    "MCDONALD": "Restaurants",
    "BURGER": "Restaurants",
    "PIZZA": "Restaurants",
    "RESTAURANT": "Restaurants",
    "CAFÉ": "Restaurants",
    
    "HOSPITAL": "Healthcare",
    "CLINIC": "Healthcare",
    "PHARMACY": "Healthcare",
    "DOCTOR": "Healthcare",
    "MEDICAL": "Healthcare",
    
    "ATT": "Utilities",
    "VERIZON": "Utilities",
    "COMCAST": "Utilities",
    "ELECTRIC": "Utilities",
    "WATER": "Utilities",
    "GAS": "Utilities",
}

# Initialize advanced NLP engine (lazy loaded)
_nlp_engine = None

def get_nlp_engine() -> Optional[TransformerNLPEngine]:
    """Get or initialize the advanced NLP engine."""
    global _nlp_engine
    if ADVANCED_NLP_AVAILABLE and _nlp_engine is None:
        try:
            _nlp_engine = TransformerNLPEngine()
        except Exception as e:
            print(f"⚠️ Failed to initialize advanced NLP: {e}")
            return None
    return _nlp_engine

def categorise(description: str) -> str:
    """
    Categorize a transaction description.
    
    Uses advanced semantic matching if available, falls back to keyword matching.
    
    :param description: Transaction description
    :return: Category string
    """
    if not description:
        return "Other"
    
    desc_upper = description.upper()
    
    # First try keyword matching (fast and reliable)
    for key, category in CATEGORY_MAP.items():
        if key in desc_upper:
            return category
    
    # Try advanced semantic categorization
    nlp_engine = get_nlp_engine()
    if nlp_engine:
        try:
            return nlp_engine.categorize_transaction_description(description)
        except Exception as e:
            print(f"⚠️ Semantic categorization failed, using default: {e}")
    
    # Default fallback
    return "Other"

class TransactionCategorizer:
    """
    Enhanced transaction categorizer using both keyword and semantic methods.
    """
    
    def __init__(self, use_advanced_nlp: bool = True):
        """
        Initialize the categorizer.
        
        :param use_advanced_nlp: Enable advanced NLP if available
        """
        self.use_advanced_nlp = use_advanced_nlp
        self.nlp_engine = get_nlp_engine() if use_advanced_nlp else None
        self.category_keywords = CATEGORY_MAP
    
    def categorize(self, description: str) -> str:
        """
        Categorize a single transaction.
        
        :param description: Transaction description
        :return: Category
        """
        return categorise(description)
    
    def categorize_batch(self, descriptions: list) -> list:
        """
        Categorize multiple transactions efficiently.
        
        :param descriptions: List of transaction descriptions
        :return: List of categories
        """
        return [self.categorize(desc) for desc in descriptions]
