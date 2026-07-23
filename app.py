"""
Flask backend for Audio Noise Remover
--------------------------------------
Receives an audio file from the frontend, cleans it using noise reduction,
and sends back the cleaned file for download.
"""

from flask import Flask, request, send_file, jsonify, render_template
from flask_cors import CORS
import librosa
import soundfile as sf
import noisereduce as nr
import os
import uuid

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {"mp3", "wav", "m4a", "ogg"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ---------------- HOME PAGE ----------------
@app.route("/")
def home():
    return render_template("index.html")


# ---------------- HEALTH CHECK ----------------
@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "Server is running"})


# ---------------- AUDIO PROCESS ----------------
@app.route("/process", methods=["POST"])
def process_audio():

    if "audio" not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    file = request.files["audio"]

    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Unsupported file type"}), 400

    file_id = str(uuid.uuid4())

    input_path = os.path.join(
        UPLOAD_FOLDER,
        f"{file_id}_{file.filename}"
    )

    file.save(input_path)

    try:
        cleaned_path = remove_noise(input_path, file_id)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if os.path.exists(input_path):
            os.remove(input_path)

    return send_file(
        cleaned_path,
        as_attachment=True,
        download_name="cleaned_audio.wav",
        mimetype="audio/wav"
    )


# ---------------- NOISE REDUCTION ----------------
def remove_noise(input_path, file_id):

    audio, sample_rate = librosa.load(
        input_path,
        sr=None,
        mono=True
    )

    noise_sample = audio[: int(0.5 * sample_rate)]

    cleaned_audio = nr.reduce_noise(
        y=audio,
        sr=sample_rate,
        y_noise=noise_sample,
        stationary=False
    )

    output_path = os.path.join(
        OUTPUT_FOLDER,
        f"{file_id}_cleaned.wav"
    )

    sf.write(output_path, cleaned_audio, sample_rate)

    return output_path


# ---------------- START SERVER ----------------
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
