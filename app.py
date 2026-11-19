import os
import tempfile
import numpy as np
import soundfile as sf
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 25 * 1024 * 1024

# YAMNet is a pretrained AudioSet sound-event model. It can recognize many
# animal/bird sound categories, but it is not a species-level wildlife expert.
yamnet_model = None
class_names = None
model_error = None

def load_model():
    global yamnet_model, class_names, model_error
    if yamnet_model is not None:
        return
    try:
        import tensorflow as tf
        import tensorflow_hub as hub
        import csv
        import urllib.request

        yamnet_model = hub.load("https://tfhub.dev/google/yamnet/1")
        labels_url = "https://storage.googleapis.com/audioset/youtube_corpus/v1/csv/class_labels_indices.csv"
        with urllib.request.urlopen(labels_url, timeout=30) as response:
            rows = list(csv.DictReader(line.decode("utf-8") for line in response))
        class_names = [row["display_name"] for row in rows]
    except Exception as exc:
        model_error = str(exc)
        raise RuntimeError(
            "Could not load YAMNet. Check your internet connection and installed dependencies. "
            "Details: " + model_error
        )

def to_mono_16k(audio, sample_rate):
    import librosa
    if audio.ndim == 2:
        audio = np.mean(audio, axis=1)
    if sample_rate != 16000:
        audio = librosa.resample(audio.astype(np.float32), orig_sr=sample_rate, target_sr=16000)
    return audio.astype(np.float32)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/classify", methods=["POST"])
def classify():
    if "audio" not in request.files:
        return jsonify({"error": "Please choose an audio file."}), 400
    file = request.files["audio"]
    if not file.filename:
        return jsonify({"error": "Please choose an audio file."}), 400

    suffix = os.path.splitext(file.filename)[1].lower()
    if suffix not in {".wav", ".flac", ".ogg", ".aiff", ".aif"}:
        return jsonify({"error": "Supported formats: WAV, FLAC, OGG and AIFF. Convert MP3 to WAV first."}), 400

    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            file.save(tmp.name)
            tmp_path = tmp.name

        audio, sr = sf.read(tmp_path, dtype="float32")
        if len(audio) == 0:
            return jsonify({"error": "The audio file is empty."}), 400
        if len(audio) / sr > 120:
            return jsonify({"error": "Please upload an audio clip of 120 seconds or less."}), 400

        audio = to_mono_16k(audio, sr)
        if len(audio) < 1600:
            return jsonify({"error": "Please upload at least 0.1 seconds of audio."}), 400

        load_model()
        scores, embeddings, spectrogram = yamnet_model(audio)
        mean_scores = np.mean(scores.numpy(), axis=0)
        top_indices = np.argsort(mean_scores)[::-1][:5]
        results = [
            {"label": class_names[int(i)], "confidence": round(float(mean_scores[i]) * 100, 2)}
            for i in top_indices
        ]
        wildlife_terms = ("bird", "animal", "frog", "cricket", "insect", "dog", "cat",
                          "cow", "horse", "sheep", "pig", "rooster", "crow", "owl",
                          "wild", "snake", "whale", " dolphin", "elephant", "monkey",
                          "lion", "tiger", "wolf", "fox", "bat")
        likely_wildlife = any(any(term in item["label"].lower() for term in wildlife_terms)
                              for item in results[:3])
        return jsonify({
            "model": "Google YAMNet (AudioSet)",
            "results": results,
            "wildlife_related": likely_wildlife,
            "note": "These are sound-event predictions, not a verified species identification. "
                    "Recording quality, distance, background noise and overlapping calls affect results."
        })
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 503
    except Exception as exc:
        return jsonify({"error": "Audio analysis failed: " + str(exc)}), 500
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
