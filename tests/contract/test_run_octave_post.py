import os
import sys

from fastapi.testclient import TestClient

SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src"))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from app import app  # noqa: E402


def test_run_octave_contract():
    # OctaveService'i sahte sonuç dönecek şekilde patch et
    from api import endpoints

    async def fake_execute_code(*args, **kwargs):
        class DummyRun:
            def __init__(self):
                self.run_id = "r1"
                self.session_id = kwargs.get("session_id")
                self.stdout = "ok"
                self.stderr = ""
                self.exit_code = 0
                self.runtime_seconds = 0.01
                self.images = []

            @property
            def success(self):
                return True

        return DummyRun()

    endpoints.octave_service.execute_code = fake_execute_code  # type: ignore[attr-defined]

    client = TestClient(app)
    payload = {"code": "print(1+1)", "session_id": "testsess"}
    response = client.post("/api/v1/run", json=payload)
    assert response.status_code == 200
    data = response.json()
    # Contract: success, stdout, stderr, exit_code, runtime_seconds
    for key in ["success", "stdout", "stderr", "exit_code", "runtime_seconds"]:
        assert key in data
