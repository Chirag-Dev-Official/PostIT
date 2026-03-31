import streamlit as st
import json
import os
from datetime import datetime
from PIL import Image

# --- 🎨 PAGE CONFIG ---
st.set_page_config(page_title="PostIT Secure 🔒", page_icon="📝", layout="wide")

# --- 📂 DATA STORAGE (The "Memory" of your app) ---
USER_DB = "users.json"

def load_users():
    if os.path.exists(USER_DB):
        with open(USER_DB, "r") as f:
            return json.load(f)
    return {}

def save_user(username, password):
    users = load_users()
    users[username] = password
    with open(USER_DB, "w") as f:
        json.dump(users, f)

# --- 🔑 LOGIN / SIGNUP SYSTEM ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🛡️ Welcome to PostIT Secure")
    
    tab1, tab2 = st.tabs(["Login", "Create Account"])
    
    with tab2:
        new_user = st.text_input("Choose a Username", placeholder="Put your username here...")
        new_pass = st.text_input("Create a Password", type="password")
        if st.button("✨ Sign Up"):
            users = load_users()
            if new_user in users:
                st.error("Username already exists!")
            elif new_user and new_pass:
                save_user(new_user, new_pass)
                st.success("Account created! Now go to the Login tab.")
            else:
                st.warning("Please fill both boxes!")

    with tab1:
        login_user = st.text_input("Username", placeholder="Enter your username...")
        login_pass = st.text_input("Password", type="password")
        if st.button("🚀 Enter PostIT"):
            users = load_users()
            if login_user in users and users[login_user] == login_pass:
                st.session_state.logged_in = True
                st.session_state.current_user = login_user
                st.rerun()
            else:
                st.error("Invalid Username or Password!")
    st.stop() # Stops the rest of the app from running until logged in

# --- 📱 MAIN POSTIT APP (Only visible after login) ---
current_user = st.session_state.current_user

with st.sidebar:
    st.title("📝 PostIT")
    st.write(f"Logged in as: **{current_user}**")
    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.rerun()
    st.divider()
    st.info("Bengaluru Dev Edition v2.0")

# --- 🧠 FEED DATABASE ---
if 'posts' not in st.session_state:
    st.session_state.posts = [{
        "user": "SYSTEM",
        "content": "🚀 PostIT Secure is Live! Welcome to the network.",
        "tag": "📢 Announcement",
        "time": "04:30 PM",
        "image": None,
        "likes": 1000
    }]

# --- ✍️ CREATE A POST ---
st.title(f"What's the genius plan today, {current_user}?")

with st.expander("➕ New Post", expanded=True):
    col1, col2 = st.columns([2, 1])
    with col1:
        post_text = st.text_area("Share your math formula or AI update...")
        uploaded_img = st.file_uploader("📸 Attach an Image", type=['png', 'jpg', 'jpeg'])
    with col2:
        category = st.selectbox("Topic", ["Math Patterns 📐", "AI & Coding 🤖", "Science 🔬", "Victory Lounge 🏆"])
        if st.button("🚀 PUBLISH"):
            if post_text:
                new_post = {
                    "user": current_user,
                    "content": post_text,
                    "tag": category,
                    "time": datetime.now().strftime("%I:%M %p"),
                    "image": uploaded_img,
                    "likes": 0
                }
                st.session_state.posts.insert(0, new_post)
                st.balloons()

st.divider()

# --- 🌎 THE FEED ---
for idx, p in enumerate(st.session_state.posts):
    with st.container():
        st.markdown(f"""
            <div style="border: 2px solid #262730; padding: 15px; border-radius: 10px; margin-bottom: 10px;">
                <h4 style="margin:0;">{p['user']} <span style="font-size: 10px; color: gray;">({p['time']})</span></h4>
                <p style="font-size: 16px; margin-top: 5px;">{p['content']}</p>
            </div>
        """, unsafe_allow_html=True)
        
        if p['image']:
            st.image(p['image'], use_container_width=True)
        
        if st.button(f"⭐ {p['likes']}", key=f"like_{idx}_{p['user']}"):
            st.session_state.posts[idx]['likes'] += 1
            st.rerun()
