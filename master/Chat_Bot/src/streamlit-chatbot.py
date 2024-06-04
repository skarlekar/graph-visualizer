import streamlit as st
import boto3
from botocore.config import Config
import json


# configure lambda client
lambda_config = Config(
    read_timeout=1000,
    connect_timeout=1000,
    retries={"max_attempts": 0}
)
client = boto3.client('lambda', region_name='us-east-1', config=lambda_config)


# define call to lambda function
def query_neptune(query):
    response = client.invoke(
        FunctionName='kg-chatbot-function',
        InvocationType='RequestResponse',
        Payload=json.dumps({'query': query})
    )
    result = json.load(response['Payload'])
    text = result['body'].strip('\"')
    text = text.replace('\n', '  ')
    return 


st.header('DeepInsight', divider='blue')

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
    response = query_neptune(prompt)

    # Display model response
    with st.chat_message("assistant"):
        st.markdown(response)
    
    # Now add model response to chat history
    st.session_state.messages.append({"role":"assistant","content":response})