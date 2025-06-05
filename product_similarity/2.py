import streamlit as st
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from st_aggrid import AgGrid, GridOptionsBuilder

# ---------- CONFIG ----------
SIMILARITY_THRESHOLD_DEFAULT = 0.85
ORION_CSV = "orion_clean.csv"
SDP_CSV = "sdp_clean.csv"
ORION_EMBEDDINGS = "orion_embeddings.npy"
SDP_EMBEDDINGS = "sdp_embeddings.npy"

# ---------- LOAD PREPROCESSED DATA ----------
@st.cache_data
def load_data_and_embeddings():
    orion_df = pd.read_csv(ORION_CSV)
    sdp_df = pd.read_csv(SDP_CSV)
    orion_embeddings = np.load(ORION_EMBEDDINGS)
    sdp_embeddings = np.load(SDP_EMBEDDINGS)
    similarity_matrix = cosine_similarity(orion_embeddings, sdp_embeddings)
    return orion_df, sdp_df, similarity_matrix

# ---------- FILTER MATCHES ----------
def filter_matches(orion_df, sdp_df, similarity_matrix, threshold):
    matches = []
    for i in range(len(orion_df)):
        for j in range(len(sdp_df)):
            score = similarity_matrix[i][j]
            if score >= threshold:
                matches.append({
                    "Orion Code": orion_df.iloc[i]["PRODUCT_CODE"],
                    "Orion Description": orion_df.iloc[i]["product_description"],
                    "SDP Code": sdp_df.iloc[j]["OFFERING_TYPE_CD"],
                    "SDP Description": sdp_df.iloc[j]["product_description"],
                    "Similarity Score": round(score, 4)
                })
    return pd.DataFrame(matches)

# ---------- STREAMLIT UI ----------
st.set_page_config(page_title="🔍 Product Similarity Analyzer", layout="wide")
st.title("🔍 Product Similarity Analysis (Interactive View)")
st.markdown("Explore and filter similar products using the interactive table below.")

threshold = st.slider("Similarity Threshold", 0.5, 0.99, SIMILARITY_THRESHOLD_DEFAULT, 0.01)

with st.spinner("Loading data and similarity matrix..."):
    orion_df, sdp_df, similarity_matrix = load_data_and_embeddings()

with st.spinner("Filtering based on selected threshold..."):
    result_df = filter_matches(orion_df, sdp_df, similarity_matrix, threshold)

if result_df.empty:
    st.warning("No matches found above the selected threshold.")
    st.stop()

# ---------- AGGRID DISPLAY ----------
st.subheader("📊 Click a row to filter by Orion Product Code")

# Build grid options
gb = GridOptionsBuilder.from_dataframe(result_df)
gb.configure_default_column(filter=True, sortable=True, resizable=True)
gb.configure_selection("single", use_checkbox=True)
grid_options = gb.build()

# Render AgGrid
grid_response = AgGrid(
    result_df,
    gridOptions=grid_options,
    height=400,
    enable_enterprise_modules=False,
    update_mode="MODEL_CHANGED",
    fit_columns_on_grid_load=True
)

# Show filtered view
if grid_response["selected_rows"]:
    selected_code = grid_response["selected_rows"][0]["Orion Code"]
    st.success(f"Showing all matches for Orion Product Code: **{selected_code}**")
    filtered_df = result_df[result_df["Orion Code"] == selected_code]
    st.dataframe(filtered_df, use_container_width=True)

    # Optionally allow download
    csv = filtered_df.to_csv(index=False)
    st.download_button("📥 Download Filtered Results", csv, file_name="filtered_results.csv")

else:
    # Show unfiltered data download
    csv = result_df.to_csv(index=False)
    st.download_button("📥 Download All Results", csv, file_name="all_results.csv")
