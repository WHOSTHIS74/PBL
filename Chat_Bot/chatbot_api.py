from fastapi import FastAPI
from pydantic import BaseModel
import os
import time
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain.memory import ConversationBufferWindowMemory
from langchain.chains import ConversationalRetrievalChain
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware to allow requests from Django app running on a different port
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can specify your Django app's URL here for added security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Your existing FastAPI code goes here...

# Load environment variables
load_dotenv()
os.environ['GOOGLE_API_KEY'] = os.getenv("GOOGLE_API_KEY")
groq_api_key = os.getenv("GROQ_API_KEY")

# Initialize FastAPI
app = FastAPI()

# Initialize embeddings, vector store, LLM, and QA chain as done in your Streamlit app
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
db = FAISS.load_local("my_vector_store", embeddings, allow_dangerous_deserialization=True)
db_retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": 4})

prompt_template = """
<s>[INST]This is a chat template for the SimpleSaral Scholarship ChatBot. Your goal is to provide precise and concise information regarding scholarships, eligibility criteria, application procedures, and deadlines. Respond based on the given scholarship data. If a question is outside the scope, provide the best response based on available knowledge.
CONTEXT: {context}
CHAT HISTORY: {chat_history}
QUESTION: {question}
ANSWER:
</s>[INST]
"""
prompt = PromptTemplate(template=prompt_template, input_variables=['context', 'question', 'chat_history'])

llm = ChatGroq(groq_api_key=groq_api_key, model_name="llama3-70b-8192")

qa = ConversationalRetrievalChain.from_llm(
    llm=llm,
    memory=ConversationBufferWindowMemory(k=2, memory_key="chat_history", return_messages=True),
    retriever=db_retriever,
    combine_docs_chain_kwargs={'prompt': prompt}
)

# Define the request body model
class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str

# Define the chatbot API endpoint
@app.post("/chatbot/ask", response_model=ChatResponse)
async def chat(request: ChatRequest):
    input_prompt = request.question
    result = qa.invoke(input=input_prompt)
    full_response = "".join(result["answer"])
    return ChatResponse(answer=full_response)
