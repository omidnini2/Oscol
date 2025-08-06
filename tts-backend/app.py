import os
import uuid
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from langdetect import detect
from TTS.api import TTS

app = Flask(__name__)
CORS(app)

# Map language code -> TTS model name
MODEL_MAP = {
    "default": "tts_models/multilingual/multi-dataset/xtts_v1",
    "fa": "tts_models/fa/custom/vits"  # فارسی (کیفیت بهتر)
}

# Cache loaded engines to avoid re-loading per request
tts_engines = {}


def get_engine_for(lang: str):
    """Return (and lazily load) an engine for a language code."""
    model_name = MODEL_MAP.get(lang, MODEL_MAP["default"])
    if model_name not in tts_engines:
        tts_engines[model_name] = TTS(model_name, gpu=False)
    return tts_engines[model_name]

EMBED_DIR = "data/embeddings"
os.makedirs(EMBED_DIR, exist_ok=True)

@app.route("/clone", methods=["POST"])
def clone_voice():
    """Accepts audio file and returns an embedding id to use later."""
    if "audio" not in request.files:
        return jsonify({"error": "audio field missing"}), 400
    audio_file = request.files["audio"]
    wav_path = os.path.join(EMBED_DIR, f"{uuid.uuid4()}.wav")
    audio_file.save(wav_path)

    # In XTTS, speaker embedding is simply the path to reference audio.
    # We store the file and return its id.
    embed_id = os.path.basename(wav_path)
    return jsonify({"embedding_id": embed_id})

@app.route("/tts", methods=["POST"])
def synthesize():
    data = request.json
    text = data.get("text")
    embed_id = data.get("embedding_id")
    if not text or not embed_id:
        return jsonify({"error": "text and embedding_id required"}), 400

    lang = data.get("lang") or detect(text)

    speaker_wav = os.path.join(EMBED_DIR, embed_id)
    if not os.path.exists(speaker_wav):
        return jsonify({"error": "embedding not found"}), 404

    output_wav = os.path.join("data", f"{uuid.uuid4()}.wav")

    engine = get_engine_for(lang)

    # If we are using the Persian VITS model, its signature differs (no language param)
    if MODEL_MAP.get(lang) == MODEL_MAP["fa"]:
        engine.tts_to_file(text=text, speaker_wav=speaker_wav, file_path=output_wav)
    else:
        engine.tts_to_file(text=text, speaker_wav=speaker_wav, language=lang, file_path=output_wav)

    return send_file(output_wav, mimetype="audio/wav", as_attachment=True, download_name="output.wav")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)