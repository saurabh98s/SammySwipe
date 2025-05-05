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
        # For each candidate, calculate a more realistic match score
        matches = []
        
        for i, candidate in enumerate(candidates):
            # Get candidate metadata or use empty dict if not available
            candidate_meta = candidate_metadata[i] if i < len(candidate_metadata) else {}
            
            # Calculate personality compatibility (if available)
            personality_score = 0.0
            if "personality_traits" in user_metadata and "personality_traits" in candidate_meta:
                user_traits = user_metadata["personality_traits"]
                candidate_traits = candidate_meta["personality_traits"]
                
                # Calculate similarity between personality traits
                similarity = 0.0
                trait_count = 0
                
                for trait in user_traits:
                    if trait in candidate_traits:
                        # Lower difference = higher similarity
                        difference = abs(user_traits[trait] - candidate_traits[trait])
                        similarity += (1.0 - difference)
                        trait_count += 1
                
                if trait_count > 0:
                    personality_score = similarity / trait_count
            
            # Calculate interest compatibility (if available)
            interest_score = 0.0
            if "interests" in user_metadata and "interests" in candidate_meta:
                user_interests = user_metadata["interests"]
                candidate_interests = candidate_meta["interests"]
                
                # Calculate similarity between interests
                similarity = 0.0
                interest_count = 0
                
                for interest in user_interests:
                    if interest in candidate_interests:
                        # Lower difference = higher similarity
                        difference = abs(user_interests[interest] - candidate_interests[interest])
                        similarity += (1.0 - difference)
                        interest_count += 1
                
                if interest_count > 0:
                    interest_score = similarity / interest_count
            
            # Calculate overall match score with weights
            # If personality or interest data is missing, use a fallback random score
            if personality_score > 0.0 and interest_score > 0.0:
                # 60% personality, 40% interests
                match_score = (0.6 * personality_score) + (0.4 * interest_score)
            else:
                # Fallback to more realistic random score (0.4-0.95)
                match_score = round(random.uniform(0.4, 0.95), 2)
            
            # Add some randomness to prevent identical scores
            match_score = min(0.95, match_score + random.uniform(-0.1, 0.1))
            match_score = max(0.4, match_score)
            
            matches.append({
                **candidate,
                "match_score": round(match_score, 2),
                "compatibility": {
                    "personality": round(personality_score * 100) if personality_score > 0 else None,
                    "interests": round(interest_score * 100) if interest_score > 0 else None
                }
            })
        
        # Sort by match score in descending order
        return sorted(matches, key=lambda m: m["match_score"], reverse=True)

class MLService:
    def __init__(self):
        # Use mock models regardless of file paths
        self.metadata_analyzer = MockUserMetadataAnalyzer()
        self.matching_model = MockEnhancedMatchingModel()
        self.fraud_model = None  # Not needed for testing
        
        # Track some stats for more realistic behavior
        self.total_matches = 0
        self.successful_matches = 0
        self.match_quality_distribution = {
            "excellent": 0,  # 90-100%
            "good": 0,       # 75-89%
            "average": 0,    # 60-74%
            "low": 0         # <60%
        }
        
        logger.info("Initialized mock ML service with enhanced mock models")

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
            
            # Get matches using the enhanced matching model
            matches = self.matching_model.get_matches(
                user.dict(),
                user_metadata,
                candidates,
                candidate_metadata
            )
            
            # Update stats
            self.total_matches += len(matches)
            for match in matches:
                score = match["match_score"]
                if score >= 0.9:
                    self.match_quality_distribution["excellent"] += 1
                    # 80% chance to be successful match
                    if random.random() < 0.8:
                        self.successful_matches += 1
                elif score >= 0.75:
                    self.match_quality_distribution["good"] += 1
                    # 60% chance to be successful match
                    if random.random() < 0.6:
                        self.successful_matches += 1
                elif score >= 0.6:
                    self.match_quality_distribution["average"] += 1
                    # 40% chance to be successful match
                    if random.random() < 0.4:
                        self.successful_matches += 1
                else:
                    self.match_quality_distribution["low"] += 1
                    # 20% chance to be successful match
                    if random.random() < 0.2:
                        self.successful_matches += 1
            
            return matches
        except Exception as e:
            logger.error(f"Error in enhanced matching: {e}")
            return []
            
    def get_match_statistics(self) -> Dict[str, Any]:
        """Get statistics about the matching process."""
        success_rate = (self.successful_matches / self.total_matches * 100) if self.total_matches > 0 else 0
        
        return {
            "total_matches_processed": self.total_matches,
            "successful_matches": self.successful_matches,
            "success_rate": round(success_rate, 1),
            "quality_distribution": self.match_quality_distribution,
            "average_score": 72.5,  # Mock average score
            "trends": {
                "weekly_matches": random.randint(50, 200),
                "weekly_success_rate": round(random.uniform(35.0, 65.0), 1),
                "most_common_interests": ["Travel", "Food", "Music", "Fitness", "Technology"]
            }
        }

# Global ML service instance
ml_service = MLService() 