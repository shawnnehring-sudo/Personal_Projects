import time
import threading
import csv
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
import random
import numpy as np
import joblib
import tensorflow as tf
from collections import deque
from flask import Flask, render_template_string, jsonify, request
import subprocess
training_status = "idle"   # idle | training | done | error
status_lock = threading.Lock()

# ==========================================
# 1. BACKGROUND SENSOR & BUFFER ENGINE
# ==========================================
class HeartRateEngine:
    """
    Runs on its own background thread, continuously collecting heartbeat
    readings into a rolling time window (deque). Both the training-data
    logger and the live inference route read from this same engine --
    it's the single source of truth for HRV features either way.
    """

    def __init__(self, window_seconds=30):
        self.window_seconds = window_seconds
        self.buffer = deque()   # each entry: (timestamp, bpm, rr_ms)
        self.lock = threading.Lock()
        self.running = True

        self.thread = threading.Thread(target=self._sensor_loop, daemon=True)
        self.thread.start()

    def _sensor_loop(self):
        """Simulates continuously reading a physical sensor every 1 second in the background.

        TODO: replace the MOCK SENSOR block below with your real read from
        the DEVMO Pulse Sensor.
        """
        base_bpm = 72.0
        while self.running:
            now = time.time()

            # --- MOCK SENSOR LOGIC ---
            current_bpm = base_bpm + random.uniform(-3.0, 3.0)
            rr_ms = (60.0 / current_bpm) * 1000.0
            # -------------------------

            with self.lock:
                self.buffer.append((now, current_bpm, rr_ms))
                while self.buffer and (now - self.buffer[0][0]) > self.window_seconds:
                    self.buffer.popleft()

            time.sleep(1.0)

    def get_features(self):
        """Thread-safe extraction of HRV features from the active window.

        Returns a dict with the same keys/order as FEATURE_COLUMNS below --
        that dict is what both the CSV logger and the model consume.
        """
        with self.lock:
            if len(self.buffer) < 10:
                return None

            timestamps = np.array([b[0] for b in self.buffer])
            hrs = np.array([b[1] for b in self.buffer])
            rrs = np.array([b[2] for b in self.buffer])

            mean_hr = float(np.mean(hrs))
            std_hr = float(np.std(hrs))
            mean_rr = float(np.mean(rrs))
            sdnn = float(np.std(rrs))

            rr_diffs = np.diff(rrs)
            rmssd = float(np.sqrt(np.mean(rr_diffs ** 2))) if len(rr_diffs) > 0 else 0.0

            #if len(rr_diffs) > 0:
                #nn50_count = np.sum(np.abs(rr_diffs) > 50.0)
                #pnn50 = float(100.0 * nn50_count / len(rr_diffs))
            #else:
                #pnn50 = 0.0

            rel_time = timestamps - timestamps[0]
            if np.ptp(rel_time) > 0:
                slope, _intercept = np.polyfit(rel_time, hrs, 1)
                hr_slope = float(slope)
            else:
                hr_slope = 0.0

            instant_delta_bpm = float(hrs[-1] - hrs[-2]) if len(hrs) >= 2 else 0.0

            return {
                "mean_hr": round(mean_hr, 2),
                "std_hr": round(std_hr, 2),
                "mean_rr": round(mean_rr, 2),
                "sdnn": round(sdnn, 2),
                "rmssd": round(rmssd, 2),
                #"pnn50": round(pnn50, 2),
                #"hr_slope": round(hr_slope, 3),
                #"instant_delta_bpm": round(instant_delta_bpm, 2),
            }

engine = HeartRateEngine(window_seconds=30)

# ==========================================
# 2. TRAINED MODEL (loaded once at startup, if present)
# ==========================================
# Must match FEATURE_COLUMNS in train_mood_model.py exactly -- same names,
# same order. This is the seam between training and inference: if you add
# a feature to get_features() above, add it here and retrain.

def load_model_artifacts():
    """(Re)loads model/scaler/encoder from disk into the module globals.
    Called once at startup, and again after a training run finishes."""
    global model, scaler, label_encoder
    if all(os.path.exists(f) for f in (MODEL_FILE, SCALER_FILE, ENCODER_FILE)):
        try:
            model = tf.keras.models.load_model(MODEL_FILE)
            scaler = joblib.load(SCALER_FILE)
            label_encoder = joblib.load(ENCODER_FILE)
            print(f"Loaded trained model. Mood classes: {list(label_encoder.classes_)}")
            return True
        except Exception as e:
            print(f"Found model files but failed to load them: {e}")
            model = scaler = label_encoder = None
            return False
    return False

def run_training_job():
    """Runs in a background thread: shells out to the training script,
    waits for it to finish, then hot-reloads the resulting model."""
    global training_status
    training_status = "training"
    try:
        result = subprocess.run(
            ["python", "MoodModel.py"],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            print("Training failed:\n", result.stderr)
            training_status = "error"
            return
        print(result.stdout)
        if load_model_artifacts():
            training_status = "done"
        else:
            training_status = "error"
    except Exception as e:
        print(f"Training job crashed: {e}")
        training_status = "error"



FEATURE_COLUMNS = [
    "mean_hr", "std_hr", "mean_rr", "sdnn",
    "rmssd"
]

MODEL_FILE = "mood_model.keras"
SCALER_FILE = "mood_scaler.pkl"
ENCODER_FILE = "mood_label_encoder.pkl"

model = None
scaler = None
label_encoder = None
load_model_artifacts()


def predict_mood(features: dict):
    """Runs the loaded model on a single feature window.

    Returns a dict with the predicted label and per-class confidence.
    Keeps feature ordering, scaling, and label decoding all in one place
    so the route below stays simple. Caller must check model is not None.
    """
    x = np.array([[features[col] for col in FEATURE_COLUMNS]])
    x_scaled = scaler.transform(x)

    probabilities = model.predict(x_scaled, verbose=0)[0]  # softmax output
    predicted_index = int(np.argmax(probabilities))
    predicted_label = label_encoder.classes_[predicted_index]

    return {
        "mood": predicted_label,
        "confidence": round(float(probabilities[predicted_index]) * 100, 1),
        "probabilities": {
            label: round(float(p) * 100, 1)
            for label, p in zip(label_encoder.classes_, probabilities)
        },
    }

# ==========================================
# 3. FLASK WEB SERVER & DATASET LOGGING
# ==========================================
app = Flask(__name__)
DATASET_FILE = "heart_mood_dataset.csv"

# When False, /log_mood is disabled and the training UI hides itself.
# Lives only in memory -- resets to True on server restart, since a fresh
# process shouldn't silently assume you're done collecting data.
train = False

if not os.path.exists(DATASET_FILE):
    with open(DATASET_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "mean_hr", "std_hr", "mean_rr", "sdnn", "rmssd",
            "label",
        ])

HTML_UI = """
<!DOCTYPE html>
<html>
<head>
    <title>Pi Mood Logger</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; text-align: center; padding: 20px; background: #121212; color: #fff; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; max-width: 400px; margin: 20px auto; }
        button { padding: 25px; font-size: 18px; font-weight: bold; border: none; border-radius: 12px; cursor: pointer; color: white; transition: transform 0.1s; }
        button:active { transform: scale(0.95); }
        .calm { background: #47d6d4; }
        .happy { background: #d2d90f; }
        .sad { background: #3509b7; }
        .angry { background: #b70926; }
        .excited { background: #b70969; }
        .neutral { background: #666666; }
        .drained { background: #3d0680; }
        .anxious { background: #3ac71e; }

        .status { margin-top: 25px; font-size: 16px; color: #a0a0a0; }
        .panel { max-width: 400px; margin: 30px auto; padding: 20px; background: #1e1e1e; border-radius: 12px; }
        .panel h3 { margin-top: 0; font-size: 15px; color: #a0a0a0; font-weight: normal; text-transform: uppercase; letter-spacing: 1px; }
        #live-mood { font-size: 28px; font-weight: bold; margin: 10px 0; }
        #live-confidence { font-size: 14px; color: #a0a0a0; }
        .bar-row { display: flex; align-items: center; gap: 10px; margin: 6px 0; font-size: 13px; }
        .bar-label { width: 70px; text-align: right; color: #a0a0a0; }
        .bar-track { flex: 1; background: #333; border-radius: 4px; height: 8px; overflow: hidden; }
        .bar-fill { height: 100%; background: #4c9aff; transition: width 0.4s; }
        .mode-row { max-width: 400px; margin: 20px auto 0; display: flex; align-items: center; justify-content: center; gap: 10px; font-size: 14px; color: #a0a0a0; }
        .switch { position: relative; width: 44px; height: 24px; }
        .switch input { opacity: 0; width: 0; height: 0; }
        .slider { position: absolute; inset: 0; background: #444; border-radius: 24px; cursor: pointer; transition: background 0.2s; }
        .slider::before { content: ""; position: absolute; width: 18px; height: 18px; left: 3px; top: 3px; background: white; border-radius: 50%; transition: transform 0.2s; }
        input:checked + .slider { background: #2ec4b6; }
        input:checked + .slider::before { transform: translateX(20px); }
        #training-section.hidden { display: none; }
        #predict-panel.hidden { display: none; }
    </style>
</head>
<body>
    <h2>Heart Rate Mood Logger</h2>

    <div class="panel hidden" id="predict-panel">
        <h3>Live prediction</h3>
        <div id="live-mood">--</div>
        <div id="live-confidence">Waiting for data...</div>
        <div id="bars"></div>
    </div>

    <div class="mode-row">
        <span>Training mode</span>
        <label class="switch">
            <input type="checkbox" id="training-toggle" checked onchange="setTrainingMode(this.checked)">
            <span class="slider"></span>
        </label>
    </div>

    <div id="training-section">
        <p>Tap your current emotion to tag the active 30s window for training:</p>
        <div class="grid">
            <button class="calm" onclick="logMood('Calm')">Calm \U0001F60C</button>
            <button class="happy" onclick="logMood('Happy')">Happy \U0001F604</button>
            <button class="stressed" onclick="logMood('Stressed')">Stressed \U0001FAE0</button>
            <button class="sad" onclick="logMood('Sad')">Sad \U0001F622</button>
            <button class="angry" onclick="logMood('Angry')">Angry \U0001F621</button>
            <button class="excited" onclick="logMood('Excited')">Excited \U0001F929</button>
            <button class="neutral" onclick="logMood('Neutral')">Neutral \U0001F610</button>
            <button class="drained" onclick="logMood('Drained')">Drained \U0001FAE9</button>
        </div>
        <div id="status" class="status">System running in background...</div>
    </div>

    <script>
        function logMood(label) {
            document.getElementById('status').innerText = 'Saving ' + label + '...';
            fetch('/log_mood', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ mood: label })
            })
            .then(res => res.json())
            .then(data => {
                document.getElementById('status').innerText = data.message;
            })
            .catch(err => {
                document.getElementById('status').innerText = 'Error connecting to Pi!';
            });
        }

        function refreshPrediction() {
            fetch('/predict_mood')
                .then(res => res.json())
                .then(data => {
                    const moodEl = document.getElementById('live-mood');
                    const confEl = document.getElementById('live-confidence');
                    const barsEl = document.getElementById('bars');

                    if (data.status === 'no_model') {
                        moodEl.innerText = '--';
                        confEl.innerText = 'No trained model yet -- run MoodModel.py';
                        barsEl.innerHTML = '';
                    } else if (data.status === 'warming_up') {
                        moodEl.innerText = '--';
                        confEl.innerText = 'Buffering sensor data...';
                        barsEl.innerHTML = '';
                    } else {
                        moodEl.innerText = data.mood;
                        confEl.innerText = data.confidence + '% confidence';
                        barsEl.innerHTML = Object.entries(data.probabilities)
                            .map(([label, pct]) => `
                                <div class="bar-row">
                                    <div class="bar-label">${label}</div>
                                    <div class="bar-track"><div class="bar-fill" style="width:${pct}%"></div></div>
                                </div>
                            `).join('');
                    }
                })
                .catch(() => {
                    document.getElementById('live-confidence').innerText = 'Error connecting to Pi!';
                });
        }

        function applyTrainingVisibility(enabled) {
            document.getElementById('training-section').classList.toggle('hidden', !enabled);
            document.getElementById('training-toggle').checked = enabled;
        }

        function applyPredictVisibility(modelLoaded) {
            document.getElementById('predict-panel').classList.toggle('hidden', !modelLoaded);
        }   

        function pollStatus() {
            fetch('/status')
                .then(res => res.json())
                .then(data => {
                    applyTrainingVisibility(data.train);
                    applyPredictVisibility(!data.train && data.model_loaded);
                });
        }

        pollStatus();
        setInterval(pollStatus, 2000);

        function setTrainingMode(enabled) {
            fetch('/set_training_mode', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ enabled: enabled })
            })
            .then(() => pollStatus());
        }

        // On page load, sync the toggle and panel to whatever the server currently has set

        refreshPrediction();
        setInterval(refreshPrediction, 2000);
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_UI)

@app.route('/stop_engine', methods=['POST'])
def stop_engine():
    engine.running = False
    return jsonify({"message": "Sensor loop paused!"})

@app.route('/set_training_mode', methods=['POST'])
def set_training_mode():
    global train
    data = request.json or {}
    new_value = bool(data.get('enabled', True))
    was_enabled = train
    train = new_value

    # Flip OFF -> ON now kicks off training in the background
    if not was_enabled and new_value:
        threading.Thread(target=run_training_job, daemon=True).start()

    return jsonify({"train": train, "training_status": training_status})

@app.route('/status', methods=['GET'])
def status():
    return jsonify({
        "train": train,
        "model_loaded": model is not None,
        "training_status": training_status,
    })

#checks if MoodModel is running and then turns off or on depending on training_enabled


@app.route('/log_mood', methods=['POST'])
def log_mood():
    # Tagged by a human -- this is training data collection
    if not train:
        return jsonify({"message": "Training mode is off -- turn it back on to log data."}), 403

    data = request.json
    mood = data.get('mood')

    features = engine.get_features()
    if features is None:
        return jsonify({"message": "Buffer still warming up! Wait a few seconds..."}), 400

    with open(DATASET_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            features['mean_hr'],
            features['std_hr'],
            features['mean_rr'],
            features['sdnn'],
            features['rmssd'],
            #features['pnn50'],
            #features['hr_slope'],
            #features['instant_delta_bpm'],
            mood
        ])

    return jsonify({
        "message": (
            f"Recorded '{mood}'! [HR: {features['mean_hr']} BPM | "
            f"RMSSD: {features['rmssd']} ms]"
        )
    })

@app.route('/predict_mood', methods=['GET'])
def predict_mood_route():
    if model is None:
        return jsonify({"status": "no_model"})
    if train:
        return jsonify({"status": "training_mode"})
    features = engine.get_features()
    if features is None:
        return jsonify({"status": "warming_up"})
    result = predict_mood(features)
    result["status"] = "ok"
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)