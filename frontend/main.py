import streamlit as st
import requests
import json
from datetime import datetime
from PIL import Image
import io
import base64

# API Configuration
API_URL = "http://localhost:8000/api/v1"

def init_session_state():
    if "token" not in st.session_state:
        st.session_state.token = None
    if "user" not in st.session_state:
        st.session_state.user = None
    if "active_page" not in st.session_state:
        st.session_state.active_page = "login"

def login_page():
    st.title("SammySwipe - Login")
    
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            response = requests.post(
                f"{API_URL}/auth/token",
                data={"username": email, "password": password}
            )
            
            if response.status_code == 200:
                data = response.json()
                st.session_state.token = data["access_token"]
                st.session_state.active_page = "matches"
                st.experimental_rerun()
            else:
                st.error("Invalid email or password")
    
    if st.button("Don't have an account? Register"):
        st.session_state.active_page = "register"
        st.experimental_rerun()

def register_page():
    st.title("SammySwipe - Register")
    
    with st.form("register_form"):
        email = st.text_input("Email")
        username = st.text_input("Username")
        full_name = st.text_input("Full Name")
        password = st.text_input("Password", type="password")
        gender = st.selectbox(
            "Gender",
            ["male", "female", "non_binary", "other"]
        )
        birth_date = st.date_input("Birth Date")
        bio = st.text_area("Bio")
        interests = st.multiselect(
            "Interests",
            ["Music", "Movies", "Sports", "Travel", "Food", "Art", "Technology", "Gaming"]
        )
        location = st.text_input("Location")
        profile_photo = st.file_uploader("Profile Photo", type=["jpg", "png", "jpeg"])
        
        submit = st.form_submit_button("Register")
        
        if submit:
            data = {
                "email": email,
                "username": username,
                "full_name": full_name,
                "password": password,
                "gender": gender,
                "birth_date": birth_date.isoformat(),
                "bio": bio,
                "interests": interests,
                "location": location
            }
            
            if profile_photo:
                img_bytes = profile_photo.read()
                img_b64 = base64.b64encode(img_bytes).decode()
                data["profile_photo"] = f"data:image/{profile_photo.type.split('/')[-1]};base64,{img_b64}"
            
            response = requests.post(
                f"{API_URL}/auth/register",
                json=data
            )
            
            if response.status_code == 200:
                st.success("Registration successful! Please login.")
                st.session_state.active_page = "login"
                st.experimental_rerun()
            else:
                st.error(response.json()["detail"])
    
    if st.button("Already have an account? Login"):
        st.session_state.active_page = "login"
        st.experimental_rerun()

def matches_page():
    st.title("SammySwipe - Matches")
    
    # Get match recommendations
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    response = requests.get(f"{API_URL}/matches/recommendations", headers=headers)
    
    if response.status_code == 200:
        matches = response.json()
        
        for match in matches:
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col1:
                if match.get("profile_photo"):
                    img_data = base64.b64decode(match["profile_photo"].split(",")[1])
                    img = Image.open(io.BytesIO(img_data))
                    st.image(img, width=150)
                else:
                    st.image("default_avatar.png", width=150)
            
            with col2:
                st.subheader(match["full_name"])
                st.write(f"Match Score: {match['match_score']}%")
                st.write(f"Bio: {match['bio']}")
                st.write(f"Interests: {', '.join(match['interests'])}")
            
            with col3:
                if st.button("Like", key=f"like_{match['id']}"):
                    response = requests.post(
                        f"{API_URL}/matches/{match['id']}",
                        headers=headers
                    )
                    if response.status_code == 200:
                        st.success("Match created!")
                
                if st.button("Pass", key=f"pass_{match['id']}"):
                    response = requests.put(
                        f"{API_URL}/matches/{match['id']}/reject",
                        headers=headers
                    )
                    if response.status_code == 200:
                        st.success("Passed!")
            
            st.markdown("---")

def main():
    init_session_state()
    
    if st.session_state.active_page == "login":
        login_page()
    elif st.session_state.active_page == "register":
        register_page()
    elif st.session_state.active_page == "matches":
        matches_page()

if __name__ == "__main__":
    main() 