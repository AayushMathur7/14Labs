import httpx
import streamlit as st

CHUNK_SIZE = 1024


async def generate_text_to_speech(text):

    voice_id = "CYw3kZ02Hs0563khs1Fj"
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key":  st.secrets["XI_API_KEY"],
    }

    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.5}
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=data, headers=headers)

        with open('output.mp3', 'wb') as f:
            async for chunk in response.aiter_bytes():
                if chunk:
                    f.write(chunk)

    return "output.mp3"
