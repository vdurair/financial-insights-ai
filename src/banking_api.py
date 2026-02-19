"""
Banking API Integration Module

Provides a unified interface for connecting to various banking APIs.
Supports Plaid and other banking data sources.

Setup:
1. Install Plaid SDK: pip install plaid-python
2. Get API credentials from https://plaid.com
3. Set environment variables:
   - PLAID_CLIENT_ID
   - PLAID_SECRET
   - PLAID_ENVIRONMENT (sandbox, development, production)

"""
import os
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import pandas as pd

# Check for required packages at module load time
try:
    from plaid import Configuration, ApiClient
    from plaid.api import plaid_api
    from plaid.model.transactions_get_request import TransactionsGetRequest
    from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
    PLAID_AVAILABLE = True
except ImportError as e:
    PLAID_AVAILABLE = False
    PLAID_ERROR = str(e)


class PlaidBankingAPI:
    """
    Interface to Plaid API for fetching real bank transactions.
    Plaid supports 12,000+ financial institutions globally.
    """

    def __init__(
        self,
        client_id: Optional[str] = None,
        secret: Optional[str] = None,
        environment: str = "sandbox",
    ) -> None:
        """
        Initialize Plaid API client.

        :param client_id: Plaid Client ID (defaults to PLAID_CLIENT_ID env var)
        :param secret: Plaid Secret (defaults to PLAID_SECRET env var)
        :param environment: 'sandbox', 'development', or 'production'
        """
        if not PLAID_AVAILABLE:
            raise ImportError(
                "Plaid SDK not installed. Run: pip install plaid-python"
            )

        self.client_id = client_id or os.getenv("PLAID_CLIENT_ID")
        self.secret = secret or os.getenv("PLAID_SECRET")
        self.environment = environment

        if not self.client_id or not self.secret:
            raise ValueError(
                "Plaid credentials not found. Set PLAID_CLIENT_ID and PLAID_SECRET env vars."
            )

        # Map environment to Plaid host
        env_map = {
            "sandbox": "https://sandbox.plaid.com",
            "development": "https://development.plaid.com",
            "production": "https://production.plaid.com",
        }
        
        configuration = Configuration(
            host=env_map.get(environment, "https://sandbox.plaid.com"),
            api_key={
                "clientId": self.client_id,
                "secret": self.secret,
            },
        )
        
        api_client = ApiClient(configuration)
        self.client = plaid_api.PlaidApi(api_client)

    def get_transactions(
        self, access_token: str, days_back: int = 90
    ) -> pd.DataFrame:
        """
        Fetch transactions from a Plaid-connected account.

        :param access_token: Access token obtained after Plaid Link authentication
        :param days_back: Number of days of history to fetch (default: 90)
        :return: DataFrame with transaction data
        """
        try:
            # Validate access token format
            if not access_token or not isinstance(access_token, str):
                raise ValueError(f"Invalid access token: {access_token}")
            
            if not access_token.startswith("access-"):
                raise ValueError(f"Access token has invalid format. Expected 'access-<env>-<id>', got: {access_token[:30]}...")
            
            print(f"🔍 Using access token: {access_token[:30]}... (length: {len(access_token)})")
            
            # Calculate date range
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days_back)
            
            # Create transactions request
            request = TransactionsGetRequest(
                access_token=access_token,
                start_date=start_date,
                end_date=end_date,
            )
            
            # Fetch transactions
            response = self.client.transactions_get(request)
            
            # Extract transactions list from response
            if hasattr(response, 'transactions'):
                # Handle API response object format
                transactions = [tx.to_dict() if hasattr(tx, 'to_dict') else dict(tx) 
                               for tx in response.transactions]
            elif isinstance(response, dict) and 'transactions' in response:
                # Handle dict response format
                transactions = response.get('transactions', [])
            else:
                # Fallback
                transactions = []
            
            # Convert to DataFrame
            if not transactions:
                return pd.DataFrame(
                    columns=["date", "amount", "description"]
                )
                
            df = pd.DataFrame(transactions)
            
            if df.empty:
                return df
            
            # Normalize columns
            df = df.rename(columns={
                "name": "description",
                "merchant_name": "merchant",
            })
            
            # Ensure date is datetime
            if "date" in df.columns:
                df["date"] = pd.to_datetime(df["date"])
            
            # Convert amount to float
            if "amount" in df.columns:
                df["amount"] = df["amount"].astype(float)
            
            return df
            
        except Exception as e:
            error_msg = f"Failed to fetch transactions from Plaid: {str(e)}"
            print(f"❌ {error_msg}")
            print(f"   Access token received: {access_token[:50] if access_token else 'None'}...")
            raise Exception(error_msg)

    def get_accounts(self, access_token: str) -> pd.DataFrame:
        """
        Get account details from a Plaid-connected item.

        :param access_token: Access token
        :return: DataFrame with account information
        """
        # For now, return empty DataFrame
        # In production, use Plaid's REST API
        return pd.DataFrame(
            columns=["account_id", "name", "type", "balance", "available"]
        )


class OpenBankingAPI:
    """
    Interface for Open Banking APIs (PSD2 in Europe, similar standards).
    Requires OAuth2 authentication and bank-specific endpoints.
    """

    def __init__(self, base_url: str, client_id: str, client_secret: str) -> None:
        """
        Initialize Open Banking API client.

        :param base_url: API base URL from your bank
        :param client_id: OAuth2 client ID
        :param client_secret: OAuth2 client secret
        """
        self.base_url = base_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token: Optional[str] = None

    def authenticate(self) -> None:
        """Obtain OAuth2 access token."""
        import requests

        token_url = f"{self.base_url}/oauth/token"
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }

        response = requests.post(token_url, data=data)
        response.raise_for_status()
        self.access_token = response.json()["access_token"]

    def get_transactions(self, account_id: str) -> pd.DataFrame:
        """
        Fetch transactions from an Open Banking API endpoint.

        :param account_id: Account ID from the bank
        :return: DataFrame with transactions
        """
        import requests

        if not self.access_token:
            self.authenticate()

        url = f"{self.base_url}/accounts/{account_id}/transactions"
        headers = {"Authorization": f"Bearer {self.access_token}"}

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        data = response.json()
        return pd.DataFrame(data)


class BankingAPIAdapter:
    """
    Unified adapter for working with different banking APIs.
    Normalizes data formats across different providers.
    """

    def __init__(self, provider: str, **kwargs):
        """
        Initialize the adapter with a specific banking API provider.

        :param provider: 'plaid', 'openbanking', or 'manual'
        :param kwargs: Provider-specific arguments
        """
        self.provider = provider

        if provider == "plaid":
            self.api = PlaidBankingAPI(**kwargs)
        elif provider == "openbanking":
            self.api = OpenBankingAPI(**kwargs)
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    def fetch_transactions(self, **kwargs) -> pd.DataFrame:
        """
        Fetch transactions from the configured banking API.
        Returns a normalized DataFrame compatible with the insights engine.
        """
        df = self.api.get_transactions(**kwargs)

        # Normalize column names
        df = df.rename(
            columns={
                "amount": "amount",
                "description": "description",
                "date": "date",
            }
        )

        # Ensure required columns exist
        required_cols = ["date", "amount", "description"]
        for col in required_cols:
            if col not in df.columns:
                raise ValueError(f"Missing required column: {col}")

        return df[required_cols]
