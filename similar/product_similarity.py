import os
import pandas as pd
import re
from sentence_transformers import SentenceTransformer, util

# ---------- CONFIG ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ORION_FILE = os.path.join(BASE_DIR, "Orion_Products.xlsx")
SDP_FILE = os.path.join(BASE_DIR, "SDP_Products.xlsx")
SIMILARITY_THRESHOLD = 0.85
MODEL_NAME = "all-MiniLM-L6-v2"

# ---------- TEXT CLEANING ----------
def clean_text(text):
    text = str(text).lower()
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# ---------- MAIN FUNCTION ----------
def compute_product_similarity():
    # Load Excel files
    orion_df = pd.read_excel(ORION_FILE)
    sdp_df = pd.read_excel(SDP_FILE)

    # Rename columns
    orion_df = orion_df.rename(columns={"PRODUCT_CODE": "product_name", "PRODUCT_DSC": "product_description"})
    sdp_df = sdp_df.rename(columns={"OFFERING_TYPE_CD": "product_name", "OFFERING_DSC": "product_description"})

    # Drop missing descriptions
    orion_df.dropna(subset=["product_description"], inplace=True)
    sdp_df.dropna(subset=["product_description"], inplace=True)

    # Clean and combine text
    orion_df["product_description"] = orion_df["product_description"].apply(clean_text)
    sdp_df["product_description"] = sdp_df["product_description"].apply(clean_text)
    orion_df["full_text"] = orion_df["product_name"] + " " + orion_df["product_description"]
    sdp_df["full_text"] = sdp_df["product_name"] + " " + sdp_df["product_description"]

    # Load model and compute embeddings
    model = SentenceTransformer(MODEL_NAME)
    orion_embeddings = model.encode(orion_df["full_text"].tolist(), convert_to_tensor=True)
    sdp_embeddings = model.encode(sdp_df["full_text"].tolist(), convert_to_tensor=True)
    similarity_matrix = util.cos_sim(orion_embeddings, sdp_embeddings).cpu().numpy()

    # Filter matches based on threshold
    matches = []
    for i in range(len(orion_df)):
        for j in range(len(sdp_df)):
            score = similarity_matrix[i][j]
            if score >= SIMILARITY_THRESHOLD:
                matches.append({
                    "Orion Code": orion_df.iloc[i]["product_name"],
                    "Orion Description": orion_df.iloc[i]["product_description"],
                    "SDP Code": sdp_df.iloc[j]["product_name"],
                    "SDP Description": sdp_df.iloc[j]["product_description"],
                    "Similarity Score": round(score, 4)
                })

    return pd.DataFrame(matches)
