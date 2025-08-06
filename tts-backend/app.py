import os
import uuid
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from langdetect import detect
from TTS.api import TTS
from faster_whisper import WhisperModel

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

# Load whisper model lazily (base size)
whisper_model = None


def transcribe_audio(path: str):
    global whisper_model
    if whisper_model is None:
        whisper_model = WhisperModel("base", device="cpu", compute_type="int8")
    segments, _ = whisper_model.transcribe(path, language="fa", beam_size=5)
    text_out = " ".join([seg.text.strip() for seg in segments])
    return text_out

# ------------------------------
# Automatic transcription + dataset add
# ------------------------------

@app.route("/transcribe", methods=["POST"])
def transcribe_and_store():
    """Receive audio, transcribe, and save (audio,text) into dataset/fa."""
    audio_file = request.files.get("audio")
    if not audio_file:
        return jsonify({"error": "audio required"}), 400

    tmp_path = os.path.join("data", "tmp", f"{uuid.uuid4()}.wav")
    os.makedirs(os.path.dirname(tmp_path), exist_ok=True)
    audio_file.save(tmp_path)

    transcript = transcribe_audio(tmp_path)

    # store in dataset
    ds_dir = os.path.join("data", "dataset", "fa")
    os.makedirs(ds_dir, exist_ok=True)
    new_id = str(uuid.uuid4())
    wav_path = os.path.join(ds_dir, f"{new_id}.wav")
    os.replace(tmp_path, wav_path)

    meta_path = os.path.join(ds_dir, "metadata.csv")
    with open(meta_path, "a", encoding="utf-8") as m:
        m.write(f"{new_id}.wav|{transcript}\n")

    return jsonify({"transcript": transcript, "id": new_id})

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

# ------------------------------
# Collect dataset samples (audio + transcript) for future fine-tuning
# ------------------------------

@app.route("/dataset", methods=["POST"])
def add_dataset():
    """Save (audio,text) pair to dataset/fa for later fine-tuning."""
    audio_file = request.files.get("audio")
    text = request.form.get("text") or (request.json and request.json.get("text"))
    lang = request.form.get("lang") or (request.json and request.json.get("lang")) or "fa"

    if not audio_file or not text:
        return jsonify({"error": "audio and text required"}), 400

    ds_dir = os.path.join("data", "dataset", lang)
    os.makedirs(ds_dir, exist_ok=True)

    file_id = str(uuid.uuid4())
    wav_path = os.path.join(ds_dir, f"{file_id}.wav")
    audio_file.save(wav_path)

    meta_path = os.path.join(ds_dir, "metadata.csv")
    with open(meta_path, "a", encoding="utf-8") as m:
        m.write(f"{file_id}.wav|{text}\n")

    return jsonify({"status": "saved", "id": file_id})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)