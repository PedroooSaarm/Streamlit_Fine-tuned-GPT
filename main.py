import openai
import streamlit as st


with st.sidebar:
    st.title('🤖💬 SF OpenAI Chatbot')
    openai.api_key = st.text_input('Intruduce tu API key de OpenAI', type='password')
    if not (openai.api_key.startswith('sk-') and len(openai.api_key)==51):
        st.warning('Introduce tus credenciales', icon='⚠️')
    else:
        st.success('Puedes proceder a chatear', icon='👉')
    st.session_state["openai_model"] = st.radio("Selecciona el modleo que deseas usar:", ("gpt-3.5-turbo", "gpt-3.5-turbo FINE_TUNED"))
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

def clear_chat_history():
    st.session_state.messages = st.session_state.messages = [
        {"role": "system", "content": prompt},
        ]
st.sidebar.button('Limpiar chat', on_click=clear_chat_history)
      
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
    st.session_state.messages.append({"role": "assistant", "content": full_response})
