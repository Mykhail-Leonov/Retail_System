import joblib
import pandas as pd
from prediction_data import (
    DATA_FILE, FEATURE_COLUMNS, MAX_MONTHS_AHEAD, VALID_LABELS,
    load_sales_data, clean_sales_data, build_features
)
from train_prediction_model import MODEL_FILE


class DemandPredictionService:

    def __init__(self, dataset_file=DATA_FILE, model_file=MODEL_FILE):
        # Load the saved models
        try:
            self.__bundle = joblib.load(model_file)
        except FileNotFoundError:
            raise FileNotFoundError("Model file not found. Run the training script first.")

        # Load the sales history
        self.__history, _ = clean_sales_data(load_sales_data(dataset_file))
        self.__last_month = pd.Period(self.__history["month"].max(), freq="M")

        # Check the saved model settings
        if self.__bundle.get("features") != FEATURE_COLUMNS:
            raise ValueError("Model features do not match the prediction code.")
        if set(self.__bundle.get("models", {})) != {"in_store", "online"}:
            raise ValueError("One or more prediction models are missing.")
        if self.__bundle.get("max_months_ahead") != MAX_MONTHS_AHEAD:
            raise ValueError("Model prediction range does not match.")
        if self.__bundle.get("last_month") != str(self.__last_month):
            raise ValueError("Sales data and models are out of date. Train the models again.")

    # Find a product in the sales history
    def get_product_name(self, product_id):
        product_id, sales = self.__get_product_sales(product_id)
        return sales.iloc[-1]["product_name"]

    def __get_product_sales(self, product_id):
        if isinstance(product_id, (bool, float)):
            raise ValueError("Enter a valid product ID.")
        try:
            product_id = int(product_id)
        except (TypeError, ValueError):
            raise ValueError("Enter a valid product ID.")

        if product_id <= 0:
            raise ValueError("Product ID must be positive.")

        sales = self.__history[self.__history["product_id"] == product_id]
        if sales.empty:
            raise KeyError("No sales history found for this product ID.")

        return product_id, sales

    # Find products in the historical sales data
    def search_products(self, query):
        if not isinstance(query, str) or not query.strip():
            raise ValueError("Enter a product name or ID.")

        products = self.__history[["product_id", "product_name"]].drop_duplicates()
        query = query.strip()
        if query.isdigit():
            matches = products[products["product_id"] == int(query)]
        else:
            matches = products[products["product_name"].str.contains(
                query, case=False, regex=False)]

        return [
            {"product_id": int(row["product_id"]), "product_name": row["product_name"]}
            for _, row in matches.sort_values("product_name").iterrows()
        ]

    # Months that can be predicted
    def available_months(self):
        return (
            str(self.__last_month + 1),
            str(self.__last_month + MAX_MONTHS_AHEAD)
        )

    # Predict demand for one product and month
    def predict_product(self, product_id, month, year):
        product_id, history = self.__get_product_sales(product_id)

        # Check the selected date
        if type(month) is not int or not 1 <= month <= 12:
            raise ValueError("Month must be between 1 and 12.")
        if type(year) is not int or not 1900 <= year <= 2100:
            raise ValueError("Enter a valid year.")

        target = pd.Period(year=year, month=month, freq="M")
        months_ahead = target.ordinal - self.__last_month.ordinal

        if not 1 <= months_ahead <= MAX_MONTHS_AHEAD:
            first, last = self.available_months()
            raise ValueError("Choose a month from {} to {}.".format(first, last))

        # Check recent sales for this product
        if pd.Period(history["month"].max(), freq="M") != self.__last_month:
            raise ValueError("No recent sales found for this product.")

        features = build_features(product_id, history, target)
        X = pd.DataFrame([features])[FEATURE_COLUMNS]

        # Get the two predictions
        predictions = {}
        for channel in ["in_store", "online"]:
            label = str(self.__bundle["models"][channel].predict(X)[0])
            if label not in VALID_LABELS:
                raise ValueError("Unexpected prediction result.")
            predictions[channel] = label

        return {
            "product_id": product_id,
            "product_name": history.iloc[-1]["product_name"],
            "month": str(target),
            "months_ahead": months_ahead,
            "in_store": predictions["in_store"],
            "online": predictions["online"]
        }
