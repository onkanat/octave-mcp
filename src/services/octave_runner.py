import os
import shutil
import subprocess
import tempfile
import time
from typing import Dict

from utils.logging import logger


class OctaveRunner:
    def __init__(self):
        self.mode = os.getenv("OCTAVE_RUNNER_MODE", "python").lower()
        self.octave_bin = shutil.which("octave") or shutil.which("octave-cli")
        # Vision modeli mi? Değilse görüntüleri dosya sisteminde tut, sadece isim dön
        self.is_vision = os.getenv("MCP_IS_VISION_MODEL", "false").lower() in ("1", "true", "yes")
        # Figür boyutları (varsayılan 620x480)
        try:
            self.fig_width = int(os.getenv("OCTAVE_FIG_WIDTH", "620"))
            self.fig_height = int(os.getenv("OCTAVE_FIG_HEIGHT", "480"))
        except Exception:
            self.fig_width, self.fig_height = 620, 480

    def clean_octave_code(self, code: str) -> str:
        """Octave kodunu temizle: comment'leri ve boş satırları kaldır."""
        lines = code.split("\n")
        cleaned_lines = []

        for line in lines:
            # Boş satırları atla
            stripped = line.strip()
            if not stripped:
                continue

            # Sadece comment olan satırları atla (% ile başlayan)
            if stripped.startswith("%"):
                continue

            # %% ile başlayan section comment'leri de atla
            if stripped.startswith("%%"):
                continue

            # Normal kod satırlarını koru (inline comment'ler dahil)
            cleaned_lines.append(line)

        return "\n".join(cleaned_lines)

    def validate_octave_syntax(self, code: str) -> tuple[bool, str]:
        """Basit Octave syntax kontrolü yap."""
        # Boş kod kontrolü
        if not code.strip():
            return False, "Error: No executable code found"

        # Temel parantez kontrolü
        if code.count("(") != code.count(")"):
            return False, "Error: Unmatched parentheses in code"

        if code.count("[") != code.count("]"):
            return False, "Error: Unmatched square brackets in code"

        # Tek tırnak kontrolü (string literals)
        single_quotes = code.count("'")
        if single_quotes % 2 != 0:
            return False, "Error: Unmatched single quotes in code"

        return True, ""

    def normalize_path_for_octave(self, path: str) -> str:
        """Path'i Octave için güvenli hale getir."""
        # Windows backslash'leri forward slash'e çevir
        normalized = path.replace("\\", "/")
        # Octave string'inde tek tırnak escape et
        normalized = normalized.replace("'", "''")
        return normalized

    def run_code(
        self,
        code: str,
        resource_limits,
        include_image_paths: bool | None = None,
    ) -> Dict:
        start = time.time()
        stdout = ""
        stderr = ""
        exit_code = -1

        # Önce kodu temizle ve validate et
        cleaned_code = self.clean_octave_code(code)
        
        if self.mode == "octave":
            is_valid, validation_error = self.validate_octave_syntax(cleaned_code)
            
            if not is_valid:
                return {
                    "success": False,
                    "stdout": "",
                    "stderr": validation_error,
                    "exit_code": -1,
                    "runtime_seconds": 0.0,
                    "images": [],
                }
            
            # Temizlenmiş kodu kullan
            code_to_run = cleaned_code
        else:
            # Python modunda da comment temizle ama validation yapma
            code_to_run = cleaned_code

        logger.debug(f"Running code (length: {len(code_to_run)} chars)")
        logger.debug(f"Code preview: {code_to_run[:100]}...")

        script_path = None
        tmp_dir = None
        timeout = getattr(resource_limits, "timeout", 10) or 10  # Timeout'u erken tanımla
        try:
            if self.mode == "octave" and self.octave_bin:
                # Octave modunda .m dosyası olarak çalıştır ve figürleri PNG olarak
                # yakalamaya çalış
                tmp_dir = tempfile.mkdtemp(prefix="octave_run_")
                script_path = os.path.join(tmp_dir, "script.m")
                wrapper_path = os.path.join(tmp_dir, "wrapper.m")
                with open(script_path, "w") as f:
                    f.write(code_to_run)
                # wrapper: kullanıcı kodunu çalıştır, mevcut figürleri PNG olarak kaydet
                base = os.path.join(tmp_dir, "fig")

                # Path güvenliği için normalize et (Windows/Unix uyumluluğu)
                safe_script_path = self.normalize_path_for_octave(script_path)
                safe_base = self.normalize_path_for_octave(base)

                # Güvenli wrapper kod oluştur - her komut noktalı virgül ile bitsin
                wrapper_lines = [
                    "try",
                    f"run('{safe_script_path}')",
                    "figs = get(0,'children')",
                    f"base = '{safe_base}'",
                    f"set(0,'defaultfigureposition', [100, 100, {self.fig_width}, "
                    f"{self.fig_height}])",
                    "for i = 1:length(figs)",
                    "  fname = sprintf('%s_%d.png', base, i)",
                    "  print(figs(i), fname, '-dpng', '-r150')",
                    "endfor",
                    "catch err",
                    "  disp(lasterror().message)",
                    "  exit(1)",
                    "end_try_catch",
                ]

                # Tek satıra çevir, noktalı virgül ile ayır
                wrapper_code = "; ".join(wrapper_lines) + ";"

                logger.debug(f"Generated wrapper code: {wrapper_code[:200]}...")

                with open(wrapper_path, "w") as f:
                    f.write(wrapper_code)
                cmd = [self.octave_bin, "--quiet", "--no-gui", wrapper_path]
                used_octave = True
            else:
                # Varsayılan: Python ile çalıştır (mevcut testlerle uyumlu)
                with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                    f.write(code_to_run)
                    script_path = f.name
                cmd = ["python3", script_path]
                used_octave = False

            logger.debug(f"Running command: {' '.join(cmd)}")
            preexec = None
            try:
                preexec = resource_limits.preexec_fn()
            except Exception:
                preexec = None
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                preexec_fn=preexec,
            )
            stdout = proc.stdout
            stderr = proc.stderr
            exit_code = proc.returncode

            # Octave başarısız olursa Python'a geri düş
            if used_octave and exit_code != 0:
                try:
                    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                        f.write(code_to_run)
                        script_path = f.name
                    cmd = ["python3", script_path]
                    proc = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=timeout,
                        preexec_fn=preexec,
                    )
                    stdout = proc.stdout
                    stderr = proc.stderr
                    exit_code = proc.returncode
                except Exception:
                    # Geri düşüş de başarısızsa, ilk hata korunur
                    pass
        except subprocess.TimeoutExpired as e:
            stderr = f"TimeoutExpired: Execution took longer than {timeout}s: {str(e)}"
            exit_code = -1
            logger.warning(f"Process timeout after {timeout}s")
        except FileNotFoundError as e:
            stderr = f"Command not found: {str(e)}. Check if Octave is installed and in PATH."
            exit_code = -1
            logger.error(f"FileNotFoundError: {str(e)}")
        except PermissionError as e:
            stderr = f"Permission denied: {str(e)}"
            exit_code = -1
            logger.error(f"PermissionError: {str(e)}")
        except Exception as e:
            stderr = f"Unexpected error: {str(e)}"
            exit_code = -1
            logger.error(f"Unexpected error in run_code: {str(e)}", exc_info=True)
        finally:
            # Geçici dosyaları temizle
            cleanup_paths = [script_path]
            if tmp_dir and os.path.isdir(tmp_dir):
                try:
                    # tmp_dir içindeki tüm dosyaları sil
                    shutil.rmtree(tmp_dir)
                    logger.debug(f"Cleaned up temporary directory: {tmp_dir}")
                except Exception as cleanup_error:
                    logger.warning(f"Failed to cleanup temp dir {tmp_dir}: {cleanup_error}")
            else:
                # Sadece script dosyasını sil
                for path in cleanup_paths:
                    try:
                        if path and os.path.exists(path):
                            os.unlink(path)
                            logger.debug(f"Cleaned up file: {path}")
                    except Exception as cleanup_error:
                        logger.warning(f"Failed to cleanup {path}: {cleanup_error}")

        runtime = round(time.time() - start, 3)

        # Görselleri topla (octave modunda çalışmışsa)
        images = []
        try:
            images_dir = (
                tmp_dir
                if self.mode == "octave"
                else (os.path.dirname(script_path) if script_path else None)
            )
            if images_dir and os.path.isdir(images_dir):
                for name in sorted(os.listdir(images_dir)):
                    if name.startswith("fig") and name.endswith(".png"):
                        show_path = self.is_vision or bool(include_image_paths)
                        if show_path:
                            images.append({"name": name, "path": os.path.join(images_dir, name)})
                        else:
                            # Vision değilse sadece isim döndür (UI’yi şişirmemek için)
                            images.append({"name": name})
        except Exception:
            pass

        # Basit çıktı kısıtlama
        max_chars = getattr(resource_limits, "max_output_chars", None)
        if max_chars and isinstance(max_chars, int):
            if stdout and len(stdout) > max_chars:
                stdout = stdout[:max_chars] + "\n...[truncated]"
            if stderr and len(stderr) > max_chars:
                stderr = stderr[:max_chars] + "\n...[truncated]"

        return {
            "success": exit_code == 0,
            "stdout": stdout,
            "stderr": stderr,
            "exit_code": exit_code,
            "runtime_seconds": runtime,
            "images": images,
        }
