import re
import json
import pickle
import os
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from typing import Dict, List, Any, Tuple

# Download NLTK resources if they don't exist
try:
    nltk.data.find('corpora/stopwords')
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('stopwords')
    nltk.download('punkt')
    nltk.download('wordnet')

class SocialDataPreprocessor:
    """Preprocesses raw social media data"""
    
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
    
    def preprocess_text(self, text: str) -> str:
        """Preprocess a single text string"""
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs, mentions, hashtags
        text = re.sub(r'http\S+', '', text)
        text = re.sub(r'@\w+', '', text)
        text = re.sub(r'#\w+', '', text)
        
        # Remove special characters and digits
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        
        # Tokenize
        tokens = word_tokenize(text)
        
        # Remove stopwords and lemmatize
        processed_tokens = [
            self.lemmatizer.lemmatize(token) 
            for token in tokens 
            if token not in self.stop_words and len(token) > 2
        ]
        
        return ' '.join(processed_tokens)
    
    def extract_text_from_raw_data(self, raw_data: Dict[str, Any]) -> str:
        """Extract text from raw social media data"""
        all_texts = []
        
        # Process Twitter data
        if 'twitter' in raw_data:
            twitter_data = raw_data['twitter']
            if 'tweets' in twitter_data:
                for tweet in twitter_data['tweets']:
                    if 'text' in tweet:
                        all_texts.append(tweet['text'])
            if 'description' in twitter_data:
                all_texts.append(twitter_data['description'])
        
        # Process Instagram data
        if 'instagram' in raw_data:
            instagram_data = raw_data['instagram']
            if 'media' in instagram_data and 'data' in instagram_data['media']:
                for post in instagram_data['media']['data']:
                    if 'caption' in post:
                        all_texts.append(post['caption'])
            if 'bio' in instagram_data:
                all_texts.append(instagram_data['bio'])
        
        # Process Facebook data
        if 'facebook' in raw_data:
            facebook_data = raw_data['facebook']
            if 'posts' in facebook_data and 'data' in facebook_data['posts']:
                for post in facebook_data['posts']['data']:
                    if 'message' in post:
                        all_texts.append(post['message'])
        
        # Join all texts
        combined_text = ' '.join(all_texts)
        
        # Preprocess the combined text
        return self.preprocess_text(combined_text)

class InterestAnalyzer:
    """Analyzes user interests from preprocessed text"""
    
    def __init__(self, model_dir: str = "ml/models"):
        self.model_dir = model_dir
        self.tfidf_path = os.path.join(model_dir, "tfidf.pkl")
        self.topic_model_path = os.path.join(model_dir, "topic_model.pkl")
        self.topic_names_path = os.path.join(model_dir, "topic_names.json")
        
        # Create model directory if it doesn't exist
        os.makedirs(model_dir, exist_ok=True)
        
        # Default topic names
        self.default_topic_names = [
            "Travel", "Food", "Technology", "Music", "Movies", 
            "Sports", "Fashion", "Art", "Books", "Fitness"
        ]
        
        # Load or train models
        self.tfidf = self._load_or_create_tfidf()
        self.topic_model = self._load_or_create_topic_model()
        self.topic_names = self._load_or_create_topic_names()
    
    def _load_or_create_tfidf(self) -> TfidfVectorizer:
        """Load existing TF-IDF model or create a new one"""
        if os.path.exists(self.tfidf_path):
            with open(self.tfidf_path, 'rb') as f:
                return pickle.load(f)
        else:
            return TfidfVectorizer(max_features=1000)
    
    def _load_or_create_topic_model(self) -> KMeans:
        """Load existing topic model or create a new one"""
        if os.path.exists(self.topic_model_path):
            with open(self.topic_model_path, 'rb') as f:
                return pickle.load(f)
        else:
            return KMeans(n_clusters=10, random_state=42)
    
    def _load_or_create_topic_names(self) -> List[str]:
        """Load existing topic names or use defaults"""
        if os.path.exists(self.topic_names_path):
            with open(self.topic_names_path, 'r') as f:
                return json.load(f)
        else:
            return self.default_topic_names
    
    def train_models(self, texts: List[str]) -> None:
        """Train TF-IDF and topic models on a corpus of texts"""
        # Fit TF-IDF vectorizer
        tfidf_matrix = self.tfidf.fit_transform(texts)
        
        # Fit topic model
        self.topic_model.fit(tfidf_matrix)
        
        # Save models
        with open(self.tfidf_path, 'wb') as f:
            pickle.dump(self.tfidf, f)
        
        with open(self.topic_model_path, 'wb') as f:
            pickle.dump(self.topic_model, f)
        
        with open(self.topic_names_path, 'w') as f:
            json.dump(self.topic_names, f)
    
    def analyze_interests(self, text: str) -> Dict[str, float]:
        """Analyze user interests from preprocessed text"""
        if not text:
            # Return empty result if no text is provided
            return {}
        
        # Transform text using TF-IDF
        tfidf_vector = self.tfidf.transform([text])
        
        # Predict topic
        topic_probabilities = {}
        
        # Calculate distance to each cluster center
        distances = self.topic_model.transform(tfidf_vector)[0]
        
        # Convert distances to probabilities (lower distance = higher probability)
        max_distance = max(distances) if distances.size > 0 else 1
        distances = [max_distance - d for d in distances]
        total = sum(distances) if sum(distances) > 0 else 1
        
        # Normalize and create dictionary of topic -> probability
        for i, distance in enumerate(distances):
            if i < len(self.topic_names):
                topic_name = self.topic_names[i]
                topic_probabilities[topic_name] = distance / total
        
        # Sort by probability (descending)
        sorted_topics = sorted(
            topic_probabilities.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Return dictionary of topics and probabilities
        return dict(sorted_topics)

# For demonstration and testing
if __name__ == "__main__":
    # Sample raw data
    sample_raw_data = {
        "twitter": {
            "tweets": [
                {"text": "Just started using SammySwipe! #dating #tech"},
                {"text": "Visited the Grand Canyon this weekend. Amazing views! #travel"},
                {"text": "New tech gadgets are always fun to try out! #technology"}
            ],
            "description": "Tech enthusiast, traveler, and foodie"
        }
    }
    
    # Initialize preprocessor
    preprocessor = SocialDataPreprocessor()
    
    # Extract and preprocess text
    processed_text = preprocessor.extract_text_from_raw_data(sample_raw_data)
    print(f"Processed text: {processed_text}")
    
    # Initialize interest analyzer
    analyzer = InterestAnalyzer()
    
    # Train models on sample data
    analyzer.train_models([processed_text])
    
    # Analyze interests
    interests = analyzer.analyze_interests(processed_text)
    print(f"User interests: {interests}") 