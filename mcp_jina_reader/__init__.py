from .main import serve


def main():
    """MCP Jina Reader - Reader functionality for MCP"""
    import asyncio

    asyncio.run(serve())


if __name__ == "__main__":
    main()
