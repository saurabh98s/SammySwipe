from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import numpy as np
import joblib
from typing import List, Dict, Any
import pandas as pd

class FraudDetectionModel:
    def __init__(self):
        self.model = IsolationForest(
            contamination=0.1,
            random_state=42
        )
        self.scaler = StandardScaler()
        
    def extract_features(self, user_data: Dict[str, Any]) -> List[float]:
        """Extract features for fraud detection."""
        features = [
            len(user_data.get("interests", [])),  # Number of interests
            len(user_data.get("bio", "")),  # Bio length
            user_data.get("profile_completeness", 0),  # Profile completeness
            user_data.get("login_frequency", 0),  # Login frequency
            user_data.get("message_frequency", 0),  # Message frequency
            user_data.get("profile_changes", 0),  # Number of profile changes
            user_data.get("reported_count", 0),  # Number of times reported
            user_data.get("match_response_rate", 0),  # Match response rate
            user_data.get("message_response_time", 0),  # Average message response time
            user_data.get("suspicious_login_count", 0)  # Number of suspicious logins
        ]
        return features
    
    def fit(self, user_data_list: List[Dict[str, Any]]):
        """Train the fraud detection model."""
        features = np.array([
            self.extract_features(user_data)
            for user_data in user_data_list
        ])
        
        # Scale features
        features_scaled = self.scaler.fit_transform(features)
        
        # Train model
        self.model.fit(features_scaled)
        
    def predict(self, user_data: Dict[str, Any]) -> bool:
        """Predict if a user is fraudulent."""
        features = np.array([self.extract_features(user_data)])
        features_scaled = self.scaler.transform(features)
        
        # -1 for anomalies (fraud), 1 for normal
        prediction = self.model.predict(features_scaled)
        return prediction[0] == -1
    
    def save_model(self, path: str):
        """Save the model to disk."""
        model_data = {
            "model": self.model,
            "scaler": self.scaler
        }
        joblib.dump(model_data, path)
    
    @classmethod
    def load_model(cls, path: str) -> "FraudDetectionModel":
        """Load the model from disk."""
        instance = cls()
        model_data = joblib.load(path)
        instance.model = model_data["model"]
        instance.scaler = model_data["scaler"]
        return instance 