import streamlit as st
import PyPDF2
import io
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Ai resume critique",page_icon="📃", layout="centered")

st.title("AI Resume Critiquer")
st.markdown("Upload your resume and get AI-powered feedback tailored to your needs!")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

uploaded_file = st.file_uploader("Upload your resume (PDF or TXT)", type=["pdf","txt"])

job_role = st.text_input("Enter the job role you're targetting(optional)")

analyze = st.button("Analyze Resume")




def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text+= page.extract_text() + "\n"
    return text



def extract_text_from_file(uploaded_file):
    if uploaded_file.type == "application/pdf":
        return extract_text_from_pdf(io.BytesIO(uploaded_file.read()))
    
    return uploaded_file.read().decode("utf-8")

def get_gemini_response_text(response):
    msg = response.choices[0].message
    
    # Direct text
    if msg.content:
        return msg.content

    # returns a parts list
    if hasattr(msg, "parts") and msg.parts:
        texts = []
        for p in msg.parts:
            if hasattr(p, "text"):
                texts.append(p.text)
        if texts:
            return "\n".join(texts)

    return "No content returned from Gemini."


if analyze and uploaded_file:
    try:
        file_content = extract_text_from_file(uploaded_file)

        if not file_content.strip():
            st.error("File does not have any content")
            st.stop()

        prompt = f"""Please analyze this resume and provide constructive feedback.
        Focus on the following aspects:
        1.Content clarity and impact
        2.Skills presentation
        3.Experience descriptions
        4.Specific improvements for {job_role if job_role else 'general job applications'}

        Resume content:{file_content}

        Please provide your analysis in a clear, structured format with specific recommendations
        
        Don't give the point:Revised Structure Suggestion
        Give the response under 600 words

        """

        client = OpenAI(
            api_key=GEMINI_API_KEY,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )

        response = client.chat.completions.create(
            model="gemini-2.5-flash",
            messages=[
                {
                    "role":"system","content":"You are an expert resume reviewer with years of experience in HR and recruitement"
                },
                {
                    "role":"user", "content":prompt
                }
            ],
            temperature=0.7,
            
        )

        st.markdown("### Analysis Results: ")
        
        output = get_gemini_response_text(response)
        
        

        st.markdown(output)


    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

