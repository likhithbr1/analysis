# product_bundles.py
import pandas as pd
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import fpgrowth, association_rules
import os

# Source system to Excel file mapping
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SOURCE_FILE_MAP = {
    "eon": os.path.join(BASE_DIR, "data/orders_details.xlsx"),
    "abc": os.path.join(BASE_DIR, "data/orders_details_abc.xlsx"),
    "xyz": os.path.join(BASE_DIR, "data/orders_details_xyz.xlsx")
}

CONFIDENCE_THRESHOLD = 0.6
SUPPORT_THRESHOLD = 0.05

def load_and_prepare_data(source_system):
    if source_system not in SOURCE_FILE_MAP:
        raise ValueError(f"Unknown source system: {source_system}")
    df = pd.read_excel(SOURCE_FILE_MAP[source_system])
    df['Items Bought'] = df['Items Bought'].apply(lambda x: x.split(','))
    return df

def get_encoded_transactions(df):
    te = TransactionEncoder()
    te_ary = te.fit(df['Items Bought']).transform(df['Items Bought'])
    return pd.DataFrame(te_ary, columns=te.columns_)

def get_product_bundles(source_system):
    df = load_and_prepare_data(source_system)
    df_encoded = get_encoded_transactions(df)

    itemsets = fpgrowth(df_encoded, min_support=SUPPORT_THRESHOLD, use_colnames=True)
    itemsets['support_count'] = (itemsets['support'] * len(df)).astype(int)
    itemsets['length'] = itemsets['itemsets'].apply(lambda x: len(x))

    bundles = itemsets[itemsets['length'] >= 2].sort_values(by='length', ascending=False)
    # Convert frozensets to list for JSON serialization
    bundles['itemsets'] = bundles['itemsets'].apply(lambda x: list(x))
    return bundles.head(20).to_dict(orient="records")

def get_recommendations(source_system):
    df = load_and_prepare_data(source_system)
    df_encoded = get_encoded_transactions(df)

    itemsets = fpgrowth(df_encoded, min_support=SUPPORT_THRESHOLD, use_colnames=True)
    rules = association_rules(itemsets, metric="confidence", min_threshold=CONFIDENCE_THRESHOLD)
    rules = rules.sort_values(by="confidence", ascending=False)

    results = []
    for _, row in rules.iterrows():
        results.append({
            "antecedents": list(row["antecedents"]),
            "consequents": list(row["consequents"]),
            "confidence": round(row["confidence"], 4)
        })
    
    return results[:20]
