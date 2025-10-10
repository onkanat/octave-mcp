import os
import sys
import threading

from fastapi.testclient import TestClient

from api.endpoints import app

sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "../../src")))


def publish_code(client, session_id, code):
    payload = {"session_id": session_id, "code": code}
    return client.post("/publish", json=payload)


def grab_code(client, session_id, result_dict):
    payload = {"session_id": session_id}
    resp = client.post("/grabcode", json=payload)
    result_dict[session_id] = resp.json().get("code")


def test_publish_grabcode_concurrency():
    client = TestClient(app)
    session_codes = {f"sess{i}": f"print('code{i}')" for i in range(5)}
    threads = []
    # Her session için publish işlemini başlat
    for session_id, code in session_codes.items():
        t = threading.Thread(target=publish_code, args=(client, session_id, code))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()

    # Her session için grabcode işlemini başlat
    result_dict = {}
    threads = []
    for session_id in session_codes:
        t = threading.Thread(target=grab_code, args=(client, session_id, result_dict))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()

    # Her session_id için doğru kodun döndüğünü kontrol et
    for session_id, code in session_codes.items():
        assert result_dict[session_id] == code
