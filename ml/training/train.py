import os
import sys
from typing import List, Dict, Any
from ..models.fraud_detection import FraudDetectionModel
from ..models.user_metadata import UserMetadataAnalyzer
from ..models.enhanced_matching import EnhancedMatchingModel
from neo4j import GraphDatabase
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ModelTrainer:
    def __init__(self):
        # Connect to Neo4j
        self.driver = GraphDatabase.driver(
            os.getenv("NEO4J_URI", "bolt://localhost:7687"),
            auth=(
                os.getenv("NEO4J_USER", "neo4j"),
                os.getenv("NEO4J_PASSWORD", "password")
            )
        )
        
        # Initialize models
        self.fraud_model = FraudDetectionModel()
        self.metadata_analyzer = UserMetadataAnalyzer()
        self.matching_model = EnhancedMatchingModel()
        
        # Create model directories
        os.makedirs("models", exist_ok=True)
    
    def fetch_training_data(self) -> List[Dict[str, Any]]:
        """Fetch user data from Neo4j for training."""
        query = """
        MATCH (u:User)
        OPTIONAL MATCH (u)-[r:MATCHED]->(m:User)
        WITH u,
             count(r) as matches_count,
             avg(CASE WHEN r.status = 'accepted' THEN 1 ELSE 0 END) as match_acceptance_rate
        OPTIONAL MATCH (u)-[s:SENT]->(receiver:User)
        WITH u, matches_count, match_acceptance_rate,
             count(s) as message_count,
             avg(size(s.content)) as avg_message_length
        RETURN {
            id: u.id,
            email: u.email,
            full_name: u.full_name,
            bio: u.bio,
            interests: u.interests,
            location: u.location,
            gender: u.gender,
            birth_date: u.birth_date,
            profile_photo: u.profile_photo,
            created_at: u.created_at,
            matches_count: matches_count,
            match_acceptance_rate: match_acceptance_rate,
            message_count: message_count,
            avg_message_length: avg_message_length,
            login_frequency: u.login_frequency,
            profile_updates: u.profile_updates,
            reported_count: u.reported_count,
            suspicious_login_count: u.suspicious_login_count
        } as user_data
        """
        
        with self.driver.session() as session:
            result = session.run(query)
            return [dict(record["user_data"]) for record in result]
    
    def train_models(self):
        """Train all ML models."""
        logger.info("Fetching training data...")
        user_data = self.fetch_training_data()
        
        if not user_data:
            logger.warning("No training data available")
            return
        
        # Train fraud detection model
        logger.info("Training fraud detection model...")
        self.fraud_model.fit(user_data)
        self.fraud_model.save_model("models/fraud_detection.joblib")
        
        # Train metadata analyzer
        logger.info("Training metadata analyzer...")
        self.metadata_analyzer.fit(user_data)
        self.metadata_analyzer.save_model("models/metadata_analyzer.joblib")
        
        # Get metadata for all users
        metadata_list = [
            self.metadata_analyzer.analyze_user(user)
            for user in user_data
        ]
        
        # Train matching model
        logger.info("Training matching model...")
        self.matching_model.fit(user_data, metadata_list)
        self.matching_model.save_model("models/matching_model.joblib")
        
        logger.info("Model training completed successfully")
    
    def close(self):
        """Close database connection."""
        self.driver.close()

def main():
    trainer = ModelTrainer()
    try:
        trainer.train_models()
    except Exception as e:
        logger.error(f"Error during model training: {e}")
        sys.exit(1)
    finally:
        trainer.close()

if __name__ == "__main__":
    main() 