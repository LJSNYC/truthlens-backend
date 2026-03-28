import io

from flask import Flask, jsonify, request
from PIL import Image, UnidentifiedImageError

from detector import detect
from supabase_service import log_scan

app = Flask(__name__)


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/analyze", methods=["POST"])
def analyze():
    if "file" not in request.files:
        return jsonify({"error": "No file provided. Send a multipart/form-data request with field 'file'."}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "File field is empty."}), 400

    try:
        image = Image.open(io.BytesIO(file.read())).convert("RGB")
    except UnidentifiedImageError:
        return jsonify({"error": "Could not decode image. Upload a valid JPEG, PNG, or WebP file."}), 400

    try:
        result = detect(image)
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 503

    try:
        user_id = request.headers.get("X-User-ID", "anonymous")
        file_type = file.content_type or "unknown"
        log_scan(user_id, result["verdict"], result["confidence"], result["reason"], file_type)
    except Exception as e:
        print(f"[supabase] logging failed: {e}")

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, port=5001)
