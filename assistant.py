import json
import re


tavily_search_tool = {
    "type": "function",
    "function": {
        "name": "tavily_search",
        "description": "Get information on recent events from the web.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query to use. For example: 'Latest news on Nvidia stock performance'",
                },
            },
            "required": ["query"],
        },
    },
}


class PodcastAssistant:
    def __init__(
        self, client, tavily_client, prompt, model="gpt-4-1106-preview"
    ):
        self._tavily_client = tavily_client
        self._client = client
        self._model = model
        self._prompt = prompt
        self.assistant = self._client.beta.assistants.create(
            name="Podcast GPT",
            instructions=self._prompt,
            tools=[tavily_search_tool],
            model=self._model,
        )

    def tavily_search(self, query):
        search_result = self._tavily_client.get_search_context(
            query, search_depth="advanced", max_tokens=8000
        )
        return search_result

    def submit_tool_outputs(self, client, thread_id, run_id, tools_to_call):
        tool_output_array = []

        for tool in tools_to_call:
            output = None
            tool_call_id = tool.id
            function_name = tool.function.name
            function_args = tool.function.arguments

            if function_name == "tavily_search":
                output = self.tavily_search(
                    query=json.loads(function_args)["query"]
                )

            if output:
                tool_output_array.append(
                    {"tool_call_id": tool_call_id, "output": output}
                )

        return client.beta.threads.runs.submit_tool_outputs(
            thread_id=thread_id, run_id=run_id, tool_outputs=tool_output_array
        )

    def extract_urls(self, text):
        # Regex pattern for extracting URLs
        url_pattern = r"https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[^ \n]*"
        # Find all matches in the text
        urls = re.findall(url_pattern, text)
        return urls
