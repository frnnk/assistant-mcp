"""
FastMCP server, aggregating all resources, tools, and prompts. 
"""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP(name="Assistant-MCP")

# Add an addition tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b


# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"


def main():
    """
    Entrypoint for MCP server
    """
    mcp.run()


if __name__ == "__main__":
    main()
