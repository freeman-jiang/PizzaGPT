import ffmpeg
from pydub import AudioSegment
import base64
import audioop
import numpy as np
import whisper
from packets import packets

model = whisper.load_model("base")



def load_audio(file_bytes: bytes, sr: int = 16_000) -> np.ndarray:
    import numpy as np
    from pydub import AudioSegment

    # Load the M4A audio file
    audio = AudioSegment.from_file(file_bytes, format="m4a")

    # Resample the audio to 16 kHz
    desired_sample_rate = 16000

    # Convert audio to the desired sample rate
    audio = audio.set_frame_rate(desired_sample_rate)

    # Convert the audio to a NumPy ndarray
    audio = np.array(audio.get_array_of_samples())
    return np.frombuffer(audio, np.int16).flatten().astype(np.float32) / 32768.0

def to_ndarray(audio):
    return np.frombuffer(audio, np.int16).flatten().astype(np.float32) / 32768.0
    
def transcribe(audio: bytes) -> str:
    result = model.transcribe(audio)
    return result['text']

def writemp3(f, sr, x, normalized=True):
    """numpy array to MP3"""
    channels = 2 if (x.ndim == 2 and x.shape[1] == 2) else 1
    if normalized:  # normalized array - each item should be a float in [-1, 1)
        y = np.int16(x * 2 ** 15)
    else:
        y = np.int16(x)
    song = AudioSegment(y.tobytes(), frame_rate=sr, sample_width=2, channels=channels)
    song.export(f, format="mp3", bitrate="320k")


total = None
for packet in packets[0:30]:
    if 'media' in packet:
        audio = base64.b64decode(packet['media']['payload'])
        audio = audioop.ulaw2lin(audio, 2)
        audio = audioop.ratecv(audio, 2, 1, 8000, 16000, None)[0]

        if total is None:
            total = audio
        else:
            total += audio
        # total.append(audio)


total = to_ndarray(total)
writemp3('out.mp3', 16000, total)
print(total, len(total))
print(transcribe(total))

# audio = transcribe(audio)
# print(audio)
