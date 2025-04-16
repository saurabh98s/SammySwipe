# SammySwipe - Advanced Dating App with Social Media Interest Analysis

A modern dating application that uses social media interest analysis and machine learning to provide intelligent matches.

## Features

- User registration and profile management
- Social media interest analysis
- ML-powered matching algorithm
- Real-time chat
- Media sharing capabilities
- Video chat features
- Graph-based relationship management

## Tech Stack

- Backend: FastAPI
- Frontend: Streamlit
- Database: Neo4j (Graph Database)
- ML Components: scikit-learn
- Authentication: JWT

## Setup Instructions

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up environment variables:
   Create a `.env` file with:
   ```
   NEO4J_URI=your_neo4j_uri
   NEO4J_USER=your_neo4j_user
   NEO4J_PASSWORD=your_neo4j_password
   JWT_SECRET_KEY=your_secret_key
   ```

3. Run the backend:
   ```bash
   uvicorn backend.main:app --reload
   ```

4. Run the frontend:
   ```bash
   streamlit run frontend/main.py
   ```

## Project Structure

```
.
├── backend/
│   ├── api/
│   ├── core/
│   ├── db/
│   ├── models/
│   └── services/
├── frontend/
│   ├── pages/
│   └── components/
├── ml/
│   ├── models/
│   └── pipeline/
└── tests/
```

## Contributing

Please read CONTRIBUTING.md for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 