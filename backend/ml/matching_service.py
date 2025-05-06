import logging
from typing import List, Dict, Any, Optional
import asyncio
from datetime import datetime

from .models import EnhancedMatchingModel
from .analyzer import UserMetadataAnalyzer

# Setup detailed logging
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

class MatchingService:
    """
    Service that provides matching recommendations based on user profiles,
    interests, and metadata analysis.
    """
    
    def __init__(self):
        """Initialize the MatchingService with required components"""
        self.matching_model = EnhancedMatchingModel()
        self.metadata_analyzer = UserMetadataAnalyzer()
        logger.info("MatchingService initialized with EnhancedMatchingModel and UserMetadataAnalyzer")
    
    async def get_matches_for_user(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get enhanced matches for a user based on compatibility scores
        
        Args:
            user_id: ID of the user to find matches for
            limit: Maximum number of matches to return
            
        Returns:
            List of user matches with compatibility scores
        """
        try:
            logger.info(f"Finding matches for user {user_id}, limit: {limit}")
            
            # Import database module here to avoid circular imports
            from ..db.database import db
            from ..db.neo4j_client import get_user_raw_interests
            
            # Get the user's data from Neo4j
            user_query = """
            MATCH (u:User {id: $user_id})
            RETURN u
            """
            
            user_result = db.execute_query(user_query, {"user_id": user_id})
            
            if not user_result:
                logger.warning(f"User {user_id} not found in database")
                return await self._get_fallback_recommendations(limit)
                
            user_data = user_result[0]["u"]
            
            # Get potential matches from Neo4j
            # Find all users of compatible gender and not the user themselves
            potential_matches_query = """
            MATCH (u:User {id: $user_id}), (other:User)
            WHERE other.id <> $user_id
            RETURN other
            LIMIT 100
            """
            
            potential_matches = db.execute_query(potential_matches_query, {"user_id": user_id})
            
            if not potential_matches:
                logger.warning(f"No potential matches found for user {user_id}")
                return await self._get_fallback_recommendations(limit)
                
            logger.info(f"Found {len(potential_matches)} potential matches for user {user_id}")
            
            # Get user's raw social media data for better interests analysis
            user_raw_data = await get_user_raw_interests(user_id)
            
            # Analyze user metadata to extract interests and traits
            user_features = self.metadata_analyzer.analyze_user_raw_data(user_raw_data)
            
            # Enrich user data with analyzed features
            enriched_user_data = {**user_data, **user_features}
            
            # Calculate compatibility scores for each potential match
            scored_matches = []
            for match in potential_matches:
                match_data = match["other"]
                
                # Get match's raw data for better interest analysis
                match_raw_data = await get_user_raw_interests(match_data["id"])
                
                # Analyze match metadata
                match_features = self.metadata_analyzer.analyze_user_raw_data(match_raw_data)
                
                # Enrich match data with analyzed features
                enriched_match_data = {**match_data, **match_features}
                
                # Calculate compatibility
                compatibility = self.matching_model.calculate_overall_compatibility(
                    enriched_user_data,
                    enriched_match_data
                )
                
                # Create match record with all relevant data
                match_record = {
                    "id": match_data["id"],
                    "full_name": match_data.get("full_name", "Unknown"),
                    "bio": match_data.get("bio", ""),
                    "interests": match_data.get("interests", []),
                    "location": match_data.get("location", ""),
                    "birth_date": match_data.get("birth_date", ""),
                    "profile_photo": match_data.get("profile_photo", ""),
                    "match_score": compatibility["match_score"],
                    "common_interests": compatibility["common_interests"],
                    "compatibility_details": compatibility["component_scores"]
                }
                
                scored_matches.append(match_record)
            
            # Sort matches by compatibility score (descending)
            scored_matches.sort(key=lambda x: x["match_score"], reverse=True)
            
            # Return top matches
            top_matches = scored_matches[:limit]
            logger.info(f"Returning {len(top_matches)} matches for user {user_id}")
            
            return top_matches
        except Exception as e:
            logger.error(f"Error getting matches for user {user_id}: {str(e)}")
            return await self._get_fallback_recommendations(limit)
    
    async def _get_fallback_recommendations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get fallback recommendations when primary matching fails
        
        Args:
            limit: Maximum number of recommendations to return
            
        Returns:
            List of user recommendations with default scores
        """
        try:
            # Import database module here to avoid circular imports
            from ..db.neo4j_client import get_random_recommendations
            
            logger.info(f"Getting {limit} fallback recommendations")
            # Use the existing random recommendations function
            recommendations = await get_random_recommendations(limit)
            
            return recommendations
        except Exception as e:
            logger.error(f"Error getting fallback recommendations: {str(e)}")
            return []
    
    async def update_user_match_statistics(self, user_id: str) -> Dict[str, Any]:
        """
        Update match statistics for a user

        Args:
            user_id: ID of the user to update statistics for

        Returns:
            Dictionary of updated statistics
        """
        try:
            from ..db.database import db

            # 1) Likes vs. dislikes sent
            history_query = """
            MATCH (u:User {id: $user_id})-[r:LIKED|DISLIKED]->(other:User)
            RETURN type(r) AS action, count(r) AS cnt
            """
            history = db.execute_query(history_query, {"user_id": user_id})
            likes = sum(r["cnt"] for r in history if r["action"] == "LIKED")
            dislikes = sum(r["cnt"] for r in history if r["action"] == "DISLIKED")

            # 2) Mutual matches
            mutual_query = """
            MATCH (u:User {id: $user_id})-[:LIKED]->(o:User)-[:LIKED]->(u)
            RETURN count(o) AS cnt
            """
            mutual = db.execute_query(mutual_query, {"user_id": user_id})
            mutual_matches = mutual[0]["cnt"] if mutual else 0

            # 3) Incoming likes (not yet responded)
            incoming_query = """
            MATCH (o:User)-[:LIKED]->(u:User {id: $user_id})
            WHERE NOT (u)-[:LIKED|DISLIKED]->(o)
            RETURN count(o) AS cnt
            """
            incoming = db.execute_query(incoming_query, {"user_id": user_id})
            incoming_likes = incoming[0]["cnt"] if incoming else 0

            # 4) Match rate
            match_rate = round(mutual_matches / max(1, likes), 2) if likes > 0 else 0.0

            # 5) Persist each stat as its own primitive property
            update_query = """
            MATCH (u:User {id: $user_id})
            SET u.likes_sent            = $likes_sent,
                u.dislikes_sent         = $dislikes_sent,
                u.mutual_matches        = $mutual_matches,
                u.incoming_likes        = $incoming_likes,
                u.match_rate            = $match_rate,
                u.statistics_updated_at = datetime()
            """
            params = {
                "user_id":         user_id,
                "likes_sent":      likes,
                "dislikes_sent":   dislikes,
                "mutual_matches":  mutual_matches,
                "incoming_likes":  incoming_likes,
                "match_rate":      match_rate
            }
            db.execute_query(update_query, params)

            logger.info(f"Updated match statistics for user {user_id}")
            return {
                "likes_sent":      likes,
                "dislikes_sent":   dislikes,
                "mutual_matches":  mutual_matches,
                "incoming_likes":  incoming_likes,
                "match_rate":      match_rate,
                "updated_at":      datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error updating match statistics for user {user_id}: {e}")
            return {
                "likes_sent":     0,
                "dislikes_sent":  0,
                "mutual_matches": 0,
                "incoming_likes": 0,
                "match_rate":     0.0,
                "updated_at":     datetime.now().isoformat(),
                "error":          str(e)
            }

    
    async def record_user_interaction(self, user_id: str, target_id: str, interaction_type: str) -> bool:
        """
        Record user interaction (like, dislike, etc.) and update match status
        
        Args:
            user_id: ID of the user performing the action
            target_id: ID of the target user
            interaction_type: Type of interaction (LIKED, DISLIKED, MATCHED)
            
        Returns:
            Boolean indicating success
        """
        try:
            # Import database module here to avoid circular imports
            from ..db.database import db
            
            # Validate interaction type
            valid_types = ["LIKED", "DISLIKED", "BLOCKED", "REPORTED", "MATCHED"]
            if interaction_type not in valid_types:
                logger.error(f"Invalid interaction type: {interaction_type}")
                return False
                
            logger.info(f"Recording {interaction_type} interaction from {user_id} to {target_id}")
            
            # Create the relationship
            if interaction_type != "MATCHED":
                # For LIKED, DISLIKED, BLOCKED, REPORTED
                query = f"""
                MATCH (u:User {{id: $user_id}}), (t:User {{id: $target_id}})
                MERGE (u)-[r:{interaction_type}]->(t)
                ON CREATE SET r.created_at = datetime()
                ON MATCH SET r.updated_at = datetime()
                """
                
                db.execute_query(query, {
                    "user_id": user_id,
                    "target_id": target_id
                })
            
            # If this is a LIKE, check if it creates a match
            if interaction_type == "LIKED":
                match_query = """
                MATCH (u:User {id: $user_id})-[:LIKED]->(t:User {id: $target_id}),
                      (t)-[:LIKED]->(u)
                RETURN count(*) > 0 as is_match
                """
                
                match_result = db.execute_query(match_query, {
                    "user_id": user_id,
                    "target_id": target_id
                })
                
                is_match = match_result[0]["is_match"] if match_result else False
                
                if is_match:
                    # Create MATCHED relationship in both directions
                    match_create_query = """
                    MATCH (u:User {id: $user_id}), (t:User {id: $target_id})
                    MERGE (u)-[r1:MATCHED]->(t)
                    MERGE (t)-[r2:MATCHED]->(u)
                    ON CREATE SET r1.created_at = datetime(), r2.created_at = datetime()
                    ON MATCH SET r1.updated_at = datetime(), r2.updated_at = datetime()
                    """
                    
                    db.execute_query(match_create_query, {
                        "user_id": user_id,
                        "target_id": target_id
                    })
                    
                    logger.info(f"Created mutual match between {user_id} and {target_id}")
                    
                    # Update both users' match statistics
                    await self.update_user_match_statistics(user_id)
                    await self.update_user_match_statistics(target_id)
                    
                    return True
            
            return True
        except Exception as e:
            logger.error(f"Error recording interaction {interaction_type} from {user_id} to {target_id}: {str(e)}")
            return False

# Create a singleton instance of the matching service
matching_service = MatchingService() 