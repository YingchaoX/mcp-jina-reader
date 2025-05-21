# Jina Reader MCP Server

MCP server implementation for Jina AI search and reading operations. This server provides a Model Context Protocol (MCP) interface to interact with Jina.ai's search and web reading capabilities.

## Features

- Search functionality through Jina.ai
- Web content reading and extraction
- Asynchronous processing
- MCP protocol integration

## Installation

1. Clone the repository:
```bash
git clone https://github.com/YingchaoX/mcp-jina-reader.git
```

2. Install dependencies using `uv`:
```bash
uv pip install -e .
```

3. Configure the MCP server by adding to your `mcpservers.json`:
```json
{
    "mcp-jina-fetch": {
        "command": ["python", "-m", "mcp_jina_reader"],
        "env": {
            "JINA_API_KEY": "your-api-key-here",
            "JINA_TIMEOUT": "10"
        }
    }
}
```

## API

### Resources

`jina://search`: Jina.ai search interface
`jina://read`: Jina.ai web reading interface

### Tools

#### search

Search for content using Jina.ai
- Input: 
  - keywords (string): Search terms

Example:
```json
{
    "name": "search",
    "arguments": {
        "keywords": "your search terms"
    }
}
```

#### read

Read and extract content from a URL
- Input:
  - url (string): URL to read and extract content from

Example:
```json
{
    "name": "read",
    "arguments": {
        "url": "https://example.com"
    }
}
```

## Environment Variables

- `JINA_API_KEY`: Your Jina.ai API key (required)
- `JINA_TIMEOUT`: Request timeout in seconds (optional, default: 10)

## License

MIT License - see [LICENSE](LICENSE) file for details
