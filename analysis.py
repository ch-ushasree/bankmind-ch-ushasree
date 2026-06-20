from pathlib import Path

import pandas as pd

#Define path to the dataset
DATA_PATH = Path(__file__).parent / "bank+marketing" / "bank" / "bank-full.csv"


def subscription_rate_by(df: pd.DataFrame, column: str) -> pd.DataFrame:
    return (
        df.assign(subscribed=df["y"].eq("yes"))
        .groupby(column, observed=False)
        .agg(customers=("subscribed", "size"), subscribers=("subscribed", "sum"), subscription_rate=("subscribed", "mean"))
        .assign(subscription_rate_pct=lambda table: table["subscription_rate"] * 100)
        .sort_values("subscription_rate_pct", ascending=False)
    )


def main():
    #Load the dataset with the seperator ";" and create helper columns for analysis
    df = pd.read_csv(DATA_PATH, sep=";")
    original_shape = df.shape

    #create age groups 
    df["age_group"] = pd.cut(
        df["age"],
        bins=[17, 30, 45, 60, float("inf")],
        labels=["18-30", "31-45", "46-60", "60+"],
    )

    #create balance bands 
    df["balance_band"] = pd.cut(
        df["balance"],
        bins=[float("-inf"), -1, 500, 1500, 5000, float("inf")],
        labels=["Negative balance", "0-500", "501-1,500", "1,501-5,000", "5,000+"],
    )

    #define ordered categories for the combined debt profile
    debt_order = [
        "No housing + No personal loan",
        "No housing + Has personal loan",
        "Has housing + No personal loan",
        "Has housing + Has personal loan",
    ]

    #Create a combined debt profile column based on the housing and loan status 
    df["debt_profile"] = pd.Categorical(
        [
            debt_order[0]
            if housing == "no" and loan == "no"
            else debt_order[1]
            if housing == "no" and loan == "yes"
            else debt_order[2]
            if housing == "yes" and loan == "no"
            else debt_order[3]
            for housing, loan in zip(df["housing"], df["loan"])
        ],
        categories=debt_order,
        ordered=True,
    )

    #Print data overview and insights
    print("Original dataset shape:", original_shape)
    print("Analysis dataset shape after helper columns:", df.shape)
    print("\nData types:")
    print(df.dtypes)
    print("\nMissing values:")
    print(df.isna().sum())
    print("\nTarget distribution (%):")
    print(df["y"].value_counts(normalize=True).mul(100).round(2))
    print("\nSubscription rate by job:")
    print(subscription_rate_by(df, "job"))
    print("\nSubscription rate by balance band:")
    print(subscription_rate_by(df, "balance_band"))
    print("\nSubscription rate by age group:")
    print(subscription_rate_by(df, "age_group"))
    print("\nSubscription rate by housing loan:")
    print(subscription_rate_by(df, "housing"))
    print("\nSubscription rate by combined debt profile:")
    print(subscription_rate_by(df, "debt_profile"))

#Entry point for the script
if __name__ == "__main__":
    main()
