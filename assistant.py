from openai import OpenAI
class PodcastAssistant:
    def __init__(self, client, model="gpt-4-1106-preview"):
        self._client = client
        self._model = model
        self.assistant = self._client.beta.assistants.create(
            name="Math Tutor",
            instructions="You are a personal math tutor. Write and run code to answer math questions.",
            tools=[{"type": "code_interpreter"}],
            model=self._model
        )


client = OpenAI()

MODEL = "gpt-4-1106-preview"

podcast_assistant = PodcastAssistant()
