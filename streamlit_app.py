import streamlit as st
import os
import pdfplumber
import docx
from openai import OpenAI
from dotenv import load_dotenv

# ---------------- Load API Key ----------------
load_dotenv()
key='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'
client = OpenAI(api_key=key)

# ---------------- Page Config ----------------
st.set_page_config(page_title="CV–JD ATS Analyzer", layout="wide")

# ---------------- Styles ----------------
st.markdown("""
<style>
.title {
    background: linear-gradient(90deg, #ab47bc, #ce93d8);
    color: white;
    text-align: center;
    padding: 18px;
    border-radius: 14px;
    font-size: 32px;
    font-weight: bold;
    margin-bottom: 25px;
}
.purple {
    color: #8e24aa;
    font-size: 22px;
    font-weight: bold;
    margin-top: 20px;
}
.teal-result {
    color: #00695c;
    background-color: #e0f2f1;
    padding: 16px;
    border-radius: 12px;
    border-left: 6px solid #00897b;
    font-size: 16px;
    line-height: 1.7;
    white-space: pre-wrap;
}
</style>

<div class="title">💜 CV–JD ATS & Interview Assistant</div>
""", unsafe_allow_html=True)

# ---------------- Helpers ----------------
def extract_cv_text(file):
    if file.name.endswith(".pdf"):
        text = ""
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
        return text

    elif file.name.endswith(".docx"):
        doc = docx.Document(file)
        return "\n".join(p.text for p in doc.paragraphs)

def ask_openai(prompt, max_tokens=600):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens
    )
    return response.choices[0].message.content

# ---------------- UI ----------------
st.markdown('<p class="purple">📄 Upload CV (PDF / DOCX)</p>', unsafe_allow_html=True)
cv_file = st.file_uploader("Upload your CV", type=["pdf", "docx"])

st.markdown('<p class="purple">🧠 Paste Job Description (JD)</p>', unsafe_allow_html=True)
jd_text = st.text_area("Job Description", height=260)

# ---------------- Processing ----------------
if cv_file and jd_text:
    cv_text = extract_cv_text(cv_file)

    if st.button("🚀 Analyze CV"):
        with st.spinner("Analyzing CV using OpenAI..."):

            ats_prompt = f"""
            You are an ATS system.
            Analyze the CV against the Job Description.

            Provide:
            1. ATS Match Score (0–100)
            2. Extracted Skills
            3. Missing Skills
            4. Resume Improvement Suggestions

            CV:
            {cv_text}

            Job Description:
            {jd_text}
            """

            ats_result = ask_openai(ats_prompt)

            interview_prompt = f"""
            Generate JD-specific interview questions.
            Sections:
            - Cloud / DevOps Architecture
            - MLOps (Azure preferred)
            - Python
            - System Design
            - Behavioral
            """

            interview_qs = ask_openai(interview_prompt)

        # ---------------- Results ----------------
        st.success("✅ Analysis Complete")

        tab1, tab2, tab3 = st.tabs([
            "📊 ATS Analysis",
            "💡 Recommendations",
            "🎤 Interview Prep"
        ])

        with tab1:
            st.markdown('<p class="purple">ATS Evaluation</p>', unsafe_allow_html=True)
            st.markdown(
                f'<div class="teal-result">{ats_result}</div>',
                unsafe_allow_html=True
            )

        with tab2:
            st.markdown('<p class="purple">Resume Recommendations</p>', unsafe_allow_html=True)
            st.markdown(
                f'<div class="teal-result">{ats_result}</div>',
                unsafe_allow_html=True
            )

        with tab3:
            st.markdown('<p class="purple">Interview Questions</p>', unsafe_allow_html=True)
            st.markdown(
                f'<div class="teal-result">{interview_qs}</div>',
                unsafe_allow_html=True
            )

        # ---------------- Download ----------------
        final_report = f"""
ATS ANALYSIS
------------
{ats_result}

INTERVIEW QUESTIONS
-------------------
{interview_qs}
"""

        st.download_button(
            "📥 Download Full Report",
            data=final_report,
            file_name="CV_JD_ATS_Report.txt"
        )

else:
    st.info("⬆️ Upload CV and paste JD to start analysis")
