from sklearn.metrics import mean_squared_error, mean_absolute_error
from Investment.exception import CustomException
import numpy as np
import sys
from Investment.entity.artifact_entity import MetricArtifact


def get_error_score(y_true, y_pred) -> MetricArtifact:
    try:
        mean_square_error_score = np.sqrt(mean_squared_error(y_true, y_pred))
        mean_absolute_error_score = np.sqrt(mean_absolute_error(y_true, y_pred))

        score_metric = MetricArtifact(
            mean_squared_error_score=mean_square_error_score,
            mean_absolute_error_score=mean_absolute_error_score
        )
        return score_metric
    except Exception as e:
        raise CustomException(e, sys)
