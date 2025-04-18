from typing import Dict, Any, List
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from .base_model import BaseModel
import logging

logger = logging.getLogger(__name__)

class EnhancedMatchingModel(BaseModel):
    def __init__(self):
        self.classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.is_fitted = False

    def fit(self, user_data: List[Dict[str, Any]], matches: List[Dict[str, Any]]) -> None:
        """Fit the model on user data and match history."""
        try:
            # Extract features and labels from matches
            X = []
            y = []
            
            for match in matches:
                feature_vector = self._create_feature_vector(
                    match["user"],
                    match["user_metadata"],
                    match["candidate"],
                    match["candidate_metadata"]
                )
                X.append(feature_vector)
                y.append(1 if match["is_match"] else 0)
            
            X = np.array(X)
            y = np.array(y)
            
            # Scale features
            X = self.scaler.fit_transform(X)
            
            # Fit the classifier
            self.classifier.fit(X, y)
            self.is_fitted = True
        except Exception as e:
            logger.error(f"Error fitting matching model: {e}")
            raise

    def get_matches(
        self,
        user: Dict[str, Any],
        user_metadata: Dict[str, Any],
        candidates: List[Dict[str, Any]],
        candidate_metadata: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Get enhanced matches for a user."""
        if not self.is_fitted:
            return []
            
        try:
            # Prepare features for all candidates
            features = []
            for candidate, metadata in zip(candidates, candidate_metadata):
                feature_vector = self._create_feature_vector(user, user_metadata, candidate, metadata)
                features.append(feature_vector)
            
            # Scale features
            features = self.scaler.transform(features)
            
            # Get match probabilities
            match_probs = self.classifier.predict_proba(features)[:, 1]
            
            # Create match results
            matches = []
            for candidate, prob in zip(candidates, match_probs):
                matches.append({
                    **candidate,
                    "match_score": float(prob * 100)
                })
            
            # Sort by match score
            matches.sort(key=lambda x: x["match_score"], reverse=True)
            
            return matches
        except Exception as e:
            logger.error(f"Error getting matches: {e}")
            return []

    def _create_feature_vector(
        self,
        user: Dict[str, Any],
        user_metadata: Dict[str, Any],
        candidate: Dict[str, Any],
        candidate_metadata: Dict[str, Any]
    ) -> np.ndarray:
        """Create a feature vector for matching."""
        features = []

        # Age difference - Use age directly if available, fallback to birth_date calculation
        user_age = user.get('age')
        candidate_age = candidate.get('age')

        if user_age is not None and candidate_age is not None:
            features.append(abs(user_age - candidate_age))
        elif user.get("birth_date") and candidate.get("birth_date"):
            # Fallback to calculating from birth_date if age is missing but birth_date exists
            try:
                user_age_calc = self._calculate_age(user["birth_date"])
                candidate_age_calc = self._calculate_age(candidate["birth_date"])
                features.append(abs(user_age_calc - candidate_age_calc))
            except Exception as e: # Handle potential parsing errors even here
                logger.debug(f"Could not calculate age from birth_date during feature creation: {e}")
                features.append(10) # Append a neutral/average age difference as fallback
        else:
            features.append(10) # Default/fallback age difference if neither age nor birth_date is usable

        # Interest similarity
        user_interests = user.get("interests", [])
        candidate_interests = candidate.get("interests", [])
        similarity = self._calculate_interest_similarity(user_interests, candidate_interests)
        features.append(similarity)

        # Activity score difference
        user_activity = user_metadata.get("activity_score", 0)
        candidate_activity = candidate_metadata.get("activity_score", 0)
        features.append(abs(user_activity - candidate_activity))

        # Profile completeness difference
        user_completeness = user_metadata.get("profile_completeness", 0)
        candidate_completeness = candidate_metadata.get("profile_completeness", 0)
        features.append(abs(user_completeness - candidate_completeness))

        # Cluster similarity
        user_cluster = user_metadata.get("cluster", -1) # Use -1 as default if missing
        candidate_cluster = candidate_metadata.get("cluster", -1)
        features.append(1 if user_cluster == candidate_cluster and user_cluster != -1 else 0)

        return np.array(features)

    def _calculate_age(self, birth_date: str) -> int:
        """Calculate age from birth date string (YYYY-MM-DD)."""
        if not birth_date: # Handle None or empty string
            raise ValueError("birth_date cannot be None or empty")
        from datetime import datetime
        try:
            birth = datetime.strptime(birth_date, "%Y-%m-%d")
            today = datetime.now()
            age = today.year - birth.year
            if today.month < birth.month or (today.month == birth.month and today.day < birth.day):
                age -= 1
            return age
        except TypeError as e:
             # Re-raise with more context if it's not a string
             raise TypeError(f"strptime() argument 1 must be str, not {type(birth_date)}. Value: {birth_date}") from e

    def _calculate_interest_similarity(self, interests1: List[str], interests2: List[str]) -> float:
        """Calculate Jaccard similarity between interest lists."""
        if not interests1 or not interests2:
            return 0.0

        set1 = set(interests1)
        set2 = set(interests2)

        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))

        return intersection / union if union > 0 else 0.0

    def fit_prepared(self, X: np.ndarray, y: np.ndarray) -> None:
        """Fit the model using pre-prepared feature matrix and labels."""
        try:
            if X.shape[0] != y.shape[0]:
                raise ValueError(f"Shape mismatch: X has {X.shape[0]} samples, y has {y.shape[0]} samples.")
            if X.shape[0] == 0:
                logger.warning("Attempting to fit MatchingModel with 0 samples. Skipping fit.")
                self.is_fitted = False
                return

            # Scale features
            logger.info(f"Scaling features for {X.shape[0]} samples...")
            X_scaled = self.scaler.fit_transform(X)

            # Fit the classifier
            logger.info("Fitting RandomForestClassifier...")
            self.classifier.fit(X_scaled, y)
            self.is_fitted = True
            logger.info("RandomForestClassifier fitting complete.")
        except Exception as e:
            logger.error(f"Error fitting matching model with prepared data: {e}", exc_info=True)
            self.is_fitted = False
            raise

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict match labels for pre-prepared feature vectors."""
        if not self.is_fitted:
            logger.error("Matching model is not fitted. Cannot predict.")
            # Return default prediction (e.g., all non-matches)
            return np.zeros(X.shape[0], dtype=int)
        try:
            X_scaled = self.scaler.transform(X)
            return self.classifier.predict(X_scaled)
        except Exception as e:
             logger.error(f"Error during matching model prediction: {e}", exc_info=True)
             # Return default prediction on error
             return np.zeros(X.shape[0], dtype=int) 