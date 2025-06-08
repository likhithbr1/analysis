# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import timedelta
from trend_analysis import generate_summary, generate_detail, get_valid_sources

app = Flask(__name__)
CORS(app)

TIME_RANGE_MAP = {
    "1w": timedelta(weeks=1),
    "1m": timedelta(days=30),
    "1y": timedelta(days=365),
    "2y": timedelta(days=730)
}

@app.route("/analysis/summary", methods=["GET"])
def trend_summary():
    source = request.args.get("source_system")
    analysis_type = request.args.get("analysis_type")

    if not source or analysis_type != "trend_analysis":
        return jsonify({"error": "Missing or invalid parameters"}), 400

    try:
        result = generate_summary(source)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/analysis/detail", methods=["GET"])
def trend_detail():
    source = request.args.get("source_system")
    analysis_type = request.args.get("analysis_type")
    product = request.args.get("product")
    time_range = request.args.get("time_range")

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

if __name__ == "__main__":
    app.run(debug=True, port=5000)
