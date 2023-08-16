from flask import Flask, jsonify
from Investment.pipeline.training_pipeline import TrainPipeline
from Investment.constant.training_pipeline import SAVED_MODEL_DIR
from Investment.components.model_trainer import ModelTrainer
from Investment.entity.config_entity import ModelTrainerConfig
from Investment.entity.artifact_entity import DataTransformationArtifact
from Investment.ml.model.estimator import ModelResolver
from Investment.utils.main_utils import load_object
import os
import pandas as pd
from datetime import timedelta
from dotenv import find_dotenv, load_dotenv
from uvicorn import run as app_run

dotenv_path = find_dotenv()
load_dotenv(dotenv_path)
APP_HOST = os.getenv("APP_HOST")
APP_PORT = os.getenv("APP_PORT")

app = Flask(__name__)

@app.route("/")
def index():
    return "Redirecting to documentation..."

@app.route("/train")
def train_route():
    try:
        train_pipeline = TrainPipeline()
        if train_pipeline.is_pipeline_running:
            return "Training pipeline is already running."
        train_pipeline.run_pipeline()
        return "Training successful !!"
    except Exception as e:
        return f"Error Occurred! {e}"


@app.post("/predict")
def predict_route():
    try:
        # Load the trained SARIMAX model
        trained_model_file_path = ModelResolver(model_dir=SAVED_MODEL_DIR)
        trained_model = load_object(trained_model_file_path)  # Replace with the actual path

        # Get the last date in the training series
        last_date = trained_model.preprocessor.index[-1]

        # Generate dates for the next 30 days
        forecast_start_date = last_date + timedelta(days=1)
        forecast_dates = pd.date_range(start=forecast_start_date, periods=30)

        # Forecast prices for the next 30 days using the trained model
        forecast_values = trained_model.model.forecast(steps=30, alpha=0.05)

        # Create a DataFrame with forecast dates and values
        forecast_df = pd.DataFrame({'Date': forecast_dates, 'Forecast': forecast_values})

        # Convert the DataFrame to JSON
        forecast_json = forecast_df.to_json(orient="records")

        return jsonify({"forecast": forecast_json})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app_run(app, host=APP_HOST, port=int(APP_PORT))
