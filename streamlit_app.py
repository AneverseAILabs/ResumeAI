import streamlit as st
import re
import yake
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ---------- Helper functions ----------
def clean_text(t):
    return re.sub(r'[^a-zA-Z0-9\s]', ' ', t.lower())

def compute_match(jd_text, cv_text, top_k=15):
    if not jd_text.strip() or not cv_text.strip():
        return None

    jd_clean = clean_text(jd_text)
    cv_clean = clean_text(cv_text)

    # TF-IDF cosine similarity
    vectorizer = TfidfVectorizer(stop_words="english", max_features=5000)
    tfidf = vectorizer.fit_transform([jd_clean, cv_clean])
    cosine_sim = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0] * 100

    # Keyword overlap
    jd_words = set(jd_clean.split())
    cv_words = set(cv_clean.split())
    common = jd_words.intersection(cv_words)
    overlap = (len(common) / len(jd_words)) * 100 if jd_words else 0

    # Extract keywords using YAKE
    kw_extractor = yake.KeywordExtractor(top=top_k)
    jd_kws = [k for k, _ in kw_extractor.extract_keywords(jd_text)]
    missing = [k for k in jd_kws if k.lower() not in cv_clean]

    return {
        "cosine": round(cosine_sim, 2),
        "overlap": round(overlap, 2),
        "common": list(common)[:15],
        "missing": missing[:10],
        "jd_keywords": jd_kws
    }

# ---------- Streamlit UI ----------
st.set_page_config(page_title="JD–CV Match Analyzer ", layout="wide")

# 💚 Custom Styles (Green, Purple, Indigo)
st.markdown("""
    <style>
    .title {
        background: linear-gradient(90deg, #66bb6a, #a5d6a7);
        color: white;
        text-align: center;
        padding: 15px;
        border-radius: 12px;
        font-size: 30px;
        font-weight: bold;
        margin-bottom: 25px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.15);
        letter-spacing: 1px;
    }
    .stButton button {
        background-color: #66bb6a !important;
        color: white !important;
        border-radius: 10px;
        font-weight: bold;
        border: none;
        transition: 0.3s;
    }
    .stButton button:hover {
        background-color: #4caf50 !important;
        transform: scale(1.03);
    }
    .purple-heading {
        color: #9c27b0;
        font-size: 22px;
        font-weight: bold;
        margin-top: 20px;
    }
    .indigo-heading {
        color: #3f51b5;
        font-size: 22px;
        font-weight: bold;
        margin-top: 20px;
    }
    </style>
    <div class="title">💚 JD–CV Match Analyzer</div>
""", unsafe_allow_html=True)

st.caption("Paste your **Job Description** and **CV text** below to get similarity %, keyword overlap, and missing skill suggestions.")

# ---------- Text Inputs ----------
st.markdown('<p class="purple-heading">🧠 Step 1: Paste Job Description (JD)</p>', unsafe_allow_html=True)
jd_text = st.text_area("Job Description", height=250, placeholder="Paste the job description text here...")

st.markdown('<p class="purple-heading">👤 Step 2: Paste CV Text</p>', unsafe_allow_html=True)
cv_text = st.text_area("Your CV", height=300, placeholder="Paste your CV/resume text here...")

# ---------- Processing ----------
if jd_text and cv_text:
    if st.button("🔍 Analyze Match"):
        with st.spinner("Analyzing JD–CV similarity..."):
            result = compute_match(jd_text, cv_text)
        if result:
            st.success("✅ Analysis complete!")

            col1, col2 = st.columns(2)
            col1.metric("Cosine Similarity", f"{result['cosine']} %")
            col2.metric("Keyword Overlap", f"{result['overlap']} %")

            st.markdown('<p class="indigo-heading">🧩 Common Keywords</p>', unsafe_allow_html=True)
            st.write(", ".join(result["common"]) if result["common"] else "None found")

            st.markdown('<p class="indigo-heading">⚠️ Missing Keywords (Consider Adding)</p>', unsafe_allow_html=True)
            st.write(", ".join(result["missing"]) if result["missing"] else "None — excellent match!")

            with st.expander("📋 Top Keywords Extracted from JD"):
                st.write(", ".join(result["jd_keywords"]))
else:
    st.info("Paste both JD and CV text above to analyze match.")
