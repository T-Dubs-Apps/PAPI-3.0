import streamlit as st
import time
import os
from gTTS import gTTS
from textblob import TextBlob
import warnings

# ---------------------------------------------------------
# CONFIG & SETUP
# ---------------------------------------------------------
# Suppress the TextBlob syntax warnings seen in your logs
warnings.filterwarnings("ignore", category=SyntaxWarning)

st.set_page_config(
    page_title="PAPI 3.0",
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
    Uses a temporary file to avoid permission locks.
    """
    try:
        tts = gTTS(text=text, lang='en')
        # Save to a generic filename
        filename = "temp_voice.mp3"
        tts.save(filename)
        
        # Open the file and read bytes so Streamlit can play it
        with open(filename, "rb") as f:
            audio_bytes = f.read()
        
        # Display audio player (hidden or visible)
        st.audio(audio_bytes, format="audio/mp3")
        
    except Exception as e:
        st.error(f"Audio Error: {e}")

def execute_app_simulation(app_name):
    """
    Simulates the execution of a sub-app on screen.
    """
    st.divider()
    st.subheader(f"🚀 Executing: {app_name}")
    
    with st.status("Initializing modules...", expanded=True) as status:
        st.write("Loading Aegis Security protocols...")
        time.sleep(0.8)
        st.write("Verifying User Permissions...")
        time.sleep(0.8)
        st.write(f"Launching {app_name} interface...")
        time.sleep(0.5)
        status.update(label=f"{app_name} is Ready", state="complete", expanded=False)
    
    # Visual placeholder for the "Executed App"
    st.success(f"Active Session: {app_name}")
    
    if "security" in app_name.lower():
        st.info("🛡️ Aegis Guard: Monitoring active threats. System Safe.")
    elif "audio" in app_name.lower():
        st.info("🎛️ Audio Workbench: Ready for input.")
    elif "stock" in app_name.lower():
        st.info("📈 Market Data Link: Established.")
    else:
        st.info(f"System: {app_name} is running in the main viewport.")

# ---------------------------------------------------------
# UI LAYOUT
# ---------------------------------------------------------

# Sidebar
with st.sidebar:
    st.title("PAPI 3.0 Interface")
    st.markdown("---")
    st.write("**System Status:** 🟢 Online")
    st.write("**Security:** 🛡️ Aegis Guard Active")
    st.write("**User:** Troy Walker")
    
    st.markdown("### Quick Commands")
    if st.button("Activate Children's Mode"):
        st.toast("Children's Mode Activated. Parental Controls Locked.")
    
    if st.button("Run System Diagnostics"):
        with st.spinner("Scanning..."):
            time.sleep(1.5)
        st.toast("All systems nominal.")

# Main Area
st.title("P.A.P.I. 3.0")
st.caption("Programmable Artificial Personal Intelligence")

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

    # Analyze sentiment (basic logic check)
    blob = TextBlob(user_input)
    
    # Check for "Execute" command
    if "execute" in user_input.lower() or "run" in user_input.lower():
        # Extract app name (simple logic)
        words = user_input.split()
        if "execute" in words:
            idx = words.index("execute")
        elif "run" in words:
            idx = words.index("run")
        else:
            idx = -1
            
        if idx != -1 and idx + 1 < len(words):
            target_app = " ".join(words[idx+1:]).capitalize()
            response_text = f"Acknowledged. Initiating launch sequence for {target_app}."
            run_app_trigger = True
        else:
            response_text = "Which application would you like me to execute?"
    else:
        # General Chat Response
        response_text = f"PAPI Processed: {user_input}"

    # 3. Display Assistant Response
    with st.chat_message("assistant"):
        st.markdown(response_text)
        speak_text(response_text)
        
        # If an app was requested, show it on screen
        if run_app_trigger:
            execute_app_simulation(target_app)

    st.session_state.messages.append({"role": "assistant", "content": response_text})