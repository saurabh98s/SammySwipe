from typing import Dict, Any, List
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from .base_model import BaseModel
import logging

logger = logging.getLogger(__name__)

class UserMetadataAnalyzer(BaseModel):
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=100)
        self.cluster_model = KMeans(n_clusters=5, random_state=42)
        self.is_fitted = False

    def fit(self, user_data: List[Dict[str, Any]]) -> None:
        """Fit the model on user data."""
        try:
            # Extract text features from user data
            texts = self._extract_text_features(user_data)
            
            # Fit the vectorizer and transform the texts
            X = self.vectorizer.fit_transform(texts)
            
            # Fit the clustering model
            self.cluster_model.fit(X)
            self.is_fitted = True
        except Exception as e:
            logger.error(f"Error fitting metadata analyzer: {e}")
            raise

    def analyze_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze user metadata and return insights."""
        if not self.is_fitted:
            return {}
            
        try:
            # Extract text features
            text = self._extract_text_features([user_data])[0]
            
            # Transform text to vector
            X = self.vectorizer.transform([text])
            
            # Get cluster assignment
            cluster = self.cluster_model.predict(X)[0]
            
            # Calculate activity score
            activity_score = self._calculate_activity_score(user_data)
            
            # Calculate profile completeness
            completeness = self._calculate_profile_completeness(user_data)
            
            return {
                "cluster": int(cluster),
                "activity_score": float(activity_score),
                "profile_completeness": float(completeness),
                "engagement_level": self._get_engagement_level(activity_score)
            }
        except Exception as e:
            logger.error(f"Error analyzing user metadata: {e}")
            return {}

    def _extract_text_features(self, user_data: List[Dict[str, Any]]) -> List[str]:
        """Extract text features from user data."""
        texts = []
        for user in user_data:
            text_parts = []
            
            # Add bio if available
            if user.get("bio"):
                text_parts.append(str(user["bio"]))
            
            # Add interests if available
            if user.get("interests"):
                text_parts.extend([str(interest) for interest in user["interests"]])
            
            # Add location if available
            if user.get("location"):
                text_parts.append(str(user["location"]))
            
            # Join all text parts with spaces
            text = " ".join(text_parts) if text_parts else "empty profile"
            texts.append(text)
        
        return texts

    def _calculate_activity_score(self, user_data: Dict[str, Any]) -> float:
        """Calculate user activity score based on available data."""
        score = 0.0
        num_factors = 0

        # Use get with default 0 for potentially missing fields
        profile_updates = user_data.get("profile_updates", 0) or 0
        login_frequency = user_data.get("login_frequency", 0) or 0
        message_count = user_data.get("message_count", 0) or 0

        # Check if fields exist and contribute to score
        if profile_updates is not None:
            # Normalize based on expected range (e.g., 10 updates = full score)
            score += min(float(profile_updates) / 10.0, 1.0)
            num_factors += 1

        if login_frequency is not None:
            # Normalize (e.g., 30 logins/period = full score) - adjust if definition changes
            score += min(float(login_frequency) / 30.0, 1.0)
            num_factors += 1

        if message_count is not None:
            # Normalize (e.g., 100 messages = full score)
            score += min(float(message_count) / 100.0, 1.0)
            num_factors += 1

        # Return average score over available factors
        return score / num_factors if num_factors > 0 else 0.0

    def _calculate_profile_completeness(self, user_data: Dict[str, Any]) -> float:
        """Calculate profile completeness score based on likely available fields."""
        # Adjust this list based on fields reliably present in your Neo4j User nodes
        # Removed birth_date (often derived), full_name (may not be essential)
        required_fields = [
            "bio",           # Text content
            "interests",     # List of interests
            "location",      # User location
            "profile_photo", # Presence of a photo URL
            "gender",        # User gender
            "age"            # User age (more reliable than birth_date)
            # Add other fields you deem important for a 'complete' profile
            # e.g., "job", "education"
        ]

        completed_count = 0
        for field in required_fields:
            value = user_data.get(field)
            # Check for presence and non-emptiness (for strings/lists)
            if value is not None and value != "" and value != []:
                completed_count += 1

        total_fields = len(required_fields)
        completeness = float(completed_count) / total_fields if total_fields > 0 else 0.0
        # logger.debug(f"Completeness for user {user_data.get('id', '?')}: {completed_count}/{total_fields} = {completeness:.2f}")
        return completeness

    def _get_engagement_level(self, activity_score: float) -> str:
        """Get user engagement level based on activity score."""
        # These thresholds might need tuning based on observed activity scores
        if activity_score >= 0.7: # Adjusted threshold example
            return "high"
        elif activity_score >= 0.3: # Adjusted threshold example
            return "medium"
        else:
            return "low" 