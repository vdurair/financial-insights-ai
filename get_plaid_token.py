"""
Generate a Plaid sandbox access token for testing
"""
import os
import requests
import json

# Your credentials
CLIENT_ID = os.getenv("PLAID_CLIENT_ID", "699208264c01cb002166c676")
SECRET = os.getenv("PLAID_SECRET", "4fd746dbc01da40fa0595279a003e1")
ENVIRONMENT = "sandbox"

def get_access_token():
    """Generate a test access token"""
    
    # Step 1: Create a public token
    print("📌 Step 1: Creating public token...")
    
    public_token_url = f"https://{ENVIRONMENT}.plaid.com/sandbox/public_token/create"
    public_token_payload = {
        "client_id": CLIENT_ID,
        "secret": SECRET,
        "institution_id": "ins_109508",  # Platypus Bank sandbox
        "initial_products": ["transactions"]
    }
    
    try:
        response = requests.post(public_token_url, json=public_token_payload)
        response.raise_for_status()
        public_token = response.json().get("public_token")
        if not public_token:
            print(f"❌ No public token in response: {response.json()}")
            return
        print(f"✅ Public token created: {public_token[:20]}...")
    except Exception as e:
        print(f"❌ Failed to create public token: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   Response: {e.response.text}")
        return
    
    # Step 2: Exchange public token for access token
    print("\n📌 Step 2: Exchanging for access token...")
    
    exchange_url = f"https://{ENVIRONMENT}.plaid.com/item/public_token/exchange"
    exchange_payload = {
        "client_id": CLIENT_ID,
        "secret": SECRET,
        "public_token": public_token
    }
    
    try:
        response = requests.post(exchange_url, json=exchange_payload)
        response.raise_for_status()
        data = response.json()
        access_token = data.get("access_token")
        
        if access_token:
            print("\n" + "=" * 60)
            print("🎉 ACCESS TOKEN GENERATED SUCCESSFULLY 🎉")
            print("=" * 60)
            print(f"Access Token: {access_token}")
            print("=" * 60 + "\n")
            
            # Save to file for easy reference
            with open("access_token.txt", "w") as f:
                f.write(access_token)
            print(f"✅ Token saved to access_token.txt")
            print(f"✅ Token length: {len(access_token)} characters\n")
            
            return access_token
        else:
            print(f"❌ No access token in response: {data}")
            return
        
    except Exception as e:
        print(f"❌ Failed to exchange for access token: {e}")
        return

if __name__ == "__main__":
    get_access_token()
