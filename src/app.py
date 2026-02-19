import streamlit as st
import pandas as pd
import os
import requests
from data_prep import load_and_prepare

# App title and subtitle (always visible)
st.title("💷 Financial Insights & Anomaly Detection AI")
st.caption("Understand your spending, spot anomalies, and improve your financial well‑being.")

# Data source selection
st.sidebar.header("📥 Data Source")
data_source = st.sidebar.radio("Choose data source:", ["Upload CSV", "Connect Bank (Plaid)"], key="data_source_radio")

# Initialize session state for data persistence across reruns
if "df" not in st.session_state:
    st.session_state.df = None

# Show file uploader if Upload CSV is selected
if data_source == "Upload CSV":
    uploaded = st.file_uploader("Upload your bank statement (CSV)", type=["csv"])
    if uploaded:
        st.session_state.df = pd.read_csv(uploaded)
    elif st.session_state.df is None:
        st.info("Upload a CSV to begin.")
        st.stop()

# Custom CSS for Coventry Building Society brand button
st.markdown(
    """
    <style>
    .coventry-btn {
        background: linear-gradient(90deg, #009CA6 0%, #006F75 100%);
        color: #fff;
        border: none;
        border-radius: 24px;
        padding: 0.75em 2em;
        font-family: 'Segoe UI', 'Arial', sans-serif;
        font-size: 1.15em;
        font-weight: 500;
        cursor: pointer;
        transition: background 0.3s, box-shadow 0.3s, transform 0.2s;
        box-shadow: 0 2px 8px rgba(0,156,166,0.08);
        outline: none;
        margin-top: 0.5em;
        margin-bottom: 1em;
        letter-spacing: 0.02em;
        display: inline-block;
    }
    .coventry-btn:hover, .coventry-btn:focus {
        background: linear-gradient(90deg, #006F75 0%, #009CA6 100%);
        box-shadow: 0 4px 16px rgba(0,156,166,0.15);
        transform: translateY(-2px) scale(1.03);
    }
    </style>
    """,
    unsafe_allow_html=True
)
from anomaly_model import train_anomaly_model, score_transactions
from insights_engine import (
    get_summary_metrics,
    get_category_breakdown,
    get_trend_data,
    get_anomalies,
    get_health_score,
    generate_insights,
)
from nlp_router import route_query
from banking_api import PlaidBankingAPI

st.set_page_config(page_title="Financial Insights AI", layout="wide")

# Initialize session state for data persistence across reruns
if "df" not in st.session_state:
    st.session_state.df = None
if "selected_tab" not in st.session_state:
    st.session_state.selected_tab = 3  # Default to "Ask AI" tab

# Helper: If Analyse button was clicked, set selected_tab to 3 before rendering tabs
if "analyse_clicked" in st.session_state and st.session_state["analyse_clicked"]:
    st.session_state.selected_tab = 3

# Helper function to create Plaid Link token (for sandbox testing)
def create_plaid_link_token(client_id, secret, environment="sandbox"):
    """Create a Plaid Link token for the UI flow"""
    try:
        url = f"https://{environment}.plaid.com/link/token/create"
        payload = {
            "client_id": client_id,
            "secret": secret,
            "user": {"client_user_id": "test-user-id"},
            "client_name": "Financial Insights AI",
            "language": "en",
            "country_codes": ["US"],
            "products": ["transactions"]
        }
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json().get("link_token")
    except Exception as e:
        st.error(f"Could not create Plaid Link token: {e}")
        return None

if data_source == "Connect Bank (Plaid)":
    st.info("🔗 **Plaid Integration**: Securely connect your bank account")
    
    # Get credentials from environment
    client_id = os.getenv("PLAID_CLIENT_ID")
    secret = os.getenv("PLAID_SECRET")
    environment = os.getenv("PLAID_ENVIRONMENT", "sandbox")
    
    if not client_id or not secret:
        st.warning("⚠️ Plaid credentials not found in environment variables.")
        st.markdown("""
        To use Plaid integration, set environment variables:
        - `PLAID_CLIENT_ID`
        - `PLAID_SECRET`
        - `PLAID_ENVIRONMENT` (sandbox/production)
        """)
        st.stop()
    
    try:
        api = PlaidBankingAPI(client_id=client_id, secret=secret, environment=environment)
        st.success(f"✅ Plaid API connected ({environment})")
    except Exception as e:
        st.error(f"❌ Plaid error: {e}")
        st.stop()
    
    # Initialize session state
    if "plaid_access_token" not in st.session_state:
        st.session_state.plaid_access_token = None
    
    st.subheader("🔐 Connect Your Bank Account")
    
    st.warning("⚠️ **Sandbox Mode**: Using test data only. Upgrade to production for real bank connections.")
    
    # Load access token from file if available
    default_token = ""
    token_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "access_token.txt")
    if os.path.exists(token_file):
        try:
            with open(token_file, "r") as f:
                default_token = f.read().strip()
        except Exception:
            pass
    

    # Input for access token
    col1, col2 = st.columns([3, 1])
    with col1:
        access_token_input = st.text_input(
            "Enter your Plaid access token:",
            value=default_token,
            type="password",
            placeholder="sandbox_..." if environment == "sandbox" else "access-prod-..."
        )

    if access_token_input:
        st.session_state.plaid_access_token = access_token_input
        # Fetch transactions button
        if st.button("🔄 Fetch Transactions", use_container_width=True):
            with st.spinner("Fetching your transactions..."):
                try:
                    st.session_state.df = api.get_transactions(access_token_input, days_back=90)
                    if not st.session_state.df.empty:
                        st.success(f"✅ Loaded {len(st.session_state.df)} transactions from your bank!")
                        st.dataframe(st.session_state.df.head(10), use_container_width=True)
                    else:
                        st.warning("⚠️ No transactions found. Check your access token and try again.")
                except Exception as e:
                    st.error(f"❌ Error fetching transactions: {str(e)}")
                    st.info("💡 Tip: Make sure your access token is valid and from the same environment (sandbox/production).")
    elif st.session_state.df is None:
        st.info("👉 Enter your Plaid access token to fetch transactions.")
        st.stop()

# Only stop if the dataframe is still None after all attempts
if st.session_state.df is None:
    st.stop()

df = load_and_prepare(st.session_state.df)

model = train_anomaly_model(df)
df = score_transactions(model, df)

total_spend, total_income, num_tx = get_summary_metrics(df)
health_score, health_text = get_health_score(df)

st.write(health_text)
st.markdown("---")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Spend", f"£{abs(total_spend):,.2f}")
col2.metric("Total Income", f"£{total_income:,.2f}")
col3.metric("Transactions", num_tx)
col4.metric("Health Score", f"{health_score}/100")

st.write(health_text)
st.markdown("---")


# Budget Recommendation Engine integration
from budget_engine import BudgetRecommendationEngine
st.subheader("Budget Recommendations")
months = st.slider("Select number of months to analyze for budget recommendations:", min_value=1, max_value=12, value=3)
budget_engine = BudgetRecommendationEngine()
recommendations = budget_engine.recommend_budget(df, months=months)
if recommendations:
    st.write(f"Recommended monthly budgets by category (based on last {months} months):")
    st.table({k: f"£{v:,.2f}" for k, v in recommendations.items()})
else:
    st.info("No budget recommendations available.")

tab_labels = ["📊 Summary", "📂 Categories", "⚠️ Anomalies", "💬 Ask AI"]
tab1, tab2, tab3, tab4 = st.tabs(tab_labels)

with tab1:
    st.subheader("Spending Trend")
    trend = get_trend_data(df)
    st.line_chart(trend.set_index("period")["amount"])

    st.subheader("Sample Transactions")
    st.dataframe(df.head(50))

with tab2:
    st.subheader("Category Breakdown")
    cat = get_category_breakdown(df)
    st.bar_chart(cat.set_index("category")["amount"])
    st.dataframe(cat)

with tab3:
    st.subheader("Unusual Transactions")
    anomalies = get_anomalies(df)
    st.dataframe(anomalies)


with tab4:

    st.subheader("Ask a Question")
    q = st.text_input(
        "Your question:",
        placeholder="e.g., starbucks, how much spent, monthly trend, or anything?"
    )

    # Single modern styled Analyse button
    analyse_clicked = st.button("Analyse", key="analyse_btn", help="Analyse your question")
    if analyse_clicked:
        st.session_state["show_ask_ai_response"] = True
    show_ask_ai_response = st.session_state.get("show_ask_ai_response", False) or analyse_clicked
    if show_ask_ai_response:
        if not q.strip():
            st.warning("Please enter a question.")
        else:
            try:
                with st.spinner("Searching..."):
                    intent, params = route_query(q, df)

                # Try to find a matching response for any query
                result = None
                user_message = ""
                if intent == "CATEGORY":
                    cat = params.get("category")
                    if cat:
                        result = df[df["category"] == cat]
                        if len(result) > 0:
                            total = abs(result['amount'].sum())
                            count = len(result)
                            col1, col2, col3 = st.columns(3)
                            col1.metric("Category", cat.title())
                            col2.metric("Total", f"£{total:,.2f}")
                            col3.metric("Count", count)
                            st.dataframe(result.head(15), use_container_width=True)
                        else:
                            user_message = f"No transactions found for category: '{cat}'."
                    else:
                        user_message = f"No matching category found for your query. Try another keyword."

                elif intent == "SEARCH":
                    # Handle fuzzy search results
                    if "search_result" in params:
                        result = params["search_result"]
                    else:
                        merchant = params.get("merchant")
                        amount_min = params.get("amount_min")
                        amount_max = params.get("amount_max")
                        import re
                        result = df.copy()
                        if merchant:
                            mask = False
                            for col in ["description", "merchant", "name"]:
                                if col in df.columns:
                                    mask = mask | df[col].astype(str).str.contains(re.escape(merchant), case=False, na=False)
                            result = result[mask]
                        if amount_min is not None or amount_max is not None:
                            if amount_min is not None:
                                result = result[abs(result["amount"]) >= amount_min]
                            if amount_max is not None:
                                result = result[abs(result["amount"]) <= amount_max]
                    if result is not None and len(result) > 0:
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Found", len(result))
                        col2.metric("Total", f"£{abs(result['amount'].sum()):,.2f}")
                        col3.metric("Avg", f"£{abs(result['amount'].mean()):,.2f}")
                        if params.get("is_fuzzy_search"):
                            search_terms = ", ".join(result['description'].unique()[:3]) if 'description' in result.columns else "Custom search"
                            st.caption(f"📍 Matched: {search_terms}")
                        st.dataframe(result.head(15), use_container_width=True)
                    else:
                        user_message = f"No transactions matched your search for: '{q}'. Please try a different keyword or phrase."

                elif intent == "ANOMALIES":
                    if anomalies is not None and len(anomalies) > 0:
                        col1, col2 = st.columns(2)
                        col1.metric("Anomalies", len(anomalies))
                        col2.metric("Avg", f"£{abs(anomalies['amount'].mean()):,.2f}")
                        st.dataframe(anomalies.head(10), use_container_width=True)
                    else:
                        user_message = "No anomalies detected in your transactions."

                elif intent == "HEALTH":
                    col1, col2 = st.columns(2)
                    col1.metric("Health Score", f"{health_score}/100")
                    col1.progress(health_score/100)
                    col2.write(health_text)

                elif intent == "TREND":
                    trend = get_trend_data(df)
                    if trend is not None and len(trend) > 0:
                        st.line_chart(trend.set_index("period")["amount"], height=300)
                    else:
                        user_message = "No trend data available for your transactions."

                elif intent == "SUMMARY":
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Spend", f"£{abs(total_spend):,.2f}")
                    col2.metric("Income", f"£{total_income:,.2f}")
                    col3.metric("Net", f"£{total_income - abs(total_spend):,.2f}")
                    col4.metric("Txns", num_tx)

                else:
                    user_message = "Sorry, I couldn't understand your question. Please try rephrasing or use a different keyword."

                if user_message:
                    st.info(user_message)

            except Exception as e:
                st.error(f"Error: {str(e)}")


st.caption("Built by Vinoth Durairaj — Open‑Source Financial AI for Everyone.")