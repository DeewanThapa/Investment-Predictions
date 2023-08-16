from Investment.utils.main_utils import load_pandas_series_data
from Investment.exception import CustomException
from Investment.logger import logging
from Investment.entity.artifact_entity import DataTransformationArtifact,ModelTrainerArtifact
from Investment.entity.config_entity import ModelTrainerConfig
import os,sys
import statsmodels.api as sm
from Investment.ml.metric.error_metric import get_error_score
from Investment.ml.model.estimator import InvestmentModel
from Investment.utils.main_utils import save_object,load_object
import pandas as pd
from datetime import datetime, timedelta

class ModelTrainer:
    def __init__(self,model_trainer_config:ModelTrainerConfig,
        data_transformation_artifact:DataTransformationArtifact):
        try:
            self.model_trainer_config=model_trainer_config
            self.data_transformation_artifact=data_transformation_artifact
        except Exception as e:
            raise CustomException(e,sys)

    def train_sarimax_model(self, train_data):
        try:
            # Train the SARIMAX model
            arima_order = (0, 1, 0)  # Specify the non-seasonal order (p, d, q)
            seasonal_order = (1, 2, 2, 3)  # Specify the seasonal order (P, D, Q, S)
            model = sm.tsa.statespace.SARIMAX(train_data, order=arima_order, seasonal_order=seasonal_order)
            model_fit = model.fit()
            return model_fit
        except Exception as e:
            raise e

    def initiate_model_trainer(self) -> ModelTrainerArtifact:
        try:
            logging.info("model training has started")
            train_file_path = self.data_transformation_artifact.transformed_train_file_path
            test_file_path = self.data_transformation_artifact.transformed_test_file_path

            # Load training series and testing series as pandas series
            train_series = load_pandas_series_data(train_file_path)
            test_series = load_pandas_series_data(test_file_path)

            # Train the SARIMAX model
            model = self.train_sarimax_model(train_series)

            # Evaluate the model on the training data
            train_predictions = model.predict(start=1, end=len(train_series))

            # Align the training data and predictions for error calculation
            train_series_aligned = train_series[1:]
            train_predictions_aligned = train_predictions[:-1]

            # Evaluate the model on the test data
            test_predictions = model.forecast(steps=len(test_series), alpha=0.05)
            train_metric = get_error_score(y_true=train_series_aligned, y_pred=train_predictions_aligned)
            test_metric = get_error_score(y_true=test_series, y_pred=test_predictions)
            logging.info(f"Train MSE: {train_metric.mean_squared_error_score}")
            logging.info(f"Test MSE: {test_metric.mean_squared_error_score}")

            preprocessor = load_object(file_path=self.data_transformation_artifact.transformed_object_file_path)
            model_dir_path = os.path.dirname(self.model_trainer_config.trained_model_file_path)
            os.makedirs(model_dir_path, exist_ok=True)

            # Save the preprocessor (fitted model) as the InvestmentModel object
            invest_model = InvestmentModel(preprocessor=preprocessor, model=model)
            save_object(self.model_trainer_config.trained_model_file_path, obj=invest_model)

            # Get the last date in the training series
            last_date = train_series.index[-1]

            # Generate dates for the next 30 days
            forecast_start_date = last_date + timedelta(days=1)
            forecast_dates = pd.date_range(start=forecast_start_date, periods=30)

            # Forecast prices for the next 30 days
            forecast_values = model.forecast(steps=30, alpha=0.05)

            # Create a DataFrame with forecast dates and values
            forecast_df = pd.DataFrame({'Date': forecast_dates, 'Forecast': forecast_values})

            # Append the forecast values to the test series
            combined_series = pd.concat([test_series, forecast_df.set_index('Date')['Forecast']])

            # Model trainer artifact
            model_trainer_artifact = ModelTrainerArtifact(
                trained_model_file_path=self.model_trainer_config.trained_model_file_path,
                train_metric_artifact=train_metric,
                test_metric_artifact=test_metric
            )
            logging.info(f"Model trainer artifact: {model_trainer_artifact}")
            return model_trainer_artifact
        except Exception as e:
            raise CustomException(e, sys)
