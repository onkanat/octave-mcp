"""
Modern FastAPI endpoints for octave-mcp service.
"""

import logging
from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse, JSONResponse

from config import get_settings
from exceptions import ExecutionError, NotFoundError, ServiceError, TimeoutError, ValidationError
from models.requests import CleanupRequest, GrabcodeRequest, PublishRequest, RunRequest
from models.responses import CleanupResponse, GrabcodeResponse, PublishResponse, RunResponse
from models.entities import ResourceLimits
from services.octave import OctaveService
from services.publish import PublishService
from services.session import SessionService

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Service dependencies
octave_service = OctaveService()
publish_service = PublishService()
session_service = SessionService()


def get_settings_dependency():
    """Dependency for settings."""
    return get_settings()


@router.post("/run", response_model=RunResponse)
async def run_octave_code(
    request: RunRequest, settings=Depends(get_settings_dependency)
) -> RunResponse:
    """
    Execute Octave/Python code with resource limits.

    Args:
        request: Code execution request
        settings: Application settings

    Returns:
        Execution result with output and metadata

    Raises:
        HTTPException: On validation or execution errors
    """
    try:
        # Derive resource limits (request overrides settings)
        limits = request.resource_limits or ResourceLimits(
            cpu_time_limit=settings.cpu_limit_seconds,
            memory_limit_mb=settings.memory_limit_mb,
            max_output_chars=settings.max_output_chars,
            max_image_size_bytes=settings.max_image_size_bytes,
            timeout=settings.timeout_seconds,
        )

        # Execute code using service
        run_result = await octave_service.execute_code(
            code=request.code,
            resource_limits=limits,
            session_id=request.session_id,
            include_image_paths=settings.is_vision_model,
        )

        # Update session if provided
        if request.session_id:
            try:
                await session_service.update_session(request.session_id, increment_run_count=True)
            except NotFoundError:
                # Session doesn't exist, create it
                await session_service.create_session(request.session_id)

        # Map domain Run to API RunResponse
        return RunResponse(
            success=run_result.success,
            stdout=run_result.stdout,
            stderr=run_result.stderr,
            exit_code=run_result.exit_code,
            runtime_seconds=run_result.runtime_seconds,
            # images: RunResponse ImageResult bekliyor; şimdilik boş liste döndürüyoruz.
            images=[],
            vectorization_warnings=None,
            error=None,
        )

    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"error": e.message, "code": e.error_code, "details": e.details},
        )
    except TimeoutError as e:
        raise HTTPException(
            status_code=status.HTTP_408_REQUEST_TIMEOUT,
            detail={"error": e.message, "code": e.error_code, "timeout": e.timeout_seconds},
        )
    except ExecutionError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": e.message,
                "code": e.error_code,
                "exit_code": e.exit_code,
                "stdout": e.stdout,
                "stderr": e.stderr,
            },
        )
    except ServiceError as e:
        logger.error(f"Service error in run endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": e.message, "code": e.error_code},
        )
    except Exception as e:
        logger.error(f"Unexpected error in run endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Internal server error", "code": "INTERNAL_ERROR"},
        )


@router.post("/publish", response_model=PublishResponse)
async def publish_run(
    request: PublishRequest, settings=Depends(get_settings_dependency)
) -> PublishResponse:
    """
    Publish a run result for sharing.

    Args:
        request: Publish request with run data
        settings: Application settings

    Returns:
        Publication details with share URL

    Raises:
        HTTPException: On validation or service errors
    """
    try:
        # Derive resource limits (request overrides settings)
        limits = request.resource_limits or ResourceLimits(
            cpu_time_limit=settings.cpu_limit_seconds,
            memory_limit_mb=settings.memory_limit_mb,
            max_output_chars=settings.max_output_chars,
            max_image_size_bytes=settings.max_image_size_bytes,
            timeout=settings.timeout_seconds,
        )

        # First execute the code if not already done
        run_result = await octave_service.execute_code(
            code=request.code,
            resource_limits=limits,
            session_id=request.session_id,
            include_image_paths=True,  # Always include images for publishing
        )

        # Publish the result
        publish_result = await publish_service.publish_run(
            run=run_result,
            title=None,
            description=None,
            expires_hours=24,
        )

        # PublishResponse modeli html_b64 vb bekliyor.
        # Dosya tabanlı yayınlama var; bu endpoint için basit bir özet üretelim.
        import base64

        html_content = f"<html><body><pre>{run_result.stdout}</pre></body></html>"
        html_b64 = base64.b64encode(html_content.encode("utf-8")).decode("utf-8")

        return PublishResponse(
            html_b64=html_b64,
            html_truncated=False,
            html_original_size=len(html_content.encode("utf-8")),
            publish_dir=str(settings.publish_dir),
            html_name=f"{publish_result.share_id}.html",
            images=[],
            warnings=[],
            error=None,
        )

    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"error": e.message, "code": e.error_code, "details": e.details},
        )
    except ServiceError as e:
        logger.error(f"Service error in publish endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": e.message, "code": e.error_code},
        )
    except Exception as e:
        logger.error(f"Unexpected error in publish endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Internal server error", "code": "INTERNAL_ERROR"},
        )


@router.get("/published/{share_id}")
async def get_published_run(share_id: str) -> JSONResponse:
    """
    Retrieve published run by share ID.

    Args:
        share_id: Share identifier

    Returns:
        Published run data and metadata

    Raises:
        HTTPException: If share not found or expired
    """
    try:
        result = await publish_service.get_published_run(share_id)
        return JSONResponse(content=result)

    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": e.message, "code": e.error_code},
        )
    except ServiceError as e:
        logger.error(f"Service error in get published endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": e.message, "code": e.error_code},
        )


@router.get("/published/{share_id}/images/{filename}")
async def get_published_image(share_id: str, filename: str) -> FileResponse:
    """
    Serve published image files.

    Args:
        share_id: Share identifier
        filename: Image filename

    Returns:
        Image file response

    Raises:
        HTTPException: If image not found
    """
    try:
        from pathlib import Path

        settings = get_settings()
        image_path = Path(settings.publish_dir) / share_id / "images" / filename

        if not image_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "Image not found", "code": "IMAGE_NOT_FOUND"},
            )

        return FileResponse(path=str(image_path), media_type="image/png", filename=filename)

    except Exception as e:
        logger.error(f"Error serving image {share_id}/{filename}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Internal server error", "code": "INTERNAL_ERROR"},
        )


@router.post("/grabcode", response_model=GrabcodeResponse)
async def grab_published_code(request: GrabcodeRequest) -> GrabcodeResponse:
    """
    Extract code from published run.

    Args:
        request: Grabcode request with share ID

    Returns:
        Code content and metadata

    Raises:
        HTTPException: If share not found or expired
    """
    try:
        # Get published run data
        result = await publish_service.get_published_run(request.share_id)
        run_data = result["run"]

        import base64

        code_text = run_data.get("code", "")
        code_b64 = base64.b64encode(code_text.encode("utf-8")).decode("utf-8")

        return GrabcodeResponse(
            code=code_text,
            code_b64=code_b64,
            line_count=len(code_text.splitlines()) if code_text else 0,
            warnings=[],
        )

    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": e.message, "code": e.error_code},
        )
    except ServiceError as e:
        logger.error(f"Service error in grabcode endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": e.message, "code": e.error_code},
        )


@router.post("/cleanup", response_model=CleanupResponse)
async def cleanup_resources(request: CleanupRequest) -> CleanupResponse:
    """
    Clean up old resources (sessions, publications, etc.).

    Args:
        request: Cleanup request with age settings

    Returns:
        Cleanup operation results

    Raises:
        HTTPException: On service errors
    """
    try:
        # Şu an yalnızca session temizliği uygulanıyor; run dosyaları için 0 döneriz.
        # max_age: saat/dakika alanlarından türet.
        age_hours = (
            request.max_age_hours
            if request.max_age_hours is not None
            else (request.max_age_days * 24 if request.max_age_days is not None else 24)
        )

        deleted_sessions = 0
        if not request.dry_run:
            deleted_sessions = await session_service.cleanup_old_sessions(max_age_hours=age_hours)

        return CleanupResponse(
            deleted_runs=0,
            deleted_sessions=deleted_sessions,
            dry_run=request.dry_run,
            errors=[],
        )

    except ServiceError as e:
        logger.error(f"Service error in cleanup endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": e.message, "code": e.error_code},
        )
    except Exception as e:
        logger.error(f"Unexpected error in cleanup endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Internal server error", "code": "INTERNAL_ERROR"},
        )


@router.get("/sessions", response_model=List[Dict])
async def list_sessions(limit: int = 50, offset: int = 0) -> List[Dict]:
    """
    List active sessions.

    Args:
        limit: Maximum number of results
        offset: Number of results to skip

    Returns:
        List of session summaries

    Raises:
        HTTPException: On service errors
    """
    try:
        return await session_service.list_sessions(limit=limit, offset=offset)

    except ServiceError as e:
        logger.error(f"Service error in list sessions endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": e.message, "code": e.error_code},
        )


@router.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "service": "octave-mcp"}
