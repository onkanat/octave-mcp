"""
Modern async Octave execution service with enhanced error handling.
"""

import asyncio
import logging
import shutil
import tempfile
import time
from pathlib import Path
from typing import Dict, List, Optional

from config import get_settings
from exceptions import (
    ExecutionError,
    ServiceError,
    TimeoutError,
    ValidationError as MCPValidationError,
)
from models.entities import ResourceLimits, Run
from utils.vectorization import analyze_vectorization

logger = logging.getLogger(__name__)


class OctaveService:
    """Async service for Octave/Python code execution."""

    def __init__(self):
        self.settings = get_settings()
        self.octave_bin = shutil.which("octave") or shutil.which("octave-cli")

    async def execute_code(
        self,
        code: str,
        resource_limits: ResourceLimits,
        session_id: Optional[str] = None,
        include_image_paths: bool = False,
    ) -> Run:
        """Execute code with resource limits and return execution result."""
        start_time = time.time()
        run_id = f"run_{int(start_time * 1000000)}"

        try:
            # Validate and clean code
            cleaned_code = await self._clean_code(code)

            if self.settings.octave_mode == "octave" and self.octave_bin:
                result = await self._execute_octave(cleaned_code, resource_limits, run_id)
            else:
                result = await self._execute_python(cleaned_code, resource_limits, run_id)

            # Add vectorization warnings for Python code
            if self.settings.octave_mode == "python":
                try:
                    result["vectorization_warnings"] = analyze_vectorization(code)
                except Exception as e:
                    logger.warning(f"Vectorization analysis failed: {e}")

            runtime = time.time() - start_time

            return Run(
                run_id=run_id,
                session_id=session_id,
                code=code,
                stdout=result.get("stdout", ""),
                stderr=result.get("stderr", ""),
                exit_code=result.get("exit_code", -1),
                runtime_seconds=round(runtime, 3),
                resource_limits=resource_limits,
                images=result.get("images", []),
            )

        except Exception as e:
            runtime = time.time() - start_time
            logger.error(f"Code execution failed for run {run_id}: {e}", exc_info=True)

            if isinstance(e, (ExecutionError, TimeoutError, ServiceError)):
                raise
            else:
                raise ServiceError(
                    f"Unexpected execution error: {str(e)}",
                    "octave_service",
                    {"run_id": run_id, "runtime": runtime},
                )

    async def _clean_code(self, code: str) -> str:
        """Clean and validate code."""
        if not code.strip():
            raise MCPValidationError("Code cannot be empty", "code")

        lines = code.split("\n")
        cleaned_lines = []

        for line in lines:
            stripped = line.strip()
            if not stripped or stripped.startswith("%") or stripped.startswith("%%"):
                continue
            cleaned_lines.append(line)

        cleaned = "\n".join(cleaned_lines)

        if self.settings.octave_mode == "octave":
            await self._validate_octave_syntax(cleaned)

        return cleaned

    async def _validate_octave_syntax(self, code: str) -> None:
        """Validate Octave syntax."""
        if not code.strip():
            raise MCPValidationError("No executable code found", "code")

        # Basic syntax checks
        if code.count("(") != code.count(")"):
            raise MCPValidationError("Unmatched parentheses in code", "code")

        if code.count("[") != code.count("]"):
            raise MCPValidationError("Unmatched square brackets in code", "code")

        if code.count("'") % 2 != 0:
            raise MCPValidationError("Unmatched single quotes in code", "code")

    async def _execute_octave(self, code: str, limits: ResourceLimits, run_id: str) -> Dict:
        """Execute code using Octave."""
        temp_dir = None
        try:
            temp_dir = Path(tempfile.mkdtemp(prefix=f"octave_{run_id}_"))
            script_path = temp_dir / "script.m"
            wrapper_path = temp_dir / "wrapper.m"

            # Write script file
            with open(script_path, "w") as f:
                f.write(code)

            # Create wrapper for figure capture
            base_path = temp_dir / "fig"
            wrapper_code = self._create_octave_wrapper(script_path, base_path)

            with open(wrapper_path, "w") as f:
                f.write(wrapper_code)

            # Execute with timeout
            return await self._run_subprocess(
                [self.octave_bin, "--quiet", "--no-gui", str(wrapper_path)], limits, temp_dir
            )

        finally:
            if temp_dir and temp_dir.exists():
                await self._cleanup_directory(temp_dir)

    async def _execute_python(self, code: str, limits: ResourceLimits, run_id: str) -> Dict:
        """Execute code using Python."""
        temp_file = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".py", delete=False, prefix=f"python_{run_id}_"
            ) as f:
                f.write(code)
                temp_file = Path(f.name)

            return await self._run_subprocess(
                ["python3", str(temp_file)], limits, temp_file.parent
            )

        finally:
            if temp_file and temp_file.exists():
                try:
                    temp_file.unlink()
                except Exception as e:
                    logger.warning(f"Failed to cleanup temp file {temp_file}: {e}")

    def _create_octave_wrapper(self, script_path: Path, base_path: Path) -> str:
        """Create Octave wrapper code for figure capture."""
        fig_width = self.settings.fig_width
        fig_height = self.settings.fig_height
        return f"""
try
    run('{script_path.as_posix()}');
    figs = get(0,'children');
    base = '{base_path.as_posix()}';
    set(0,'defaultfigureposition', [100, 100, {fig_width}, {fig_height}]);
    for i = 1:length(figs)
        fname = sprintf('%s_%d.png', base, i);
        print(figs(i), fname, '-dpng', '-r150');
    endfor
catch err
    disp(lasterror().message);
    exit(1);
end_try_catch
"""

    async def _run_subprocess(
        self, cmd: List[str], limits: ResourceLimits, work_dir: Path
    ) -> Dict:
        """Run subprocess with resource limits."""
        try:
            # Create subprocess with limits
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=work_dir,
                preexec_fn=self._create_preexec_fn(limits),
            )

            # Wait with timeout
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), timeout=limits.timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                raise TimeoutError(f"Execution timeout after {limits.timeout}s", limits.timeout)

            stdout_str = stdout.decode("utf-8", errors="replace")
            stderr_str = stderr.decode("utf-8", errors="replace")

            # Apply output limits
            if len(stdout_str) > limits.max_output_chars:
                stdout_str = stdout_str[: limits.max_output_chars] + "\n...[truncated]"

            if len(stderr_str) > limits.max_output_chars:
                stderr_str = stderr_str[: limits.max_output_chars] + "\n...[truncated]"

            # Collect images
            images = await self._collect_images(work_dir)

            return {
                "stdout": stdout_str,
                "stderr": stderr_str,
                "exit_code": process.returncode or 0,
                "images": images,
            }

        except Exception as e:
            if isinstance(e, TimeoutError):
                raise
            raise ServiceError(f"Subprocess execution failed: {e}", "subprocess")

    def _create_preexec_fn(self, limits: ResourceLimits):
        """Create preexec function for resource limiting."""

        def preexec():
            try:
                import resource

                if limits.cpu_time_limit:
                    resource.setrlimit(
                        resource.RLIMIT_CPU, (limits.cpu_time_limit, limits.cpu_time_limit)
                    )

                if limits.memory_limit_mb:
                    mem_bytes = limits.memory_limit_mb * 1024 * 1024
                    resource.setrlimit(resource.RLIMIT_AS, (mem_bytes, mem_bytes))

            except (ImportError, AttributeError, OSError):
                # Resource limiting not available on this platform
                pass

        return preexec

    async def _collect_images(self, work_dir: Path) -> List[str]:
        """Collect generated image files."""
        images = []
        try:
            if not work_dir.exists():
                return images

            for file_path in work_dir.iterdir():
                if file_path.name.startswith("fig") and file_path.suffix == ".png":
                    if self.settings.is_vision_model:
                        images.append(str(file_path))
                    else:
                        images.append(file_path.name)

        except Exception as e:
            logger.warning(f"Failed to collect images from {work_dir}: {e}")

        return sorted(images)

    async def _cleanup_directory(self, directory: Path) -> None:
        """Safely cleanup temporary directory."""
        try:
            if directory.exists():
                shutil.rmtree(directory)
                logger.debug(f"Cleaned up directory: {directory}")
        except Exception as e:
            logger.warning(f"Failed to cleanup directory {directory}: {e}")
