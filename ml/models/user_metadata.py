from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import numpy as np
import joblib
from typing import List, Dict, Any
import pandas as pd
from datetime import datetime

class UserMetadataAnalyzer:
    def __init__(self, n_clusters: int = 10):
        self.text_vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english'
        )
        self.interest_vectorizer = TfidfVectorizer(
            max_features=100
        )
        self.clustering = KMeans(
            n_clusters=n_clusters,
            random_state=42
        )
        self.pca = PCA(n_components=50)
        
    def extract_features(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract features from user metadata."""
        # Combine text data
        bio = user_data.get('bio', '') or ''
        interests = user_data.get('interests', []) or []
        text_data = f"{bio} {' '.join(interests)}"
        
        # Extract behavioral features
        behavioral_features = {
            "profile_completeness": self._calculate_profile_completeness(user_data),
            "activity_score": self._calculate_activity_score(user_data),
            "social_score": self._calculate_social_score(user_data),
            "engagement_score": self._calculate_engagement_score(user_data)
        }
        
        return {
            "text_data": text_data,
            "interests": interests,
            **behavioral_features
        }
    
    def _calculate_profile_completeness(self, user_data: Dict[str, Any]) -> float:
        """Calculate profile completeness score."""
        required_fields = [
            "full_name", "bio", "interests", "location", "profile_photo",
            "gender", "birth_date"
        ]
        
        score = sum(1 for field in required_fields if user_data.get(field)) / len(required_fields)
        return float(score)
    
    def _calculate_activity_score(self, user_data: Dict[str, Any]) -> float:
        """Calculate user activity score."""
        factors = {
            "login_frequency": float(user_data.get("login_frequency", 0) or 0),
            "profile_updates": float(user_data.get("profile_updates", 0) or 0),
            "message_count": float(user_data.get("message_count", 0) or 0),
            "match_interactions": float(user_data.get("match_interactions", 0) or 0)
        }
        
        weights = {
            "login_frequency": 0.3,
            "profile_updates": 0.2,
            "message_count": 0.3,
            "match_interactions": 0.2
        }
        
        return sum(score * weights[factor] for factor, score in factors.items())
    
    def _calculate_social_score(self, user_data: Dict[str, Any]) -> float:
        """Calculate user social score."""
        factors = {
            "matches_count": float(user_data.get("matches_count", 0) or 0),
            "messages_received": float(user_data.get("messages_received", 0) or 0),
            "likes_received": float(user_data.get("likes_received", 0) or 0),
            "response_rate": float(user_data.get("response_rate", 0) or 0)
        }
        
        weights = {
            "matches_count": 0.3,
            "messages_received": 0.3,
            "likes_received": 0.2,
            "response_rate": 0.2
        }
        
        return sum(score * weights[factor] for factor, score in factors.items())
    
    def _calculate_engagement_score(self, user_data: Dict[str, Any]) -> float:
        """Calculate user engagement score."""
        factors = {
            "avg_message_length": float(user_data.get("avg_message_length", 0) or 0),
            "avg_response_time": float(user_data.get("avg_response_time", 0) or 0),
            "profile_view_count": float(user_data.get("profile_view_count", 0) or 0),
            "match_acceptance_rate": float(user_data.get("match_acceptance_rate", 0) or 0)
        }
        
        weights = {
            "avg_message_length": 0.2,
            "avg_response_time": 0.3,
            "profile_view_count": 0.2,
            "match_acceptance_rate": 0.3
        }
        
        return sum(score * weights[factor] for factor, score in factors.items())
    
    def fit(self, user_data_list: List[Dict[str, Any]]):
        """Train the metadata analysis model."""
        if not user_data_list:
            raise ValueError("No training data provided")
            
        features = [self.extract_features(user_data) for user_data in user_data_list]
        
        # Process text data
        text_data = [f["text_data"] for f in features]
        if not any(text_data):  # If all text data is empty
            text_vectors = np.zeros((len(text_data), 1))
        else:
            text_vectors = self.text_vectorizer.fit_transform(text_data).toarray()
        
        # Process interests
        interests_data = [" ".join(f["interests"]) for f in features]
        if not any(interests_data):  # If all interests are empty
            interest_vectors = np.zeros((len(interests_data), 1))
        else:
            interest_vectors = self.interest_vectorizer.fit_transform(interests_data).toarray()
        
        # Combine features
        behavioral_features = np.array([[
            f["profile_completeness"],
            f["activity_score"],
            f["social_score"],
            f["engagement_score"]
        ] for f in features])
        
        # Combine all features
        combined_features = np.hstack([
            text_vectors,
            interest_vectors,
            behavioral_features
        ])
        
        # Reduce dimensionality if we have enough samples
        if combined_features.shape[0] > 1:
            n_components = min(50, combined_features.shape[0] - 1)
            self.pca = PCA(n_components=n_components)
            reduced_features = self.pca.fit_transform(combined_features)
        else:
            reduced_features = combined_features
        
        # Cluster users if we have enough samples
        n_clusters = min(10, len(user_data_list))
        self.clustering = KMeans(n_clusters=n_clusters, random_state=42)
        self.clustering.fit(reduced_features)
    
    def analyze_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a user's metadata and return insights."""
        features = self.extract_features(user_data)
        
        # Process text data
        text_data = [features["text_data"]]
        if not any(text_data):  # If text data is empty
            text_vectors = np.zeros((1, 1))
        else:
            text_vectors = self.text_vectorizer.transform(text_data).toarray()
        
        # Process interests
        interests_data = [" ".join(features["interests"])]
        if not any(interests_data):  # If interests are empty
            interest_vectors = np.zeros((1, 1))
        else:
            interest_vectors = self.interest_vectorizer.transform(interests_data).toarray()
        
        # Combine features
        behavioral_features = np.array([[
            features["profile_completeness"],
            features["activity_score"],
            features["social_score"],
            features["engagement_score"]
        ]])
        
        # Combine all features
        combined_features = np.hstack([
            text_vectors,
            interest_vectors,
            behavioral_features
        ])
        
        # Reduce dimensionality
        reduced_features = self.pca.transform(combined_features)
        
        # Get cluster
        cluster = self.clustering.predict(reduced_features)[0]
        
        return {
            "cluster": int(cluster),
            "profile_completeness": float(features["profile_completeness"]),
            "activity_score": float(features["activity_score"]),
            "social_score": float(features["social_score"]),
            "engagement_score": float(features["engagement_score"])
        }
    
    def save_model(self, path: str):
        """Save the model to disk."""
        model_data = {
            "text_vectorizer": self.text_vectorizer,
            "interest_vectorizer": self.interest_vectorizer,
            "clustering": self.clustering,
            "pca": self.pca
        }
        joblib.dump(model_data, path)
    
    @classmethod
    def load_model(cls, path: str) -> "UserMetadataAnalyzer":
        """Load the model from disk."""
        instance = cls()
        model_data = joblib.load(path)
        instance.text_vectorizer = model_data["text_vectorizer"]
        instance.interest_vectorizer = model_data["interest_vectorizer"]
        instance.clustering = model_data["clustering"]
        instance.pca = model_data["pca"]
        return instance 