# main.py
import streamlit as st
from transformers import pipeline
from docx import Document
import pdfplumber
from io import BytesIO

# Load the QA model from your notebook
qa_pipeline = pipeline("question-answering", model="deepset/roberta-base-squad2")

# Sidebar setup
st.sidebar.title("🔐 Setup")
st.sidebar.success("Model loaded locally. No token needed ✅")

# App title and description
st.title("🧑‍⚖ Legal Document Chatbot")
st.markdown("""
Upload a legal document and interact with an AI-powered legal assistant.
Ask about risky clauses, obligations, or any part of the document.
""")

# File uploader
uploaded_file = st.file_uploader("📄 Upload Legal Document", type=["pdf", "docx", "txt"])

# Helper to extract text from supported files
def extract_text(file):
    try:
        if file.type == "application/pdf":
            with pdfplumber.open(BytesIO(file.read())) as pdf:
                return "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
        elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            doc = Document(BytesIO(file.read()))
            return "\n".join([para.text for para in doc.paragraphs])
        else:
            return file.read().decode("utf-8", errors="ignore")
    except Exception as e:
        st.error(f"❌ Failed to extract text: {e}")
        return ""

# Chat state memory
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Core logic
if uploaded_file:
    document_text = extract_text(uploaded_file)

    if document_text:
        st.success("✅ Document processed successfully.")
        st.subheader("💬 Ask a question about the document")

        user_query = st.text_input("Your question:", placeholder="e.g. What are the risky clauses?")

        if user_query:
            with st.spinner("Analyzing document..."):
                result = qa_pipeline({
                    "context": document_text,
                    "question": user_query
                })
                answer = result.get("answer", "⚠ No answer found.")
                st.session_state.chat_history.append(("You", user_query))
                st.session_state.chat_history.append(("AI", answer.strip()))

        # Display chat history
        for sender, msg in st.session_state.chat_history:
            st.markdown(f"**{sender}:** {msg}")
    else:
        st.warning("⚠ No text extracted from the document.")
else:
    st.info("📄 Upload a document to begin chatting.")
