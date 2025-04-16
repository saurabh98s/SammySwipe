import streamlit as st
import requests
from PIL import Image
import io
import base64

# API Configuration
API_URL = "http://localhost:8000/api/v1"

def settings_page():
    st.title("SammySwipe - Settings")
    
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    
    # Get current user data
    response = requests.get(f"{API_URL}/users/me", headers=headers)
    
    if response.status_code == 200:
        user_data = response.json()
        
        # Profile Settings
        st.header("Profile Settings")
        
        with st.form("profile_form"):
            full_name = st.text_input("Full Name", value=user_data["full_name"])
            bio = st.text_area("Bio", value=user_data.get("bio", ""))
            interests = st.multiselect(
                "Interests",
                ["Music", "Movies", "Sports", "Travel", "Food", "Art", "Technology", "Gaming"],
                default=user_data.get("interests", [])
            )
            location = st.text_input("Location", value=user_data.get("location", ""))
            
            # Display current profile photo
            if user_data.get("profile_photo"):
                st.image(user_data["profile_photo"], width=200)
            
            # Upload new profile photo
            profile_photo = st.file_uploader("Update Profile Photo", type=["jpg", "png", "jpeg"])
            
            submit = st.form_submit_button("Save Profile")
            
            if submit:
                data = {
                    "full_name": full_name,
                    "bio": bio,
                    "interests": interests,
                    "location": location
                }
                
                response = requests.put(
                    f"{API_URL}/users/me",
                    headers=headers,
                    json=data
                )
                
                if response.status_code == 200:
                    st.success("Profile updated successfully!")
                else:
                    st.error("Failed to update profile")
                
                # Upload new profile photo if provided
                if profile_photo:
                    files = {"file": profile_photo}
                    response = requests.post(
                        f"{API_URL}/users/me/photo",
                        headers=headers,
                        files=files
                    )
                    
                    if response.status_code == 200:
                        st.success("Profile photo updated successfully!")
                    else:
                        st.error("Failed to update profile photo")
        
        # Matching Preferences
        st.header("Matching Preferences")
        
        with st.form("preferences_form"):
            min_age = st.slider("Minimum Age", 18, 100, 18)
            max_age = st.slider("Maximum Age", 18, 100, 50)
            
            preferred_gender = st.multiselect(
                "Preferred Gender",
                ["male", "female", "non_binary", "other"]
            )
            
            max_distance = st.number_input(
                "Maximum Distance (km)",
                min_value=1,
                max_value=1000,
                value=50
            )
            
            interests_weight = st.slider(
                "Importance of Shared Interests",
                0.0,
                1.0,
                0.5,
                help="How much should shared interests affect match scores?"
            )
            
            submit = st.form_submit_button("Save Preferences")
            
            if submit:
                data = {
                    "min_age": min_age,
                    "max_age": max_age,
                    "preferred_gender": preferred_gender,
                    "max_distance": max_distance,
                    "interests_weight": interests_weight
                }
                
                response = requests.put(
                    f"{API_URL}/users/me/preferences",
                    headers=headers,
                    json=data
                )
                
                if response.status_code == 200:
                    st.success("Preferences updated successfully!")
                else:
                    st.error("Failed to update preferences")
        
        # Account Settings
        st.header("Account Settings")
        
        if st.button("Logout"):
            st.session_state.token = None
            st.session_state.user = None
            st.session_state.active_page = "login"
            st.experimental_rerun()

def main():
    if st.session_state.token:
        settings_page()
    else:
        st.error("Please login first")
        st.session_state.active_page = "login"
        st.experimental_rerun()

if __name__ == "__main__":
    main() 