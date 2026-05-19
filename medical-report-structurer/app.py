from flask import Flask, jsonify, render_template, request

from backend.parser import parse_medical_report


app = Flask(
    __name__,
    template_folder="frontend",
    static_folder="frontend/static",
)


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/api/parse")
def parse_report():
    payload = request.get_json(silent=True) or {}
    text = payload.get("text", "")

    if not isinstance(text, str) or not text.strip():
        return jsonify({"error": "请输入需要解析的医学文本"}), 400

    return jsonify(parse_medical_report(text))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
