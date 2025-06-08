from flask import Flask, request, jsonify
from flask_cors import CORS
from product_bundles import get_product_bundles, get_recommendations

app = Flask(__name__)
CORS(app)

@app.route("/bundles", methods=["POST"])
def fetch_bundles():
    data = request.get_json()
    source = data.get("source_system")

    if not source:
        return jsonify({"error": "Missing source_system"}), 400

    try:
        bundles = get_product_bundles(source)
        return jsonify({"bundles": bundles})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/recommendations", methods=["POST"])
def fetch_recommendations():
    data = request.get_json()
    source = data.get("source_system")

    if not source:
        return jsonify({"error": "Missing source_system"}), 400

    try:
        recommendations = get_recommendations(source)
        return jsonify({"recommendations": recommendations})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
