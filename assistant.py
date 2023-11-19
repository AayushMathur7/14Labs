from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class PodcastAssistant:
    def __init__(self, client, prompt, model="gpt-4-1106-preview"):
        self._client = client
        self._model = model
        self._prompt = prompt
        self.assistant = self._client.beta.assistants.create(
            name="Podcast GPT",
            instructions=self._prompt,
            tools=[{"type": "retrieval"}],
            model=self._model
        )

