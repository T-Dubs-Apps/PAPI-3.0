import streamlit as st
from textblob import TextBlob
from better_profanity import profanity
from gTTS import gTTS
import io
import logging

logging.basicConfig(level=logging.ERROR)
st.set_page_config(page_title="PAPI-3 Cloud", page_icon="☁️", layout="wide")

if 'user_tier' not in st.session_state: st.session_state['user_tier'] = None
if 'chat_history' not in st.session_state: st.session_state['chat_history'] = []
if 'assistant_name' not in st.session_state: st.session_state['assistant_name'] = "PAPI"

def get_audio_bytes(text):
    try:
        tts = gTTS(text, lang='en')
        fp = io.BytesIO(); tts.write_to_fp(fp); return fp
    except: return None

def guardian_scan(text):
    if profanity.contains_profanity(text): return False, "⚠️ Language Alert"
    if TextBlob(text).sentiment.polarity < -0.3: return True, "intervention"
    return True, "clean"

def main():
    with st.sidebar:
        if not st.session_state['user_tier']:
            key = st.text_input("Key", type="password")
            if st.button("Login"):
                if key=="0000": st.session_state.update({'user_tier':"Child", 'assistant_name':"Mentor"})
                elif key=="7777": st.session_state['user_tier']="Platinum"
                st.experimental_rerun()
        else:
            st.success(f"Tier: {st.session_state['user_tier']}")
            if st.button("Logout"): st.session_state.clear(); st.experimental_rerun()

    st.header(f"{st.session_state['assistant_name']} (Cloud)")
    if st.session_state['user_tier']:
        for chat in st.session_state['chat_history']:
            with st.chat_message(chat["role"]):
                st.write(chat["msg"])
                if chat.get("audio"): st.audio(chat["audio"], format='audio/mp3')
        
        txt = st.chat_input("Message...")
        if txt:
            st.session_state['chat_history'].append({"role":"user", "msg":txt})
            safe, stat = guardian_scan(txt)
            reply = f"BLOCK: {stat}" if not safe else f"Processed: {txt}"
            audio = get_audio_bytes(reply) if safe else None
            st.session_state['chat_history'].append({"role":"assistant", "msg":reply, "audio":audio})
            st.experimental_rerun()

if __name__ == "__main__": main()