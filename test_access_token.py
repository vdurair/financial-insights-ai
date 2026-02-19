"""
Test Plaid access token to diagnose issues
"""
import os
import sys

# Fix encoding for Windows
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from src.banking_api import PlaidBankingAPI

# Read the access token from file
try:
    with open("access_token.txt", "r") as f:
        access_token = f.read().strip()
except FileNotFoundError:
    print("ERROR: access_token.txt not found. Run get_plaid_token.py first")
    exit(1)

print(f"[INFO] Access Token: {access_token}")
print(f"[INFO] Length: {len(access_token)} characters")
print(f"[OK] Format check: {access_token.startswith('access-')}")

# Try to use it
print("\n[INFO] Testing Plaid API with access token...")
try:
    api = PlaidBankingAPI(
        client_id="699208264c01cb002166c676",
        secret="4fd746dbc01da40fa0595279a003e1",
        environment="sandbox"
    )
    
    print("[OK] Plaid API initialized")
    print("[INFO] Fetching transactions...")
    
    df = api.get_transactions(access_token, days_back=30)
    
    if df.empty:
        print("[WARN] No transactions found (but API call succeeded!)")
    else:
        print(f"[OK] Successfully fetched {len(df)} transactions")
        print(f"\nColumns: {list(df.columns)}")
        print(f"\nFirst few rows:\n{df.head()}")
        
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()
