import streamlit as st
import json
import os

# 1. Setup Page
st.set_page_config(page_title="PostIT Social", page_icon="🌐")

# 2. Database Helper
DB_FILE = 'users.json'

def load_data():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, 'r') as f:
        return json.load(f)

def save_data(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# 3. App Logic
st.title("🌐 PostIT: Social Media")

if 'user' not in st.session_state:
    st.session_state.user = None

if not st.session_state.user:
    menu = ["Login", "Sign Up"]
    choice = st.sidebar.selectbox("Menu", menu)
    
    username = st.text_input("Username")
    password = st.text_input("Password", type='password')
    
    if choice == "Sign Up":
        if st.button("Create Account"):
            data = load_data()
            if username in data:
                st.error("Username already exists!")
            else:
                data[username] = {"password": password, "posts": []}
                save_data(data)
                st.success("Account created! Please Login.")
    else:
        if st.button("Login"):
            data = load_data()
            if username in data and data[username]["password"] == password:
                st.session_state.user = username
                st.rerun()
            else:
                st.error("Invalid credentials")

else:
    st.sidebar.write(f"Logged in as: **{st.session_state.user}**")
    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.rerun()

    # --- THE SOCIAL PART ---
    tab1, tab2 = st.tabs(["🌎 Global Feed", "✍️ Post Something"])

    with tab2:
        new_post = st.text_area("What's on your mind?")
        if st.button("Post to World"):
            data = load_data()
            data[st.session_state.user]["posts"].append(new_post)
            save_data(data)
            st.success("Posted!")

    with tab1:
        st.subheader("Recent Activity")
        data = load_data()
        all_posts = []
        for user, info in data.items():
            for p in info.get("posts", []):
                all_posts.append({"user": user, "content": p})
        
        for post in reversed(all_posts):
            st.info(f"**{post['user']}**: {post['content']}")
