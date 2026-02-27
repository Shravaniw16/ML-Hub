import librosa
import numpy as np
import math

def analyze_audio(filepath):
    y, sr = librosa.load(filepath, sr=None, mono=True)

    duration = librosa.get_duration(y=y, sr=sr)

    rms_values = librosa.feature.rms(y=y)
    rms_mean = float(np.mean(rms_values))

    # Safety: avoid NaN / None
    if math.isnan(rms_mean):
        rms_mean = 0.0

    return {
        "duration_seconds": round(duration, 2),
        "sample_rate": sr,
        "rms_energy": round(rms_mean, 6)
    }
