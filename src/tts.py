from dotenv import load_dotenv
from dataclasses import dataclass
from speechify import Speechify
from pprint import pprint
from scipy.signal import resample_poly

import os
import base64
import av
import io
import wave
import numpy as np

load_dotenv()

client = Speechify(token=os.getenv('SPEECHIFY_API_KEY'))

@dataclass
class LanguageConfiguration:
    language_code: str  
    languade_model: str

supported_languages = {
    "en": LanguageConfiguration('en-US', 'en-US-Chirp3-HD-Charon'),
    "hi": LanguageConfiguration('hi-IN', 'hi-IN-Chirp3-HD-Charon'),
    "he": LanguageConfiguration('he-IL', 'he-IL-Wavenet-D'),
}

class AACtoPCMConverter:
    def __init__(self, target_sample_rate: int = 16000, target_format: str = 's16', target_layout: str = 'mono'):
        self.codec = av.CodecContext.create('aac', 'r')
        self.target_format = target_format
        self.target_layout = target_layout
        self.resampler = av.AudioResampler(
            format=target_format,
            layout=target_layout,
            rate=target_sample_rate
        )

    def set_target_sample_rate(self, sample_rate: int):
        if sample_rate <= 0:
            raise ValueError("Sample rate must be a positive integer")
        self.resampler = av.AudioResampler(
            format=self.target_format,
            layout=self.target_layout,
            rate=sample_rate
        )


    def decode_chunk(self, aac_chunk: bytes) -> bytes:

        output_pcm = bytearray()
        packets = self.codec.parse(aac_chunk)

        for packet in packets:
            frames = self.codec.decode(packet)
            for frame in frames:
                resampled_frames = self.resampler.resample(frame)
                for resampled_frames in resampled_frames:
                    output_pcm.extend(bytes(resampled_frames.planes[0]))

        return bytes(output_pcm)

    def decode(self, aac_data: bytes) -> bytes:
        output_pcm = bytearray()

        with av.open(io.BytesIO(aac_data), 'r', format='aac') as container:
            stream = container.streams.audio[0]
            for frame in container.decode(stream):
                resampled_frames = self.resampler.resample(frame)
                for resampled_frame in resampled_frames:
                    output_pcm.extend(bytes(resampled_frame.planes[0]))

        return bytes(output_pcm)

aac_converter = AACtoPCMConverter(target_sample_rate=16000, target_format='s16', target_layout='mono')

def synthesize_audio(text: str, sample_rate: int) -> bytes:
    """Synthesizes audio using the Speechify Text to Speech API."""
    response = client.tts.audio.speech(input=text, voice_id='giorgia', audio_format='wav', language='he-IL', model='simba-multilingual')

    if response.audio_data is None:
        raise Exception("TTS synthesis produced no audio")

    frame_rate = 48000
    pcm_bytes = base64.b64decode(response.audio_data)
    with wave.open(io.BytesIO(base64.b64decode(response.audio_data)), 'rb') as wav_file:
        pcm_bytes = wav_file.readframes(wav_file.getnframes())
        frame_rate = wav_file.getframerate()

    audio_array = np.frombuffer(pcm_bytes, dtype=np.int16).astype(np.float32)

    return resample_poly(audio_array, up=sample_rate, down=frame_rate).astype(np.int16).tobytes()

if __name__ == "__main__":
    with wave.open('output.wav', 'rb') as wav_file:
        pprint(f"Audio format: {wav_file.getcomptype()} {wav_file.getsampwidth()} {wav_file.getframerate()} {wav_file.getnchannels()}")
        
        pcm_bytes = wav_file.readframes(wav_file.getnframes())
        frame_rate = wav_file.getframerate()
