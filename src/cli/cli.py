"""
Modern async CLI for octave-mcp service.
"""
import asyncio
import json
import logging
import sys
from typing import Optional

import click
import httpx

logger = logging.getLogger(__name__)


class CLIError(Exception):
    """CLI specific errors."""
    pass


class OCTAVEClient:
    """Async HTTP client for octave-mcp service."""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.client = httpx.AsyncClient()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    async def run_code(
        self,
        code: str,
        session_id: Optional[str] = None,
        timeout: int = 30
    ) -> dict:
        """Execute code via API."""
        payload = {
            "code": code,
            "session_id": session_id,
            "resource_limits": {
                "timeout": timeout,
                "max_output_chars": 20000
            }
        }

        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/run",
                json=payload,
                timeout=timeout + 10
            )
            response.raise_for_status()
            return response.json()

        except httpx.HTTPError as e:
            raise CLIError(f"API request failed: {e}")

    async def publish_code(
        self,
        code: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        session_id: Optional[str] = None,
        expires_hours: int = 24
    ) -> dict:
        """Publish code via API."""
        payload = {
            "code": code,
            "title": title,
            "description": description,
            "session_id": session_id,
            "expires_hours": expires_hours,
            "resource_limits": {
                "timeout": 30,
                "max_output_chars": 20000
            }
        }

        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/publish",
                json=payload,
                timeout=40
            )
            response.raise_for_status()
            return response.json()

        except httpx.HTTPError as e:
            raise CLIError(f"API request failed: {e}")

    async def grab_code(self, share_id: str) -> dict:
        """Get published code via API."""
        payload = {"share_id": share_id}

        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/grabcode",
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            return response.json()

        except httpx.HTTPError as e:
            raise CLIError(f"API request failed: {e}")

    async def list_sessions(self, limit: int = 50) -> dict:
        """List sessions via API."""
        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/sessions",
                params={"limit": limit},
                timeout=10
            )
            response.raise_for_status()
            return response.json()

        except httpx.HTTPError as e:
            raise CLIError(f"API request failed: {e}")

    async def cleanup(
        self,
        max_age_hours: int = 24,
        cleanup_sessions: bool = True,
        cleanup_publications: bool = True,
        dry_run: bool = False
    ) -> dict:
        """Cleanup old resources via API."""
        payload = {
            "max_age_hours": max_age_hours,
            "cleanup_sessions": cleanup_sessions,
            "cleanup_publications": cleanup_publications,
            "dry_run": dry_run
        }

        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/cleanup",
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()

        except httpx.HTTPError as e:
            raise CLIError(f"API request failed: {e}")


def get_base_url() -> str:
    """Get base URL from environment or settings."""
    import os
    return os.environ.get("MCP_SERVER_URL", "http://127.0.0.1:8000")


@click.group()
@click.option("--debug", is_flag=True, help="Enable debug logging")
@click.option("--base-url", help="Override base URL")
@click.pass_context
def cli(ctx, debug: bool, base_url: Optional[str]):
    """Octave MCP CLI - Modern async client for code execution service."""
    if debug:
        logging.basicConfig(level=logging.DEBUG)

    ctx.ensure_object(dict)
    ctx.obj["base_url"] = base_url or get_base_url()


@cli.command()
@click.option("--code", "-c", required=True, help="Code to execute")
@click.option("--session-id", "-s", help="Optional session ID")
@click.option("--timeout", "-t", default=30, help="Execution timeout in seconds")
@click.option("--file", "-f", type=click.Path(exists=True), help="Read code from file")
@click.option("--output", "-o", type=click.Path(), help="Save output to file")
@click.pass_context
def run(ctx, code, session_id, timeout, file, output):
    """Execute Octave/Python code."""
    async def _run():
        # Read code from file if specified
        actual_code = code
        if file:
            with open(file, 'r') as f:
                actual_code = f.read()

        async with OCTAVEClient(ctx.obj["base_url"]) as client:
            try:
                result = await client.run_code(actual_code, session_id, timeout)

                if output:
                    # Save to file
                    with open(output, 'w') as f:
                        json.dump(result, f, indent=2, ensure_ascii=False)
                    print(f"Output saved to {output}")
                else:
                    # Display result
                    print("Execution Result:")
                    print(f"Run ID: {result.get('run_id', 'N/A')}")
                    print(f"Exit Code: {result.get('exit_code', 'N/A')}")
                    print(f"Runtime: {result.get('runtime_seconds', 'N/A')}s")

                    if result.get('stdout'):
                        print("\nSTDOUT:")
                        print(result['stdout'])

                    if result.get('stderr'):
                        print("\nSTDERR:")
                        print(result['stderr'])

                    if result.get('images'):
                        print(f"\nImages: {len(result['images'])}")

            except CLIError as e:
                print(f"Error: {e}")
                sys.exit(1)

    asyncio.run(_run())


@cli.command()
@click.option("--code", "-c", required=True, help="Code to publish")
@click.option("--title", "-t", help="Publication title")
@click.option("--description", "-d", help="Publication description")
@click.option("--session-id", "-s", help="Optional session ID")
@click.option("--expires", "-e", default=24, help="Expiration hours")
@click.option("--file", "-f", type=click.Path(exists=True), help="Read code from file")
@click.pass_context
def publish(ctx, code, title, description, session_id, expires, file):
    """Publish code for sharing."""
    async def _publish():
        # Read code from file if specified
        actual_code = code
        if file:
            with open(file, 'r') as f:
                actual_code = f.read()

        async with OCTAVEClient(ctx.obj["base_url"]) as client:
            try:
                result = await client.publish_code(
                    actual_code, title, description, session_id, expires
                )

                print("Publication successful!")
                print(f"Share ID: {result.get('share_id')}")
                print(f"Share URL: {result.get('share_url')}")
                print(f"Expires at: {result.get('expires_at')}")

            except CLIError as e:
                print(f"Error: {e}")
                sys.exit(1)

    asyncio.run(_publish())


@cli.command()
@click.argument("share_id")
@click.option("--output", "-o", type=click.Path(), help="Save code to file")
@click.pass_context
def grabcode(ctx, share_id, output):
    """Extract code from published share."""
    async def _grabcode():
        async with OCTAVEClient(ctx.obj["base_url"]) as client:
            try:
                result = await client.grab_code(share_id)

                if output:
                    # Save to file
                    with open(output, 'w') as f:
                        f.write(result.get('code', ''))
                    print(f"Code saved to {output}")
                else:
                    # Display code
                    print(f"Title: {result.get('title', 'N/A')}")
                    if result.get('description'):
                        print(f"Description: {result['description']}")
                    print("\nCode:")
                    print(result.get('code', 'No code found'))

            except CLIError as e:
                print(f"Error: {e}")
                sys.exit(1)

    asyncio.run(_grabcode())


@cli.command()
@click.option("--limit", "-l", default=50, help="Maximum number of sessions to list")
@click.pass_context
def sessions(ctx, limit):
    """List active sessions."""
    async def _sessions():
        async with OCTAVEClient(ctx.obj["base_url"]) as client:
            try:
                sessions = await client.list_sessions(limit)

                if not sessions:
                    print("No sessions found")
                    return

                print("Active Sessions:")
                print("-" * 60)
                for session in sessions:
                    print(f"ID: {session.get('session_id', 'N/A')}")
                    print(f"Description: {session.get('description', 'N/A')}")
                    print(f"Runs: {session.get('run_count', 0)}")
                    print(f"Last Access: {session.get('last_accessed', 'N/A')}")
                    print("-" * 60)

            except CLIError as e:
                print(f"Error: {e}")
                sys.exit(1)

    asyncio.run(_sessions())


@cli.command()
@click.option("--max-age", "-a", default=24, help="Maximum age in hours")
@click.option("--sessions/--no-sessions", default=True, help="Cleanup sessions")
@click.option("--publications/--no-publications", default=True, help="Cleanup publications")
@click.option("--dry-run", is_flag=True, help="Show what would be cleaned without doing it")
@click.pass_context
def cleanup(ctx, max_age, sessions, publications, dry_run):
    """Clean up old resources."""
    async def _cleanup():
        async with OCTAVEClient(ctx.obj["base_url"]) as client:
            try:
                result = await client.cleanup(
                    max_age_hours=max_age,
                    cleanup_sessions=sessions,
                    cleanup_publications=publications,
                    dry_run=dry_run
                )

                action = "Would clean" if dry_run else "Cleaned"
                print(f"{action} up resources:")
                print(f"Sessions: {result.get('cleaned_sessions', 0)}")
                print(f"Publications: {result.get('cleaned_publications', 0)}")

            except CLIError as e:
                print(f"Error: {e}")
                sys.exit(1)

    asyncio.run(_cleanup())


if __name__ == "__main__":
    cli()