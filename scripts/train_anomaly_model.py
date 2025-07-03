import pandas as pd
from sklearn.ensemble import IsolationForest
import joblib
import argparse
import os

def train_model(input_path: str, output_path: str):
    """
    Trains an Isolation Forest model and saves it to a file.

    Args:
        input_path (str): The path to the training data (CSV file).
        output_path (str): The path where the trained model will be saved.
    """
    print(f"Loading data from {input_path}...")
    try:
        data = pd.read_csv(input_path)
    except FileNotFoundError:
        print(f"Error: Training data file not found at {input_path}")
        return

    # For this example, we assume the CSV contains 'cpu_percent' and 'memory_percent'
    # In a real scenario, more sophisticated feature selection would be applied.
    features = ['cpu_percent', 'memory_percent']
    if not all(feature in data.columns for feature in features):
        print(f"Error: CSV must contain the columns: {', '.join(features)}")
        return

    X_train = data[features]

    print("Training Isolation Forest model...")
    # The 'contamination' parameter is one of the most important to tune.
    # It represents the expected proportion of outliers in the data set.
    # 'auto' is a good starting point.
    model = IsolationForest(contamination='auto', random_state=42)
    model.fit(X_train)

    # Ensure the output directory exists
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    print(f"Saving trained model to {output_path}...")
    joblib.dump(model, output_path)
    print("Model training complete and saved successfully.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train an Isolation Forest anomaly detection model.")
    parser.add_argument("--input", type=str, required=True, help="Path to the input training data (CSV).")
    parser.add_argument("--output", type=str, required=True, help="Path to save the trained model file.")
    
    args = parser.parse_args()
    
    train_model(args.input, args.output) 