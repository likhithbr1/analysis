import streamlit as st
import pandas as pd
import numpy as np
import re
from sentence_transformers import SentenceTransformer, util

# ---------- CONFIG ----------
SIMILARITY_THRESHOLD_DEFAULT = 0.85
MODEL_NAME = "all-MiniLM-L6-v2"
ORION_FILE = "Orion_Products.xlsx"
SDP_FILE = "SDP_Products.xlsx"

# ---------- CLEANING FUNCTION ----------
def clean_text(text):
    text = str(text).lower()
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# ---------- LOAD & PREPROCESS DATA ----------
@st.cache_data
def load_and_prepare_data():
    orion_df = pd.read_excel(ORION_FILE)
    sdp_df = pd.read_excel(SDP_FILE)

    orion_df = orion_df.rename(columns={"PRODUCT_CODE": "product_name", "PRODUCT_DSC": "product_description"})
    sdp_df = sdp_df.rename(columns={"OFFERING_TYPE_CD": "product_name", "OFFERING_DSC": "product_description"})

    orion_df.dropna(subset=["product_description"], inplace=True)
    sdp_df.dropna(subset=["product_description"], inplace=True)

    orion_df["product_description"] = orion_df["product_description"].apply(clean_text)
    sdp_df["product_description"] = sdp_df["product_description"].apply(clean_text)

    orion_df["full_text"] = orion_df["product_name"] + " " + orion_df["product_description"]
    sdp_df["full_text"] = sdp_df["product_name"] + " " + sdp_df["product_description"]

    return orion_df, sdp_df

# ---------- SIMILARITY FUNCTION ----------
@st.cache_resource
def load_model():
    return SentenceTransformer(MODEL_NAME)

def find_similar_products(orion_df, sdp_df, model, threshold):
    orion_embeddings = model.encode(orion_df["full_text"].tolist(), convert_to_tensor=True)
    sdp_embeddings = model.encode(sdp_df["full_text"].tolist(), convert_to_tensor=True)

    cos_sim_matrix = util.cos_sim(orion_embeddings, sdp_embeddings)

    matches = []
    for i in range(len(orion_df)):
        for j in range(len(sdp_df)):
            score = cos_sim_matrix[i][j].item()
            if score >= threshold:
                matches.append({
                    "Orion Code": orion_df.iloc[i]["product_name"],
                    "Orion Description": orion_df.iloc[i]["product_description"],
                    "SDP Code": sdp_df.iloc[j]["product_name"],
                    "SDP Description": sdp_df.iloc[j]["product_description"],
                    "Similarity Score": round(score, 4)
                })

    return pd.DataFrame(matches)

# ---------- STREAMLIT UI ----------
st.set_page_config(page_title="🔍 Product Similarity Analyzer", layout="wide")
st.title("🔍 Product Similarity Analysis")
st.markdown("Compare products between Orion and SDP systems using semantic similarity.")

threshold = st.slider("Similarity Threshold", 0.5, 0.99, SIMILARITY_THRESHOLD_DEFAULT, 0.01)

with st.spinner("Loading and processing data..."):
    orion_df, sdp_df = load_and_prepare_data()
    model = load_model()
    result_df = find_similar_products(orion_df, sdp_df, model, threshold)

if not result_df.empty:
    st.success(f"Found {len(result_df)} similar product pairs above the threshold.")
    st.dataframe(result_df, use_container_width=True)
    csv = result_df.to_csv(index=False)
    st.download_button("📥 Download Results as CSV", csv, file_name="similar_products.csv")
else:
    st.warning("No similar products found above the selected threshold.")
