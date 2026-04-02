import streamlit as st
import json
import os
import re
import random
import string
from datetime import datetime, timedelta

# --- 1. BRANDING & CONFIG ---
st.set_page_config(page_title="PostIT: Social Media", page_icon="📬", layout="centered")

# Hide Streamlit UI for the "Spy App" Look
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

DB_FILE = 'users.json'

# --- 2. CORE ENGINE ---
def load_data():
    if not os.path.exists(DB_FILE): return {}
    with open(DB_FILE, 'r') as f:
        try: return json.load(f)
        except: return {}

def save_data(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def is_password_strong(password):
    if len(password) < 7: return False, "Min 7 characters!"
    if not re.search(r"[\$₹£€¥]", password): return False, "Must include a currency sign (₹/$/£)!"
    return True, "Strong"

# --- 3. AUTHENTICATION & SECURITY ---
st.title("📬 PostIT: Social Media")
if 'user' not in st.session_state: st.session_state.user = None
data = load_data()

if not st.session_state.user:
    menu = ["Login", "Sign Up"]
    choice = st.sidebar.selectbox("Portal", menu)
    u_name = st.text_input("Username").strip()

    if u_name in data and "lockout_until" in data[u_name]:
        lock_time = datetime.fromisoformat(data[u_name]["lockout_until"])
        if datetime.now() < lock_time:
            st.error(f"🚫 SUSPENDED! Back in {(lock_time - datetime.now()).seconds // 3600}h.")
            st.stop()

    if choice == "Sign Up":
        pwd = st.text_input("Password", type='password')
        if st.button("Create Account"):
            ok, msg = is_password_strong(pwd)
            if not ok: st.error(msg)
            elif u_name in data: st.warning("Name taken!")
            else:
                code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                data[u_name] = {"password": pwd, "recovery_code": code, "posts": [], "is_pro": False, "attempts": 0}
                save_data(data)
                st.success("✅ Success!")
                st.code(f"RECOVERY CODE: {code}")

    elif choice == "Login":
        pwd = st.text_input("Password", type='password')
        if st.button("Login"):
            if u_name in data and data[u_name]["password"] == pwd:
                st.session_state.user = u_name
                data[u_name]["attempts"] = 0
                save_data(data)
                st.rerun()
            elif u_name in data:
                data[u_name]["attempts"] = data[u_name].get("attempts", 0) + 1
                if data[u_name]["attempts"] >= 3:
                    data[u_name]["lockout_until"] = (datetime.now() + timedelta(hours=48)).isoformat()
                save_data(data)
                st.error("Wrong details!")

# --- 4. MAIN SOCIAL INTERFACE ---
else:
    with st.sidebar:
        st.write(f"Logged in as: **{st.session_state.user}**")
        if data[st.session_state.user].get("is_pro"): st.success("👑 PRO")
        if st.button("Logout"): 
            st.session_state.user = None
            st.rerun()
        
        st.divider()
        st.subheader("👑 PostIT Pro")
        # Updated "Coming Soon" section
        st.warning("🚀 PRO Launching Today!")
        st.info("Get ready for the ₹9 Crown. QR Code coming very soon!")

    t1, t2 = st.tabs(["🌎 Feed", "✍️ Post"])

    with t2:
        topic = st.selectbox("Topic", ["Other (Math/Sci/AI)", "Finance", "Art", "Geography", "Politics"])
        msg = st.text_area("What's on your mind?")
        if st.button("Post"):
            new_post = {
                "id": str(random.randint(1000, 9999)),
                "content": msg,
                "topic": topic,
                "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "likes": [],
                "comments": []
            }
            data[st.session_state.user]["posts"].append(new_post)
            save_data(data)
            st.success("Posted!")

    with t1:
        f_topic = st.multiselect("Filter", ["All", "Finance", "Art", "Geography", "Politics", "Other (Math/Sci/AI)"], default="All")
        feed = []
        for u, info in data.items():
            for p in info.get("posts", []):
                if "All" in f_topic or p.get("topic") in f_topic:
                    feed.append({"u": u, "p": p, "is_pro": info.get("is_pro")})
        
        for item in sorted(feed, key=lambda x: x['p']['time'], reverse=True):
            user, post = item['u'], item['p']
            badge = " 👑" if item['is_pro'] else ""
            
            with st.container(border=True):
                st.markdown(f"**{user}{badge}** | `{post.get('topic')}`")
                st.write(post['content'])
                
                # Interaction Row
                col1, col2 = st.columns([1, 4])
                if col1.button(f"❤️ {len(post.get('likes', []))}", key=f"lk_{post['id']}"):
                    if st.session_state.user not in post['likes']:
                        post['likes'].append(st.session_state.user)
                        save_data(data)
                        st.rerun()
                
                with st.expander(f"💬 {len(post.get('comments', []))} Comments"):
                    for c in post.get('comments', []):
                        st.caption(f"**{c['u']}**: {c['m']}")
                    
                    new_c = st.text_input("Add comment...", key=f"in_{post['id']}")
                    if st.button("Send", key=f"btn_{post['id']}"):
                        if new_c:
                            post['comments'].append({"u": st.session_state.user, "m": new_c})
                            save_data(data)
                            st.rerun()
