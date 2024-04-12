import streamlit as st

def get_model_response(user_input):
    # Write code to call model here
    return "mock model response"

# Init chatbot history
if "messages" not in st.session_state:
    st.session_state.messages=[]

# Display the previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("Type your question here"):

    # Display the user message
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role":"user","content":prompt})

    # Call model using user prompt
    response = get_model_response(prompt)

    # Display model response
    with st.chat_message("assistant"):
        st.markdown(response)
    
    # Now add model response to chat history
    st.session_state.messages.append({"role":"assistant","content":response})