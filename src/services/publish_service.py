import os
import shutil
from base64 import b64encode
from typing import Dict

from utils.config import get_env_str

from .store import session_code_store


class PublishService:
    def publish(self, code: str, session_id: str | None, options: dict | None = None) -> Dict:
        if session_id:
            session_code_store[session_id] = code

        runs_root = get_env_str("MCP_RUNS_ROOT", os.path.abspath("runs")) or os.path.abspath("runs")
        session_folder = session_id or "anonymous"
        publish_dir = os.path.join(runs_root, session_folder, "published")
        os.makedirs(publish_dir, exist_ok=True)

        # Hazır görselleri (varsa) topla: runs_root altındaki en yeni octave_run_*
        # klasöründen fig_*.png
        images_relpaths = []
        try:
            candidates = []
            for name in os.listdir(runs_root):
                if name.startswith("octave_run_"):
                    p = os.path.join(runs_root, name)
                    if os.path.isdir(p):
                        try:
                            candidates.append((os.path.getmtime(p), p))
                        except Exception:
                            continue
            candidates.sort(reverse=True)
            latest_dir = candidates[0][1] if candidates else None
            if latest_dir:
                imgs_dir = os.path.join(publish_dir, "images")
                os.makedirs(imgs_dir, exist_ok=True)
                for fname in sorted(os.listdir(latest_dir)):
                    if fname.startswith("fig") and fname.endswith(".png"):
                        src = os.path.join(latest_dir, fname)
                        dst = os.path.join(imgs_dir, fname)
                        try:
                            shutil.copy2(src, dst)
                            images_relpaths.append(f"images/{fname}")
                        except Exception:
                            continue
        except Exception:
            pass

        # Basit HTML şablonu: kod + varsa görsel galeri
        gallery_html = "\n".join(
            [
                f"<div><img src='{rp}' alt='{rp}' /></div>"
                for rp in images_relpaths
            ]
        )
        html = (
            "<html><body>"
            "<h2>Published Code</h2>"
            f"<pre class='code'>{code}</pre>"
            + ("<h3>Figures</h3>" + gallery_html if images_relpaths else "")
            + "</body></html>"
        )
        html_bytes = html.encode("utf-8")
        html_b64 = b64encode(html_bytes).decode("utf-8")

        html_name = "script_publish.html"
        html_path = os.path.join(publish_dir, html_name)
        try:
            with open(html_path, "wb") as f:
                f.write(html_bytes)
        except Exception:
            # Disk yazımı başarısız olsa bile API sözleşmesini koru
            pass

        return {
            "html_b64": html_b64,
            "html_truncated": False,
            "html_original_size": len(html_bytes),
            "publish_dir": publish_dir,
            "html_name": html_name,
            "images": images_relpaths,
            "warnings": [],
        }
