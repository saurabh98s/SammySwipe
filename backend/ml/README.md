# ML Module Documentation

## Overview
The ML module provides enhanced matching capabilities for the SammySwipe application using machine learning techniques. It currently consists of two main components:

1. **User Metadata Analyzer**: Processes user profiles to extract features, calculate scores (activity, completeness), and cluster users based on text and metadata.
2. **Enhanced Matching Model**: Predicts match compatibility between user pairs based on various features.

Training and evaluation are now primarily performed using the OkCupid dataset (`backend/ml/okcupid/okcupid_profiles.csv`). Since this dataset lacks real user activity and match interaction data, these aspects are **simulated** during the training/evaluation process described in `evaluate_models.py`.

## Components

### User Metadata Analyzer (`ml.models.user_metadata.UserMetadataAnalyzer`)

Processes user data to extract meaningful insights.

*   **Text Analysis**: Uses TF-IDF vectorization on combined user essays (`bio` field derived from OkCupid `essay0`-`essay9`).
*   **Clustering**: Uses K-means clustering on TF-IDF vectors to segment users.
*   **Activity Scoring (Simulated)**: Calculates a score based on simulated `login_frequency`, `profile_updates`, and `message_count`. *Note: This is not based on real user activity in the current script.*
*   **Profile Completeness Scoring**: Calculates a score based on the presence of key fields (e.g., bio, interests, location, etc., as mapped from OkCupid data).
*   **Engagement Level**: Categorizes users (high/medium/low) based on the calculated activity score.

**Features Used (OkCupid Mapping):**
*   `bio`: Combined and cleaned text from `essay0` through `essay9`.
*   `interests`: Derived list from various categorical OkCupid columns (e.g., `drinks`, `smokes`, `job`, `pets`, `religion`, `orientation`).
*   Simulated activity fields: `login_frequency`, `profile_updates`, `message_count`.
*   Other profile fields used for completeness calculation.

### Enhanced Matching Model (`ml.models.enhanced_matching.EnhancedMatchingModel`)

Uses a Random Forest Classifier (`sklearn.ensemble.RandomForestClassifier`) trained on **synthetically generated match labels** to predict compatibility.

*   **Feature Vector (`_create_feature_vector`)**: Creates a vector for a user pair based on:
    *   Age difference (using `age` field from OkCupid).
    *   Interest similarity (Jaccard similarity on the derived `interests` list).
    *   Activity score difference (using simulated scores from metadata).
    *   Profile completeness difference (using scores from metadata).
    *   Cluster similarity (whether both users fall into the same cluster determined by the `UserMetadataAnalyzer`).
*   **Training Labels (Synthetic)**: Match labels (`is_match=True/False`) are generated in `evaluate_models.py` by calculating a similarity score between random user pairs (based on age, location, text similarity, metadata) and applying a threshold. *These are not real user matches.*
*   **Output**: Provides `get_matches` method to score potential candidates for a user (used by `MLService`).

## Model Training and Evaluation (`evaluate_models.py`)

The `backend/ml/evaluate_models.py` script orchestrates the training and evaluation process using the OkCupid dataset and synthetic data generation.

**Workflow:**
1.  **Load Data**: Loads the full `okcupid_profiles.csv` using `load_okcupid_data`.
2.  **Process/Simulate**: Cleans text, derives `interests` from categorical columns, and simulates activity fields (`login_frequency`, `profile_updates`, etc.) for each user.
3.  **Split Users**: Splits the list of processed *user* dictionaries into training and testing sets (e.g., 80/20 split).
4.  **Train Metadata Analyzer**: Trains the `UserMetadataAnalyzer` on the *training user set*. Saves the model (e.g., `metadata_analyzer_okcupid.joblib`).
5.  **Analyze All Users**: Uses the trained `UserMetadataAnalyzer` to analyze *all* loaded users (both train and test sets) to generate their metadata profiles (scores, cluster). Stores this in `user_metadata_map`.
6.  **Generate Synthetic Matches**: Calls `generate_match_pairs`. This function:
    *   Selects a large number of random user pairs.
    *   Calculates a compatibility score for each pair based on age, location, text similarity (TF-IDF cosine), and metadata similarity.
    *   Assigns a synthetic `is_match` label based on a `match_compatibility_threshold`.
    *   Stores these pairs along with user data and pre-calculated metadata.
7.  **Split Match Pairs**: Splits the list of generated *match pair* dictionaries into training and testing sets (e.g., 80/20 split).
8.  **Train Matching Model**: Trains the `EnhancedMatchingModel` using the *training match pair set*. It uses the `fit_prepared` method, taking pre-calculated feature vectors and synthetic labels. Saves the model (e.g., `matching_model_okcupid.joblib`).
9.  **Evaluate Models**:
    *   Evaluates the `EnhancedMatchingModel` on the *test match pair set*. Prints metrics (Accuracy, Precision, Recall, F1, Classification Report) and saves a confusion matrix (`confusion_matrix_okcupid.png`).
    *   Evaluates the `UserMetadataAnalyzer` on the *test user set* (using the pre-calculated metadata). Prints metrics (average scores, engagement distribution) and saves the distribution plot (`engagement_distribution_okcupid.png`).

**To Run:**
```bash
# Ensure you are in the root project directory
cd /path/to/SammySwipe

# Make sure dependencies are installed
pip install -r backend/requirements-ml.txt

# Run the evaluation script (this may take a long time)
python backend/ml/evaluate_models.py
```
Models are saved in `backend/ml/models/` and plots in `backend/ml/visualizations/`.

## Model Metrics (OkCupid + Synthetic Data - Apr 2025 Example)

*Metrics obtained from a run of `evaluate_models.py`. These will vary based on dataset version, code changes, and random seeds.*

### Metadata Analyzer (Evaluated on Test Users)
*   **Average Activity Score (Simulated)**: ~0.501 ± 0.157
*   **Average Profile Completeness**: ~0.571 ± **0.000** *(Note: Zero std dev indicates an issue needs investigation - all users might have the same score)*
*   **Engagement Level Distribution (Test Set Example)**:
    *   High: ~88 users
    *   Medium: ~8463 users
    *   Low: ~3011 users

### Matching Model (Evaluated on Test Match Pairs w/ Synthetic Labels)
*   **Accuracy**: ~0.951
*   **Precision (Class 1 - Match)**: ~0.979
*   **Recall (Class 1 - Match)**: ~0.965
*   **F1 Score (Class 1 - Match)**: ~0.972
*   **Precision (Class 0 - No Match)**: ~0.749
*   **Recall (Class 0 - No Match)**: ~0.843
*   **Caveat**: These metrics primarily reflect the model's ability to learn the rules used for *synthetic label generation*. They **do not guarantee** real-world matching performance.

## Future Changes and Improvements

If you want to modify or improve the ML models, consider these areas:

1.  **Profile Completeness**: Investigate and fix the zero standard deviation issue in the profile completeness score calculation or data mapping.
2.  **Synthetic Match Generation (`generate_match_pairs`)**:
    *   Refine the `compatibility_score` calculation with more nuanced features or weights.
    *   Experiment with different `match_compatibility_threshold` values to adjust the balance of synthetic labels.
    *   Implement more sophisticated negative sampling (e.g., hard negatives) instead of purely random pairs.
3.  **Feature Engineering (`load_okcupid_data`, `_create_feature_vector`)**:
    *   Improve interest extraction from OkCupid fields.
    *   Explore using more OkCupid columns (e.g., height, ethnicity) if relevant.
    *   Handle missing values more strategically (e.g., imputation instead of default values).
    *   Incorporate more complex text analysis (e.g., topic modeling on essays).
4.  **Model Selection & Tuning**:
    *   Try different algorithms for the `EnhancedMatchingModel` (e.g., Gradient Boosting, Logistic Regression, Neural Networks).
    *   Tune hyperparameters for `RandomForestClassifier`, `KMeans`, `TfidfVectorizer`, etc. (e.g., using GridSearchCV or RandomizedSearchCV, although this requires adapting the script significantly).
    *   Experiment with different `n_clusters` for `UserMetadataAnalyzer`.
5.  **Real Ground Truth**: The biggest improvement would be to incorporate real user interaction data (likes, swipes, messages leading to conversations) to create *actual* ground-truth match labels for training the `EnhancedMatchingModel`. This would provide much more reliable performance metrics.
6.  **Model Adaptation**: Ensure the `fit` or `fit_prepared` methods of the model classes align with the data structure provided by the `evaluate_models.py` script.

## Dependencies

Ensure the following are installed (see `backend/requirements-ml.txt`):
*   numpy
*   scikit-learn
*   joblib
*   pandas
*   scipy
*   matplotlib
*   seaborn 