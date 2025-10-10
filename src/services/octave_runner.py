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
        self.is_vision = os.getenv(
            "MCP_IS_VISION_MODEL", "false").lower() in (
            "1", "true", "yes")
        # Figür boyutları (varsayılan 620x480)
        try:
            self.fig_width = int(os.getenv("OCTAVE_FIG_WIDTH", "620"))
            self.fig_height = int(os.getenv("OCTAVE_FIG_HEIGHT", "480"))
        except Exception:
            self.fig_width, self.fig_height = 620, 480

    def run_code(
            self,
            code: str,
            resource_limits,
            include_image_paths: bool | None = None) -> Dict:
        start = time.time()
        stdout = ""
        stderr = ""
        exit_code = -1

        script_path = None
        tmp_dir = None
        try:
            if self.mode == "octave" and self.octave_bin:
                # Octave modunda .m dosyası olarak çalıştır ve figürleri PNG olarak
                # yakalamaya çalış
                tmp_dir = tempfile.mkdtemp(prefix="octave_run_")
                script_path = os.path.join(tmp_dir, "script.m")
                wrapper_path = os.path.join(tmp_dir, "wrapper.m")
                with open(script_path, "w") as f:
                    f.write(code)
                # wrapper: kullanıcı kodunu çalıştır, mevcut figürleri PNG olarak kaydet
                base = os.path.join(tmp_dir, "fig")
                wrapper_code = (
                    "try;"
                    f"run('{script_path}');"
                    "figs = get(0,'children');"
                    f"base='{base}';"
                    f"set(0,'defaultfigureposition',[100, 100, {self.fig_width}, {self.fig_height}]);"
                    "for i = 1:length(figs);"
                    " fname = sprintf('%s_%d.png', base, i);"
                    " print(figs(i), fname, '-dpng', '-r150');"
                    " end;"
                    "catch err; disp(lasterror().message); exit(1); end;"
                )
                with open(wrapper_path, "w") as f:
                    f.write(wrapper_code)
                cmd = [self.octave_bin, "--quiet", "--no-gui", wrapper_path]
                used_octave = True
            else:
                # Varsayılan: Python ile çalıştır (mevcut testlerle uyumlu)
                with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                    f.write(code)
                    script_path = f.name
                cmd = ["python3", script_path]
                used_octave = False

            logger.debug(f"Running command: {' '.join(cmd)}")
            timeout = getattr(resource_limits, "timeout", 10) or 10
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
                        f.write(code)
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
            stderr = f"TimeoutExpired: {str(e)}"
            exit_code = -1
        except Exception as e:
            stderr = str(e)
            exit_code = -1
        finally:
            try:
                if script_path and os.path.exists(script_path):
                    os.unlink(script_path)
            except Exception:
                pass

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
                            images.append(
                                {"name": name, "path": os.path.join(images_dir, name)})
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
