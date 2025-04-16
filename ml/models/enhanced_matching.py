from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
import numpy as np
import joblib
from typing import List, Dict, Any
import pandas as pd
from datetime import datetime

class EnhancedMatchingModel:
    def __init__(self):
        self.scaler = StandardScaler()
        self.user_embeddings = {}
        
    def extract_features(self, user_data: Dict[str, Any], metadata: Dict[str, Any]) -> List[float]:
        """Extract features for matching."""
        features = [
            metadata.get("profile_completeness", 0),
            metadata.get("activity_score", 0),
            metadata.get("social_score", 0),
            metadata.get("engagement_score", 0),
            len(user_data.get("interests", [])),
            len(user_data.get("bio", "")),
            user_data.get("match_acceptance_rate", 0),
            user_data.get("response_rate", 0),
            metadata.get("cluster", 0)
        ]
        return features
    
    def calculate_compatibility_score(
        self,
        user1_data: Dict[str, Any],
        user2_data: Dict[str, Any],
        user1_metadata: Dict[str, Any],
        user2_metadata: Dict[str, Any]
    ) -> float:
        """Calculate compatibility score between two users."""
        # Interest similarity
        interests1 = set(user1_data.get("interests", []))
        interests2 = set(user2_data.get("interests", []))
        interest_similarity = len(interests1.intersection(interests2)) / len(interests1.union(interests2)) if interests1 or interests2 else 0
        
        # Location proximity (if available)
        location_score = self._calculate_location_score(user1_data, user2_data)
        
        # Activity compatibility
        activity_compatibility = 1 - abs(
            user1_metadata.get("activity_score", 0) - 
            user2_metadata.get("activity_score", 0)
        )
        
        # Social compatibility
        social_compatibility = 1 - abs(
            user1_metadata.get("social_score", 0) - 
            user2_metadata.get("social_score", 0)
        )
        
        # Engagement compatibility
        engagement_compatibility = 1 - abs(
            user1_metadata.get("engagement_score", 0) - 
            user2_metadata.get("engagement_score", 0)
        )
        
        # Cluster compatibility
        cluster_compatibility = 1.0 if user1_metadata.get("cluster") == user2_metadata.get("cluster") else 0.5
        
        # Weighted combination
        weights = {
            "interest_similarity": 0.3,
            "location_score": 0.15,
            "activity_compatibility": 0.15,
            "social_compatibility": 0.15,
            "engagement_compatibility": 0.15,
            "cluster_compatibility": 0.1
        }
        
        total_score = (
            interest_similarity * weights["interest_similarity"] +
            location_score * weights["location_score"] +
            activity_compatibility * weights["activity_compatibility"] +
            social_compatibility * weights["social_compatibility"] +
            engagement_compatibility * weights["engagement_compatibility"] +
            cluster_compatibility * weights["cluster_compatibility"]
        )
        
        return total_score
    
    def _calculate_location_score(self, user1_data: Dict[str, Any], user2_data: Dict[str, Any]) -> float:
        """Calculate location proximity score."""
        # This is a placeholder. In a real application, you would use geocoding and distance calculation
        if user1_data.get("location") == user2_data.get("location"):
            return 1.0
        return 0.5
    
    def fit(self, user_data_list: List[Dict[str, Any]], metadata_list: List[Dict[str, Any]]):
        """Train the matching model."""
        features = np.array([
            self.extract_features(user_data, metadata)
            for user_data, metadata in zip(user_data_list, metadata_list)
        ])
        
        # Scale features
        features_scaled = self.scaler.fit_transform(features)
        
        # Store user embeddings
        for i, (user_data, features) in enumerate(zip(user_data_list, features_scaled)):
            self.user_embeddings[user_data["id"]] = features
    
    def get_matches(
        self,
        user_data: Dict[str, Any],
        user_metadata: Dict[str, Any],
        candidate_data_list: List[Dict[str, Any]],
        candidate_metadata_list: List[Dict[str, Any]],
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """Get top matches for a user."""
        matches = []
        
        for candidate_data, candidate_metadata in zip(candidate_data_list, candidate_metadata_list):
            if candidate_data["id"] == user_data["id"]:
                continue
                
            compatibility_score = self.calculate_compatibility_score(
                user_data,
                candidate_data,
                user_metadata,
                candidate_metadata
            )
            
            matches.append({
                "user_id": candidate_data["id"],
                "compatibility_score": compatibility_score,
                **candidate_data,
                "metadata": candidate_metadata
            })
        
        # Sort by compatibility score
        matches.sort(key=lambda x: x["compatibility_score"], reverse=True)
        
        return matches[:top_k]
    
    def save_model(self, path: str):
        """Save the model to disk."""
        model_data = {
            "scaler": self.scaler,
            "user_embeddings": self.user_embeddings
        }
        joblib.dump(model_data, path)
    
    @classmethod
    def load_model(cls, path: str) -> "EnhancedMatchingModel":
        """Load the model from disk."""
        instance = cls()
        model_data = joblib.load(path)
        instance.scaler = model_data["scaler"]
        instance.user_embeddings = model_data["user_embeddings"]
        return instance 