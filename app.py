from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st


#Path to the bank marketing dataset 
DATA_PATH = Path(__file__).parent / "bank+marketing" / "bank" / "bank-full.csv"

#Derived features that are added to the dataset for analysis and display purposes. These columns are not part of the original dataset but are created based on the original data to facilitate insights and visualizations in the dashboard.
DERIVED_COLUMNS = ["subscribed", "subscription_status", "age_group", "balance_band", "debt_profile"]

#Streamlit page configuration and custom CSS for styling the dashboard components.
st.set_page_config(
    page_title="Bank RM Cross-Sell Insights",
    layout="wide",
)

st.markdown(
    """
    <style>
    .stApp h1,
    .stApp h2,
    .stApp h3,
    [data-testid="stMarkdownContainer"] h1,
    [data-testid="stMarkdownContainer"] h2,
    [data-testid="stMarkdownContainer"] h3 {
        color: rgb(61, 157, 243) !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        border-bottom: 1px solid #d9e2ec;
    }
    .stTabs [data-baseweb="tab"] {
        height: 46px;
        padding: 0 18px;
        border-radius: 6px 6px 0 0;
        background-color: #f7fafc;
        color: #1f2933;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #e6f4f1;
        border-bottom: 3px solid #2a9d8f;
        color: #102a43;
    }
    [data-testid="stMetric"] {
        background-color: #fbfcfd;
        border: 1px solid #e5ebf0;
        border-radius: 8px;
        padding: 14px 16px;
    }
    [data-testid="stMetric"] * {
        color: #102a43;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Data loading and preprocessing 

@st.cache_data
def load_data() -> pd.DataFrame:
    """Load the UCI bank marketing dataset and add analysis-friendly columns."""
    df = pd.read_csv(DATA_PATH, sep=";")
    df["subscribed"] = df["y"].eq("yes").astype(int)
    df["subscription_status"] = np.where(df["subscribed"].eq(1), "Subscribed", "Not subscribed")
    df["age_group"] = pd.cut(
        df["age"],
        bins=[17, 30, 45, 60, np.inf],
        labels=["18-30", "31-45", "46-60", "60+"],
        right=True,
    )
    df["balance_band"] = pd.cut(
        df["balance"],
        bins=[-np.inf, -1, 500, 1500, 5000, np.inf],
        labels=["Negative balance", "0-500", "501-1,500", "1,501-5,000", "5,000+"],
        right=True,
    )
    debt_order = [
        "No housing + No personal loan",
        "No housing + Has personal loan",
        "Has housing + No personal loan",
        "Has housing + Has personal loan",
    ]
    df["debt_profile"] = np.select(
        [
            df["housing"].eq("no") & df["loan"].eq("no"),
            df["housing"].eq("no") & df["loan"].eq("yes"),
            df["housing"].eq("yes") & df["loan"].eq("no"),
            df["housing"].eq("yes") & df["loan"].eq("yes"),
        ],
        debt_order,
        default="Unknown",
    )
    df["debt_profile"] = pd.Categorical(df["debt_profile"], categories=debt_order, ordered=True)
    return df

# Filtering and sidebar controls 
def apply_filters(df: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.header("RM Filters")
    st.sidebar.caption("Use these to focus the insights on a specific customer base.")

    jobs = st.sidebar.multiselect("Job type", sorted(df["job"].unique()))
    education = st.sidebar.multiselect("Education", sorted(df["education"].unique()))
    marital = st.sidebar.multiselect("Marital status", sorted(df["marital"].unique()))
    housing = st.sidebar.multiselect("Housing loan", sorted(df["housing"].unique()))
    loan = st.sidebar.multiselect("Personal loan", sorted(df["loan"].unique()))

    min_age, max_age = int(df["age"].min()), int(df["age"].max())
    age_range = st.sidebar.slider("Age range", min_age, max_age, (min_age, max_age))

    min_balance, max_balance = int(df["balance"].min()), int(df["balance"].max())
    balance_range = st.sidebar.slider(
        "Account balance range",
        min_balance,
        max_balance,
        (min_balance, max_balance),
        step=100,
    )

    filtered = df.copy()
    if jobs:
        filtered = filtered[filtered["job"].isin(jobs)]
    if education:
        filtered = filtered[filtered["education"].isin(education)]
    if marital:
        filtered = filtered[filtered["marital"].isin(marital)]
    if housing:
        filtered = filtered[filtered["housing"].isin(housing)]
    if loan:
        filtered = filtered[filtered["loan"].isin(loan)]

    filtered = filtered[
        filtered["age"].between(age_range[0], age_range[1])
        & filtered["balance"].between(balance_range[0], balance_range[1])
    ]
    return filtered


def subscription_summary(df: pd.DataFrame, group_col: str) -> pd.DataFrame:
    summary = (
        df.groupby(group_col, observed=False)
        .agg(
            customers=("subscribed", "size"),
            subscribers=("subscribed", "sum"),
            subscription_rate=("subscribed", "mean"),
            avg_balance=("balance", "mean"),
        )
        .reset_index()
    )
    summary["subscription_rate_pct"] = summary["subscription_rate"] * 100
    return summary


def add_rate_bar(summary: pd.DataFrame, x_col: str, title: str):
    fig = px.bar(
        summary,
        x=x_col,
        y="subscription_rate_pct",
        text=summary["subscription_rate_pct"].round(1).astype(str) + "%",
        hover_data={
            "customers": ":,",
            "subscribers": ":,",
            "subscription_rate_pct": ":.2f",
        },
        labels={
            x_col: "",
            "subscription_rate_pct": "Subscription rate (%)",
            "customers": "Customers",
            "subscribers": "Subscribers",
        },
        title=title,
        color="subscription_rate_pct",
        color_continuous_scale=["#d8e2dc", "#4d908e", "#f94144"],
    )
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_layout(
        height=420,
        coloraxis_showscale=False,
        margin=dict(t=70, b=40, l=30, r=20),
    )
    return fig


def build_priority_segments(df: pd.DataFrame) -> pd.DataFrame:
    segment_cols = ["job", "age_group", "education", "housing", "loan"]
    segments = (
        df.groupby(segment_cols, observed=False)
        .agg(
            customers=("subscribed", "size"),
            subscribers=("subscribed", "sum"),
            subscription_rate=("subscribed", "mean"),
            avg_balance=("balance", "mean"),
        )
        .reset_index()
    )
    segments = segments[segments["customers"] >= 100].copy()
    if segments.empty:
        return segments

    balance_rank = segments["avg_balance"].rank(pct=True)
    volume_rank = segments["customers"].rank(pct=True)
    segments["rm_priority_score"] = (
        segments["subscription_rate"] * 70
        + balance_rank * 15
        + volume_rank * 15
    )
    segments["subscription_rate"] = segments["subscription_rate"] * 100
    segments["avg_balance"] = segments["avg_balance"].round(0)
    segments["rm_priority_score"] = segments["rm_priority_score"].round(1)
    return segments.sort_values("rm_priority_score", ascending=False)


def show_dataset_health(df: pd.DataFrame, expanded: bool = False):
    raw_df = df.drop(columns=DERIVED_COLUMNS, errors="ignore")
    with st.expander("Dataset health check", expanded=expanded):
        left, right = st.columns(2)
        with left:
            st.write("Shape")
            st.code(f"{raw_df.shape[0]:,} rows x {raw_df.shape[1]:,} original columns")
            st.write("Data types")
            st.dataframe(raw_df.dtypes.astype(str).rename("dtype"), use_container_width=True)
        with right:
            missing = raw_df.isna().sum().rename("missing_values")
            st.write("Missing values")
            st.dataframe(missing[missing.gt(0)] if missing.gt(0).any() else missing, use_container_width=True)
            st.write("Target distribution")
            target_distribution = pd.DataFrame(
                {
                    "customers": raw_df["y"].value_counts(),
                    "percentage": raw_df["y"].value_counts(normalize=True).mul(100).round(2),
                }
            )
            st.dataframe(target_distribution, use_container_width=True)


def main():
    if not DATA_PATH.exists():
        st.error(f"Dataset not found at {DATA_PATH}")
        st.stop()

    df = load_data()
    filtered = apply_filters(df)

    st.title("AI-Driven Cross-Sell Insights for Bank Relationship Managers")
    st.caption(
        "An interactive Track A dashboard using the UCI Bank Marketing Dataset. "
        "The goal is to reveal which customer groups are most likely to accept a new financial product."
    )

    if filtered.empty:
        st.warning("No customers match the current filters. Relax one or more filters to continue.")
        st.stop()

    total_customers = len(filtered)
    subscribers = int(filtered["subscribed"].sum())
    subscription_rate = filtered["subscribed"].mean() * 100
    avg_balance = filtered["balance"].mean()
    top_job_row = subscription_summary(filtered, "job").sort_values("subscription_rate_pct", ascending=False).iloc[0]

    kpi_cols = st.columns(5)
    kpi_cols[0].metric("Customers", f"{total_customers:,}")
    kpi_cols[1].metric("Subscribers", f"{subscribers:,}")
    kpi_cols[2].metric("Subscription rate", f"{subscription_rate:.2f}%")
    kpi_cols[3].metric("Avg. balance", f"{avg_balance:,.0f} EUR")
    kpi_cols[4].metric("Best job segment", str(top_job_row["job"]), f"{top_job_row['subscription_rate_pct']:.1f}%")

    analysis_tab, priority_tab, data_tab = st.tabs(
        ["Exploratory Analysis", "RM Priority List", "Data Health + Raw Data"]
    )

    #TAB - 1 : Exploratory Analysis 
    with analysis_tab:
        st.subheader("Exploratory Analysis")
        st.caption("Use this tab when you want to understand the patterns behind product subscription.")

        #Chart 1 : Subscription by job type 
        job_summary = subscription_summary(filtered, "job").sort_values("subscription_rate_pct", ascending=False)
        st.plotly_chart(
            add_rate_bar(job_summary, "job", "Which job types have the highest subscription rate?"),
            use_container_width=True,
        )
        st.info(
            f"{job_summary.iloc[0]['job']} customers currently lead this filtered view at "
            f"{job_summary.iloc[0]['subscription_rate_pct']:.2f}%. "
            "For RMs, this separates high-conversion segments from high-volume but lower-response segments."
        )

        #Charts 2 and 3 : Age and balance segmentation views 
        col_a, col_b = st.columns(2)
        with col_a:
            balance_summary = subscription_summary(filtered, "balance_band")
            st.plotly_chart(
                add_rate_bar(balance_summary, "balance_band", "Does balance change subscription likelihood?"),
                use_container_width=True,
            )
            best_balance = balance_summary.sort_values("subscription_rate_pct", ascending=False).iloc[0]
            st.info(
                f"The strongest balance band in this view is {best_balance['balance_band']} "
                f"at {best_balance['subscription_rate_pct']:.2f}%. "
                "This helps RMs prioritize customers with stronger deposit relationships."
            )

        with col_b:
            age_summary = subscription_summary(filtered, "age_group")
            st.plotly_chart(
                add_rate_bar(age_summary, "age_group", "How does subscription differ across age groups?"),
                use_container_width=True,
            )
            best_age = age_summary.sort_values("subscription_rate_pct", ascending=False).iloc[0]
            st.info(
                f"The highest age-group response in this view is {best_age['age_group']} "
                f"at {best_age['subscription_rate_pct']:.2f}%. "
                "Age can be a practical targeting lens when combined with job and loan status."
            )

        #Chart-4 : Housing loan impact on subscription
        housing_summary = subscription_summary(filtered, "housing").sort_values("housing")
        st.plotly_chart(
            add_rate_bar(housing_summary, "housing", "Does having a housing loan reduce product uptake?"),
            use_container_width=True,
        )
        if set(housing_summary["housing"]) == {"no", "yes"}:
            no_rate = housing_summary.loc[housing_summary["housing"].eq("no"), "subscription_rate_pct"].iloc[0]
            yes_rate = housing_summary.loc[housing_summary["housing"].eq("yes"), "subscription_rate_pct"].iloc[0]
            st.info(
                f"Customers without a housing loan convert at {no_rate:.2f}% versus {yes_rate:.2f}% "
                "for customers with a housing loan. This suggests existing debt commitments matter in cross-sell timing."
            )

        #Chart-5 : Combined debt profile view (Most actionable debt segmentation for RMs)
        debt_summary = subscription_summary(filtered, "debt_profile")
        st.plotly_chart(
            add_rate_bar(debt_summary, "debt_profile", "Debt load reveals which calls RMs should deprioritize"),
            use_container_width=True,
        )
        if len(debt_summary) == 4:
            debt_free_rate = debt_summary.loc[
                debt_summary["debt_profile"].eq("No housing + No personal loan"), "subscription_rate_pct"
            ].iloc[0]
            double_debt_rate = debt_summary.loc[
                debt_summary["debt_profile"].eq("Has housing + Has personal loan"), "subscription_rate_pct"
            ].iloc[0]
            st.warning(
                f"Debt-free customers convert at {debt_free_rate:.2f}%, while customers carrying both housing and personal "
                f"loans convert at only {double_debt_rate:.2f}%. For an RM, this is more actionable than the housing-only "
                "view: customers with two active loan commitments are low-priority outreach unless there is another strong signal."
            )

    #Tab-2 : RM priority list 
    with priority_tab:
        st.subheader("RM Priority List")
        st.caption(
            "A daily call-planning view. Segments are ranked using subscription rate, average balance, and segment size. "
            "This is an analytical priority score, not a trained prediction model."
        )
        segments = build_priority_segments(filtered)
        if segments.empty:
            st.warning("Not enough customers in the filtered view to build stable priority segments.")
        else:
            display_cols = [
                "rm_priority_score",
                "job",
                "age_group",
                "education",
                "housing",
                "loan",
                "customers",
                "subscribers",
                "subscription_rate",
                "avg_balance",
            ]
            top_segment = segments.iloc[0]
            seg_cols = st.columns(4)
            seg_cols[0].metric("Top score", f"{top_segment['rm_priority_score']:.1f}")
            seg_cols[1].metric("Top segment rate", f"{top_segment['subscription_rate']:.2f}%")
            seg_cols[2].metric("Segment customers", f"{int(top_segment['customers']):,}")
            seg_cols[3].metric("Avg. segment balance", f"{top_segment['avg_balance']:,.0f} EUR")
            st.dataframe(
                segments[display_cols].head(20),
                use_container_width=True,
                hide_index=True,
                column_config={
                    "rm_priority_score": st.column_config.NumberColumn("Priority score", format="%.1f"),
                    "subscription_rate": st.column_config.NumberColumn("Subscription rate (%)", format="%.2f"),
                    "avg_balance": st.column_config.NumberColumn("Avg. balance (EUR)", format="%.0f"),
                },
            )
            st.info(
                "This tab is designed for repeat use: an RM can open the tool, apply portfolio filters, "
                "and go straight to the call-priority table without scrolling through exploratory charts."
            )

    #Tab-3 : Data health and raw data display for auditing and transparency
    with data_tab:
        st.subheader("Data Health + Raw Data")
        st.caption("Use this tab to audit the filtered dataset before trusting the dashboard conclusions.")
        show_dataset_health(filtered, expanded=True)
        st.write("Filtered customer sample")
        st.dataframe(filtered.drop(columns=DERIVED_COLUMNS, errors="ignore").head(200), use_container_width=True)


if __name__ == "__main__":
    main()
