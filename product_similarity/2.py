import streamlit as st
import pandas as pd
import numpy as np
import re
from sentence_transformers import SentenceTransformer, util
from sklearn.metrics.pairwise import cosine_similarity
from st_aggrid import AgGrid, GridOptionsBuilder

# ---------- CONFIG ----------
SIMILARITY_THRESHOLD_DEFAULT = 0.85
MODEL_NAME = "all-MiniLM-L6-v2"
ORION_FILE = "Orion_Products.xlsx"
SDP_FILE = "SDP_Products.xlsx"

# ---------- TEXT CLEANING ----------
def clean_text(text):
    text = str(text).lower()
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# ---------- LOAD & PREPROCESS ----------
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

# ---------- PRECOMPUTE EMBEDDINGS + SIMILARITY ----------
@st.cache_data
def precompute_similarity_matrix(orion_df, sdp_df):
    model = SentenceTransformer(MODEL_NAME)
    orion_embeddings = model.encode(orion_df["full_text"].tolist(), convert_to_numpy=True)
    sdp_embeddings = model.encode(sdp_df["full_text"].tolist(), convert_to_numpy=True)
    similarity_matrix = cosine_similarity(orion_embeddings, sdp_embeddings)
    return similarity_matrix

# ---------- FILTER MATCHES ----------
def filter_matches(orion_df, sdp_df, similarity_matrix, threshold):
    matches = []
    for i in range(len(orion_df)):
        for j in range(len(sdp_df)):
            score = similarity_matrix[i][j]
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
st.title("🔍 Product Similarity Analysis (with Row Filtering)")
st.markdown("Explore and filter similar products using an interactive grid below.")

threshold = st.slider("Similarity Threshold", 0.5, 0.99, SIMILARITY_THRESHOLD_DEFAULT, 0.01)

with st.spinner("Loading and computing similarity (runs once)..."):
    orion_df, sdp_df = load_and_prepare_data()
    similarity_matrix = precompute_similarity_matrix(orion_df, sdp_df)

with st.spinner("Filtering based on threshold..."):
    result_df = filter_matches(orion_df, sdp_df, similarity_matrix, threshold)

if result_df.empty:
    st.warning("No similar product pairs found above the threshold.")
    st.stop()

# ---------- AGGRID INTERACTIVE TABLE ----------
st.subheader("📊 Click a row to filter by Orion Product Code")

gb = GridOptionsBuilder.from_dataframe(result_df)
gb.configure_default_column(filter=True, sortable=True, resizable=True)
gb.configure_selection("single", use_checkbox=True)
grid_options = gb.build()

grid_response = AgGrid(
    result_df,
    gridOptions=grid_options,
    height=450,
    update_mode="MODEL_CHANGED",
    fit_columns_on_grid_load=True
)

# ---------- HANDLE ROW SELECTION ----------
if grid_response["selected_rows"]:
    selected_code = grid_response["selected_rows"][0]["Orion Code"]
    filtered_df = result_df[result_df["Orion Code"] == selected_code]
    st.success(f"Showing matches for Orion Product: **{selected_code}**")
    st.dataframe(filtered_df, use_container_width=True)

    csv = filtered_df.to_csv(index=False)
    st.download_button("📥 Download Filtered Results", csv, file_name="filtered_results.csv")
else:
    st.dataframe(result_df, use_container_width=True)
    csv = result_df.to_csv(index=False)
    st.download_button("📥 Download All Results", csv, file_name="similar_products.csv")
