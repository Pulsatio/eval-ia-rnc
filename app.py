import streamlit as st
from ai_calls import query, get_initial_message

st.set_page_config(page_title="Asistente de docencia", page_icon="🤖")

st.title("🤖 Asistente IA de docencia")


initial_message = get_initial_message()

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": get_initial_message()}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    current_state = None

    
    st.chat_message("user").write(prompt)
    with st.spinner("Pensando..."):
        respuesta_bot = query(prompt,st.session_state.messages[-1])
   
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.messages.append({"role": "assistant", "content": respuesta_bot})
    st.chat_message("assistant").write(respuesta_bot)
