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
        """Calculate user activity score."""
        score = 0.0
        
        # Profile updates
        if "profile_updates" in user_data:
            score += min(user_data["profile_updates"] / 10, 1.0)
        
        # Login frequency
        if "login_frequency" in user_data:
            score += min(user_data["login_frequency"] / 30, 1.0)
        
        # Message count
        if "message_count" in user_data:
            score += min(user_data["message_count"] / 100, 1.0)
        
        return score / 3.0

    def _calculate_profile_completeness(self, user_data: Dict[str, Any]) -> float:
        """Calculate profile completeness score."""
        required_fields = [
            "bio", "interests", "location", "profile_photo",
            "full_name", "gender", "birth_date"
        ]
        
        completed = sum(1 for field in required_fields if field in user_data and user_data[field])
        return completed / len(required_fields)

    def _get_engagement_level(self, activity_score: float) -> str:
        """Get user engagement level based on activity score."""
        if activity_score >= 0.8:
            return "high"
        elif activity_score >= 0.4:
            return "medium"
        else:
            return "low" 