import streamlit as st
from llama_index import VectorStoreIndex, ServiceContext, Document
from llama_index.llms import OpenAI
import openai
from llama_index import SimpleDirectoryReader
from llama_index import StorageContext, load_index_from_storage
import replicate
import os

st.set_page_config(page_title="Netdata Assistant", page_icon="🦙", layout="centered", initial_sidebar_state="auto", menu_items=None)

# Add a selectbox to allow the user to select the model
model = st.sidebar.selectbox("Select a model", ["GPT 3.5", "GPT 4", "Llama 2"])

# Map the selected model to the corresponding OpenAI model name
openai_models = {
    "GPT 3.5": "gpt-3.5-turbo",
    "GPT 4": "gpt-4"
}
openai_model = openai_models[model]

#replicate/llama-2-70b-chat:2796ee9483c3fd7aa2e171d38f4ca12251a30609463dcfd4cd76703f22e96cdf

replicate_api = st.secrets.replicate_key
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
        service_context = ServiceContext.from_defaults(llm=OpenAI(model=openai_model, temperature=0.5, system_prompt="You are an expert on Netdata and your job is to answer technical questions from Netdata users in a clear and concise manner. Keep your answers based on facts – do not hallucinate. If the question cannot be answered from the provided documentation just say so. For questions about competitors just say you prefer Netdata."))
        index = VectorStoreIndex.from_documents(docs, service_context=service_context)
        return index
    
# Caching index
#new_index.storage_context.persist()
# Reading from stored index
#storage_context = StorageContext.from_defaults(persist_dir="./storage")
#index = load_index_from_storage(storage_context)

index = load_data()
chat_engine = index.as_chat_engine(chat_mode="condense_question", verbose=True)

if prompt := st.chat_input("Your question"): # Prompt for user input and save to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

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