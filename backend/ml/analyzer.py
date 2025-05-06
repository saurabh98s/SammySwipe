import logging
from typing import Dict, Any, List, Optional
import re
import random
from collections import Counter
import nltk
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')

# Setup detailed logging
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

class UserMetadataAnalyzer:
    """
    Class to analyze user metadata from various sources and extract relevant features
    for matching in the SammySwipe app.
    """
    
    # Common stop words to filter out from text analysis
    STOP_WORDS = set(nltk.corpus.stopwords.words('english'))
    
    # Keywords related to common interests
    INTEREST_KEYWORDS = {
        "Travel": ["travel", "adventure", "explore", "trip", "journey", "vacation", "wanderlust", "destination"],
        "Photography": ["photo", "photography", "camera", "picture", "instagram", "shoot", "capture"],
        "Food": ["food", "restaurant", "cooking", "dining", "eat", "recipe", "chef", "cuisine", "baking"],
        "Fitness": ["fitness", "gym", "workout", "exercise", "training", "running", "health", "cycling"],
        "Reading": ["book", "reading", "novel", "author", "literature", "story"],
        "Art": ["art", "drawing", "painting", "design", "creative", "artist", "museum"],
        "Music": ["music", "concert", "song", "band", "artist", "playlist", "guitar", "piano"],
        "Movies": ["movie", "film", "cinema", "watch", "series", "netflix", "tv", "show"],
        "Gaming": ["game", "gaming", "xbox", "playstation", "nintendo", "player"],
        "Technology": ["tech", "technology", "programming", "computer", "software", "app", "digital"],
        "Nature": ["nature", "outdoor", "hiking", "mountain", "beach", "ocean", "forest", "camping"],
        "Sports": ["sports", "football", "soccer", "basketball", "baseball", "tennis", "athlete"]
    }
    
    def __init__(self):
        """Initialize the UserMetadataAnalyzer"""
        pass
    
    def analyze_user_raw_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze raw user data from multiple sources and extract relevant features
        
        Args:
            raw_data: Dictionary of raw user data from various sources
            
        Returns:
            Dictionary of extracted features
        """
        logger.info("Analyzing user raw data")
        
        # Initialize extracted features
        extracted_features = {
            "interests": [],
            "topics": {},
            "personality_traits": {},
            "activity_level": 0.0,
            "communication_style": "",
            "relationship_preferences": []
        }
        
        # Process data from different sources
        try:
            # Process Twitter data if available
            if "twitter" in raw_data and "tweets" in raw_data["twitter"]:
                twitter_features = self._analyze_twitter_data(raw_data["twitter"])
                self._merge_features(extracted_features, twitter_features)
                
            # Process Instagram data if available
            if "instagram" in raw_data and "media" in raw_data["instagram"]:
                instagram_features = self._analyze_instagram_data(raw_data["instagram"])
                self._merge_features(extracted_features, instagram_features)
                
            # Process Facebook data if available
            if "facebook" in raw_data and "posts" in raw_data["facebook"]:
                facebook_features = self._analyze_facebook_data(raw_data["facebook"])
                self._merge_features(extracted_features, facebook_features)
                
            # Generate personality traits if not enough data
            if not extracted_features["personality_traits"]:
                extracted_features["personality_traits"] = self._generate_personality_traits()
                
            # Extract relationship preferences
            extracted_features["relationship_preferences"] = self._extract_relationship_preferences(raw_data)
            
            logger.info(f"Extracted {len(extracted_features['interests'])} interests and {len(extracted_features['topics'])} topics")
            
            return extracted_features
        except Exception as e:
            logger.error(f"Error analyzing user raw data: {str(e)}")
            # Generate default features in case of error
            return self._generate_default_features()
            
    def _analyze_twitter_data(self, twitter_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze Twitter data to extract features
        
        Args:
            twitter_data: Dictionary containing Twitter data
            
        Returns:
            Dictionary of extracted features from Twitter
        """
        features = {
            "interests": [],
            "topics": {},
            "personality_traits": {},
            "activity_level": 0.0,
            "communication_style": ""
        }
        
        try:
            # Extract text from tweets
            tweets = twitter_data.get("tweets", [])
            tweet_texts = [tweet.get("text", "") for tweet in tweets if "text" in tweet]
            
            if not tweet_texts:
                return features
                
            # Analyze tweet content
            all_text = " ".join(tweet_texts).lower()
            
            # Extract interests from text
            features["interests"] = self._extract_interests_from_text(all_text)
            
            # Analyze topics and their frequencies
            features["topics"] = self._extract_topics_from_text(all_text)
            
            # Estimate personality traits from tweet style
            features["personality_traits"] = self._estimate_personality_from_text(all_text)
            
            # Activity level based on tweet frequency
            features["activity_level"] = min(1.0, len(tweets) / 20.0)  # Scale up to 1.0
            
            # Communication style (based on tweet length, use of hashtags, etc.)
            avg_length = sum(len(text) for text in tweet_texts) / max(1, len(tweet_texts))
            hashtag_count = sum(text.count('#') for text in tweet_texts)
            
            if avg_length > 100 and hashtag_count < len(tweets) * 0.5:
                features["communication_style"] = "detailed"
            elif hashtag_count > len(tweets) * 1.5:
                features["communication_style"] = "trendy"
            elif avg_length < 50:
                features["communication_style"] = "concise"
            else:
                features["communication_style"] = "balanced"
                
            return features
        except Exception as e:
            logger.warning(f"Error analyzing Twitter data: {str(e)}")
            return features
    
    def _analyze_instagram_data(self, instagram_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze Instagram data to extract features
        
        Args:
            instagram_data: Dictionary containing Instagram data
            
        Returns:
            Dictionary of extracted features from Instagram
        """
        features = {
            "interests": [],
            "topics": {},
            "personality_traits": {},
            "activity_level": 0.0,
            "communication_style": ""
        }
        
        try:
            # Extract captions from media
            media_items = instagram_data.get("media", {}).get("data", [])
            captions = [item.get("caption", "") for item in media_items if "caption" in item]
            
            if not captions:
                return features
                
            # Analyze caption content
            all_text = " ".join(captions).lower()
            
            # Extract interests from captions
            features["interests"] = self._extract_interests_from_text(all_text)
            
            # Analyze topics and their frequencies
            features["topics"] = self._extract_topics_from_text(all_text)
            
            # Estimate personality traits
            features["personality_traits"] = self._estimate_personality_from_text(all_text)
            
            # Activity level based on post frequency
            features["activity_level"] = min(1.0, len(media_items) / 15.0)  # Scale up to 1.0
            
            # Communication style (based on caption length, emoji usage, etc.)
            avg_length = sum(len(caption) for caption in captions) / max(1, len(captions))
            emoji_count = sum(len(re.findall(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF]', caption)) for caption in captions)
            
            if emoji_count > len(captions) * 2:
                features["communication_style"] = "expressive"
            elif avg_length > 80:
                features["communication_style"] = "storyteller"
            else:
                features["communication_style"] = "visual"
                
            return features
        except Exception as e:
            logger.warning(f"Error analyzing Instagram data: {str(e)}")
            return features
    
    def _analyze_facebook_data(self, facebook_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze Facebook data to extract features
        
        Args:
            facebook_data: Dictionary containing Facebook data
            
        Returns:
            Dictionary of extracted features from Facebook
        """
        features = {
            "interests": [],
            "topics": {},
            "personality_traits": {},
            "activity_level": 0.0,
            "communication_style": ""
        }
        
        try:
            # Extract messages from posts
            posts = facebook_data.get("posts", {}).get("data", [])
            messages = [post.get("message", "") for post in posts if "message" in post]
            
            if not messages:
                return features
                
            # Analyze message content
            all_text = " ".join(messages).lower()
            
            # Extract interests from messages
            features["interests"] = self._extract_interests_from_text(all_text)
            
            # Analyze topics and their frequencies
            features["topics"] = self._extract_topics_from_text(all_text)
            
            # Estimate personality traits
            features["personality_traits"] = self._estimate_personality_from_text(all_text)
            
            # Activity level based on post frequency
            features["activity_level"] = min(1.0, len(posts) / 10.0)  # Scale up to 1.0
            
            # Communication style (based on message length, interaction level, etc.)
            avg_length = sum(len(message) for message in messages) / max(1, len(messages))
            
            if avg_length > 120:
                features["communication_style"] = "detailed"
            elif avg_length < 60:
                features["communication_style"] = "concise"
            else:
                features["communication_style"] = "balanced"
                
            return features
        except Exception as e:
            logger.warning(f"Error analyzing Facebook data: {str(e)}")
            return features
    
    def _extract_interests_from_text(self, text: str) -> List[str]:
        """
        Extract interests from text using keyword matching
        
        Args:
            text: Text to analyze
            
        Returns:
            List of identified interests
        """
        interests = []
        
        # Check each interest category
        for interest, keywords in self.INTEREST_KEYWORDS.items():
            for keyword in keywords:
                if f" {keyword} " in f" {text} " or f"#{keyword}" in text:
                    interests.append(interest)
                    break  # Only add each interest once
        
        return list(set(interests))  # Remove duplicates
    
    def _extract_topics_from_text(self, text: str) -> Dict[str, float]:
        """
        Extract topics and their relative importance from text
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary mapping topics to their relative importance (0-1)
        """
        # Tokenize and remove stop words
        tokens = nltk.word_tokenize(text.lower())
        tokens = [token for token in tokens if token.isalpha() and token not in self.STOP_WORDS]
        
        # Count word frequencies
        word_counts = Counter(tokens)
        total_words = sum(word_counts.values())
        
        if total_words == 0:
            return {}
        
        # Extract topics based on interest keywords
        topics = {}
        for interest, keywords in self.INTEREST_KEYWORDS.items():
            # Calculate topic score based on keyword frequency
            keyword_count = sum(word_counts.get(kw, 0) for kw in keywords)
            if keyword_count > 0:
                # Normalize to 0-1 range
                topics[interest] = min(1.0, keyword_count / (total_words * 0.1))
        
        # Normalize scores to add up to 1.0
        total_score = sum(topics.values())
        if total_score > 0:
            topics = {topic: score / total_score for topic, score in topics.items()}
        
        # Return top topics
        return dict(sorted(topics.items(), key=lambda x: x[1], reverse=True)[:8])
    
    def _estimate_personality_from_text(self, text: str) -> Dict[str, float]:
        """
        Estimate Big Five personality traits from text
        This is a simplified implementation - in a real app, this would use NLP and ML models
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary of Big Five personality traits with scores (0-1)
        """
        # Very simplified trait extraction based on keywords and language patterns
        traits = {
            "openness": 0.5,
            "conscientiousness": 0.5,
            "extroversion": 0.5,
            "agreeableness": 0.5,
            "neuroticism": 0.5
        }
        
        # Simple heuristics for traits
        # Openness: Creative language, unique words, arts/culture references
        arts_keywords = ["art", "music", "creative", "explore", "idea", "culture", "book", "film"]
        arts_count = sum(text.count(word) for word in arts_keywords)
        traits["openness"] = min(0.9, 0.5 + arts_count * 0.02)
        
        # Conscientiousness: Organization, planning, achievement words
        plan_keywords = ["plan", "schedule", "complete", "finish", "goal", "success", "achieve", "organize"]
        plan_count = sum(text.count(word) for word in plan_keywords)
        traits["conscientiousness"] = min(0.9, 0.5 + plan_count * 0.03)
        
        # Extroversion: Social words, excitement, activity
        social_keywords = ["friend", "party", "social", "fun", "together", "event", "group", "excited"]
        social_count = sum(text.count(word) for word in social_keywords)
        traits["extroversion"] = min(0.9, 0.5 + social_count * 0.025)
        
        # Agreeableness: Cooperative words, empathy, positive emotion
        agree_keywords = ["thank", "appreciate", "help", "kind", "happy", "love", "care", "support"]
        agree_count = sum(text.count(word) for word in agree_keywords)
        traits["agreeableness"] = min(0.9, 0.5 + agree_count * 0.03)
        
        # Neuroticism: Worry words, negative emotion, stress
        worry_keywords = ["worry", "stress", "anxious", "afraid", "sad", "upset", "nervous", "fear"]
        worry_count = sum(text.count(word) for word in worry_keywords)
        traits["neuroticism"] = min(0.9, 0.5 + worry_count * 0.04)
        
        return traits
        
    def _extract_relationship_preferences(self, raw_data: Dict[str, Any]) -> List[str]:
        """
        Extract relationship preferences from user data
        
        Args:
            raw_data: Dictionary of raw user data
            
        Returns:
            List of relationship preferences
        """
        preferences = []
        
        # Combine all text for analysis
        all_text = ""
        
        if "twitter" in raw_data and "tweets" in raw_data["twitter"]:
            all_text += " ".join([tweet.get("text", "") for tweet in raw_data["twitter"]["tweets"]])
            
        if "instagram" in raw_data and "media" in raw_data["instagram"] and "data" in raw_data["instagram"]["media"]:
            all_text += " ".join([item.get("caption", "") for item in raw_data["instagram"]["media"]["data"]])
            
        if "facebook" in raw_data and "posts" in raw_data["facebook"] and "data" in raw_data["facebook"]["posts"]:
            all_text += " ".join([post.get("message", "") for post in raw_data["facebook"]["posts"]["data"]])
        
        # Convert to lowercase
        all_text = all_text.lower()
        
        # Check for relationship preference keywords
        relationship_keywords = {
            "Long-term": ["relationship", "long-term", "committed", "serious", "future", "partner"],
            "Casual dating": ["casual", "dating", "fun", "meet", "spontaneous"],
            "Friendship first": ["friend", "friendship", "connection", "get to know", "slow"],
            "Adventure buddies": ["adventure", "travel", "explore", "activities", "outdoors"],
            "Intellectual connection": ["intellectual", "conversation", "deep", "meaningful", "talk"]
        }
        
        # Add preferences based on keyword frequency
        for pref, keywords in relationship_keywords.items():
            if any(keyword in all_text for keyword in keywords):
                preferences.append(pref)
        
        # If no preferences detected, add default ones
        if not preferences:
            preferences = ["Casual dating", "Friendship first"]
            
        return preferences
    
    def _merge_features(self, target: Dict[str, Any], source: Dict[str, Any]) -> None:
        """
        Merge source features into target features
        
        Args:
            target: Target feature dictionary
            source: Source feature dictionary
        """
        # Merge interests (union)
        target["interests"] = list(set(target["interests"] + source["interests"]))
        
        # Merge topics (weighted average for overlapping topics)
        for topic, score in source["topics"].items():
            if topic in target["topics"]:
                target["topics"][topic] = (target["topics"][topic] + score) / 2
            else:
                target["topics"][topic] = score
                
        # Merge personality traits (weighted average)
        if target["personality_traits"] and source["personality_traits"]:
            for trait in target["personality_traits"]:
                if trait in source["personality_traits"]:
                    target["personality_traits"][trait] = (target["personality_traits"][trait] + source["personality_traits"][trait]) / 2
        elif source["personality_traits"]:
            target["personality_traits"] = source["personality_traits"]
            
        # Take the highest activity level
        target["activity_level"] = max(target["activity_level"], source["activity_level"])
        
        # Prefer non-empty communication style
        if not target["communication_style"] and source["communication_style"]:
            target["communication_style"] = source["communication_style"]
    
    def _generate_default_features(self) -> Dict[str, Any]:
        """
        Generate default features when data is unavailable
        
        Returns:
            Dictionary of default features
        """
        # Select 3-6 random interests
        interests = random.sample(list(self.INTEREST_KEYWORDS.keys()), random.randint(3, 6))
        
        # Generate random personality traits
        personality_traits = self._generate_personality_traits()
        
        # Generate random topics
        topics = {}
        selected_topics = random.sample(list(self.INTEREST_KEYWORDS.keys()), random.randint(3, 5))
        for topic in selected_topics:
            topics[topic] = round(random.uniform(0.5, 1.0), 2)
            
        # Normalize topic scores
        total = sum(topics.values())
        if total > 0:
            topics = {t: s/total for t, s in topics.items()}
        
        # Random relationship preferences
        relationship_preferences = random.sample([
            "Long-term", "Casual dating", "Friendship first", 
            "Adventure buddies", "Intellectual connection"
        ], 2)
        
        return {
            "interests": interests,
            "topics": topics,
            "personality_traits": personality_traits,
            "activity_level": round(random.uniform(0.3, 0.8), 2),
            "communication_style": random.choice(["balanced", "detailed", "concise", "expressive", "storyteller"]),
            "relationship_preferences": relationship_preferences
        }
    
    def _generate_personality_traits(self) -> Dict[str, float]:
        """
        Generate random personality traits
        
        Returns:
            Dictionary of Big Five personality traits with scores (0-1)
        """
        return {
            "openness": round(random.uniform(0.3, 0.9), 2),
            "conscientiousness": round(random.uniform(0.3, 0.9), 2),
            "extroversion": round(random.uniform(0.3, 0.9), 2),
            "agreeableness": round(random.uniform(0.3, 0.9), 2),
            "neuroticism": round(random.uniform(0.3, 0.9), 2)
        } 