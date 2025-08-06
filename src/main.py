import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import Response, StreamingResponse
import asyncio
from dotenv import load_dotenv
from google.cloud import texttospeech
import re
import base64
from langdetect import detect
from dataclasses import dataclass
from speechify import AudioStreamRequestAccept, Speechify
from dotenv import load_dotenv
from speechify.tts.audio.types.get_speech_request_audio_format import GetSpeechRequestAudioFormat
from speechify.tts.types.get_speech_response import GetSpeechResponse
import os

load_dotenv()

client = Speechify(token=os.getenv("SPEECHIFY_API_KEY"))

logging.basicConfig(level=logging.INFO)

texttospeech_client = texttospeech.TextToSpeechClient()
bytes_per_sample = 2

app = FastAPI()

def clean_text_for_tts(text: str) -> str:
    """
    Removes emojis, URLs, mentions, hashtags, and extra whitespace from a string.
    """
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "]+",
        flags=re.UNICODE,
    )
    
    # Remove emojis
    text = emoji_pattern.sub(r'', text)
    
    # Remove URLs
    text = re.sub(r'https?:\/\/\S+', '', text)
    
    # Remove mentions (@user) and hashtags (#topic)
    text = re.sub(r'[@#]\w+', '', text)
    
    # Replace multiple whitespace characters with a single space
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

@dataclass
class LanguageConfiguration:
    language_code: str  
    languade_model: str

supported_languages = {
    "en": LanguageConfiguration('en-US', 'en-US-Chirp3-HD-Charon'),
    "hi": LanguageConfiguration('hi-IN', 'hi-IN-Chirp3-HD-Charon'),
    "he": LanguageConfiguration('he-IL', 'he-IL-Wavenet-D'),
}

def synthesize_audio(text: str, sample_rate: int) -> bytes:
    """Synthesizes audio using the GCloud Text to Speech API."""

    response = client.tts.audio.speech(input=text, voice_id='moshe', audio_format='wav', language='he-IL')
    if response.audio_data is None:
        raise Exception("TTS synthesis produced no audio")
    return base64.b64decode(response.audio_data[44:])

    # languageConfiguration = supported_languages['he'] # try: detected_lang = detect(text) if detected_lang in supported_languages: languageConfiguration = supported_languages[detected_lang] 
    # # except:
        # # raise
    # synthesis_input = texttospeech.SynthesisInput(text=text)
    # voice = texttospeech.VoiceSelectionParams(language_code=languageConfiguration.language_code, name=languageConfiguration.languade_model)

    # # check if the sample rate is available
    # audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.LINEAR16, sample_rate_hertz=sample_rate)

    # response = texttospeech_client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)

    # # remove the wav header from LINEAR 16 data
    # return response.audio_content[44:]

@app.post("/synthesize")
async def synthesize(request: Request):
    logging.info(f"Request started")
    try:
        async with asyncio.timeout(30):
            request = await request.json()

            if 'message' not in request:
                raise HTTPException(status_code=400, detail="Missing or invalid 'message' object in request body")

            message = request['message']
            message['text'] = clean_text_for_tts(message['text'])

            # Validate message type
            if 'type' not in message or message['type'] != 'voice-request':
                raise HTTPException(status_code=400, detail="Invalid message type")

            # Validate text content
            if 'text' not in message or not message['text']:
                raise HTTPException(status_code=400, detail="Invalid or missing text")

            if 'sampleRate' not in message:
                raise HTTPException(status_code=400, detail="Invalid or missing sampleRate")

            print("MESSAGE TEXT: ", message['text'])

            # Validate sample rate
            valid_sample_rates = [8000, 16000, 22050, 24000, 44100]
            if message['sampleRate'] not in valid_sample_rates:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported sample rate. Supported rates: {valid_sample_rates}"
                )

            logging.info(f"Synthesizing: length={len(message['text'])}, rate={message['sampleRate']} Hz")

            audio_buffer = synthesize_audio(message['text'], message['sampleRate'])
            # audio_buffer =  tts(message['text'], message['sampleRate'])

            if not audio_buffer:
                raise Exception("TTS synthesis produced no audio")

            logging.info(f"TTS completed")

            # Return raw audio bytes with the correct content type
            return Response(content=audio_buffer, media_type="application/octet-stream")

    except asyncio.TimeoutError:
        logging.error(f"Request timed out.")
        return HTTPException(status_code=408, detail="Request timeout")
    except HTTPException as e:
        logging.error(f"TTS failed: {e.detail}")
        raise HTTPException(status_code=e.status_code, detail=f"TTS synthesis failed: {e.detail}")
    except Exception as e:
        logging.error(f"TTS failed: {e}")
        raise HTTPException(status_code=500, detail="Unexpected error occured")
