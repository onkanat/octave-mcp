import asyncio
import json
import os
import sys
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

CODE = """
X = linspace(0, 2*pi, 360);
Y = sin(X.^2);
figure; plot(X, Y, 'b-', 'LineWidth', 1.5); grid on; title('Y = sin(X^2)');
""".strip()


async def main():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    server_py = os.path.join(repo_root, "src", "mcp_server.py")

    env = os.environ.copy()
    env.setdefault("MCP_RUNS_ROOT", os.path.join(repo_root, "runs"))
    env.setdefault("OCTAVE_RUNNER_MODE", "octave")

    params = StdioServerParameters(
        command=sys.executable,
        args=[server_py],
        env=env,
    )

    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            sid = "demo1"

            pub = await session.call_tool("octave_publish", {"code": CODE, "session_id": sid})
            print("publish:", json.dumps(pub.model_dump(), ensure_ascii=False)[:200])

            grab = await session.call_tool("octave_grabcode", {"session_id": sid})
            print("grabcode:", json.dumps(grab.model_dump(), ensure_ascii=False))

            run = await session.call_tool(
                "octave_run",
                {"code": CODE, "session_id": sid, "images_b64": True, "max_image_bytes": 180000},
            )
            print("run:", json.dumps(run.model_dump(), ensure_ascii=False)[:400])


if __name__ == "__main__":
    asyncio.run(main())
