import sys
import pandas as pd
from Investment.logger import logging
from Investment.exception import CustomException
from Investment.entity.artifact_entity import DataTransformationArtifact, DataValidationArtifact
from Investment.entity.config_entity import DataTransformationConfig
from Investment.utils.main_utils import save_pandas_series_data, save_object


class DataTransformation:
    def __init__(self, data_validation_artifact: DataValidationArtifact,
                 data_transformation_config: DataTransformationConfig):
        self.data_validation_artifact = data_validation_artifact
        self.data_transformation_config = data_transformation_config

    @staticmethod
    def read_data(file_path) -> pd.DataFrame:
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise CustomException(e, sys)

    def get_data_transformed(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Arranging Date column & converting date column as index
        :param df: The DataFrame to be transformed
        :return: The transformed DataFrame
        """
        try:
            logging.info("Initiating data transformation")
            # Convert 'Date' column to datetime
            df['Date'] = pd.to_datetime(df['Date'])

            # Set the 'Date' column as the index
            df.set_index('Date', inplace=True)

            logging.info("Data transformation completed")
            return df  # Return the transformed DataFrame
        except Exception as e:
            raise CustomException(e, sys)

    def initiate_data_transformation(self) -> DataTransformationArtifact:
        try:
            logging.info("initiating data transformation and saving the transformed data")
            train_df = DataTransformation.read_data(self.data_validation_artifact.valid_train_file_path)
            test_df = DataTransformation.read_data(self.data_validation_artifact.valid_test_file_path)

            # Transform data
            final_train_df = self.get_data_transformed(train_df)
            final_test_df = self.get_data_transformed(test_df)
            preprocessor_data = pd.concat([final_train_df, final_test_df], axis=0)

            # Save panda series data
            save_pandas_series_data(self.data_transformation_config.transformed_train_file_path, series=final_train_df)
            save_pandas_series_data(self.data_transformation_config.transformed_test_file_path, series=final_test_df)

            # Save the preprocessor object using save_object function
            save_object(self.data_transformation_config.transformed_object_file_path, preprocessor_data)

            # Preparing artifact
            data_transformation_artifact = DataTransformationArtifact(
                transformed_object_file_path=self.data_transformation_config.transformed_object_file_path,
                transformed_train_file_path=self.data_transformation_config.transformed_train_file_path,
                transformed_test_file_path=self.data_transformation_config.transformed_test_file_path,
            )
            logging.info(f"Data transformation artifact: {data_transformation_artifact}")
            return data_transformation_artifact
        except Exception as e:
            raise CustomException(e, sys)
