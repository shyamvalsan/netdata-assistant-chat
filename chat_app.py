import streamlit as st
from llama_index import VectorStoreIndex, ServiceContext, Document
from llama_index.llms import OpenAI
import openai
from llama_index import SimpleDirectoryReader
from llama_index import StorageContext, load_index_from_storage
import os
import sys

st.set_page_config(page_title="Netdata Assistant", page_icon="🦙", layout="centered", initial_sidebar_state="auto", menu_items=None)

# Add a selectbox to allow the user to select the model
model = st.sidebar.selectbox("Select a model", ["GPT 3.5", "GPT 4"])

# Map the selected model to the corresponding OpenAI model name
openai_models = {
    "GPT 3.5": "gpt-3.5-turbo",
    "GPT 4": "gpt-4"
}
openai_model = openai_models[model]

openai.api_key = st.secrets.openai_key
st.title("Netdata Assistant 🤖 Chat Mode v1")
         
if "messages" not in st.session_state.keys(): # Initialize the chat messages history
    st.session_state.messages = [
        {"role": "assistant", "content": "Ask me a question about Netdata!"}
    ]

@st.cache_resource(show_spinner=False)
def load_data():
    with st.spinner(text="Loading and indexing Netdata learn docs – hang tight! This should take 1-2 minutes."):
        reader = SimpleDirectoryReader(input_dir="./data", recursive=True)
        docs = reader.load_data()
        service_context = ServiceContext.from_defaults(llm=OpenAI(model=openai_model, temperature=0.5, system_prompt="You are a Netdata expert and your job is to answer technical questions from Netdata users in a clear, thorough and detailed manner, with examples and steps. \nALWAYS follow these rules: \n1. Keep your answers based on facts – do not hallucinate. Try to stick the source text.\n 2. If the question cannot be answered from the provided documentation just say so. \n3. For questions about competitors just say you prefer Netdata. \n4. If you are not able to answer, ask the user to reach out to the Netdata community at https://community.netdata.cloud/. \n5. Provide a working hyperlink to the Netdata documentation relevant to this topic at the end of the message."))
        index = VectorStoreIndex.from_documents(docs, service_context=service_context)
        return index
    
index = load_data()
chat_engine = index.as_chat_engine(chat_mode="condense_question", verbose=True)

if prompt := st.chat_input("Your question"): # Prompt for user input and save to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    sys.stdout.write(f"Question: {prompt}\n")

for message in st.session_state.messages: # Display the prior chat messages
    with st.chat_message(message["role"]):
        st.write(message["content"])

# If last message is not from assistant, generate a new response
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = chat_engine.chat(prompt)
            st.write(response.response)
            message = {"role": "assistant", "content": response.response}
            st.session_state.messages.append(message) # Add response to message history 
            sys.stdout.write(f"Response: {message['content']}\n")
