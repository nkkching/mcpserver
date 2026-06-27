import httpx
import json
from mcp.server.fastmcp import FastMCP

# Create an MCP server using FastMCP
mcp = FastMCP("PowerAutomateMCPServer")

# The Power Automate API endpoint provided by the user
POWER_AUTOMATE_ENDPOINT = "https://a8afc1d6d727ef81b23e4ba9d001ea.92.environment.api.powerplatform.com:443/powerautomate/automations/direct/workflows/897f276ab8db4974915818329ffe2c49/triggers/manual/paths/invoke?api-version=1&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=GU2Gfu-6Ex7AZ4J-9eD8tRVAfrGcDmRUgai0GYxlWTQ"

@mcp.tool()
async def invoke_power_automate_workflow(payload: dict | None = None) -> str:
    """
    Invokes the specific Power Automate workflow.
    
    Args:
        payload: Optional dictionary containing the JSON payload to send to the workflow.
                 This should match the schema expected by the Power Automate HTTP trigger.
                 
    Returns:
        A string containing the response from the Power Automate workflow or an error message.
    """
    try:
        # Use httpx for asynchronous HTTP requests
        async with httpx.AsyncClient() as client:
            # Power Automate HTTP triggers expect a POST request with JSON content
            headers = {"Content-Type": "application/json"}
            
            # Send the request
            response = await client.post(
                POWER_AUTOMATE_ENDPOINT,
                json=payload if payload is not None else {},
                headers=headers,
                timeout=30.0
            )
            
            # Check if the request was successful
            response.raise_for_status()
            
            # Try to return the JSON response if available, otherwise return text
            try:
                result = response.json()
                return json.dumps(result, indent=2)
            except ValueError:
                return response.text if response.text else "Workflow invoked successfully (No content returned)."
                
    except httpx.HTTPStatusError as e:
        return f"HTTP error occurred: {e.response.status_code} - {e.response.text}"
    except httpx.RequestError as e:
        return f"An error occurred while requesting: {e}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"

if __name__ == "__main__":
    # Run the server using stdio transport by default
    # This is the standard way MCP servers communicate with clients (like Claude Desktop)
    mcp.run()
