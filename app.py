import streamlit as st
from textblob import TextBlob
from better_profanity import profanity
from PIL import Image

# --- CONFIGURATION & SESSION STATE ---
st.set_page_config(page_title="PAPI-3 Interface", page_icon="🤖", layout="wide")

if 'user_tier' not in st.session_state:
    st.session_state['user_tier'] = None
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []
if 'user_avatar' not in st.session_state:
    # Default avatar placeholder
    st.session_state['user_avatar'] = "👤" 

# --- CUSTOM CSS INJECTION ---
def inject_adult_css():
    """Injects CSS for pulsating background and rounded profile images."""
    st.markdown(
        """
        <style>
        /* 1. The Pulsating Background Animation */
        @keyframes gradientPulse {
            0% {background-position: 0% 50%;}
            50% {background-position: 100% 50%;}
            100% {background-position: 0% 50%;}
        }

        /* Apply animation to the main Streamlit container */
        .stApp {
            background: linear-gradient(-45deg, #1a1a2e, #16213e, #0f3460, #53354a);
            background-size: 400% 400%;
            animation: gradientPulse 15s ease infinite;
            color: white; /* Ensure text stays readable */
        }
        
        /* 2. Styling for uploaded profile pictures to make them round */
        [data-testid="stImage"] {
            border-radius: 50%;
            overflow: hidden;
            width: 120px; height: 120px; /* Fixed size for icon feel */
            border: 3px solid #00d4ff; /* glowing border */
            box-shadow: 0 0 15px #00d4ff;
            margin-bottom: 20px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# --- 1. THE GUARDIAN (Safety Layer) ---
# (Kept simple for this demo, same as before)
def guardian_scan(text, tier):
    if profanity.contains_profanity(text):
        return False, "⚠️ Language Alert: Please use kind words."
    if tier == "Child":
        blob = TextBlob(text)
        if blob.sentiment.polarity < -0.3:
             return True, "intervention" 
    return True, "clean"

# --- 2. THE BRAIN (Logic) ---
# (Kept simple for this demo, same as before)
def papi_brain(text, tier, safety_status):
    response = ""
    if safety_status == "intervention":
        response = "I notice you seem a bit down. Remember, mistakes mean you are learning! Let's try again. 🦁"
    elif tier == "Child":
        response = f"That's a great observation! Why do you think '{text}' happens? (I'm here to help you figure it out!)"
    elif tier in ["Silver", "Gold", "Platinum"]:
        response = f"[SYSTEM]: Processing request: '{text}'. Awaiting further input."
        
    return response

# --- 3. THE UI (Main Interface) ---
def main():
    # --- SIDEBAR: Login & Customization ---
    with st.sidebar:
        st.title("🤖 PAPI Systems")
        
        # If not logged in, show login
        if st.session_state['user_tier'] is None:
            st.header("Login")
            key = st.text_input("Enter Key", type="password")
            if st.button("Connect"):
                if key == "0000":
                    st.session_state['user_tier'] = "Child"
                    # Default child avatar
                    st.session_state['user_avatar'] = "🐼"
                    st.experimental_rerun()
                elif key == "2222":
                    st.session_state['user_tier'] = "Silver"
                    st.experimental_rerun()
                elif key == "7777":
                    st.session_state['user_tier'] = "Platinum"
                    st.experimental_rerun()
        
        # If Logged in, show customized controls
        else:
            tier = st.session_state['user_tier']
            st.subheader(f"Tier: {tier.upper()}")

            # --- CUSTOMIZATION SECTION ---
            st.divider()
            
            if tier == "Child":
                # --- CHILD FRIENDLY AVATAR CREATOR ---
                st.write("### Choose Your Buddy!")
                friendly_avatars = {
                    "Brave Lion": "🦁", "Curious Panda": "🐼", "Smart Fox": "🦊",
                    "Happy Pup": "🐶", "Magical Unicorn": "🦄", "Cool Dino": "🦖"
                }
                avatar_choice = st.radio("Pick one:", list(friendly_avatars.keys()))
                # Update session state with the chosen emoji
                st.session_state['user_avatar'] = friendly_avatars[avatar_choice]
                st.write(f"Hello, {avatar_choice}! {st.session_state['user_avatar']}")

            else:
                # --- ADULT TIER: PULSATING BG & PHOTO UPLOAD ---
                # Inject the CSS animation
                inject_adult_css()
                
                st.write("### Profile Icon")
                uploaded_file = st.file_uploader("Upload custom icon", type=['jpg', 'png', 'jpeg'])
                
                if uploaded_file is not None:
                    # Display the uploaded image (CSS makes it round)
                    image = Image.open(uploaded_file)
                    st.image(image)
                    # In a real app, you'd save this image. For now, we use a generic icon for chat.
                    st.session_state['user_avatar'] = "⚡" # Indicates custom user
                else:
                    st.info("Upload a square photo for best results.")

            # --- COMMON CONTROLS ---
            st.divider()
            if st.button("Logout"):
                st.session_state.clear()
                st.experimental_rerun()

    # --- MAIN CHAT AREA ---
    # Header showing the current persona/avatar
    st.header(f"PAPI-3 Online {st.session_state['user_avatar']}" )
    
    if st.session_state['user_tier']:
        # Display Chat History with Avatars
        for chat in st.session_state['chat_history']:
            # Determine avatar based on role
            if chat["role"] == "user":
                avatar = st.session_state['user_avatar']
            else:
                avatar = "🤖" # PAPI's avatar icon

            with st.chat_message(chat["role"], avatar=avatar):
                st.write(chat["msg"])
        
        # Input Area
        user_input = st.chat_input(f"Type here, {st.session_state['user_tier']} user...")
        
        if user_input:
            # 1. User Message
            st.session_state['chat_history'].append({"role": "user", "msg": user_input})
            with st.chat_message("user", avatar=st.session_state['user_avatar']):
                st.write(user_input)
            
            # 2. Guardian Scan
            safe, status = guardian_scan(user_input, st.session_state['user_tier'])
            
            if not safe:
                error_msg = f"[AEGIS BLOCK]: {status}"
                st.session_state['chat_history'].append({"role": "assistant", "msg": error_msg})
                with st.chat_message("assistant", avatar="🛡️"):
                    st.error(error_msg)
            else:
                # 3. Brain Response
                bot_reply = papi_brain(user_input, st.session_state['user_tier'], status)
                st.session_state['chat_history'].append({"role": "assistant", "msg": bot_reply})
                with st.chat_message("assistant", avatar="🤖"):
                    st.write(bot_reply)
    else:
        st.info("Please log in using the sidebar.")

if __name__ == "__main__":
    main()
