import os
import streamlit as st
import pdfplumber
import groq
import warnings

# Get API key from environment variable
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Check if the API Key is missing
if not GROQ_API_KEY:
    st.error("🚨 API Key is missing. Please set GROQ_API_KEY as an environment variable.")
    st.stop()  # Stop execution if the API key is missing

# Initialize Groq Client
client = groq.Client(api_key=GROQ_API_KEY)

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    with pdfplumber.open(pdf_file) as pdf:
        text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
    return text if text else "No text found in the PDF."

# Function to get LLM response from Groq
def get_llm_response(prompt):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": "You are a medical assistant that explains medical reports in simple terms."},
                  {"role": "user", "content": prompt}],
        max_tokens=4096
    )
    return response.choices[0].message.content  

# Set page config for Streamlit
st.set_page_config(page_title="Medical Report Interpreter", page_icon="🩺", layout="wide")

# Sidebar with project details
st.sidebar.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQV-PFR6zbhtbjj6GE8Ju1T6CNsUcI3wwLVhla7aSZFrgxN2pptNTcIxP0&s", use_container_width=True)
st.sidebar.title("🩺 Medical Report Interpreter")
st.sidebar.markdown("""
This tool helps **interpret medical reports** in **simple terms** and suggests 
relevant **questions to ask your doctor**. 

- 📄 Upload a **PDF** or **TXT** file.
- 🧑‍⚕️ AI will **explain** your medical report.
- ❓ Get **questions** for your doctor.
""")
st.sidebar.info("⚡ Powered by **Groq AI & Streamlit**")

# Custom Background CSS for Streamlit
st.markdown(
    """
    <style>
        body {
            background-image: url("https://source.unsplash.com/1600x900/?health,medicine");
            background-size: cover;
        }
        .stApp {
            background-color: rgba(255, 255, 255, 0.8);
            padding: 20px;
            border-radius: 10px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Main UI
st.title("🩺 Medical Report Interpreter")

# File upload widget
uploaded_file = st.file_uploader("📂 Upload your medical report (PDF or TXT)", type=["pdf", "txt"])

if uploaded_file:
    st.subheader("📄 Extracted Report")
    
    # Read text from uploaded file
    if uploaded_file.type == "application/pdf":
        report_text = extract_text_from_pdf(uploaded_file)
    else:
        report_text = uploaded_file.getvalue().decode("utf-8")
    
    # Display extracted text in a text area
    st.text_area("📜 Medical Report", report_text, height=200)

    # Create two columns for features
    col1, col2 = st.columns(2)

    # Explain the medical report
    with col1:
        if st.button("🔍 Explain Report", use_container_width=True):
            with st.spinner("Analyzing..."):
                explanation_prompt = f"Explain this medical report in simple terms:\n\n{report_text}"
                explanation = get_llm_response(explanation_prompt)
            st.subheader("📝 Explanation")
            st.write(explanation)

    # Generate questions for the doctor
    with col2:
        if st.button("❓ Questions to Ask Your Doctor", use_container_width=True):
            with st.spinner("Generating questions..."):
                question_prompt = f"Based on this medical report, suggest questions a patient should ask their doctor:\n\n{report_text}"
                questions = get_llm_response(question_prompt)
            st.subheader("🩺 Suggested Questions")
            st.write(questions)
