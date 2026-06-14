from flask import Blueprint, request, jsonify
from app.services.gemini_service import analyze_code_with_gemini

analysis_bp = Blueprint("analysis", __name__, url_prefix="/api")

@analysis_bp.route("/analyze", methods=["POST"])
def analyze_code():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        code = data.get("code", "")
        language = data.get("language", "python")

        if not code.strip():
            return jsonify({"error": "Code cannot be empty"}), 400

        result = analyze_code_with_gemini(code, language)
        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

