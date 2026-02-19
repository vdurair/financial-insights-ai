import pandas as pd

class BudgetRecommendationEngine:
    def __init__(self):
        pass

    def recommend_budget(self, df, categories=None, months=3):
        """
        Recommend monthly budget for each category based on past spending.
        df: DataFrame with columns ['date', 'amount', 'category']
        categories: list of categories to recommend for (optional)
        months: number of past months to analyze
        Returns: dict {category: recommended_budget}
        """
        df = df.copy()
        df['date'] = pd.to_datetime(df['date'])
        cutoff = df['date'].max() - pd.DateOffset(months=months)
        df_recent = df[df['date'] >= cutoff]
        if categories is None:
            categories = df_recent['category'].unique()
        recommendations = {}
        for cat in categories:
            cat_spend = df_recent[df_recent['category'] == cat]['amount']
            monthly_avg = abs(cat_spend.sum()) / months if months > 0 else 0
            recommendations[cat] = round(monthly_avg, 2)
        return recommendations
