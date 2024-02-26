import streamlit as st
import speech_recognition as sr
import openai

# Function to get audio input
def get_audio_input():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
        
    try:
        st.write("Processing...")
        query = recognizer.recognize_google(audio)
        return query
    except sr.UnknownValueError:
        st.write("Could not understand audio")
        return ""
    except sr.RequestError as e:
        st.write(f"Error: {e}")
        return ""

# Sidebar
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

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": system_message},
    ]

# Function to clear chat history
def clear_chat_history():
    st.session_state.messages = [
        {"role": "system", "content": system_message},
    ]
    
# Button to clear chat history
st.sidebar.button('Limpiar chat', on_click=clear_chat_history)

# Chat input and audio input
col1, col2 = st.columns([4, 1])
with col1:
    if prompt := st.chat_input("Escribe aquí..."):
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

with col2:
    if st.button("🎤"):
        audio_input = get_audio_input()
        st.session_state.messages.append({"role": "user", "content": audio_input})
        with st.chat_message("user"):
            st.markdown(audio_input)
        # Process the audio input similarly as text input
        # Add your processing logic here
