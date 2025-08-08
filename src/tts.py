from typing import Iterable
from dotenv import load_dotenv
from resemble import Resemble

load_dotenv()

Resemble.api_key('A10ZIFWnLv25nSy68JUJGAtt')
Resemble.syn_server_url('https://f.cluster.resemble.ai/stream')

project_uuid = Resemble.v2.projects.all(1, 10)['items'][0]['uuid']
voice_uuid = Resemble.v2.voices.all(1, 10)['items'][0]['uuid']

# The API of resemble isn't implemented efficiently, so we need to create our own version of the audio synthesis function

def synthesize_audio(text: str, sample_rate: int) -> Iterable[bytes]:
    """Synthesizes audio using the Resemble Text to Speech API."""

    data = Resemble.v2.clips.stream(project_uuid, voice_uuid, text, sample_rate=sample_rate, ignore_wav_header=True)
    for chunk in data:
        yield bytes(chunk)

if __name__ == "__main__":
    print(Resemble.v2.voices.all(1, 10)['items'])
