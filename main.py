import openai
import streamlit as st

def clear_chat_history():
    st.session_state.messages = st.session_state.messages = [
        {"role": "system", "content": system_message},
        ]
    
with st.sidebar:
    st.title('🤖💬 SF OpenAI Chatbot')
    st.sidebar.info("Este chatbot utiliza el modelo de lenguaje GPT-3.5 de OpenAI para responder a tus preguntas. ¡Pruébalo!")
    
    openai.api_key = st.text_input('Intruduce tu API key de OpenAI', type='password')
    if not (openai.api_key.startswith('sk-') and len(openai.api_key)==51):
        st.warning('Introduce tus credenciales', icon='⚠️')
    else:
        st.success('Puedes proceder a chatear', icon='👉')
                
    system_message = st.text_area(label='Mensaje de sistema:',
                                height=180,
                                placeholder='Instrucciones que complementan el comportamiento de tu modelo de fine-tuning. Ej: Responde siempre alegre.')
    
    st.session_state["openai_model"] = st.radio("Selecciona el modleo que deseas usar:", ("gpt-3.5-turbo", "gpt-3.5-turbo FINE_TUNED"))
    st.sidebar.button('Limpiar chat', on_click=clear_chat_history)
    


if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": system_message},
        ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Escribe aquí..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        if st.session_state["openai_model"] == "gpt-3.5-turbo FINE_TUNED":
            model_name = "ft:gpt-3.5-turbo-0613:xrealityfactory:streamlit-test:8wrJg3Ol"
        else:
            model_name = st.session_state["openai_model"]
        for response in openai.chat.completions.create(
            model=model_name,
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True
        ):
            full_response += str(response.choices[0].delta.content)
        message_placeholder.markdown(full_response[:-4] + "▌")
        message_placeholder.markdown(full_response[:-4])
    st.session_state.messages.append({"role": "assistant", "content": full_response[:-4]})

