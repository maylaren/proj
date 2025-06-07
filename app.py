from flask import Flask, render_template, request, send_from_directory, redirect, url_for
import os
import librosa
import soundfile as sf
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
ALLOWED_EXTENSIONS = {'wav', 'mp3'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return redirect(url_for('index'))

    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return redirect(url_for('player', filename=filename))

    return redirect(url_for('index'))

@app.route('/player/<filename>')
def player(filename):
    return render_template('player.html', filename=filename)

@app.route('/process/<filename>', methods=['POST'])
def process(filename):
    speed = float(request.form['speed'])
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    output_path = os.path.join(app.config['PROCESSED_FOLDER'], f"processed_{filename}.wav")

    y, sr = librosa.load(input_path, sr=None)
    y_stretched = librosa.effects.time_stretch(y, speed)
    sf.write(output_path, y_stretched, sr)

    return send_from_directory(app.config['PROCESSED_FOLDER'], f"processed_{filename}.wav", as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
