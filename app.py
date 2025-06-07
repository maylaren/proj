from flask import Flask, render_template, request, send_file
from pydub import AudioSegment
import os
import librosa
import soundfile as sf
import uuid

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
PROCESSED_FOLDER = "processed"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return "No file uploaded", 400

    file = request.files["file"]
    if file.filename == "":
        return "No file selected", 400

    file_ext = file.filename.rsplit(".", 1)[1].lower()
    if file_ext not in ["mp3", "wav"]:
        return "Unsupported file format", 400

    raw_filename = f"{uuid.uuid4()}"
    raw_filepath = os.path.join(UPLOAD_FOLDER, f"{raw_filename}.{file_ext}")
    file.save(raw_filepath)

    if file_ext == "mp3":
        # Convert MP3 to WAV using pydub
        sound = AudioSegment.from_mp3(raw_filepath)
        wav_filename = f"{raw_filename}.wav"
        wav_filepath = os.path.join(UPLOAD_FOLDER, wav_filename)
        sound.export(wav_filepath, format="wav")
    else:
        wav_filename = f"{raw_filename}.wav"
        wav_filepath = raw_filepath  # Already WAV

    return render_template("player.html", filename=wav_filename)

@app.route("/process", methods=["POST"])
def process():
    speed = float(request.form.get("speed", 1.0))
    filename = request.form.get("filename")
    input_path = os.path.join(UPLOAD_FOLDER, filename)
    y, sr = librosa.load(input_path)

    y_stretched = librosa.effects.time_stretch(y, speed)
    output_filename = f"processed_{filename.rsplit('.', 1)[0]}.wav"
    output_path = os.path.join(PROCESSED_FOLDER, output_filename)
    sf.write(output_path, y_stretched, sr)

    return send_file(output_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=False, use_reloader=False)
