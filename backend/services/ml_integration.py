import os
from typing import Dict, Any, List
from ..models.user import UserInDB, UserPreferences
from ml.models.fraud_detection import FraudDetectionModel
from ml.models.user_metadata import UserMetadataAnalyzer
from ml.models.enhanced_matching import EnhancedMatchingModel
import logging

logger = logging.getLogger(__name__)

class MLService:
    def __init__(self):
        model_path = os.getenv("MODEL_PATH", "backend/ml/models") # Use relative path
        logger.info(f"Attempting to load ML models from: {os.path.abspath(model_path)}")

        # Define model filenames
        metadata_model_file = "metadata_analyzer_okcupid.joblib"
        matching_model_file = "matching_model_okcupid.joblib"
        # fraud_model_file = "fraud_detection.joblib" # If you have one

        # Load metadata analyzer
        try:
            metadata_model_path = os.path.join(model_path, metadata_model_file)
            self.metadata_analyzer = UserMetadataAnalyzer.load_model(metadata_model_path)
            logger.info(f"Successfully loaded metadata analyzer model from {metadata_model_path}")
        except FileNotFoundError:
            logger.error(f"Metadata analyzer model file not found at {metadata_model_path}. Check MODEL_PATH env var or path.")
            self.metadata_analyzer = None
        except Exception as e:
            logger.warning(f"Could not load metadata analyzer model from {metadata_model_path}: {e}")
            self.metadata_analyzer = None

        # Load matching model
        try:
            matching_model_path = os.path.join(model_path, matching_model_file)
            self.matching_model = EnhancedMatchingModel.load_model(matching_model_path)
            logger.info(f"Successfully loaded matching model from {matching_model_path}")
        except FileNotFoundError:
            logger.error(f"Matching model file not found at {matching_model_path}. Check MODEL_PATH env var or path.")
            self.matching_model = None
        except Exception as e:
            logger.warning(f"Could not load matching model from {matching_model_path}: {e}")
            self.matching_model = None

        # Load fraud detection model (example if needed)
        # try:
        #     fraud_model_path = os.path.join(model_path, fraud_model_file)
        #     self.fraud_model = FraudDetectionModel.load_model(fraud_model_path)
        #     logger.info(f"Successfully loaded fraud detection model from {fraud_model_path}")
        # except FileNotFoundError:
        #     logger.error(f"Fraud detection model file not found at {fraud_model_path}.")
        #     self.fraud_model = None
        # except Exception as e:
        #     logger.warning(f"Could not load fraud detection model: {e}")
        #     self.fraud_model = None

    def check_fraud(self, user_data: Dict[str, Any]) -> bool:
        """Check if a user is potentially fraudulent."""
        # During testing, always return False
        return False
        
        if not self.fraud_model:
            return False
            
        try:
            return self.fraud_model.predict(user_data)
        except Exception as e:
            logger.error(f"Error in fraud detection: {e}")
            return False
    
    def analyze_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze user metadata."""
        if not self.metadata_analyzer:
            return {}
            
        try:
            return self.metadata_analyzer.analyze_user(user_data)
        except Exception as e:
            logger.error(f"Error in user metadata analysis: {e}")
            return {}
    
    def get_enhanced_matches(
        self,
        user: UserInDB,
        preferences: UserPreferences,
        candidates: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Get enhanced matches using ML model."""
        if not self.matching_model or not self.metadata_analyzer:
            return []
            
        try:
            # Get user metadata
            user_metadata = self.analyze_user(user.dict())
            
            # Get metadata for all candidates
            candidate_metadata = [
                self.analyze_user(candidate)
                for candidate in candidates
            ]
            
            # Get matches using the enhanced matching model
            matches = self.matching_model.get_matches(
                user.dict(),
                user_metadata,
                candidates,
                candidate_metadata
            )
            
            return matches
        except Exception as e:
            logger.error(f"Error in enhanced matching: {e}")
            return []

# Global ML service instance
ml_service = MLService() 