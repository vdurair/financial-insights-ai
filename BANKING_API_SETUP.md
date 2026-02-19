# Banking API Integration Guide

This guide explains how to integrate real banking APIs with the AI Financial Insights project.

## Overview

The project now supports multiple data sources:
1. **CSV Upload** (existing) - Upload bank statements manually
2. **Plaid API** (recommended) - Connect 12,000+ financial institutions
3. **Open Banking APIs** - PSD2 and similar standards (extensible)

## Option 1: Plaid Integration (Recommended)

Plaid is the most user-friendly option, supporting major banks worldwide.

### Setup Steps

#### 1. Create a Plaid Account
- Visit https://plaid.com
- Sign up for a free account
- Navigate to the Dashboard

#### 2. Get Your Credentials
In the Plaid Dashboard:
- Go to **Settings > Keys**
- Copy your **Client ID**
- Copy your **Secret**
- Note your **Environment** (sandbox for testing, production for real banks)

#### 3. Install Plaid SDK
```bash
pip install plaid-python
```

#### 4. Set Environment Variables
```powershell
# Windows PowerShell
[Environment]::SetEnvironmentVariable("PLAID_CLIENT_ID", "your_client_id", "User")
[Environment]::SetEnvironmentVariable("PLAID_SECRET", "your_secret", "User")
[Environment]::SetEnvironmentVariable("PLAID_ENVIRONMENT", "sandbox", "User")

# Then restart your terminal or application
```

#### 5. Use in Application
```python
from banking_api import BankingAPIAdapter

adapter = BankingAPIAdapter(
    provider="plaid",
    client_id="your_client_id",
    secret="your_secret",
    environment="sandbox"
)

# Fetch transactions (requires access token from Plaid Link)
transactions_df = adapter.fetch_transactions(access_token="your_access_token")
```

#### 6. Plaid Link Integration (Full Flow)
For production use, implement Plaid Link in the Streamlit app:

```python
import streamlit as st
from banking_api import PlaidBankingAPI

api = PlaidBankingAPI()

# Step 1: Create Link token
link_token = api.create_link_token(user_id="user123")

# Step 2: User authenticates via Plaid Link (handled by JavaScript frontend)
# Step 3: Exchange public token for access token
access_token = api.exchange_public_token(public_token)

# Step 4: Fetch transactions
transactions = api.get_transactions(access_token)
```

### Testing with Sandbox
Use these test credentials in Plaid Sandbox:
- **Username**: `user_good`
- **Password**: `pass_good`
- **MFA**: Leave blank

## Option 2: Open Banking APIs (PSD2 Europe)

For European banks using PSD2 (Payment Services Directive 2):

### Setup Steps

#### 1. Get Bank API Credentials
Contact your bank's developer portal for:
- API Base URL
- OAuth2 Client ID
- OAuth2 Client Secret

#### 2. Example: Implementing with a specific bank

```python
from banking_api import BankingAPIAdapter

adapter = BankingAPIAdapter(
    provider="openbanking",
    base_url="https://api.yourbank.com",
    client_id="your_client_id",
    client_secret="your_client_secret"
)

transactions = adapter.fetch_transactions(account_id="123456")
```

## Integration with App

The Streamlit app now supports banking API connections:

### 1. Run the App
```bash
streamlit run src/app.py
```

### 2. In the Sidebar
- Choose "Connect Bank (Plaid)"
- Check "Configure Plaid Credentials"
- Enter your Plaid Client ID and Secret
- Click "Fetch Transactions"

### 3. Security Notes
- Never commit credentials to git
- Use environment variables or secret management
- In production, use Plaid Link for secure authentication
- Enable OAuth2 in your bank's settings

## Data Format Standardization

All banking APIs are normalized to this format:

```
date          | amount  | description
2024-02-13    | 45.99   | Grocery Store
2024-02-12    | 1200.00 | Salary Deposit
```

This matches the CSV format, so no code changes needed in downstream modules.

## Error Handling

Common issues and solutions:

### "Plaid credentials not found"
- Set environment variables (see Step 4 above)
- Restart your terminal after setting env vars

### "Unsupported operation for this account"
- Account may not support transactions API
- Try different test credentials in sandbox
- Contact your bank's support

### "API rate limit exceeded"
- Implement caching (example below)
- Plaid allows 100 transactions/month in sandbox

```python
import streamlit as st
from datetime import datetime

@st.cache_data(ttl=3600)  # Cache for 1 hour
def cached_transactions(access_token):
    return adapter.fetch_transactions(access_token)
```

## Advanced: Multi-Account Support

Fetch from multiple connected accounts:

```python
api = PlaidBankingAPI()
accounts = api.get_accounts(access_token)

for _, account in accounts.iterrows():
    print(f"Account: {account['name']}, Balance: {account['balance']}")
    
    transactions = api.get_transactions(
        access_token,
        account_id=account['account_id']
    )
```

## Security Best Practices

1. **Never commit secrets** to git
2. **Use environment variables** for credentials
3. **Enable IP whitelisting** in Plaid dashboard
4. **Rotate secrets** regularly
5. **Use Plaid Link** for user authentication (not manual tokens)
6. **Log access** for compliance/auditing
7. **Encrypt** stored access tokens

## Next Steps

- [ ] Sign up for Plaid account
- [ ] Get sandbox credentials
- [ ] Install plaid-python
- [ ] Test with sandbox credentials
- [ ] Upgrade to production when ready
- [ ] Implement Plaid Link for user-facing auth
- [ ] Add multi-account support
- [ ] Set up transaction caching

## Support

- Plaid Docs: https://plaid.com/docs
- API Reference: https://plaid.com/docs/api
- Troubleshooting: https://plaid.com/docs/troubleshooting
