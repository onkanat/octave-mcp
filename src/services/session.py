"""
Modern async session service for persistent execution contexts.
"""

import json
import logging
import shutil
import time
from pathlib import Path
from typing import Dict, List, Optional

from config import get_settings
from exceptions import NotFoundError, ServiceError, ValidationError
from models.entities import Session

logger = logging.getLogger(__name__)


class SessionService:
    """Async service for managing persistent execution sessions."""

    def __init__(self):
        self.settings = get_settings()
        self.session_dir = Path("/tmp/octave_sessions")
        self.session_dir.mkdir(parents=True, exist_ok=True)

    async def create_session(
        self, session_id: Optional[str] = None, description: Optional[str] = None
    ) -> Session:
        """
        Create a new execution session.

        Args:
            session_id: Optional custom session ID
            description: Optional session description

        Returns:
            Created session instance

        Raises:
            ValidationError: If session_id is invalid
            ServiceError: If session creation fails
        """
        try:
            if session_id is None:
                session_id = self._generate_session_id()

            # Validate session ID
            if not self._is_valid_session_id(session_id):
                raise ValidationError(f"Invalid session ID: {session_id}", "session_id")

            session_path = self.session_dir / session_id

            # Check if session already exists
            if session_path.exists():
                raise ValidationError(f"Session {session_id} already exists", "session_id")

            # Create session directory
            await self._create_session_directory(session_path)

            # Create session object
            session = Session(
                session_id=session_id,
                work_dir=session_path,
                description=description or f"Session {session_id}",
                created_at=time.time(),
                last_accessed=time.time(),
                run_count=0,
                session_dir=str(session_path),
            )

            # Save session metadata
            await self._save_session_metadata(session_path, session)

            logger.info(f"Created session {session_id}")
            return session

        except Exception as e:
            if isinstance(e, (ValidationError, ServiceError)):
                raise
            logger.error(f"Failed to create session {session_id}: {e}", exc_info=True)
            raise ServiceError(f"Session creation failed: {e}", "session_service")

    async def get_session(self, session_id: str) -> Session:
        """
        Retrieve session by ID.

        Args:
            session_id: Session identifier

        Returns:
            Session instance

        Raises:
            NotFoundError: If session not found
            ServiceError: If retrieval fails
        """
        try:
            session_path = self.session_dir / session_id

            if not session_path.exists():
                raise NotFoundError(f"Session {session_id} not found", "session", session_id)

            # Load session metadata
            session = await self._load_session_metadata(session_path)

            # Update last accessed time
            session.last_accessed = time.time()
            await self._save_session_metadata(session_path, session)

            return session

        except Exception as e:
            if isinstance(e, NotFoundError):
                raise
            logger.error(f"Failed to get session {session_id}: {e}", exc_info=True)
            raise ServiceError(f"Session retrieval failed: {e}", "session_service")

    async def list_sessions(self, limit: int = 50, offset: int = 0) -> List[Dict]:
        """
        List sessions with pagination.

        Args:
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            List of session summaries
        """
        try:
            results = []

            # Get all session directories
            session_dirs = [
                d
                for d in self.session_dir.iterdir()
                if d.is_dir() and self._is_valid_session_id(d.name)
            ]

            # Sort by last accessed time (newest first)
            session_dirs.sort(key=lambda d: d.stat().st_mtime, reverse=True)

            # Apply pagination
            paginated_dirs = session_dirs[offset : offset + limit]

            for session_path in paginated_dirs:
                try:
                    session = await self._load_session_metadata(session_path)

                    results.append(
                        {
                            "session_id": session.session_id,
                            "description": session.description,
                            "created_at": session.created_at,
                            "last_accessed": session.last_accessed,
                            "run_count": session.run_count,
                        }
                    )

                except Exception as e:
                    logger.warning(f"Failed to load session {session_path.name}: {e}")
                    continue

            return results

        except Exception as e:
            logger.error(f"Failed to list sessions: {e}", exc_info=True)
            raise ServiceError(f"List operation failed: {e}", "session_service")

    async def update_session(
        self, session_id: str, description: Optional[str] = None, increment_run_count: bool = False
    ) -> Session:
        """
        Update session metadata.

        Args:
            session_id: Session identifier
            description: New description
            increment_run_count: Whether to increment run count

        Returns:
            Updated session instance

        Raises:
            NotFoundError: If session not found
            ServiceError: If update fails
        """
        try:
            session_path = self.session_dir / session_id

            if not session_path.exists():
                raise NotFoundError(f"Session {session_id} not found", "session", session_id)

            # Load current session
            session = await self._load_session_metadata(session_path)

            # Update fields
            if description is not None:
                session.description = description

            if increment_run_count:
                session.run_count += 1

            session.last_accessed = time.time()

            # Save updated session
            await self._save_session_metadata(session_path, session)

            logger.debug(f"Updated session {session_id}")
            return session

        except Exception as e:
            if isinstance(e, NotFoundError):
                raise
            logger.error(f"Failed to update session {session_id}: {e}", exc_info=True)
            raise ServiceError(f"Session update failed: {e}", "session_service")

    async def delete_session(self, session_id: str) -> None:
        """
        Delete session and all associated data.

        Args:
            session_id: Session identifier

        Raises:
            NotFoundError: If session not found
            ServiceError: If deletion fails
        """
        try:
            session_path = self.session_dir / session_id

            if not session_path.exists():
                raise NotFoundError(f"Session {session_id} not found", "session", session_id)

            # Remove session directory and all contents
            shutil.rmtree(session_path)

            logger.info(f"Deleted session {session_id}")

        except Exception as e:
            if isinstance(e, NotFoundError):
                raise
            logger.error(f"Failed to delete session {session_id}: {e}", exc_info=True)
            raise ServiceError(f"Session deletion failed: {e}", "session_service")

    async def cleanup_old_sessions(self, max_age_hours: int = 24) -> int:
        """
        Clean up old sessions.

        Args:
            max_age_hours: Maximum session age in hours

        Returns:
            Number of sessions cleaned up
        """
        try:
            cleaned_count = 0
            cutoff_time = time.time() - (max_age_hours * 3600)

            for session_path in self.session_dir.iterdir():
                if not session_path.is_dir():
                    continue

                try:
                    session = await self._load_session_metadata(session_path)

                    if session.last_accessed < cutoff_time:
                        shutil.rmtree(session_path)
                        cleaned_count += 1
                        logger.info(f"Cleaned up old session {session.session_id}")

                except Exception as e:
                    logger.warning(f"Failed to check session {session_path.name}: {e}")
                    continue

            return cleaned_count

        except Exception as e:
            logger.error(f"Session cleanup failed: {e}", exc_info=True)
            raise ServiceError(f"Cleanup failed: {e}", "session_service")

    def _generate_session_id(self) -> str:
        """Generate unique session ID."""
        import uuid

        return str(uuid.uuid4())[:8]

    def _is_valid_session_id(self, session_id: str) -> bool:
        """Validate session ID format."""
        if not session_id or len(session_id) < 4 or len(session_id) > 32:
            return False

        # Check for safe characters only
        import re

        return bool(re.match(r"^[a-zA-Z0-9_-]+$", session_id))

    async def _create_session_directory(self, session_path: Path) -> None:
        """Create session directory structure."""
        try:
            session_path.mkdir(parents=True, exist_ok=True)
            (session_path / "runs").mkdir(exist_ok=True)
            (session_path / "workspace").mkdir(exist_ok=True)
        except Exception as e:
            raise ServiceError(f"Failed to create session directory: {e}", "directory_creation")

    async def _save_session_metadata(self, session_path: Path, session: Session) -> None:
        """Save session metadata."""
        metadata_file = session_path / "session.json"
        try:
            with open(metadata_file, "w") as f:
                json.dump(session.model_dump(), f, indent=2, default=str)
        except Exception as e:
            raise ServiceError(f"Failed to save session metadata: {e}", "file_write")

    async def _load_session_metadata(self, session_path: Path) -> Session:
        """Load session metadata."""
        metadata_file = session_path / "session.json"
        try:
            with open(metadata_file, "r") as f:
                data = json.load(f)
                return Session(**data)
        except Exception as e:
            raise ServiceError(f"Failed to load session metadata: {e}", "file_read")
