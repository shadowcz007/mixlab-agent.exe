from openai import AsyncOpenAI

class LLMClient:
    def __init__(self, api_base_url, api_key, model):
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=api_base_url if api_base_url else None  # Use default OpenAI URL if not specified
        )
        self.model = model

    async def generate(self, prompt):
        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an AI assistant."},
                {"role": "user", "content": prompt}
            ],
            stream=True
        )
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content