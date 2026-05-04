# services/ai_service.py
from anthropic import AsyncAnthropic
from anthropic.types import MessageParam, TextBlock
from fastapi import Depends
from typing import Annotated
from models import Shipment
from config import settings


_client: AsyncAnthropic | None = None  # private to this module


def init_anthropic_client() -> AsyncAnthropic:
    global _client
    _client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
    return _client


def get_anthropic_client() -> AsyncAnthropic:
    if _client is None:
        raise RuntimeError("Anthropic client not initialized")
    return _client


SHIPMENT_SYSTEM_PROMPT = """
You are a shipment assistant. You help users understand and analyze shipment data.
You can summarize shipment details, flag anomalies (e.g. unusually heavy packages),
and answer questions about a specific shipment.
Always be concise and factual. Do not make up data.
"""


class AIService:
    def __init__(self, client: AsyncAnthropic):
        self.client = client

    async def _ask(self, system: str, question: str) -> str:
        """Base single-turn method — all other methods build on this."""
        messages: list[MessageParam] = [{"role": "user", "content": question}]
        response = await self.client.messages.create(
            model="claude-opus-4-7",
            max_tokens=1024,
            system=system,
            messages=messages,
        )

        for block in response.content:
            if isinstance(block, TextBlock):
                return block.text

        raise ValueError("No text block found in response")

    async def answer_about_shipment(self, shipment: Shipment, question: str) -> str:
        context = f"""
        Shipment context:
        {shipment.model_dump_json(indent=2)}

        User question: {question}
        """
        return await self._ask(SHIPMENT_SYSTEM_PROMPT, context)


# --- DI setup ---


def get_ai_service(
    client: Annotated[AsyncAnthropic, Depends(get_anthropic_client)],
) -> AIService:
    return AIService(client)


AIServiceDep = Annotated[AIService, Depends(get_ai_service)]
