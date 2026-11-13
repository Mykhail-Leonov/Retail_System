from pathlib import Path
import joblib
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score
from prediction_data import (
    DATA_FILE, FEATURE_COLUMNS, MAX_MONTHS_AHEAD,
    load_sales_data, clean_sales_data, prepare_training_data, build_features
)

MODEL_FILE = Path(__file__).resolve().parent / "retail_demand_models.joblib"

CHANNEL_COLUMNS = {
    "in_store": "in_store_units_sold",
    "online": "online_units_sold"
}


# Find Low, Medium and High ranges for each sales channel
def get_thresholds(data):
    thresholds = {}
    for channel, column in CHANNEL_COLUMNS.items():
        thresholds[channel] = (
            float(data[column].quantile(1 / 3)),
            float(data[column].quantile(2 / 3))
        )
    return thresholds


# Get the correct labels for each model
def get_labels(data, channel, thresholds):
    if channel == "overall":
        return data["demand_label"]

    low, high = thresholds[channel]

    def find_label(units):
        if units <= low:
            return "Low"
        if units <= high:
            return "Medium"
        return "High"

    return data[CHANNEL_COLUMNS[channel]].apply(find_label)


# Train the three Decision Tree models
def fit_models(data, thresholds):
    models = {}
    X = data[FEATURE_COLUMNS]

    for channel in ["overall", "in_store", "online"]:
        y = get_labels(data, channel, thresholds)
        model = DecisionTreeClassifier(max_depth=3, random_state=42)
        model.fit(X, y)
        models[channel] = model

    return models


# Check predictions on the last 12 historical months
def evaluate_models(clean, examples):
    last_month = pd.Period(clean["month"].max(), freq="M")
    cutoff = last_month - MAX_MONTHS_AHEAD
    cutoff_date = cutoff.to_timestamp()

    # Only train on data known before the test period
    old_sales = clean[clean["month"] <= cutoff_date]
    training = examples[examples["target_month"] <= cutoff_date]

    if training.empty:
        raise ValueError("Not enough historical data for model testing.")

    thresholds = get_thresholds(old_sales)
    models = fit_models(training, thresholds)

    # Predict future months with the same historical cutoff
    test_rows = []
    for product_id, product_sales in clean.groupby("product_id"):
        history = product_sales[product_sales["month"] <= cutoff_date]

        for months_ahead in range(1, MAX_MONTHS_AHEAD + 1):
            target_month = cutoff + months_ahead
            actual = product_sales[
                product_sales["month"] == target_month.to_timestamp()
            ]
            if actual.empty:
                continue

            try:
                features = build_features(product_id, history, target_month)
            except ValueError:
                continue

            row = actual.iloc[0]
            features["demand_label"] = row["demand_label"]
            features["in_store_units_sold"] = int(row["in_store_units_sold"])
            features["online_units_sold"] = int(row["online_units_sold"])
            test_rows.append(features)

    if not test_rows:
        raise ValueError("No historical predictions available for testing.")

    testing = pd.DataFrame(test_rows)
    scores = {}
    horizon_scores = {}

    for channel, model in models.items():
        actual = get_labels(testing, channel, thresholds)
        predicted = model.predict(testing[FEATURE_COLUMNS])
        scores[channel] = float(accuracy_score(actual, predicted))

        # See whether longer predictions are less accurate
        horizon_scores[channel] = {}
        for name, start, end in [("1-3", 1, 3), ("4-6", 4, 6), ("7-12", 7, 12)]:
            selected = testing["months_ahead"].between(start, end)
            horizon_scores[channel][name] = float(
                accuracy_score(actual[selected], predicted[selected])
            ) if selected.any() else None

    return {
        "cutoff": str(cutoff),
        "training_examples": len(training),
        "testing_examples": len(testing),
        "scores": scores,
        "by_horizon": horizon_scores
    }


# Train final models and save them
def train_models():
    clean, summary = clean_sales_data(load_sales_data(DATA_FILE))
    examples = prepare_training_data(clean)

    evaluation = evaluate_models(clean, examples)

    # Train again with all the available sales history
    thresholds = get_thresholds(clean)
    models = fit_models(examples, thresholds)

    bundle = {
        "models": models,
        "features": FEATURE_COLUMNS,
        "thresholds": thresholds,
        "last_month": str(pd.Period(clean["month"].max(), freq="M")),
        "max_months_ahead": MAX_MONTHS_AHEAD,
        "evaluation": evaluation
    }
    joblib.dump(bundle, MODEL_FILE)

    print("Clean sales records:", summary["clean"])
    print("Training examples for final models:", len(examples))
    print("Test period:", str(pd.Period(evaluation["cutoff"]) + 1), "to", bundle["last_month"])
    print("Historical training examples:", evaluation["training_examples"])
    print("Historical testing examples:", evaluation["testing_examples"])
    for channel in ["overall", "in_store", "online"]:
        print("\n" + channel.replace("_", " ").title() + " accuracy: {:.1%}".format(
            evaluation["scores"][channel]
        ))
        for period, accuracy in evaluation["by_horizon"][channel].items():
            if accuracy is not None:
                print("  " + period + " months: {:.1%}".format(accuracy))

    print("\nSaved:", MODEL_FILE.name)
    return bundle


if __name__ == "__main__":
    train_models()
