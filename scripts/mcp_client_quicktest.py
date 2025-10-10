import asyncio
import json
import os
import sys
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

# Quick local test for the MCP stdio server.
# Usage: python scripts/mcp_client_quicktest.py

async def main():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    server_py = os.path.join(repo_root, "src", "mcp_server.py")

    env = os.environ.copy()
    env.setdefault("MCP_RUNS_ROOT", os.path.join(repo_root, "runs"))

    params = StdioServerParameters(
        command=sys.executable,
        args=[server_py],
        env=env,
    )

    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # 1) publish
            pub = await session.call_tool(
                "octave_publish", {"code": "print('from mcp')", "session_id": "m1"}
            )
            print("publish:", json.dumps(pub.model_dump(), ensure_ascii=False)[:200])

            # 2) grabcode
            grab = await session.call_tool("octave_grabcode", {"session_id": "m1"})
            print("grabcode:", json.dumps(grab.model_dump(), ensure_ascii=False)[:200])

            # 3) run
            run = await session.call_tool("octave_run", {"code": "print('run ok')", "session_id": "m1"})
            print("run:", json.dumps(run.model_dump(), ensure_ascii=False)[:200])

            # 4) cleanup (dry-run)
            cl = await session.call_tool("admin_cleanup", {"dry_run": True})
            print("cleanup:", json.dumps(cl.model_dump(), ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(main())
