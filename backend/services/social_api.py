from fastapi import HTTPException
from typing import Dict, Any, Optional
import json
import os
import requests
import logging

logger = logging.getLogger(__name__)

# Environment variables would normally hold these credentials
TWITTER_CLIENT_ID = os.getenv("TWITTER_CLIENT_ID", "twitter_client_id")
TWITTER_CLIENT_SECRET = os.getenv("TWITTER_CLIENT_SECRET", "twitter_client_secret")
TWITTER_REDIRECT_URI = os.getenv("TWITTER_REDIRECT_URI", "http://localhost:8000/api/v1/auth/twitter/callback")

FACEBOOK_APP_ID = os.getenv("FACEBOOK_APP_ID", "facebook_app_id")
FACEBOOK_APP_SECRET = os.getenv("FACEBOOK_APP_SECRET", "facebook_app_secret")
FACEBOOK_REDIRECT_URI = os.getenv("FACEBOOK_REDIRECT_URI", "http://localhost:8000/api/v1/auth/facebook/callback")

INSTAGRAM_CLIENT_ID = os.getenv("INSTAGRAM_CLIENT_ID", "instagram_client_id")
INSTAGRAM_CLIENT_SECRET = os.getenv("INSTAGRAM_CLIENT_SECRET", "instagram_client_secret")
INSTAGRAM_REDIRECT_URI = os.getenv("INSTAGRAM_REDIRECT_URI", "http://localhost:8000/api/v1/auth/instagram/callback")

class MockSocialAPIService:
    """
    Mock service for social media API integrations.
    Used for development and testing purposes.
    """
    
    async def twitter_oauth_redirect(self):
        """Mock Twitter OAuth redirect URL."""
        logger.info("Mock: Generating Twitter OAuth redirect URL")
        return "https://mock-twitter-oauth.com/authorize?client_id=mock_client_id"
    
    async def twitter_oauth_callback(self, code: str):
        """Mock Twitter OAuth callback."""
        logger.info(f"Mock: Processing Twitter OAuth callback with code: {code}")
        return {
            "access_token": "mock_twitter_access_token",
            "refresh_token": "mock_twitter_refresh_token",
            "expires_in": 3600
        }
    
    async def twitter_fetch_user_data(self, access_token: str):
        """Mock fetching Twitter user data."""
        logger.info(f"Mock: Fetching Twitter user data with token: {access_token}")
        return {
            "id": "12345678",
            "screen_name": "mock_twitter_user",
            "name": "Mock Twitter User",
            "description": "This is a mock Twitter profile for testing",
            "followers_count": 1234,
            "friends_count": 567,
            "tweets": [
                {"id": "111", "text": "This is my first mock tweet #testing"},
                {"id": "222", "text": "I love using SammySwipe! #dating #app"},
                {"id": "333", "text": "Just visited the Grand Canyon! Amazing views! #travel"},
                {"id": "444", "text": "Excited about the new iPhone release! #technology"},
                {"id": "555", "text": "Trying out a new recipe tonight! #cooking"}
            ]
        }
    
    async def facebook_oauth_redirect(self):
        """Mock Facebook OAuth redirect URL."""
        logger.info("Mock: Generating Facebook OAuth redirect URL")
        return "https://mock-facebook-oauth.com/dialog/oauth?client_id=mock_client_id"
    
    async def facebook_oauth_callback(self, code: str):
        """Mock Facebook OAuth callback."""
        logger.info(f"Mock: Processing Facebook OAuth callback with code: {code}")
        return {
            "access_token": "mock_facebook_access_token",
            "expires_in": 3600
        }
    
    async def facebook_fetch_user_data(self, access_token: str):
        """Mock fetching Facebook user data."""
        logger.info(f"Mock: Fetching Facebook user data with token: {access_token}")
        return {
            "id": "87654321",
            "name": "Mock Facebook User",
            "email": "mock.user@example.com",
            "picture": {
                "data": {
                    "url": "https://mock-profile-pics.com/facebook.jpg"
                }
            },
            "posts": {
                "data": [
                    {"id": "post1", "message": "Enjoying the weekend with friends!"},
                    {"id": "post2", "message": "Just went to an amazing concert! #music"},
                    {"id": "post3", "message": "Trying out this new dating app called SammySwipe!"},
                    {"id": "post4", "message": "Happy birthday to my best friend!"},
                    {"id": "post5", "message": "Looking forward to my vacation next week! #travel"}
                ]
            }
        }
    
    async def instagram_oauth_redirect(self):
        """Mock Instagram OAuth redirect URL."""
        logger.info("Mock: Generating Instagram OAuth redirect URL")
        return "https://mock-instagram-oauth.com/oauth/authorize?client_id=mock_client_id"
    
    async def instagram_oauth_callback(self, code: str):
        """Mock Instagram OAuth callback."""
        logger.info(f"Mock: Processing Instagram OAuth callback with code: {code}")
        return {
            "access_token": "mock_instagram_access_token",
            "user_id": "9876543210"
        }
    
    async def instagram_fetch_user_data(self, access_token: str):
        """Mock fetching Instagram user data."""
        logger.info(f"Mock: Fetching Instagram user data with token: {access_token}")
        return {
            "id": "9876543210",
            "username": "mock_insta_user",
            "full_name": "Mock Instagram User",
            "bio": "This is a mock Instagram profile for testing",
            "media": {
                "data": [
                    {"id": "media1", "caption": "Beautiful sunset at the beach! #travel #sunset"},
                    {"id": "media2", "caption": "Delicious dinner at the new restaurant! #food #foodie"},
                    {"id": "media3", "caption": "Hiking adventure this weekend! #nature #outdoors"},
                    {"id": "media4", "caption": "Movie night with friends! #movies #fun"},
                    {"id": "media5", "caption": "New outfit for my date tonight! #fashion"}
                ]
            }
        }

# Global instance
social_api_service = MockSocialAPIService() 