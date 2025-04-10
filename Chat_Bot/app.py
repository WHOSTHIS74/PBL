import streamlit as st
import os
import time
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain.memory import ConversationBufferWindowMemory
from langchain.chains import ConversationalRetrievalChain
from dotenv import load_dotenv

# Set up environment variables
load_dotenv()
os.environ['GOOGLE_API_KEY'] = os.getenv("GOOGLE_API_KEY")
groq_api_key = os.getenv("GROQ_API_KEY")

# Streamlit UI setup
st.set_page_config(page_title="SimpleSaral - Scholarship ChatBot", page_icon="🎓")
col1, col2, col3 = st.columns([1, 4, 1])

# Title and Subtitle
st.title("SimpleSaral Scholarship ChatBot 🎓")
st.subheader("Get scholarship information in a simple chat interface")

# Custom CSS to make the design more modern
st.markdown("""
    <style>
    /* Body Background Color */
    .reportview-container {
        background-color: #f4f8fb;
        padding-top: 2em;
    }
    
    /* Chat area styling */
    .stChatMessage {
        padding: 10px;
        border-radius: 12px;
        background-color: #f3f4f6;
        margin-bottom: 15px;
        font-size: 1.1em;
        max-width: 75%;
        word-wrap: break-word;
    }
    
    /* User chat message */
    .user .stChatMessage {
        background-color: #007bff;
        color: white;
    }
    
    /* Assistant chat message */
    .assistant .stChatMessage {
        background-color: #e0e0e0;
        color: black;
    }
    
    /* Button Styling */
    div.stButton > button:first-child {
        background-color: #4CAF50;
        color: white;
        border-radius: 12px;
        padding: 10px 24px;
        font-size: 1.1em;
        width: 100%;
    }
    div.stButton > button:active {
        background-color: #45a049;
    }
    
    /* Input box styling */
    .stTextInput > div > div > input {
        border-radius: 12px;
        padding: 10px;
        font-size: 1em;
        border: 1px solid #ddd;
    }
    </style>
""", unsafe_allow_html=True)

# Reset conversation function
def reset_conversation():
    st.session_state.messages = []
    st.session_state.memory.clear()

# Initialize session state for storing conversation messages and memory
if "messages" not in st.session_state:
    st.session_state.messages = []

if "memory" not in st.session_state:
    st.session_state.memory = ConversationBufferWindowMemory(k=2, memory_key="chat_history", return_messages=True)

# Initialize embeddings and vector store
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
db = FAISS.load_local("my_vector_store", embeddings, allow_dangerous_deserialization=True)
db_retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": 4})

# Define the prompt template
prompt_template = """
<s>[INST]This is a chat template for the SimpleSaral Scholarship ChatBot. Your goal is to provide precise and concise information regarding scholarships, eligibility criteria, application procedures, and deadlines. Respond based on the given scholarship data. If a question is outside the scope, provide the best response based on available knowledge.
CONTEXT: {context}
CHAT HISTORY: {chat_history}
QUESTION: {question}
ANSWER:
</s>[INST]
"""
prompt = PromptTemplate(template=prompt_template, input_variables=['context', 'question', 'chat_history'])

# Initialize the LLM
llm = ChatGroq(groq_api_key=groq_api_key, model_name="llama3-70b-8192")

# Set up the QA chain
qa = ConversationalRetrievalChain.from_llm(
    llm=llm,
    memory=st.session_state.memory,
    retriever=db_retriever,
    combine_docs_chain_kwargs={'prompt': prompt}
)

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message.get("role")):
        st.write(message.get("content"))

# Input prompt
input_prompt = st.chat_input("Ask me about scholarships!")

if input_prompt:
    with st.chat_message("user"):
        st.write(input_prompt)

    # Save user message to session
    st.session_state.messages.append({"role": "user", "content": input_prompt})

    # Assistant's response
    with st.chat_message("assistant"):
        with st.status("Thinking 💡...", expanded=True):
            result = qa.invoke(input=input_prompt)
            message_placeholder = st.empty()
            full_response = ""

            # Simulate typing effect
            for chunk in result["answer"]:
                full_response += chunk
                time.sleep(0.02)
                message_placeholder.markdown(full_response + " ▌")

        # Reset button
        st.button('Reset All Chat 🗑️', on_click=reset_conversation)

    # Save assistant's message to session
    st.session_state.messages.append({"role": "assistant", "content": result["answer"]})
