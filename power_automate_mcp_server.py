import httpx
import json
import os
from fastmcp import FastMCP          # <-- changed from mcp.server.fastmcp

mcp = FastMCP("PowerAutomateMCPServer" )

POWER_AUTOMATE_ENDPOINT = os.environ.get(
    "POWER_AUTOMATE_ENDPOINT",
    "https://e9a5c353a85a4d198de384982869cd.36.environment.api.powerplatform.com:443/powerautomate/automations/direct/workflows/afad2278ea4d4408afd0d6c37e303d23/triggers/manual/paths/invoke?api-version=1&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=CTz4JjVgLaKTyDLc5bRLZE9ElLGekgkLP_A5J0i1D-A"
 )

@mcp.tool()
async def invoke_power_automate_workflow(payload: dict | None = None) -> str:
    """
    Invokes the Power Automate workflow via its HTTP trigger.

    Args:
        payload: Optional JSON payload to forward to the workflow trigger.

    Returns:
        The workflow response as a JSON string, or an error message.
    """
    try:
        async with httpx.AsyncClient( ) as client:
            response = await client.post(
                POWER_AUTOMATE_ENDPOINT,
                json=payload if payload is not None else {},
                headers={"Content-Type": "application/json"},
                timeout=30.0,
            )
            response.raise_for_status()
            try:
                return json.dumps(response.json(), indent=2)
            except ValueError:
                return response.text or "Workflow invoked successfully (no content returned)."
    except httpx.HTTPStatusError as e:
        return f"HTTP error: {e.response.status_code} — {e.response.text}"
    except httpx.RequestError as e:
        return f"Request error: {e}"
    except Exception as e:
        return f"Unexpected error: {e}"

# ASGI app — used by Uvicorn on Render
app = mcp.http_app( )           # fastmcp uses http_app( ) without path arg by default
application = app              # alias for Azure App Service compatibility

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    mcp.run(transport="http", host="0.0.0.0", port=port )
