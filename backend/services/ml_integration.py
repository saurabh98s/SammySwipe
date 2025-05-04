import os
from typing import Dict, Any, List
from ..models.user import UserInDB, UserPreferences
import logging
import random

logger = logging.getLogger(__name__)

# Mock ML models
class MockUserMetadataAnalyzer:
    @staticmethod
    def load_model(path):
        logger.info(f"Loading mock metadata analyzer model (ignoring path: {path})")
        return MockUserMetadataAnalyzer()
        
    def analyze_user(self, user_data):
        # Generate random metadata for the user
        return {
            "personality_traits": {
                "openness": round(random.uniform(0.3, 0.9), 2),
                "conscientiousness": round(random.uniform(0.3, 0.9), 2),
                "extroversion": round(random.uniform(0.3, 0.9), 2),
                "agreeableness": round(random.uniform(0.3, 0.9), 2),
                "neuroticism": round(random.uniform(0.3, 0.9), 2)
            },
            "interests": {
                "travel": round(random.uniform(0.2, 0.9), 2),
                "food": round(random.uniform(0.2, 0.9), 2),
                "music": round(random.uniform(0.2, 0.9), 2),
                "sports": round(random.uniform(0.2, 0.9), 2),
                "tech": round(random.uniform(0.2, 0.9), 2),
                "arts": round(random.uniform(0.2, 0.9), 2)
            }
        }

class MockEnhancedMatchingModel:
    @staticmethod
    def load_model(path):
        logger.info(f"Loading mock matching model (ignoring path: {path})")
        return MockEnhancedMatchingModel()
        
    def get_matches(self, user, user_metadata, candidates, candidate_metadata):
        # For each candidate, generate a random match score
        return [
            {**candidate, "match_score": round(random.uniform(0.4, 0.95), 2)}
            for candidate in candidates
        ]

class MLService:
    def __init__(self):
        # Use mock models regardless of file paths
        self.metadata_analyzer = MockUserMetadataAnalyzer()
        self.matching_model = MockEnhancedMatchingModel()
        self.fraud_model = None  # Not needed for testing
        
        logger.info("Initialized mock ML service with mock models")

    def check_fraud(self, user_data: Dict[str, Any]) -> bool:
        """Check if a user is potentially fraudulent."""
        # Always return False for testing
        return False
    
    def analyze_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze user metadata using mock analyzer."""
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
        """Get enhanced matches using mock matching model."""
        try:
            # Get user metadata
            user_metadata = self.analyze_user(user.dict())
            
            # Get metadata for all candidates
            candidate_metadata = [
                self.analyze_user(candidate)
                for candidate in candidates
            ]
            
            # Get matches using the mock matching model
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