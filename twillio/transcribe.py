import whisper
import numpy as np
import ffmpeg

model = whisper.load_model("base")


def load_audio(file_bytes: bytes, sr: int = 16_000) -> np.ndarray:
    from pydub import AudioSegment
    import numpy as np

    # Load the M4A audio file
    audio = AudioSegment.from_file(file_bytes, format="m4a")

    # Resample the audio to 16 kHz
    desired_sample_rate = 16000

    # Convert audio to the desired sample rate
    audio = audio.set_frame_rate(desired_sample_rate)

    # Convert the audio to a NumPy ndarray
    audio = np.array(audio.get_array_of_samples())
    return np.frombuffer(audio, np.int16).flatten().astype(np.float32) / 32768.0

audio = load_audio("/Users/henry/Documents/triplecheese.m4a")

def transcribe(audio: np.ndarray) -> str:
    result = model.transcribe(audio)
    return result['text']
