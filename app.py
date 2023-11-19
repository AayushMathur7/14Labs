from logo import render_logo
from assistant import PodcastAssistant
import streamlit as st
import openai
import uuid
import time
import pandas as pd
import io
from openai import OpenAI
import os
from text_to_speech import generate_text_to_speech
import asyncio
import nest_asyncio
nest_asyncio.apply()


# Initialize OpenAI client
client = OpenAI()

# Your chosen model
MODEL = "gpt-4-1106-preview"

# Initialize session state variables
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "run" not in st.session_state:
    st.session_state.run = {"status": None}

if "messages" not in st.session_state:
    st.session_state.messages = []

if "retry_error" not in st.session_state:
    st.session_state.retry_error = 0

# Set up the page
st.set_page_config(page_title="Enter title here")
render_logo()
st.sidebar.markdown("### Configurations")

# File uploader for CSV, XLS, XLSX
uploaded_file = st.file_uploader(
    "Upload your file", type=["csv", "xls", "xlsx"])

if st.button('Generate Podcast'):
    mp3_path = asyncio.run(generate_text_to_speech(
        "Hello, my name is Eleven. I am a virtual assistant."
    ))
    if mp3_path is not None:
        audio_file = open(mp3_path, 'rb')
        audio_bytes = audio_file.read()
        st.audio(audio_bytes, format='audio/mp3')
duration = st.sidebar.selectbox(
    'Choose Podcast Duration',
    ('1 minute', '5 minutes', '15 minutes')
)

host = st.sidebar.radio(
    'Choose the Podcast Host',
    ('Conan O’Brien', 'Joe Rogan', 'Oprah Winfrey', 'Marc Maron', 'Terry Gross')
)

genres = st.sidebar.multiselect(
    'Select Podcast Genres',
    ('Comedy', 'News', 'Technology', 'Education', 'Health')
)

PROMPT = f"""
As a podcast generator assistant, you are tasked with creating a personalized podcast episode based on the following user preferences:

- Duration: {duration}
- Host: {host}
- Genres: {', '.join(genres)}

You are supposed to generate a podcast episode that is {duration} long, hosted by {host}, and covers topics in {' and '.join(genres)}. The episode will reflect the user's chosen genres, ensuring a tailored and engaging listening experience.

When the user provides URLs, you should read the content of the URL, and use that as content for the podcast episode.

You will only generate the podcast when the user types "/generate".
"""

podcast_assistant = PodcastAssistant(client, PROMPT)

# Initialize OpenAI assistant
if "assistant" not in st.session_state:
    openai.api_key = st.secrets["OPENAI_API_KEY"]
    st.session_state.assistant = openai.beta.assistants.retrieve(
        podcast_assistant.assistant.id)
    st.session_state.thread = client.beta.threads.create(
        metadata={'session_id': st.session_state.session_id}
    )

# Display chat messages
elif hasattr(st.session_state.run, 'status') and st.session_state.run.status == "completed":
    st.session_state.messages = client.beta.threads.messages.list(
        thread_id=st.session_state.thread.id
    )
    for message in reversed(st.session_state.messages.data):
        if message.role in ["user", "assistant"]:
            with st.chat_message(message.role):
                for content_part in message.content:
                    message_text = content_part.text.value
                    st.markdown(message_text)

# Chat input and message creation with file ID
if prompt := st.chat_input("How can I help you?"):
    with st.chat_message('user'):
        st.write(prompt)

    message_data = {
        "thread_id": st.session_state.thread.id,
        "role": "user",
        "content": prompt
    }

    # Include file ID in the request if available
    if "file_id" in st.session_state:
        message_data["file_ids"] = [st.session_state.file_id]

    st.session_state.messages = client.beta.threads.messages.create(
        **message_data)

    st.session_state.run = client.beta.threads.runs.create(
        thread_id=st.session_state.thread.id,
        assistant_id=st.session_state.assistant.id,
    )
    if st.session_state.retry_error < 3:
        time.sleep(1)
        st.rerun()

# Handle run status
if hasattr(st.session_state.run, 'status'):
    if st.session_state.run.status == "running":
        with st.chat_message('assistant'):
            st.write("Thinking ......")
        if st.session_state.retry_error < 3:
            time.sleep(1)
            st.rerun()

    elif st.session_state.run.status == "failed":
        st.session_state.retry_error += 1
        with st.chat_message('assistant'):
            if st.session_state.retry_error < 3:
                st.write("Run failed, retrying ......")
                time.sleep(3)
                st.rerun()
            else:
                st.error(
                    "FAILED: The OpenAI API is currently processing too many requests. Please try again later ......")

    elif st.session_state.run.status != "completed":
        st.session_state.run = client.beta.threads.runs.retrieve(
            thread_id=st.session_state.thread.id,
            run_id=st.session_state.run.id,
        )
        if st.session_state.retry_error < 3:
            time.sleep(3)
            st.rerun()
