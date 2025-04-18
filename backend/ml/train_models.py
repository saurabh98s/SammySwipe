import os
import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta
import random
from ml.models.user_metadata import UserMetadataAnalyzer
from ml.models.enhanced_matching import EnhancedMatchingModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_test_data(num_users: int = 100) -> tuple:
    """Generate test data for model training."""
    users = []
    matches = []
    
    # Sample data
    interests = ["reading", "music", "sports", "travel", "cooking", "gaming", "art", "movies", "fitness", "photography"]
    locations = ["New York", "London", "Paris", "Tokyo", "Sydney", "Berlin", "Mumbai", "Dubai", "Singapore", "Toronto"]
    
    # Generate users
    for i in range(num_users):
        # Generate random birth date (18-50 years old)
        days_old = random.randint(18*365, 50*365)
        birth_date = (datetime.now() - timedelta(days=days_old)).strftime("%Y-%m-%d")
        
        user = {
            "id": f"user_{i}",
            "email": f"user{i}@example.com",
            "username": f"user{i}",
            "full_name": f"User {i}",
            "gender": random.choice(["male", "female", "other"]),
            "birth_date": birth_date,
            "bio": f"Bio for user {i}",
            "interests": random.sample(interests, random.randint(2, 5)),
            "location": random.choice(locations),
            "profile_photo": f"photo_{i}.jpg",
            "login_frequency": random.randint(1, 30),
            "profile_updates": random.randint(1, 10),
            "message_count": random.randint(0, 100),
            "matches_count": random.randint(0, 20)
        }
        users.append(user)
    
    # Generate matches
    for i in range(num_users):
        for j in range(i + 1, num_users):
            if random.random() < 0.3:  # 30% chance of match
                match = {
                    "user": users[i],
                    "user_metadata": {
                        "activity_score": (users[i]["login_frequency"] + users[i]["profile_updates"]) / 2,
                        "profile_completeness": len([x for x in [users[i]["bio"], users[i]["interests"], users[i]["location"], users[i]["profile_photo"]] if x]) / 4
                    },
                    "candidate": users[j],
                    "candidate_metadata": {
                        "activity_score": (users[j]["login_frequency"] + users[j]["profile_updates"]) / 2,
                        "profile_completeness": len([x for x in [users[j]["bio"], users[j]["interests"], users[j]["location"], users[j]["profile_photo"]] if x]) / 4
                    },
                    "is_match": True
                }
                matches.append(match)
    
    return users, matches

def train_and_save_models():
    """Train and save the ML models."""
    try:
        # Create models directory if it doesn't exist
        models_dir = os.path.join(os.path.dirname(__file__), "models")
        os.makedirs(models_dir, exist_ok=True)
        
        # Generate test data
        logger.info("Generating test data...")
        users, matches = generate_test_data()
        
        if not users:
            logger.warning("No users found for training")
            return
        
        # Train metadata analyzer
        logger.info("Training metadata analyzer...")
        metadata_analyzer = UserMetadataAnalyzer()
        metadata_analyzer.fit(users)
        metadata_analyzer.save_model(os.path.join(models_dir, "metadata_analyzer.joblib"))
        logger.info("Metadata analyzer trained and saved")
        
        # Train matching model
        if matches:
            logger.info("Training matching model...")
            matching_model = EnhancedMatchingModel()
            matching_model.fit(users, matches)
            matching_model.save_model(os.path.join(models_dir, "matching_model.joblib"))
            logger.info("Matching model trained and saved")
        else:
            logger.warning("No match history found for training matching model")
        
    except Exception as e:
        logger.error(f"Error training models: {e}")
        raise

if __name__ == "__main__":
    train_and_save_models() 