import whisper
import numpy as np
import ffmpeg
import base64
import audioop

model = whisper.load_model("base")


# sample_packet = {'event': 'media', 'sequenceNumber': '2', 'media': {'track': 'inbound', 'chunk': '1', 'timestamp': '111', 'payload': '/v7+/v7//////////////37/fn7/fn5+fn1+fn59fv7+/n7+/v7+/n5+/v5+fv7+/n1+fn59fv39/v7+/v79/v///////37/////fv//fn5+/v//fn5+fn5+fn5+ff7+/v5+/v5+fv7+/v5+fv79/f////////99fX7+/v5+fn7+/v7+//////5+/////35+fX7+/v7/fX1+/n7+/v5+/g=='}, 'streamSid': 'MZ028b92550b1f27f642712e00e87aab28'}
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


def transcribe(audio: bytes) -> str:
    audio = np.frombuffer(audio, np.int16).flatten().astype(np.float32) / 32768.0
    result = model.transcribe(audio)
    return result['text']


# audio = transcribe(audio)
# print(audio)
