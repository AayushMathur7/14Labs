from logo import render_logo
from assistant import PodcastAssistant
import streamlit as st
import openai
import uuid
import time
import pandas as pd
from openai import OpenAI

import os
from text_to_speech import generate_text_to_speech
import asyncio
import nest_asyncio

nest_asyncio.apply()

from tavily import TavilyClient
from llama_hub.web.news import NewsArticleReader
import re


def fetch_and_append_articles(urls):
    # Initialize an empty DataFrame if it doesn't exist in the session state
    if "articles" not in st.session_state:
        st.session_state["articles"] = pd.DataFrame(
            columns=["Title", "Publish Date", "URL"]
        )

    new_articles = []
    for url in urls:
        # Escape special characters for regular expression
        escaped_url = re.escape(url)

        # Check if the URL is already in the DataFrame
        if (
            not st.session_state["articles"]["URL"]
            .str.contains(escaped_url, regex=True)
            .any()
        ):
            try:
                # Fetch document data
                documents = reader.load_data([url])

                # Extract relevant data
                for doc in documents:
                    new_article = {
                        "Title": doc.metadata.get("title", "No Title"),
                        "Publish Date": doc.metadata.get(
                            "publish_date", "No Date"
                        ),
                        "URL": doc.metadata.get("link", url),
                    }
                    new_articles.append(new_article)
            except Exception as e:
                st.error(f"An error occurred while fetching {url}: {e}")

    # Update session state
    if new_articles:
        new_df = pd.DataFrame(new_articles)
        st.session_state["articles"] = pd.concat(
            [st.session_state["articles"], new_df], ignore_index=True
        )


# Initialize OpenAI client
client = OpenAI()
tavily_client = TavilyClient(api_key=st.secrets["TAVILY_API_KEY"])

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
    "Upload your file", type=["csv", "xls", "xlsx"]
)

duration = st.sidebar.selectbox(
    "Choose Podcast Duration", ("1 minute", "5 minutes", "15 minutes")
)

host = st.sidebar.radio(
    "Choose the Podcast Host",
    (
        "Conan O’Brien",
        "Sam Altman",
        "David Attenborough",
    ),
)

if st.button("Generate Podcast"):
    mp3_path = asyncio.run(
        generate_text_to_speech(
            host,
            "Hello! My name is Eleven. I am a virtual assistant that can help you generate a podcast episode.",
        )
    )
    if mp3_path is not None:
        audio_file = open(mp3_path, "rb")
        audio_bytes = audio_file.read()
        st.audio(audio_bytes, format="audio/mp3")

genres = st.sidebar.multiselect(
    "Select Podcast Genres",
    ("Comedy", "News", "Technology", "Education", "Health"),
)

PROMPT = f"""
As a podcast generator assistant, you are tasked with creating a personalized podcast episode based on the following user preferences:

- Duration: {duration}
- Host: {host}
- Genres: {', '.join(genres)}

You are supposed to generate a podcast episode that is {duration} long, hosted by {host}, and covers topics in {' and '.join(genres)}. The episode will reflect the user's chosen genres, ensuring a tailored and engaging listening experience.

You may also receive news content from web URLs, which should inform the content of your porcast script.

You will only generate the podcast when the user types "/generate".

You will use the provided Tavily search API function to find relevant news article URLs to supplement your content when the user types "/news" followed by the topic

Do not use Tavily search API function otherwise.

Do not generate the podcast otherwise.

If you are not generating the podcast, you should respond to the user's chat messages with your findings.

When you generate the podcast, you should only provide the transcript of the podcast itself. Your response should not incorporate any bullshit before or after the content of the transcript.
"""

podcast_assistant = PodcastAssistant(client, tavily_client, PROMPT)
# podcast_assistant = {"assistant": {"id": "asst_WHdn0UmJCvQHfXWpwtcYVau2"}}

# Initialize the NewsArticleReader
reader = NewsArticleReader(use_nlp=False)

# Initialize session state for storing articles
if "articles" not in st.session_state:
    st.session_state.articles = pd.DataFrame(
        columns=["Title", "Publish Date", "URL"]
    )

# Input for single URL
col1, col2 = st.columns([8, 2])

with col1:
    url = st.text_input(
        label="**Add article**", placeholder="Add URL for your podcast content"
    )

with col2:
    st.markdown("")
    fetch_news = st.button("Fetch News")

if fetch_news and url:
    fetch_and_append_articles([url])

with st.expander("**Article List**"):
    if "articles" in st.session_state and not st.session_state.articles.empty:
        st.data_editor(
            st.session_state.articles, hide_index=True, num_rows="dynamic"
        )

# Initialize OpenAI assistant
if "assistant" not in st.session_state:
    openai.api_key = st.secrets["OPENAI_API_KEY"]
    st.session_state.assistant = openai.beta.assistants.retrieve(
        # podcast_assistant.assistant.id
        "asst_WHdn0UmJCvQHfXWpwtcYVau2"
    )
    st.session_state.thread = client.beta.threads.create(
        metadata={"session_id": st.session_state.session_id}
    )

# Display chat messages
elif (
    hasattr(st.session_state.run, "status")
    and st.session_state.run.status == "completed"
):
    st.session_state.messages = client.beta.threads.messages.list(
        thread_id=st.session_state.thread.id
    )

    for message in reversed(st.session_state.messages.data):
        if message.role in ["user", "assistant"] and not message.content[
            0
        ].text.value.startswith("Title:"):
            with st.chat_message(message.role):
                for content_part in message.content:
                    message_text = content_part.text.value
                    st.markdown(message_text)

                    web_links = podcast_assistant.extract_urls(message_text)

                    if web_links:
                        fetch_and_append_articles(web_links)

# Chat input and message creation with file ID
if prompt := st.chat_input("Type /generate to create podcast"):
    with st.chat_message("user"):
        st.write(prompt)

    if prompt == "/generate":
        news_content = ""

        if not st.session_state.articles.empty:
            for _, row in st.session_state.articles.iterrows():
                url = row["URL"]
                try:
                    # Reload content for each URL
                    document = reader.load_data([url])[0]
                    title = document.metadata.get("title", "No Title")
                    content = document.text
                    news_content += f"Title: {title}\nContent: {content}\n\n"
                except Exception as e:
                    st.error(
                        f"An error occurred while fetching content for {url}: {e}"
                    )

            message_data = {
                "thread_id": st.session_state.thread.id,
                "role": "user",
                "content": news_content,
            }

            st.session_state.messages = client.beta.threads.messages.create(
                **message_data
            )

    message_data = {
        "thread_id": st.session_state.thread.id,
        "role": "user",
        "content": prompt,
    }

    # Include file ID in the request if available
    if "file_id" in st.session_state:
        message_data["file_ids"] = [st.session_state.file_id]

    st.session_state.messages = client.beta.threads.messages.create(
        **message_data
    )

    st.session_state.run = client.beta.threads.runs.create(
        thread_id=st.session_state.thread.id,
        assistant_id=st.session_state.assistant.id,
    )
    if st.session_state.retry_error < 3:
        time.sleep(1)
        st.rerun()

# Handle run status
if hasattr(st.session_state.run, "status"):
    if st.session_state.run.status == "running":
        with st.chat_message("assistant"):
            st.write("Thinking ......")
        if st.session_state.retry_error < 3:
            time.sleep(1)
            st.rerun()

    elif st.session_state.run.status == "requires_action":
        st.session_state.run = podcast_assistant.submit_tool_outputs(
            client,
            st.session_state.thread.id,
            st.session_state.run.id,
            st.session_state.run.required_action.submit_tool_outputs.tool_calls,
        )
        with st.chat_message("assistant"):
            st.write("Fetching the latest news ......")
        if st.session_state.retry_error < 3:
            time.sleep(1)
            st.rerun()

    elif st.session_state.run.status == "failed":
        st.session_state.retry_error += 1
        with st.chat_message("assistant"):
            if st.session_state.retry_error < 3:
                st.write("Run failed, retrying ......")
                time.sleep(3)
                st.rerun()
            else:
                st.error(
                    "FAILED: The OpenAI API is currently processing too many requests. Please try again later ......"
                )

    elif st.session_state.run.status != "completed":
        st.session_state.run = client.beta.threads.runs.retrieve(
            thread_id=st.session_state.thread.id,
            run_id=st.session_state.run.id,
        )
        if st.session_state.retry_error < 3:
            time.sleep(3)
            st.rerun()
