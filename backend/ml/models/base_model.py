import joblib
import os
from typing import Any, Dict
import logging

logger = logging.getLogger(__name__)

class BaseModel:
    @classmethod
    def load_model(cls, model_path: str) -> 'BaseModel':
        """Load a saved model from disk."""
        try:
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"Model file not found: {model_path}")
            return joblib.load(model_path)
        except Exception as e:
            logger.error(f"Error loading model from {model_path}: {e}")
            raise

    def save_model(self, model_path: str) -> None:
        """Save the model to disk."""
        try:
            os.makedirs(os.path.dirname(model_path), exist_ok=True)
            joblib.dump(self, model_path)
        except Exception as e:
            logger.error(f"Error saving model to {model_path}: {e}")
            raise

    def predict(self, data: Dict[str, Any]) -> Any:
        """Make predictions using the model."""
        raise NotImplementedError("Subclasses must implement predict method") 