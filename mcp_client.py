"""
MCP Client using Official Python SDK with Streamable HTTP Transport
Provides a clean interface for connecting to MCP servers
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from contextlib import AsyncExitStack

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

logger = logging.getLogger(__name__)

class MCPSDKClient:
    """MCP client using the official Python SDK with Streamable HTTP transport"""
    
    def __init__(self, server_url: str):
        self.server_url = server_url
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self._initialized = False
        self._tools_cache: Optional[List[Dict[str, Any]]] = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
    
    async def initialize(self) -> Dict[str, Any]:
        """Initialize connection with MCP server"""
        if self._initialized:
            return {"result": "already_initialized"}
        
        try:
            # Create streamable HTTP transport
            read_stream, write_stream, _ = await self.exit_stack.enter_async_context(
                streamablehttp_client(self.server_url)
            )
            
            # Create session
            self.session = await self.exit_stack.enter_async_context(
                ClientSession(read_stream, write_stream)
            )
            
            # Initialize the session
            result = await self.session.initialize()
            self._initialized = True
            
            logger.info(f"MCP client initialized successfully: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to initialize MCP client: {e}")
            raise
    
    async def list_tools(self) -> Dict[str, Any]:
        """Get list of available tools from MCP server"""
        if not self._initialized:
            await self.initialize()
        
        try:
            result = await self.session.list_tools()
            
            # Cache tools for easier access
            if hasattr(result, 'tools'):
                self._tools_cache = result.tools
            
            # Convert to dict format for compatibility
            return {
                "result": {
                    "tools": [tool.model_dump() for tool in result.tools] if hasattr(result, 'tools') else []
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to list tools: {e}")
            raise
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a specific tool on the MCP server"""
        if not self._initialized:
            await self.initialize()
        
        try:
            result = await self.session.call_tool(name, arguments)
            
            # Convert to dict format for compatibility
            return {
                "result": {
                    "content": [
                        content.model_dump() if hasattr(content, 'model_dump') else content 
                        for content in result.content
                    ] if hasattr(result, 'content') else []
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to call tool {name}: {e}")
            raise
    
    async def get_cached_tools(self) -> List[Dict[str, Any]]:
        """Get cached tools list"""
        if self._tools_cache is None:
            tools_response = await self.list_tools()
            self._tools_cache = tools_response.get("result", {}).get("tools", [])
        return self._tools_cache
    
    async def close(self) -> None:
        """Clean up resources"""
        try:
            await self.exit_stack.aclose()
            self.session = None
            self._initialized = False
            self._tools_cache = None
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

class MCPClientFactory:
    """Factory for creating MCP clients"""
    
    @staticmethod
    def create_sdk_client(server_url: str) -> MCPSDKClient:
        """Create MCP client using official SDK with Streamable HTTP transport"""
        return MCPSDKClient(server_url)