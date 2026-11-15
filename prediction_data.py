from pathlib import Path
import pandas as pd

DATA_FILE = Path(__file__).resolve().parent / "smart_retail_sales.csv"

REQUIRED_COLUMNS = [
    "month", "product_id", "product_name", "category",
    "in_store_units_sold", "online_units_sold", "demand_label"
]

VALID_LABELS = ["Low", "Medium", "High"]


MAX_MONTHS_AHEAD = 12
HISTORY_MONTHS = 12
FEATURE_COLUMNS = [
    "product_id", "month_number", "months_ahead",
    "last_store", "last_online", "average_store_3", "average_online_3",
    "average_store_12", "average_online_12"
]


# Load sales data
def load_sales_data(filename=DATA_FILE):
    try:
        df = pd.read_csv(filename)
    except FileNotFoundError:
        raise FileNotFoundError("Sales dataset could not be found.")

    # Check columns
    for column in REQUIRED_COLUMNS:
        if column not in df.columns:
            raise KeyError("Missing required column: " + column)

    # Check if empty
    if df.empty:
        raise ValueError("Sales dataset is empty.")

    return df


# Clean sales data
def clean_sales_data(df):

    # Check columns
    for column in REQUIRED_COLUMNS:
        if column not in df.columns:
            raise KeyError("Missing required column: " + column)

    if df.empty:
        raise ValueError("Sales dataset is empty.")

    # Copy the data
    clean = df.copy()

    # Convert dates
    clean["month"] = pd.to_datetime(
        clean["month"], format="%Y-%m", errors="coerce"
    )

    # Convert numbers
    number_columns = [
        "product_id", "in_store_units_sold", "online_units_sold"
    ]

    for column in number_columns:
        clean[column] = pd.to_numeric(clean[column], errors="coerce")

    # Clean text
    for column in ["product_name", "category", "demand_label"]:
        clean[column] = clean[column].fillna("").astype(str).str.strip()

    # Remove missing values
    clean = clean.dropna(subset=REQUIRED_COLUMNS)

    # Remove invalid numbers
    clean = clean[
        (clean["product_id"] > 0)
        & (clean["in_store_units_sold"] >= 0)
        & (clean["online_units_sold"] >= 0)
    ]

    # Check for whole numbers
    for column in number_columns:
        clean = clean[clean[column] % 1 == 0]

    # Check names and labels
    clean = clean[
        (clean["product_name"] != "")
        & (clean["category"] != "")
        & clean["demand_label"].isin(VALID_LABELS)
    ]

    invalid_count = len(df) - len(clean)

    # Remove duplicate records
    before_duplicates = len(clean)
    clean = clean.drop_duplicates(subset=["product_id", "month"])
    duplicate_count = before_duplicates - len(clean)

    # Check if any valid data remains
    if clean.empty:
        raise ValueError("No valid sales data remains after cleaning.")

    # Check product names and categories
    if (clean.groupby("product_id")["product_name"].nunique() > 1).any():
        raise ValueError("Conflicting product names found for one product ID.")

    if (clean.groupby("product_id")["category"].nunique() > 1).any():
        raise ValueError("Conflicting product categories found for one product ID.")

    # Convert to integers
    for column in number_columns:
        clean[column] = clean[column].astype(int)

    # Sort the data
    clean = clean.sort_values(
        ["product_id", "month"]
    ).reset_index(drop=True)

    # Cleaning summary
    summary = {
        "original": len(df),
        "invalid": invalid_count,
        "duplicates": duplicate_count,
        "clean": len(clean)
    }

    return clean, summary


# Prepare one prediction input
def build_features(product_id, history, target_month):
    # Use the last 12 months of sales
    recent = history.sort_values("month").tail(HISTORY_MONTHS)
    if len(recent) < HISTORY_MONTHS:
        raise ValueError("At least 12 months of sales history are required.")

    # Check there are no missing months
    months = recent["month"].dt.to_period("M").tolist()
    for i in range(1, len(months)):
        if months[i] != months[i - 1] + 1:
            raise ValueError("The last 12 months must be consecutive.")

    target = pd.Period(target_month, freq="M")
    months_ahead = target.ordinal - months[-1].ordinal

    if not 1 <= months_ahead <= MAX_MONTHS_AHEAD:
        raise ValueError("Prediction must be 1 to 12 months ahead.")

    last = recent.iloc[-1]
    last_three = recent.tail(3)

    return {
        "product_id": int(product_id),
        "month_number": int(target.month),
        "months_ahead": months_ahead,
        "last_store": int(last["in_store_units_sold"]),
        "last_online": int(last["online_units_sold"]),
        "average_store_3": float(last_three["in_store_units_sold"].mean()),
        "average_online_3": float(last_three["online_units_sold"].mean()),
        "average_store_12": float(recent["in_store_units_sold"].mean()),
        "average_online_12": float(recent["online_units_sold"].mean())
    }

# Make examples for training the model
def prepare_training_data(clean):
    examples = []

    for product_id, group in clean.groupby("product_id"):
        group = group.sort_values("month").reset_index(drop=True)
        sales_by_month = {
            pd.Period(row["month"], freq="M"): row
            for _, row in group.iterrows()
        }

        # Start after the first 12 months
        for i in range(HISTORY_MONTHS - 1, len(group)):
            history = group.iloc[i - HISTORY_MONTHS + 1:i + 1]
            start_month = pd.Period(history.iloc[-1]["month"], freq="M")

            for months_ahead in range(1, MAX_MONTHS_AHEAD + 1):
                target_month = start_month + months_ahead
                target = sales_by_month.get(target_month)
                if target is None:
                    continue

                try:
                    features = build_features(product_id, history, target_month)
                except ValueError:
                    continue

                # Target month's sales are answers, not input features
                features["target_month"] = target_month.to_timestamp()
                features["demand_label"] = target["demand_label"]
                features["in_store_units_sold"] = int(target["in_store_units_sold"])
                features["online_units_sold"] = int(target["online_units_sold"])
                examples.append(features)

    if not examples:
        raise ValueError("Not enough historical data for training.")

    return pd.DataFrame(examples)
