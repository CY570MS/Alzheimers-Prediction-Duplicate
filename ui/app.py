# ui/app.py
import streamlit as st
import pandas as pd

FINAL_PATH = "final_ranked_candidates.csv"
PAPERS_PATH = "phase3/outputs/phase3_papers.csv"

st.set_page_config(
    page_title="AI Alzheimer's Drug Discovery",
    layout="wide"
)

# ---------------------------
# Load data
# ---------------------------
@st.cache_data
def load_data():
    final_df = pd.read_csv(FINAL_PATH)
    papers_df = pd.read_csv(PAPERS_PATH)
    return final_df, papers_df

final_df, papers_df = load_data()

# ---------------------------
# Header
# ---------------------------
st.title("🧠 AI-Driven Alzheimer’s Drug Discovery")
st.markdown("""
We combine **machine learning**, **biological reasoning**, and **automated literature analysis**
to identify promising drug candidates for Alzheimer’s disease.
""")

# ---------------------------
# Pipeline explanation
# ---------------------------
with st.expander("🔍 How the system works"):
    st.markdown("""
**Phase 1 – Blood–Brain Barrier Screening**  
Predicts which drugs can cross the BBB using molecular features.

**Phase 2 – Mechanism Plausibility**  
Checks whether drugs target Alzheimer-relevant biological mechanisms.

**Phase 3 – Literature Intelligence**  
Automatically reads thousands of research papers and scores positive vs negative evidence.

**Final Output**  
A ranked shortlist of drug candidates with supporting evidence.
""")

st.divider()

# ---------------------------
# Final ranking table
# ---------------------------
st.subheader("🏆 Final Ranked Drug Candidates")

top_n = st.slider("Number of drugs to show", 5, 50, 15)

display_cols = [
    "drug_name",
    "final_score",
    "phase2_score",
    "signed_score",
    "net_positive",
    "n_papers",
    "models",
    "confidence"
]

st.dataframe(
    final_df[display_cols]
    .head(top_n)
    .style.format({
        "final_score": "{:.3f}",
        "phase2_score": "{:.3f}",
        "signed_score": "{:.2f}",
        "confidence": "{:.2f}"
    }),
    use_container_width=True
)

st.divider()

# ---------------------------
# Drug detail explorer
# ---------------------------
st.subheader("🔬 Explore Drug Evidence")

search_query = st.text_input("🔎 Search for a drug (type to filter)")

if search_query:
    filtered = final_df[
        final_df["drug_name"]
        .str.contains(search_query, case=False, na=False)
    ]
else:
    filtered = final_df

selected_drug = st.selectbox(
    "Select a drug",
    filtered["drug_name"].unique()
)


drug_row = final_df[final_df["drug_name"] == selected_drug].iloc[0]

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Final Score", f"{drug_row['final_score']:.3f}")
with col2:
    st.metric("Phase 2 (Mechanism)", f"{drug_row['phase2_score']:.3f}")
with col3:
    st.metric("Phase 3 (Literature)", f"{drug_row['signed_score']:.2f}")

st.markdown(f"""
**Models observed:** `{drug_row['models']}`  
**Positive vs Negative evidence:** `{int(drug_row['net_positive'])}`  
""")

# ---------------------------
# Paper evidence
# ---------------------------
st.subheader("📄 Supporting Literature")

drug_papers = papers_df[papers_df["drug"] == selected_drug]

if drug_papers.empty:
    st.info(
        "No Alzheimer-specific preclinical literature was found for this drug. "
        "This may indicate a novel candidate or lack of published studies."
    )

else:
    for _, row in drug_papers.head(5).iterrows():
        st.markdown(f"""
**{row['title']}**  
• Model: `{row['model']}`  
• Direction: `{row['direction']}`  
• Outcomes: `{row['outcomes']}`  
• Year: `{row['pub_year']}`  
""")
        st.markdown("---")
