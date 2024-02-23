import openai
import streamlit as st

# Function to generate response using the selected model
def generate_response(prompt, model):
    full_response = ""
    for response in openai.ChatCompletion.create(
        model=model,
        messages=[{"role": m["role"], "content": m["content"]}
                  for m in st.session_state.messages], stream=True):
        full_response += response.choices[0].delta.get("content", "")
    return full_response

with st.sidebar:
    st.title('🤖💬 SF OpenAI Chatbot')
    openai.api_key = st.text_input('Enter OpenAI API token:', type='password')
    if not (openai.api_key.startswith('sk-') and len(openai.api_key)==51):
        st.warning('Please enter your credentials!', icon='⚠️')
    else:
        st.success('Proceed to entering your prompt message!', icon='👉')
    model_selection = st.radio("Select Model", ("gpt-3.5-turbo", "gpt-3.5-turbo FINE_TUNED"))

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        if model_selection == "gpt-3.5-turbo":
            full_response = generate_response(prompt, "gpt-3.5-turbo")
        else:
            full_response = generate_response(prompt, "gpt-3.5-turbo FINE_TUNED")
        message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})
