# ./adk_agent_samples/mcp_agent/agent.py
import asyncio
from dotenv import load_dotenv
import os # Required for path operations
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters, StdioConnectionParams
# Load environment variables from .env file in the parent directory
# Place this near the top, before using env vars like API keys
load_dotenv()


root_agent = LlmAgent(
    model='gemini-2.0-flash',
    name='speaker',
    instruction=(
            "You are a Text-to-Speech agent. Take the text provided by the user or coordinator and "
            "use the available ElevenLabs TTS tool to convert it into audio. "
            "When calling the text_to_speech tool, set the parameter 'voice_name' to 'Rachel'. "
            "Return the result from the tool (expected to be a URL)."
        ),
    tools=[
        MCPToolset(
            connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command='uvx',
                args=['elevenlabs-mcp'],
                env={"ELEVENLABS_API_KEY": os.environ.get("ELEVENLABS_API_KEY", "")}
            ),
            timeout=160
            ),
            # Optional: Filter which tools from the MCP server are exposed
            # tool_filter=['list_directory', 'read_file']
            tool_filter=['text_to_speech']  # Solo esa herramienta expuesta

        )
    ],
)


