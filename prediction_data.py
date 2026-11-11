
from pathlib import Path
import pandas as pd

DATA_FILE = Path(__file__).resolve().parent / "smart_retail_sales.csv"

REQUIRED_COLUMNS = [
    "month", "product_id", "product_name", "category",
    "in_store_units_sold", "online_units_sold", "demand_label"
]

VALID_LABELS = ["Low", "Medium", "High"]


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
