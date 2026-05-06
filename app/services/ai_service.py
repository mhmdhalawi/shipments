# services/ai_service.py
import json
from anthropic import AsyncAnthropic
from anthropic.types import MessageParam, TextBlock, ToolUseBlock
from fastapi import Depends
from collections.abc import Callable, Awaitable
from typing import Annotated
from models import Shipment, ShipmentStatus
from config import settings


_client: AsyncAnthropic | None = None  # private to this module


# initialize the Anthropic client at startup and store in module-level variable
def init_anthropic_client() -> AsyncAnthropic:
    global _client
    _client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
    return _client


SHIPMENT_SYSTEM_PROMPT = """
You are a shipment assistant. You help users understand and analyze shipment data.
You can summarize shipment details, flag anomalies (e.g. unusually heavy packages),
and answer questions about a specific shipment.
Always be concise and factual. Do not make up data.
"""

TOOLS: list = [
    {
        "name": "get_all_shipments",
        "description": "Retrieve all shipments from the database.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_shipment_by_id",
        "description": "Retrieve a single shipment by its ID.",
        "input_schema": {
            "type": "object",
            "properties": {
                "shipment_id": {
                    "type": "string",
                    "description": "The UUID of the shipment",
                }
            },
            "required": ["shipment_id"],
        },
    },
    {
        "name": "get_shipments_by_status",
        "description": "Retrieve all shipments with a specific status.",
        "input_schema": {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "enum": [s.value for s in ShipmentStatus],
                    "description": "The status to filter by",
                }
            },
            "required": ["status"],
        },
    },
]

# type alias for the tool handler functions passed in from outside
ToolHandler = Callable[..., Awaitable[list[Shipment] | Shipment | None]]


class AIService:
    def __init__(self, client: AsyncAnthropic):
        self.client = client

    async def _run_tool(
        self, tool_name: str, tool_input: dict, handlers: dict[str, ToolHandler]
    ) -> str:
        """Execute the tool Claude requested and return result as JSON string."""
        handler = handlers.get(tool_name)
        if not handler:
            return json.dumps({"error": f"Unknown tool: {tool_name}"})

        result = await handler(**tool_input)

        if result is None:
            return json.dumps({"error": "Not found"})
        if isinstance(result, list):
            return json.dumps([json.loads(s.model_dump_json()) for s in result])
        return result.model_dump_json()

    async def chat(self, question: str, handlers: dict[str, ToolHandler]) -> str:
        """Agentic loop — Claude keeps calling tools until it has an answer."""
        messages: list[MessageParam] = [{"role": "user", "content": question}]

        while True:
            response = await self.client.messages.create(
                model="claude-opus-4-6",
                max_tokens=1024,
                system=SHIPMENT_SYSTEM_PROMPT,
                tools=TOOLS,
                messages=messages,
            )

            # Claude is done, return the text answer
            if response.stop_reason == "end_turn":
                for block in response.content:
                    if isinstance(block, TextBlock):
                        return block.text
                raise ValueError("No text block found in response")

            # Claude wants to use a tool
            if response.stop_reason == "tool_use":
                # append Claude's response to message history
                messages.append({"role": "assistant", "content": response.content})

                # execute all requested tools and collect results
                tool_results = []
                for block in response.content:
                    if isinstance(block, ToolUseBlock):
                        result = await self._run_tool(block.name, block.input, handlers)
                        tool_results.append(
                            {
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": result,
                            }
                        )

                # append tool results and let Claude continue
                messages.append({"role": "user", "content": tool_results})


# --- DI setup ---
def get_anthropic_client() -> AsyncAnthropic:
    if _client is None:
        raise RuntimeError("Anthropic client not initialized")
    return _client


def get_ai_service(
    client: Annotated[AsyncAnthropic, Depends(get_anthropic_client)],
) -> AIService:
    return AIService(client)


AIServiceDep = Annotated[AIService, Depends(get_ai_service)]
