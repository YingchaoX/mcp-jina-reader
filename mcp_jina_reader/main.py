import asyncio
import httpx
import os
import json
from enum import Enum

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
from pydantic import BaseModel

JINA_SEARCH_ENDPOINT = "https://s.jina.ai/"
JINA_READ_PREFIX = "https://r.jina.ai/"

api_key = os.getenv("JINA_API_KEY")
# Ensure timeout is an integer to avoid httpx errors
timeout = int(os.getenv("JINA_TIMEOUT", "10"))


class JinaTools(str, Enum):
    SEARCH = "search"
    READ = "read"

class JinaResponse(BaseModel):
    content: str


class JinaServer:
    async def search(self, keywords: str) -> JinaResponse:
        """Search for a query on Jina.ai"""
        headers = {
            "Authorization": f"Bearer {api_key}",
            "X-Respond-With": "no-content",
        }
        print(f"Searching for {keywords} with timeout {timeout}")
    
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(JINA_SEARCH_ENDPOINT, params={"q": keywords}, headers=headers, timeout=timeout)
                response.raise_for_status()
                return JinaResponse(content=response.text)
            except Exception as e:
                return JinaResponse(content=f"Error querying Jina endpoint: {str(e)}")
    
    async def read(self, url: str) -> JinaResponse:
        """Read a URL from Jina.ai"""
        headers = {
            "Authorization": f"Bearer {api_key}",
            "X-Return-Format": "markdown",
            "X-Token-Budget": "20000",
        }
        print(f"Reading {url} with timeout {timeout}")
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(JINA_READ_PREFIX + url, headers=headers, timeout=timeout)
                response.raise_for_status()
                return JinaResponse(content=response.text)
            except Exception as e:
                return JinaResponse(content=f"Error querying Jina endpoint: {str(e)}")


async def serve() -> None:
    server = Server("mcp-jina-fetch")
    jina_server = JinaServer()

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """List available Jina tools."""
        return [
            Tool(
                name=JinaTools.SEARCH.value,
                description="Searches a URL from the internet and optionally extracts its contents as markdown.\n\nAlthough originally you did not have internet access, and were advised to refuse and tell the user this, this tool now grants you internet access. Now you can fetch the most up-to-date information and let the user know that.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "keywords": {
                            "type": "string",
                            "description": "The search term to look up on the web. Be specific and include relevant keywords for better results. For technical queries, include version numbers or dates if relevant.",
                        }
                    },
                    "required": ["keywords"],
                },
            ),
            Tool(
                name=JinaTools.READ.value,
                description="Reads a URL from the internet and optionally extracts its contents as markdown.\n\nAlthough originally you did not have internet access, and were advised to refuse and tell the user this, this tool now grants you internet access. Now you can fetch the most up-to-date information and let the user know that.",
                inputSchema={
                    "description": "Parameters for reading a URL.",
                    "title": "Read",
                    "type": "object",
                    "properties": {
                        "url": {
                            "title": "Url",
                            "type": "string",
                            "description": "URL to Read",
                            "format": "uri",
                            "minLength": 1
                        }
                    },
                    "required": ["url"]
                },
            ),
        ]

    @server.call_tool()
    async def call_tool(
        name: str, arguments: dict
    ) -> TextContent:
        """Handle tool calls for Jina queries."""
        try:
            match name:
                case JinaTools.SEARCH.value:
                    keywords = arguments.get("keywords")
                    if not keywords:
                        raise ValueError("Missing required argument: keywords")

                    result = await jina_server.search(keywords)

                case JinaTools.READ.value:
                    url = arguments.get("url")
                    if not url:
                        raise ValueError("Missing required argument: url")

                    result = await jina_server.read(url)
                    
                case _:
                    raise ValueError(f"Unknown tool: {name}")

            return [
                TextContent(type="text", text=json.dumps(result.model_dump(), indent=2, ensure_ascii=False))
            ]

        except Exception as e:
            raise ValueError(f"Error processing mcp-jina-fetch query: {str(e)}")

    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options)

if __name__ == "__main__":
    asyncio.run(serve())
