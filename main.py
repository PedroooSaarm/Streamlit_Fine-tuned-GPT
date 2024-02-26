import openai
import streamlit as st
import base64
from audio_recorder_streamlit import audio_recorder
import os


# Sidebar content
with st.sidebar:
    st.title('🤖💬 SF OpenAI Chatbot')
    st.sidebar.info("Este chatbot utiliza el modelo de lenguaje GPT-3.5 de OpenAI para responder a tus preguntas. ¡Pruébalo!")
    
    openai.api_key = st.text_input('Introduce tu API key de OpenAI', type='password')
    if not (openai.api_key.startswith('sk-') and len(openai.api_key)==51):
        st.warning('Introduce tus credenciales', icon='⚠️')
    else:
        st.success('Puedes proceder a chatear', icon='👉')
                
    system_message = st.text_area(label='Mensaje de sistema:',
                                height=180,
                                placeholder='Instrucciones que complementan el comportamiento de tu modelo de fine-tuning. Ej: Responde siempre alegre.')
    
    st.session_state["openai_model"] = st.radio("Selecciona el modelo que deseas usar:", ("gpt-3.5-turbo", "gpt-3.5-turbo FINE_TUNED"))
    
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": system_message},
    ]

# Function to clear chat history
def clear_chat_history():
    st.session_state.messages = [
        {"role": "system", "content": system_message},
    ]

# Function to transcribe speech to text
def speech_to_text(audio_data):
    with open(audio_data, "rb") as audio_file:
        transcript = openai.audio.transcriptions.create(
            model="whisper-1",
            response_format="text",
            file=audio_file
        )
    return transcript

# Function to convert text to speech
def text_to_speech(input_text):
    response = openai.audio.speech.create(
        model="tts-1",
        voice="nova",
        input=input_text
    )
    webm_file_path = "temp_audio_play.mp3"
    with open(webm_file_path, "wb") as f:
        response.stream_to_file(webm_file_path)
    return webm_file_path

# Function to autoplay audio
def autoplay_audio(file_path: str):
    with open(file_path, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode("utf-8")
    md = f"""
    <audio autoplay>
    <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
    </audio>
    """
    st.markdown(md, unsafe_allow_html=True)

# Button to clear chat history
st.sidebar.button('Limpiar chat', on_click=clear_chat_history)

# Container for the microphone
footer_container = st.container()
with footer_container:
    audio_bytes = audio_recorder()

# Handle audio input
if audio_bytes:
    # Transcribe audio
    with st.spinner("Transcribing..."):
        webm_file_path = "temp_audio.mp3"
        with open(webm_file_path, "wb") as f:
            f.write(audio_bytes)
        
        transcript = speech_to_text(webm_file_path)
        st.session_state.messages.append({"role": "user", "content": transcript})
        os.remove(webm_file_path)

# Chat input field
if prompt := st.text_input("Escribe aquí o graba tu pregunta...", key="user_input"):
    if prompt.strip() != "":
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            for response in openai.chat.completions.create(
                model = st.session_state["openai_model"],
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True
            ): full_response += str(response.choices[0].delta.content)
            message_placeholder.markdown(full_response[:-4] + "▌")
            message_placeholder.markdown(full_response[:-4])
        st.session_state.messages.append({"role": "assistant", "content": full_response[:-4]})
