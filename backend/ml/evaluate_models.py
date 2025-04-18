import os
import logging
import numpy as np
import pandas as pd  # Added
from sklearn.model_selection import train_test_split  # Added
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report
)
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta
import random
import sys
import re # Added for cleaning text
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity # Added

# Add the backend directory to the Python path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(backend_dir)

from ml.models.user_metadata import UserMetadataAnalyzer
from ml.models.enhanced_matching import EnhancedMatchingModel # Re-added

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s') # Improved logging format
logger = logging.getLogger(__name__)

INTEREST_CATEGORICAL_COLS = [
    'body_type', 'diet', 'drinks', 'drugs', 'education', 'ethnicity',
    'job', 'offspring', 'pets', 'religion', 'sign', 'smokes', 'speaks', 'status'
]

def clean_text(text):
    if pd.isna(text):
        return ""
    text = str(text).lower()
    text = re.sub(r'<[^>]+>', '', text)  # Remove HTML tags
    text = re.sub(r'[^a-z\s]', '', text) # Remove non-alpha characters (keep spaces)
    text = re.sub(r'\s+', ' ', text).strip() # Normalize whitespace
    return text

def load_okcupid_data(filepath: str) -> List[Dict[str, Any]]:
    """Load and process the full OkCupid CSV file, simulating missing fields."""
    try:
        logger.info(f"Loading full dataset from {filepath}...")
        df = pd.read_csv(filepath)
        logger.info(f"Loaded {len(df)} profiles.")

        users = []
        required_columns = ['age', 'sex', 'orientation', 'location'] + [f'essay{i}' for i in range(10)] + INTEREST_CATEGORICAL_COLS
        if not all(col in df.columns for col in required_columns):
             # Find missing columns for a more informative error
             missing = [col for col in required_columns if col not in df.columns]
             raise ValueError(f"CSV file missing required columns: {missing}. Found: {df.columns.tolist()}")

        logger.info("Processing profiles (this may take a while)...")
        processed_count = 0
        for index, row in df.iterrows():
            # Combine essays into a single bio/text field
            essays = [clean_text(row[f'essay{i}']) for i in range(10)]
            text_data = " ".join(filter(None, essays))

            # Extract potential interests from categorical columns
            interests = []
            for col in INTEREST_CATEGORICAL_COLS:
                value = row[col]
                if pd.notna(value) and str(value).lower() != 'nan':
                    # Add prefix to distinguish interest type
                    interest_text = clean_text(f"{col}_{value}")
                    if interest_text:
                        interests.append(interest_text)
            # Add orientation as an interest/tag
            if pd.notna(row['orientation']):
                 interests.append(f"orientation_{clean_text(row['orientation'])}")

            # Simulate activity data
            login_frequency = random.randint(0, 30) # days between logins (0 = daily)
            profile_updates = random.randint(0, 5)
            message_count = random.randint(0, 200)
            matches_count = random.randint(0, 50)
            # Simulate other potential fields used by models if necessary
            # e.g., match_interactions, messages_received, response_rate etc.
            # These are harder to simulate realistically without interaction data.
            # Let's keep it simple for now.

            # Map columns
            user = {
                "id": f"okcupid_{index}",
                "age": int(row['age']) if pd.notna(row['age']) else None,
                "gender": str(row['sex']) if pd.notna(row['sex']) else None,
                "orientation": str(row['orientation']) if pd.notna(row['orientation']) else None,
                "location": str(row['location']).split(',')[0] if pd.notna(row['location']) else None, # Take city
                "bio": text_data,
                "interests": interests,
                # Simulated Activity/Behavioral Fields
                "login_frequency": login_frequency,
                "profile_updates": profile_updates,
                "message_count": message_count,
                "matches_count": matches_count,
                # Other potential fields (often derived or missing)
                "full_name": None,
                "birth_date": None, # Can't easily derive from age
                "profile_photo": None,
                "height": row.get('height'), # Keep some original fields if needed
                # Add more fields if EnhancedMatchingModel requires them
            }

            # Basic filtering: ensure essential fields for basic function are present
            if user["age"] and user["gender"] and user["location"] and user["bio"]:
                 users.append(user)
                 processed_count += 1
            else:
                logger.debug(f"Skipping profile index {index} due to missing core data (age/gender/location/bio)")

            if (index + 1) % 5000 == 0:
                 logger.info(f"Processed {index + 1}/{len(df)} profiles...")

        logger.info(f"Finished processing. Successfully processed {processed_count}/{len(df)} profiles.")
        if processed_count < len(df):
             logger.warning(f"Filtered out {len(df) - processed_count} profiles due to missing core data.")
        return users

    except FileNotFoundError:
        logger.error(f"Error: File not found at {filepath}")
        raise
    except Exception as e:
        logger.error(f"Error loading or processing OkCupid data: {e}", exc_info=True)
        raise

def generate_match_pairs(users: List[Dict[str, Any]], metadata_map: Dict[str, Dict[str, Any]], num_pairs: int = 200000, compatibility_threshold: float = 0.1) -> List[Dict[str, Any]]:
    """Generate synthetic match pairs based on user similarity."""
    logger.info(f"Generating {num_pairs} synthetic match pairs (this may take a while)...")
    match_pairs = []
    user_ids = [u['id'] for u in users]
    user_bios = [u['bio'] for u in users]
    num_users = len(users)

    if num_users < 2:
        logger.warning("Not enough users to generate pairs.")
        return []

    # Pre-calculate TF-IDF vectors for bios for efficiency
    logger.info("Calculating TF-IDF vectors for user bios...")
    vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(user_bios)
    logger.info("TF-IDF calculation complete.")

    positive_matches = 0
    negative_matches = 0

    processed_pairs_count = 0
    while len(match_pairs) < num_pairs and processed_pairs_count < num_pairs * 5: # Add a safety break
        processed_pairs_count += 1
        # Select two distinct random users
        idx1, idx2 = random.sample(range(num_users), 2)
        user1_id, user2_id = user_ids[idx1], user_ids[idx2]
        user1, user2 = users[idx1], users[idx2]

        # Skip if metadata is missing (shouldn't happen if called correctly)
        if user1_id not in metadata_map or user2_id not in metadata_map:
            logger.warning(f"Missing metadata for user {user1_id} or {user2_id}. Skipping pair.")
            continue

        user1_meta = metadata_map[user1_id]
        user2_meta = metadata_map[user2_id]

        # Calculate compatibility score
        score = 0.0
        components = 0

        # 1. Age difference (normalized)
        if user1.get('age') and user2.get('age'):
            age_diff = abs(user1['age'] - user2['age'])
            score += max(0, 1 - (age_diff / 20)) # Score decreases as age diff increases (max score at 0 diff, 0 score at 20+ diff)
            components += 1

        # 2. Location match
        if user1.get('location') and user2.get('location'):
            if user1['location'] == user2['location']:
                score += 1.0
            components += 1

        # 3. Essay similarity
        try:
            similarity = cosine_similarity(tfidf_matrix[idx1], tfidf_matrix[idx2])[0][0]
            score += similarity
            components += 1
        except Exception as e:
             logger.debug(f"Could not calculate cosine similarity for pair {idx1}-{idx2}: {e}")

        # 4. Metadata similarity (e.g., cluster, activity/completeness scores)
        if user1_meta.get('cluster') is not None and user2_meta.get('cluster') is not None:
            if user1_meta['cluster'] == user2_meta['cluster']:
                score += 0.5 # Bonus for same cluster
            components += 1
        # Add similarity for scores if desired (e.g., profile completeness)
        if user1_meta.get('profile_completeness') is not None and user2_meta.get('profile_completeness') is not None:
             comp_diff = abs(user1_meta['profile_completeness'] - user2_meta['profile_completeness'])
             score += max(0, 0.5 - comp_diff) # Max 0.5 if scores identical
             components +=1

        # Normalize score
        final_score = score / components if components > 0 else 0.0

        # Determine match label
        is_match = final_score >= compatibility_threshold

        # Try to maintain some balance (optional)
        # if is_match and positive_matches > negative_matches * 1.5: continue
        # if not is_match and negative_matches > positive_matches * 1.5: continue

        if is_match: positive_matches += 1
        else: negative_matches += 1

        match_pair = {
            "user": user1,
            "user_metadata": user1_meta,
            "candidate": user2,
            "candidate_metadata": user2_meta,
            "is_match": is_match
        }
        match_pairs.append(match_pair)

        if len(match_pairs) % 10000 == 0:
            logger.info(f"Generated {len(match_pairs)}/{num_pairs} match pairs... (+{positive_matches}/-{negative_matches})")

    logger.info(f"Finished generating pairs. Total: {len(match_pairs)} (+{positive_matches}/-{negative_matches}). Compatibility threshold: {compatibility_threshold:.2f}")
    if processed_pairs_count >= num_pairs * 5:
        logger.warning("Reached maximum pair processing limit before generating desired number of pairs.")
    return match_pairs

def evaluate_metadata_analyzer(model: UserMetadataAnalyzer, test_users: List[Dict[str, Any]], metadata_map: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Evaluate the metadata analyzer model using pre-calculated metadata."""
    try:
        predictions = []
        for user in test_users:
            user_id = user['id']
            if user_id in metadata_map:
                predictions.append(metadata_map[user_id])
            else:
                # Fallback if metadata somehow missing (shouldn't happen)
                logger.warning(f"Metadata missing for test user {user_id} during evaluation.")
                analysis = model.analyze_user(user) # Re-analyze as fallback
                if analysis: predictions.append(analysis)

        if not predictions:
            logger.warning("No valid predictions from metadata analyzer on test set")
            # Return default dict
            return {
                "avg_activity_score": 0.0, "std_activity_score": 0.0,
                "avg_completeness": 0.0, "std_completeness": 0.0,
                "cluster_distribution": {"high_engagement": 0, "medium_engagement": 0, "low_engagement": 0}
            }

        # Calculate metrics
        activity_scores = [p.get("activity_score", 0.0) for p in predictions]
        completeness_scores = [p.get("profile_completeness", 0.0) for p in predictions]
        engagement_levels = [p.get("engagement_level", "low") for p in predictions]

        metrics = {
            "avg_activity_score": np.mean(activity_scores),
            "std_activity_score": np.std(activity_scores),
            "avg_completeness": np.mean(completeness_scores),
            "std_completeness": np.std(completeness_scores),
            "cluster_distribution": {
                "high_engagement": sum(1 for level in engagement_levels if level == "high"),
                "medium_engagement": sum(1 for level in engagement_levels if level == "medium"),
                "low_engagement": sum(1 for level in engagement_levels if level == "low")
            }
        }
        return metrics
    except Exception as e:
        logger.error(f"Error evaluating metadata analyzer: {e}", exc_info=True)
        # Return default dict on error
        return {
            "avg_activity_score": 0.0, "std_activity_score": 0.0,
            "avg_completeness": 0.0, "std_completeness": 0.0,
            "cluster_distribution": {"high_engagement": 0, "medium_engagement": 0, "low_engagement": 0}
        }

def evaluate_matching_model(model: EnhancedMatchingModel, test_matches: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Evaluate the matching model using the generated test match pairs."""
    try:
        X_test = []
        y_test = []

        logger.info(f"Preparing test data for matching model from {len(test_matches)} pairs...")
        missing_metadata_count = 0
        for match in test_matches:
            # Ensure metadata is present within the match pair dictionary
            if not match.get('user_metadata') or not match.get('candidate_metadata'):
                 missing_metadata_count += 1
                 continue
            try:
                 feature_vector = model._create_feature_vector(
                    match["user"],
                    match["user_metadata"],
                    match["candidate"],
                    match["candidate_metadata"]
                )
                 X_test.append(feature_vector)
                 y_test.append(1 if match["is_match"] else 0)
            except Exception as e:
                 logger.error(f"Error creating feature vector for a match pair: {e}")
                 # Optionally skip this pair or handle error differently
                 continue

        if missing_metadata_count > 0:
            logger.warning(f"Skipped {missing_metadata_count} match pairs during evaluation due to missing metadata.")

        if not X_test or not y_test:
            logger.warning("No valid test data pairs generated for matching model evaluation.")
            # Return default dict
            return {
                "accuracy": 0.0, "precision": 0.0, "recall": 0.0, "f1": 0.0,
                "confusion_matrix": [[0, 0], [0, 0]], "classification_report": "No data available"
            }

        X_test = np.array(X_test)
        y_test = np.array(y_test)

        logger.info(f"Predicting matches for {len(X_test)} test pairs...")
        y_pred = model.predict(X_test) # Use predict method of the base class or model

        # Calculate metrics
        logger.info("Calculating matching model metrics...")
        cm = confusion_matrix(y_test, y_pred)
        report = classification_report(y_test, y_pred, zero_division=0)

        metrics = {
            "accuracy": accuracy_score(y_test, y_pred),
            "precision": precision_score(y_test, y_pred, zero_division=0),
            "recall": recall_score(y_test, y_pred, zero_division=0),
            "f1": f1_score(y_test, y_pred, zero_division=0),
            "confusion_matrix": cm.tolist(),
            "classification_report": report
        }
        return metrics
    except Exception as e:
        logger.error(f"Error evaluating matching model: {e}", exc_info=True)
        # Return default dict on error
        return {
            "accuracy": 0.0, "precision": 0.0, "recall": 0.0, "f1": 0.0,
            "confusion_matrix": [[0, 0], [0, 0]], "classification_report": "Error during evaluation"
        }

def plot_confusion_matrix(confusion_matrix_data: List[List[int]], title: str, output_dir: str):
    """Plot confusion matrix."""
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, 'confusion_matrix_okcupid.png') # New filename
    try:
        plt.figure(figsize=(8, 6))
        sns.heatmap(confusion_matrix_data, annot=True, fmt='d', cmap='Blues')
        plt.title(title)
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        plt.savefig(filepath)
        plt.close()
        logger.info(f"Confusion matrix saved to {filepath}")
    except Exception as e:
        logger.error(f"Error plotting confusion matrix: {e}")

def plot_engagement_distribution(distribution: Dict[str, int], output_dir: str):
    """Plot engagement level distribution."""
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, 'engagement_distribution_okcupid.png') # New filename
    try:
        plt.figure(figsize=(8, 6))
        levels = list(distribution.keys())
        counts = list(distribution.values())
        plt.bar(levels, counts)
        plt.title('User Engagement Level Distribution (Test Set - OkCupid)')
        plt.ylabel('Number of Users')
        plt.savefig(filepath)
        plt.close()
        logger.info(f"Engagement distribution plot saved to {filepath}")
    except Exception as e:
        logger.error(f"Error plotting engagement distribution: {e}")

def main():
    """Main training and evaluation function using full OkCupid data."""
    try:
        # --- Configuration ---
        okcupid_csv_path = os.path.join(backend_dir, "ml", "okcupid", "okcupid_profiles.csv")
        models_dir = os.path.join(os.path.dirname(__file__), "models")
        plots_dir = os.path.join(os.path.dirname(__file__), "visualizations")
        user_test_set_size = 0.2 # 20% of users for testing metadata analyzer
        match_pair_test_set_size = 0.2 # 20% of generated pairs for testing matching model
        num_match_pairs_to_generate = 200000 # Number of synthetic pairs
        match_compatibility_threshold = 0.15 # Threshold for labelling synthetic matches (adjust as needed)
        random_state = 42

        # Create directories
        os.makedirs(models_dir, exist_ok=True)
        os.makedirs(plots_dir, exist_ok=True)

        # 1. Load and Process All OkCupid Users
        all_users = load_okcupid_data(okcupid_csv_path)
        if not all_users:
             logger.error("No users loaded from OkCupid data. Exiting.")
             return

        # 2. Split Users into Train/Test
        logger.info(f"Splitting {len(all_users)} users into training ({1-user_test_set_size:.0%}) and testing ({user_test_set_size:.0%})...")
        train_users, test_users = train_test_split(
            all_users, test_size=user_test_set_size, random_state=random_state
        )
        logger.info(f"Training users: {len(train_users)}, Test users: {len(test_users)}")

        # 3. Train Metadata Analyzer
        logger.info("Initializing Metadata Analyzer...")
        metadata_analyzer = UserMetadataAnalyzer()
        logger.info("Training Metadata Analyzer on training users (this may take time)...")
        metadata_analyzer.fit(train_users)
        metadata_analyzer_path = os.path.join(models_dir, "metadata_analyzer_okcupid.joblib")
        metadata_analyzer.save_model(metadata_analyzer_path)
        logger.info(f"Metadata Analyzer trained and saved to {metadata_analyzer_path}")

        # 4. Analyze All Users (Train + Test)
        logger.info("Analyzing metadata for ALL users (train + test)...")
        user_metadata_map = {}
        analysis_errors = 0
        for i, user in enumerate(all_users):
            try:
                analysis = metadata_analyzer.analyze_user(user)
                if analysis:
                     user_metadata_map[user['id']] = analysis
                else:
                    analysis_errors += 1
            except Exception as e:
                logger.debug(f"Could not analyze metadata for user {user['id']}: {e}")
                analysis_errors += 1
            if (i + 1) % 5000 == 0:
                 logger.info(f"Analyzed metadata for {i+1}/{len(all_users)} users...")
        logger.info(f"Finished metadata analysis for {len(user_metadata_map)} users. Errors: {analysis_errors}")

        # 5. Generate Synthetic Match Pairs
        all_match_pairs = generate_match_pairs(
            all_users,
            user_metadata_map,
            num_pairs=num_match_pairs_to_generate,
            compatibility_threshold=match_compatibility_threshold
        )
        if not all_match_pairs:
             logger.error("Failed to generate any match pairs. Cannot train Matching Model.")
             # Optionally continue to evaluate only metadata analyzer
             # ... (evaluation code for metadata analyzer still runs below)
        else:
            # 6. Split Match Pairs into Train/Test
            logger.info(f"Splitting {len(all_match_pairs)} match pairs into training ({1-match_pair_test_set_size:.0%}) and testing ({match_pair_test_set_size:.0%})...")
            train_matches, test_matches = train_test_split(
                all_match_pairs, test_size=match_pair_test_set_size, random_state=random_state
            )
            logger.info(f"Training matches: {len(train_matches)}, Test matches: {len(test_matches)}")

            # 7. Train Matching Model
            logger.info("Initializing Enhanced Matching Model...")
            matching_model = EnhancedMatchingModel()
            logger.info("Training Matching Model on training match pairs (this may take time)...")
            # The fit method for EnhancedMatchingModel might need adjustment
            # Does it expect users+matches, or just the structured match pairs?
            # Assuming it needs the structured pairs based on its _create_feature_vector use
            # We might need to adapt the model's fit method if it expects separate lists
            try:
                # We need to pass data in the format expected by the model's fit method.
                # Let's assume for now it can work with the list of match dicts
                # or we need to extract X_train, y_train from train_matches.
                logger.info("Preparing training data for Matching Model...")
                X_train_match = []
                y_train_match = []
                prep_errors = 0
                for match in train_matches:
                     if not match.get('user_metadata') or not match.get('candidate_metadata'): continue
                     try:
                         fv = matching_model._create_feature_vector(
                             match["user"], match["user_metadata"],
                             match["candidate"], match["candidate_metadata"]
                         )
                         X_train_match.append(fv)
                         y_train_match.append(1 if match["is_match"] else 0)
                     except Exception as e:
                        logger.debug(f"Error creating feature vector for training pair: {e}")
                        prep_errors += 1
                if prep_errors > 0: logger.warning(f"Encountered {prep_errors} errors preparing training features for matching model.")

                if X_train_match:
                    logger.info(f"Fitting Matching model with {len(X_train_match)} training examples...")
                    matching_model.fit_prepared(np.array(X_train_match), np.array(y_train_match))
                    matching_model_path = os.path.join(models_dir, "matching_model_okcupid.joblib")
                    matching_model.save_model(matching_model_path)
                    logger.info(f"Matching Model trained and saved to {matching_model_path}")
                else:
                    logger.error("No training data could be prepared for the Matching Model.")

            except AttributeError as ae:
                 logger.error(f"The EnhancedMatchingModel might need a `fit_prepared` method or its `fit` method adjusted. Error: {ae}", exc_info=True)
                 # Skip saving and evaluating if training failed
                 test_matches = [] # Prevent evaluation
            except Exception as e:
                 logger.error(f"Error training Matching Model: {e}", exc_info=True)
                 test_matches = [] # Prevent evaluation

            # 8. Evaluate Matching Model
            if test_matches:
                 logger.info("Evaluating Matching Model on the test match pairs...")
                 matching_metrics = evaluate_matching_model(matching_model, test_matches)
                 logger.info("\n--- Matching Model Metrics (Test Set - Synthetic Labels) ---")
                 if matching_metrics:
                     logger.info(f"Accuracy: {matching_metrics.get('accuracy', 0.0):.3f}")
                     logger.info(f"Precision: {matching_metrics.get('precision', 0.0):.3f}")
                     logger.info(f"Recall: {matching_metrics.get('recall', 0.0):.3f}")
                     logger.info(f"F1 Score: {matching_metrics.get('f1', 0.0):.3f}")
                     logger.info("\nClassification Report:\n" + matching_metrics.get('classification_report', 'N/A'))
                     if "confusion_matrix" in matching_metrics:
                         plot_confusion_matrix(
                             matching_metrics["confusion_matrix"],
                             "Matching Model Confusion Matrix (OkCupid - Synthetic Labels)",
                             plots_dir
                         )
                 else:
                     logger.info("Matching model metrics could not be calculated.")
            else:
                 logger.warning("Skipping matching model evaluation as no test matches were available or training failed.")

        # 9. Evaluate Metadata Analyzer (on Test Users)
        logger.info("Evaluating Metadata Analyzer on the test users...")
        metadata_metrics = evaluate_metadata_analyzer(metadata_analyzer, test_users, user_metadata_map)
        logger.info("\n--- Metadata Analyzer Metrics (Test Set) ---")
        if metadata_metrics:
            logger.info(f"Average Activity Score (Simulated): {metadata_metrics.get('avg_activity_score', 0.0):.3f} ± {metadata_metrics.get('std_activity_score', 0.0):.3f}")
            logger.info(f"Average Profile Completeness: {metadata_metrics.get('avg_completeness', 0.0):.3f} ± {metadata_metrics.get('std_completeness', 0.0):.3f}")
            logger.info("\nEngagement Level Distribution (Test Set):")
            if "cluster_distribution" in metadata_metrics:
                 for level, count in metadata_metrics["cluster_distribution"].items():
                     logger.info(f"{level.capitalize()}: {count} users")
            else:
                 logger.info("No distribution data available.")
            # Plot engagement distribution
            if metadata_metrics and "cluster_distribution" in metadata_metrics:
                 plot_engagement_distribution(metadata_metrics["cluster_distribution"], plots_dir)
            else:
                 logger.warning("Could not generate engagement distribution plot.")
        else:
            logger.info("Metadata metrics could not be calculated.")

        logger.info(f"\nEvaluation complete! Check models in '{models_dir}' and plots in '{plots_dir}'.")
        logger.info("Note: Match metrics are based on synthetically generated labels.")

    except Exception as e:
        logger.error(f"Critical error during main execution: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    main() 