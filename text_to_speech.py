import time
import httpx
import streamlit as st
from hosts import Narrator
from pydub import AudioSegment

CHUNK_SIZE = 1024


def generate_text_to_speech(narrator: Narrator, text: str):
    voice_id = narrator.value.voice_id
    file_id = narrator.value.file_id

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": st.secrets["XI_API_KEY"],
    }

    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.5}
    }

    timeout = httpx.Timeout(120.0)

    with httpx.Client(timeout=timeout) as client:
        response = client.post(url, json=data, headers=headers)

        with open(f'data/audio/body/{file_id}.mp3', 'wb') as f:
            for chunk in response.iter_bytes():
                if chunk:
                    f.write(chunk)


def add_intro_outro(narrator: Narrator):
    # Define the duration of the silence (in milliseconds)
    silence_duration = 500
    silence = AudioSegment.silent(duration=silence_duration)

    host = narrator.value.file_id

    # Paths to your MP3 files
    intro_path = f"data/audio/intro/{host}.mp3"
    body_path = f"data/audio/body/{host}.mp3"

    # Load the two audio files
    intro = AudioSegment.from_mp3(intro_path)
    body = AudioSegment.from_mp3(body_path)

    # Define the duration of the crossfade (in milliseconds)
    intro_fade_out_duration = 2500
    body_fade_in_duration = 750

    # Concatenate with a crossfade
    intro = intro.fade_out(intro_fade_out_duration)
    body = body.fade_in(body_fade_in_duration)
    complete_audio = intro.append(silence).append(body)

    # Export the final audio
    complete_path = f"data/audio/complete/{host}.mp3"
    complete_audio.export(complete_path, format="mp3")

    # Wait for the file to be written
    time.sleep(2)


def generate_complete_audio(narrator: Narrator, text: str):
    # Generate content audio
    generate_text_to_speech(narrator, text)

    # Add intro and outro
    add_intro_outro(narrator)

    # Return the path to the complete audio
    return f"data/audio/complete/{narrator.value.file_id}.mp3"
