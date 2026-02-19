def get_summary_metrics(df):
    total_spend = df[df["amount"] < 0]["amount"].sum()
    total_income = df[df["amount"] > 0]["amount"].sum()
    num_tx = len(df)
    return total_spend, total_income, num_tx

def get_category_breakdown(df):
    return df.groupby("category")["amount"].sum().reset_index()

def get_trend_data(df):
    return (
        df.assign(period=df["date"].dt.to_period("M").astype(str))
          .groupby("period")["amount"]
          .sum()
          .reset_index()
    )

def get_anomalies(df):
    return df[df["is_anomaly"] == True]

def get_health_score(df):
    anomalies = df["is_anomaly"].sum()
    savings_ratio = df[df["amount"] > 0]["amount"].sum() / abs(df[df["amount"] < 0]["amount"].sum() + 1)

    score = 100
    score -= anomalies * 2
    score += min(savings_ratio * 10, 20)

    score = max(0, min(100, int(score)))

    explanation = "Your financial health is moderate."
    if score > 80:
        explanation = "Your financial health is strong."
    elif score < 50:
        explanation = "Your financial health needs improvement."

    return score, explanation

def generate_insights(df):
    insights = []

    groceries = df[df["category"] == "Groceries"]["amount"].sum()
    if groceries:
        insights.append(f"Your grocery spending this period is £{abs(groceries):,.2f}.")

    anomalies = df["is_anomaly"].sum()
    if anomalies > 0:
        insights.append(f"{anomalies} transactions appear unusual.")

    return insights