import streamlit as st
import time
import os
from gTTS import gTTS
from textblob import TextBlob
import warnings

# ---------------------------------------------------------
# CONFIG & SETUP
# ---------------------------------------------------------
# Suppress specific syntax warnings to keep logs clean
warnings.filterwarnings("ignore", category=SyntaxWarning)

st.set_page_config(
    page_title="PAPI 3.0-1",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# CORE FUNCTIONS
# ---------------------------------------------------------

def speak_text(text):
    """
    Converts text to speech using gTTS and plays it.
    Uses a try/except block to prevent app crashes if audio fails.
    """
    if not text.strip():
        return

    try:
        tts = gTTS(text=text, lang='en')
        # Save to a generic filename to avoid clutter
        filename = "temp_voice.mp3"
        tts.save(filename)
        
        # Open the file and read bytes so Streamlit can play it safely
        with open(filename, "rb") as f:
            audio_bytes = f.read()
        
        # Display audio player (visible to allow replay)
        st.audio(audio_bytes, format="audio/mp3", start_time=0)
        
    except Exception as e:
        st.warning(f"Audio interface offline (Text-only mode active): {e}")

def execute_app_simulation(app_name):
    """
    Simulates the execution of a sub-app on screen with a visual loader.
    """
    st.divider()
    st.subheader(f"🚀 Executing: {app_name}")
    
    # Visual Progress Bar
    progress_text = f"Initializing {app_name} protocols..."
    my_bar = st.progress(0, text=progress_text)

    for percent_complete in range(100):
        time.sleep(0.01)
        my_bar.progress(percent_complete + 1, text=progress_text)
    time.sleep(0.5)
    my_bar.empty()
    
    # Status Indicators
    with st.status("System Check", expanded=True) as status:
        st.write("Loading Aegis Security protocols...")
        time.sleep(0.5)
        st.write("Verifying User Permissions...")
        time.sleep(0.5)
        st.write(f"Launching {app_name} interface...")
        time.sleep(0.5)
        status.update(label=f"{app_name} is Ready", state="complete", expanded=False)
    
    # Success Message
    st.success(f"Active Session: {app_name}")
    
    # Dummy Interface based on app name
    col1, col2 = st.columns([1, 4])
    with col1:
        st.markdown("### 🖥️")
    with col2:
        if "security" in app_name.lower():
            st.info("🛡️ **Aegis Guard**: Monitoring active threats. \n\nStatus: **System Safe**.")
        elif "audio" in app_name.lower():
            st.info("🎛️ **Audio Workbench**: Input channels open. \n\nFrequency: **44.1kHz**.")
        elif "stock" in app_name.lower():
            st.info("📈 **Market Data Link**: Connection Established. \n\nData Feed: **Live**.")
        else:
            st.info(f"System: **{app_name}** is running in the main viewport.")

# ---------------------------------------------------------
# UI LAYOUT
# ---------------------------------------------------------

# Sidebar
with st.sidebar:
    st.title("PAPI 3.0-1")
    st.caption("System Interface")
    st.markdown("---")
    st.write("**System Status:** 🟢 Online")
    st.write("**Security:** 🛡️ Aegis Guard Active")
    st.write("**User:** Troy Walker")
    
    st.markdown("### Quick Commands")
    if st.button("Activate Children's Mode"):
        st.toast("Children's Mode Activated. Parental Controls Locked.")
    
    if st.button("Run Diagnostics"):
        with st.spinner("Scanning system files..."):
            time.sleep(1.5)
        st.toast("All systems nominal.")

# Main Area
st.title("P.A.P.I. 3.0-1")
st.markdown("**Programmable Artificial Personal Intelligence**")

# Chat / Command Interface
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
user_input = st.chat_input("Enter command or chat with PAPI...")

if user_input:
    # 1. Display User Message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # 2. Logic Processing
    response_text = ""
    run_app_trigger = False
    target_app = ""
    user_input_lower = user_input.lower()
    
    # Command Parser
    if "execute" in user_input_lower or "run" in user_input_lower:
        words = user_input.split()
        keyword = "execute" if "execute" in user_input_lower else "run"
        try:
            lower_words = [w.lower() for w in words]
            if keyword in lower_words:
                idx = lower_words.index(keyword)
                if idx + 1 < len(words):
                    target_app = " ".join(words[idx+1:]).capitalize()
                    response_text = f"Acknowledged. Initiating launch sequence for {target_app}."
                    run_app_trigger = True
                else:
                    response_text = "Which application would you like me to execute?"
        except:
            response_text = "I couldn't identify the application name."

    elif "hello" in user_input_lower:
        response_text = "Greetings, Troy. Systems are online and awaiting your command."
    elif "status" in user_input_lower:
        response_text = "All systems operational. Battery at 98%. Security active."
    else:
        response_text = f"Processing command: {user_input}"

    # 3. Display Assistant Response
    with st.chat_message("assistant"):
        st.markdown(response_text)
        speak_text(response_text)
        
        if run_app_trigger:
            execute_app_simulation(target_app)

    st.session_state.messages.append({"role": "assistant", "content": response_text})