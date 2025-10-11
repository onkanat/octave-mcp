"""
Modern async publish service for sharing octave execution results.
"""

import json
import logging
import secrets
import shutil
import time
from pathlib import Path
from typing import Dict, List, Optional

from config import get_settings
from exceptions import NotFoundError, ServiceError, ValidationError
from models.entities import PublishShare, Run
from utils.security import sanitize_filename

logger = logging.getLogger(__name__)


class PublishService:
    """Async service for publishing and managing shared execution results."""

    def __init__(self):
        self.settings = get_settings()
        self.publish_dir = Path(self.settings.publish_dir)
        self.publish_dir.mkdir(parents=True, exist_ok=True)

    async def publish_run(
        self,
        run: Run,
        title: Optional[str] = None,
        description: Optional[str] = None,
        expires_hours: int = 24,
    ) -> PublishShare:
        """
        Publish a run result for sharing.

        Args:
            run: The execution run to publish
            title: Optional title for the publication
            description: Optional description
            expires_hours: Hours until expiration

        Returns:
            Publish instance with share URL

        Raises:
            ValidationError: If run data is invalid
            ServiceError: If publish operation fails
        """
        try:
            # Generate unique share ID
            share_id = await self._generate_share_id()
            publish_path = self.publish_dir / share_id

            # Create publication directory
            await self._create_publish_directory(publish_path)

            # Calculate expiration
            expires_at = time.time() + (expires_hours * 3600)

            # Create publish record
            publish = PublishShare(
                share_id=share_id,
                run_id=run.run_id,
                title=title or f"Run {run.run_id}",
                description=description,
                expires_at=expires_at,
                created_at=time.time(),
                view_count=0,
            )

            # Save run data
            await self._save_run_data(publish_path, run)

            # Copy image files if they exist
            await self._copy_images(run.images, publish_path)

            # Save publish metadata
            await self._save_publish_metadata(publish_path, publish)

            logger.info(f"Published run {run.run_id} as {share_id}")
            return publish

        except Exception as e:
            logger.error(f"Failed to publish run {run.run_id}: {e}", exc_info=True)
            if isinstance(e, (ValidationError, ServiceError)):
                raise
            raise ServiceError(f"Publish operation failed: {e}", "publish_service")

    async def get_published_run(self, share_id: str) -> Dict:
        """
        Retrieve published run by share ID.

        Args:
            share_id: The share identifier

        Returns:
            Dict containing run data and metadata

        Raises:
            NotFoundError: If share ID not found or expired
            ServiceError: If retrieval fails
        """
        try:
            publish_path = self.publish_dir / share_id

            if not publish_path.exists():
                raise NotFoundError(f"Share ID {share_id} not found", "share", share_id)

            # Load publish metadata
            publish = await self._load_publish_metadata(publish_path)

            # Check expiration
            if time.time() > publish.expires_at:
                await self._cleanup_expired_publish(publish_path)
                raise NotFoundError(f"Share ID {share_id} has expired", "share", share_id)

            # Load run data
            run_data = await self._load_run_data(publish_path)

            # Update view count
            publish.view_count += 1
            await self._save_publish_metadata(publish_path, publish)

            # Get image URLs
            image_urls = await self._get_image_urls(publish_path, share_id)

            return {
                "publish": publish,
                "run": run_data,
                "images": image_urls,
                "share_url": f"{self.settings.base_url}/published/{share_id}",
            }

        except Exception as e:
            if isinstance(e, NotFoundError):
                raise
            logger.error(f"Failed to get published run {share_id}: {e}", exc_info=True)
            raise ServiceError(f"Retrieval failed: {e}", "publish_service")

    async def list_published_runs(self, limit: int = 50, offset: int = 0) -> List[Dict]:
        """
        List published runs with pagination.

        Args:
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            List of published run summaries
        """
        try:
            results = []

            # Get all publish directories
            publish_dirs = [
                d for d in self.publish_dir.iterdir() if d.is_dir() and len(d.name) == 16
            ]

            # Sort by creation time (newest first)
            publish_dirs.sort(key=lambda d: d.stat().st_ctime, reverse=True)

            # Apply pagination
            paginated_dirs = publish_dirs[offset : offset + limit]

            for publish_path in paginated_dirs:
                try:
                    publish = await self._load_publish_metadata(publish_path)

                    # Skip expired publications
                    if time.time() > publish.expires_at:
                        continue

                    results.append(
                        {
                            "share_id": publish.share_id,
                            "title": publish.title,
                            "description": publish.description,
                            "created_at": publish.created_at,
                            "expires_at": publish.expires_at,
                            "view_count": publish.view_count,
                            "share_url": f"{self.settings.base_url}/published/{publish.share_id}",
                        }
                    )

                except Exception as e:
                    logger.warning(f"Failed to load publish {publish_path.name}: {e}")
                    continue

            return results

        except Exception as e:
            logger.error(f"Failed to list published runs: {e}", exc_info=True)
            raise ServiceError(f"List operation failed: {e}", "publish_service")

    async def cleanup_expired_publications(self) -> int:
        """
        Clean up expired publications.

        Returns:
            Number of publications cleaned up
        """
        try:
            cleaned_count = 0
            current_time = time.time()

            for publish_path in self.publish_dir.iterdir():
                if not publish_path.is_dir():
                    continue

                try:
                    publish = await self._load_publish_metadata(publish_path)

                    if current_time > publish.expires_at:
                        await self._cleanup_expired_publish(publish_path)
                        cleaned_count += 1
                        logger.info(f"Cleaned up expired publication {publish.share_id}")

                except Exception as e:
                    logger.warning(f"Failed to check publication {publish_path.name}: {e}")
                    continue

            return cleaned_count

        except Exception as e:
            logger.error(f"Cleanup operation failed: {e}", exc_info=True)
            raise ServiceError(f"Cleanup failed: {e}", "publish_service")

    async def _generate_share_id(self) -> str:
        """Generate unique share ID."""
        while True:
            share_id = secrets.token_urlsafe(12)[:16]
            if not (self.publish_dir / share_id).exists():
                return share_id

    async def _create_publish_directory(self, publish_path: Path) -> None:
        """Create publication directory structure."""
        try:
            publish_path.mkdir(parents=True, exist_ok=True)
            (publish_path / "images").mkdir(exist_ok=True)
        except Exception as e:
            raise ServiceError(f"Failed to create publish directory: {e}", "directory_creation")

    async def _save_run_data(self, publish_path: Path, run: Run) -> None:
        """Save run data to publication directory."""
        run_file = publish_path / "run.json"
        try:
            with open(run_file, "w") as f:
                json.dump(run.model_dump(), f, indent=2, default=str)
        except Exception as e:
            raise ServiceError(f"Failed to save run data: {e}", "file_write")

    async def _copy_images(self, image_paths: List[str], publish_path: Path) -> None:
        """Copy image files to publication directory."""
        if not image_paths:
            return

        images_dir = publish_path / "images"

        for image_path in image_paths:
            try:
                source_path = Path(image_path)
                if source_path.exists():
                    filename = sanitize_filename(source_path.name)
                    dest_path = images_dir / filename
                    shutil.copy2(source_path, dest_path)
                    logger.debug(f"Copied image {source_path} to {dest_path}")
            except Exception as e:
                logger.warning(f"Failed to copy image {image_path}: {e}")

    async def _save_publish_metadata(self, publish_path: Path, publish: PublishShare) -> None:
        """Save publication metadata."""
        metadata_file = publish_path / "metadata.json"
        try:
            with open(metadata_file, "w") as f:
                json.dump(publish.model_dump(), f, indent=2, default=str)
        except Exception as e:
            raise ServiceError(f"Failed to save metadata: {e}", "file_write")

    async def _load_publish_metadata(self, publish_path: Path) -> PublishShare:
        """Load publication metadata."""
        metadata_file = publish_path / "metadata.json"
        try:
            with open(metadata_file, "r") as f:
                data = json.load(f)
                return PublishShare(**data)
        except Exception as e:
            raise ServiceError(f"Failed to load metadata: {e}", "file_read")

    async def _load_run_data(self, publish_path: Path) -> Dict:
        """Load run data from publication directory."""
        run_file = publish_path / "run.json"
        try:
            with open(run_file, "r") as f:
                return json.load(f)
        except Exception as e:
            raise ServiceError(f"Failed to load run data: {e}", "file_read")

    async def _get_image_urls(self, publish_path: Path, share_id: str) -> List[str]:
        """Get image URLs for published run."""
        images_dir = publish_path / "images"
        image_urls = []

        if not images_dir.exists():
            return image_urls

        try:
            for image_file in images_dir.iterdir():
                if image_file.is_file() and image_file.suffix.lower() in [".png", ".jpg", ".jpeg"]:
                    url = f"{self.settings.base_url}/published/{share_id}/images/{image_file.name}"
                    image_urls.append(url)
        except Exception as e:
            logger.warning(f"Failed to get image URLs: {e}")

        return sorted(image_urls)

    async def _cleanup_expired_publish(self, publish_path: Path) -> None:
        """Remove expired publication directory."""
        try:
            if publish_path.exists():
                shutil.rmtree(publish_path)
        except Exception as e:
            logger.error(f"Failed to cleanup expired publish {publish_path}: {e}")
