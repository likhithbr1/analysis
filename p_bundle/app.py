from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import timedelta

# Import all logic modules
from trend_analysis import generate_summary, generate_detail, get_valid_sources
from demand_forecast import get_forecast_summary, get_forecast_detail
from product_bundles import get_product_bundles, get_recommendations

# Initialize app
app = Flask(__name__)
CORS(app)

# Time range mapping
TIME_RANGE_MAP = {
    "1w": timedelta(weeks=1),
    "1m": timedelta(days=30),
    "1y": timedelta(days=365),
    "2y": timedelta(days=730)
}

### ----- TREND ANALYSIS ROUTES ----- ###

@app.route("/analysis/summary", methods=["POST"])
def trend_summary():
    data = request.get_json()
    source = data.get("source_system")
    analysis_type = data.get("analysis_type")

    if not source or analysis_type != "trend_analysis":
        return jsonify({"error": "Missing or invalid parameters"}), 400

    try:
        result = generate_summary(source)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/analysis/detail", methods=["POST"])
def trend_detail():
    data = request.get_json()
    source = data.get("source_system")
    analysis_type = data.get("analysis_type")
    product = data.get("product")
    time_range = data.get("time_range")

    if not all([source, product, time_range]) or analysis_type != "trend_analysis":
        return jsonify({"error": "Missing or invalid parameters"}), 400

    if time_range not in TIME_RANGE_MAP:
        return jsonify({"error": "Invalid time_range"}), 400

    try:
        result = generate_detail(source, product, TIME_RANGE_MAP[time_range])
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/analysis/sources", methods=["GET"])
def list_sources():
    return jsonify(get_valid_sources())


### ----- DEMAND FORECASTING ROUTES ----- ###

@app.route("/forecast/summary", methods=["POST"])
def forecast_summary():
    data = request.get_json()
    source = data.get("source_system")

    if not source:
        return jsonify({"error": "Missing source_system"}), 400

    try:
        product_list = get_forecast_summary(source)
        return jsonify({"products": product_list})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/forecast/detail", methods=["POST"])
def forecast_detail():
    data = request.get_json()
    source = data.get("source_system")
    product = data.get("product")

    if not source or not product:
        return jsonify({"error": "Missing source_system or product"}), 400

    try:
        forecast = get_forecast_detail(source, product)
        return jsonify(forecast)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


### ----- PRODUCT BUNDLING ROUTES ----- ###

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


### ----- MAIN ----- ###
if __name__ == "__main__":
    app.run(debug=True, port=5000)
