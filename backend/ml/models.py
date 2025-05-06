from pydantic import BaseModel
from typing import List, Dict, Any, Optional, Union
import logging
import math
from datetime import datetime

# Setup detailed logging
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

class EnhancedMatchingModel(BaseModel):
    """
    Enhanced matching model for SammySwipe that calculates compatibility scores
    based on multiple factors including interests, location, and personality traits.
    """
    
    # Model parameters and weights
    interest_weight: float = 0.4
    location_weight: float = 0.2
    age_weight: float = 0.1
    personality_weight: float = 0.3
    
    # Personality compatibility matrix (how well traits complement each other)
    personality_compatibility: Dict[str, Dict[str, float]] = {
        "openness": {"openness": 0.8, "conscientiousness": 0.5, "extroversion": 0.7, "agreeableness": 0.6, "neuroticism": 0.3},
        "conscientiousness": {"openness": 0.5, "conscientiousness": 0.8, "extroversion": 0.4, "agreeableness": 0.7, "neuroticism": 0.3},
        "extroversion": {"openness": 0.7, "conscientiousness": 0.4, "extroversion": 0.6, "agreeableness": 0.8, "neuroticism": 0.3},
        "agreeableness": {"openness": 0.6, "conscientiousness": 0.7, "extroversion": 0.8, "agreeableness": 0.9, "neuroticism": 0.4},
        "neuroticism": {"openness": 0.3, "conscientiousness": 0.3, "extroversion": 0.3, "agreeableness": 0.4, "neuroticism": 0.2}
    }
    
    class Config:
        arbitrary_types_allowed = True
    
    def calculate_interest_compatibility(self, user_interests: List[str], other_interests: List[str]) -> float:
        """
        Calculate interest compatibility using the Jaccard similarity coefficient
        
        Args:
            user_interests: List of the user's interests
            other_interests: List of the other user's interests
            
        Returns:
            Float between 0 and 1 representing interest compatibility
        """
        if not user_interests or not other_interests:
            return 0.0
            
        # Convert to sets for easier operations
        user_set = set(user_interests)
        other_set = set(other_interests)
        
        # Jaccard similarity: intersection size / union size
        intersection_size = len(user_set.intersection(other_set))
        union_size = len(user_set.union(other_set))
        
        if union_size == 0:
            return 0.0
            
        return intersection_size / union_size
    
    def calculate_location_compatibility(self, user_location: Dict[str, Any], other_location: Dict[str, Any]) -> float:
        """
        Calculate location compatibility based on distance
        
        Args:
            user_location: Dict with lat/long for the user
            other_location: Dict with lat/long for the other user
            
        Returns:
            Float between 0 and 1 representing location compatibility (1 = close, 0 = far)
        """
        # Default to medium compatibility if location data is missing
        if not user_location or not other_location:
            return 0.5
            
        try:
            # Extract coordinates
            user_lat = float(user_location.get("latitude", 0))
            user_long = float(user_location.get("longitude", 0))
            other_lat = float(other_location.get("latitude", 0))
            other_long = float(other_location.get("longitude", 0))
            
            # Calculate Haversine distance (distance between two points on a sphere)
            R = 6371  # Earth radius in km
            
            # Convert to radians
            lat1, lon1 = math.radians(user_lat), math.radians(user_long)
            lat2, lon2 = math.radians(other_lat), math.radians(other_long)
            
            # Haversine formula
            dlon = lon2 - lon1
            dlat = lat2 - lat1
            a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
            distance = R * c
            
            # Convert distance to compatibility score (closer = higher score)
            # Max compatibility (1.0) at 0km, min (0.1) at 100km or more
            max_distance = 100.0  # km
            compatibility = max(0.1, 1.0 - min(distance / max_distance, 0.9))
            
            return compatibility
        except (ValueError, TypeError) as e:
            logger.warning(f"Error calculating location compatibility: {e}")
            return 0.5
    
    def calculate_age_compatibility(self, user_age: int, other_age: int) -> float:
        """
        Calculate age compatibility based on age difference
        
        Args:
            user_age: Age of the user
            other_age: Age of the other user
            
        Returns:
            Float between 0 and 1 representing age compatibility
        """
        if not user_age or not other_age:
            return 0.5
            
        # Calculate age difference
        age_diff = abs(user_age - other_age)
        
        # Convert to compatibility score
        # 0-3 years: 1.0-0.9
        # 4-7 years: 0.8-0.6
        # 8-15 years: 0.5-0.3
        # 16+ years: 0.2
        if age_diff <= 3:
            return 1.0 - (age_diff * 0.03)
        elif age_diff <= 7:
            return 0.8 - ((age_diff - 4) * 0.05)
        elif age_diff <= 15:
            return 0.5 - ((age_diff - 8) * 0.025)
        else:
            return 0.2
    
    def calculate_personality_compatibility(self, user_traits: Dict[str, float], other_traits: Dict[str, float]) -> float:
        """
        Calculate personality compatibility based on the Big Five personality traits
        
        Args:
            user_traits: Dict of the user's Big Five personality traits and scores
            other_traits: Dict of the other user's Big Five personality traits and scores
            
        Returns:
            Float between 0 and 1 representing personality compatibility
        """
        if not user_traits or not other_traits:
            return 0.5
            
        # Calculate weighted compatibility for each trait
        total_weight = 0
        weighted_compatibility = 0
        
        for user_trait, user_score in user_traits.items():
            if user_trait in self.personality_compatibility and user_trait in other_traits:
                other_score = other_traits[user_trait]
                
                # Get compatibility factor from matrix
                compatibility_factor = self.personality_compatibility[user_trait][user_trait]
                
                # Calculate similarity (1 - absolute difference)
                trait_similarity = 1 - abs(user_score - other_score)
                
                # Apply compatibility factor
                trait_compatibility = trait_similarity * compatibility_factor
                
                # Weight higher for extreme traits (closer to 0 or 1)
                trait_importance = 0.5 + abs(user_score - 0.5)
                
                weighted_compatibility += trait_compatibility * trait_importance
                total_weight += trait_importance
        
        if total_weight == 0:
            return 0.5
            
        return weighted_compatibility / total_weight
    
    def calculate_overall_compatibility(
        self,
        user_data: Dict[str, Any],
        other_user_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate overall compatibility between two users, with detailed scores
        
        Args:
            user_data: Dict containing the user's profile data
            other_user_data: Dict containing the other user's profile data
            
        Returns:
            Dict with overall match score and component scores
        """
        logger.info(f"Calculating compatibility between {user_data.get('full_name', 'Unknown')} and {other_user_data.get('full_name', 'Unknown')}")
        
        # Calculate individual component scores
        interest_score = self.calculate_interest_compatibility(
            user_data.get("interests", []),
            other_user_data.get("interests", [])
        )
        
        location_score = self.calculate_location_compatibility(
            user_data.get("coordinates", {}),
            other_user_data.get("coordinates", {})
        )
        
        age_score = self.calculate_age_compatibility(
            user_data.get("age", 0),
            other_user_data.get("age", 0)
        )
        
        personality_score = self.calculate_personality_compatibility(
            user_data.get("personality_traits", {}),
            other_user_data.get("personality_traits", {})
        )
        
        # Calculate weighted overall score
        overall_score = (
            interest_score * self.interest_weight +
            location_score * self.location_weight +
            age_score * self.age_weight +
            personality_score * self.personality_weight
        )
        
        # Ensure score is between 0.4 and 0.95 for better user experience
        # (avoiding extremely low or perfect scores)
        overall_score = max(0.4, min(0.95, overall_score))
        
        # Round to 2 decimal places
        overall_score = round(overall_score, 2)
        
        # Calculate common interests
        user_interests = set(user_data.get("interests", []))
        other_interests = set(other_user_data.get("interests", []))
        common_interests = list(user_interests.intersection(other_interests))
        
        logger.info(f"Match score: {overall_score} (Interests: {interest_score:.2f}, Location: {location_score:.2f}, Age: {age_score:.2f}, Personality: {personality_score:.2f})")
        
        return {
            "match_score": overall_score,
            "component_scores": {
                "interest_score": round(interest_score, 2),
                "location_score": round(location_score, 2),
                "age_score": round(age_score, 2),
                "personality_score": round(personality_score, 2)
            },
            "common_interests": common_interests
        } 