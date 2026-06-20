# Bank RM Cross-Sell Insights Dashboard

This is a Track A data analysis submission for the AI-driven cross-sell recommendation system project. It helps a bank Relationship Manager understand which customer segments are more likely to accept a new financial product.

## What It Does

- Loads the UCI Bank Marketing `bank-full.csv` dataset.
- Shows dataset shape, data types, missing values, and target distribution.
- Answers the required business questions with interactive charts.
- Adds RM-friendly sidebar filters and KPI cards.
- Uses tabs for exploratory analysis, the daily RM priority list, and data health/raw samples.
- Adds a combined debt-profile insight using both `housing` and `loan`.
- Includes a priority-segment table to highlight promising customer groups without forcing daily users to scroll past every chart.

## Dataset

This project uses the UCI Bank Marketing Dataset from a Portuguese bank's direct marketing campaign. The app expects the full dataset file:

```text
bank+marketing/bank/bank-full.csv
```

Download source: [UCI Bank Marketing Dataset](https://archive.ics.uci.edu/dataset/222/bank+marketing)

Key columns:

- `age`, `job`, `marital`, `education`: customer demographics
- `balance`: average yearly account balance in EUR
- `housing`, `loan`: existing loan products
- `y`: whether the customer subscribed to the offered product

## Project Structure

```text
AI club/
|-- app.py                         # Main Streamlit dashboard
|-- analysis.py                    # Standalone analysis script
|-- EXPLANATION.md                 # Required written explanation
|-- README.md                      # Project overview and run instructions
|-- requirements.txt               # Python dependencies
|-- .gitignore                     # Keeps only bank-full.csv from the dataset folder
`-- bank+marketing/
    `-- bank/
        `-- bank-full.csv          # Dataset used by the app
```

## Run Locally

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the Streamlit dashboard:

```bash
streamlit run app.py
```

Optional script version of the analysis:

```bash
python analysis.py
```

## Notes For Submission

The repository is configured to include only `bank+marketing/bank/bank-full.csv` from the extracted dataset folder. Extra UCI files such as `bank.csv`, `bank-names.txt`, and `bank-additional/` are ignored.
