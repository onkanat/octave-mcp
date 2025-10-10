import argparse
import json
import os
import sys

import requests


def main():
    parser = argparse.ArgumentParser(description="Octave MCP CLI")
    subparsers = parser.add_subparsers(dest="command")

    run_parser = subparsers.add_parser("run", help="Octave kodu çalıştır")
    run_parser.add_argument("--code", required=True)
    run_parser.add_argument("--session_id", required=False)

    publish_parser = subparsers.add_parser("publish", help="Koddan HTML üret")
    publish_parser.add_argument("--code", required=True)
    publish_parser.add_argument("--session_id", required=False)

    grabcode_parser = subparsers.add_parser("grabcode", help="Session'dan kodu getir")
    grabcode_parser.add_argument("--session_id", required=True)

    args = parser.parse_args()
    base_url = os.environ.get("MCP_SERVER_URL", "http://127.0.0.1:8000")
    if args.command == "run":
        payload = {"code": args.code, "session_id": args.session_id}
        try:
            r = requests.post(f"{base_url}/run_octave", json=payload)
            print(json.dumps(r.json(), indent=2, ensure_ascii=False))
        except requests.exceptions.RequestException as e:
            print(
                f"Sunucuya bağlanılamadı: {base_url}. Uygulamayı başlattınız mı? Hata: {e}",
                file=sys.stderr,
            )
            sys.exit(1)
    elif args.command == "publish":
        payload = {"code": args.code, "session_id": args.session_id}
        try:
            r = requests.post(f"{base_url}/publish", json=payload)
            print(json.dumps(r.json(), indent=2, ensure_ascii=False))
        except requests.exceptions.RequestException as e:
            print(
                f"Sunucuya bağlanılamadı: {base_url}. Uygulamayı başlattınız mı? Hata: {e}",
                file=sys.stderr,
            )
            sys.exit(1)
    elif args.command == "grabcode":
        payload = {"session_id": args.session_id}
        try:
            r = requests.post(f"{base_url}/grabcode", json=payload)
            print(json.dumps(r.json(), indent=2, ensure_ascii=False))
        except requests.exceptions.RequestException as e:
            print(
                f"Sunucuya bağlanılamadı: {base_url}. Uygulamayı başlattınız mı? Hata: {e}",
                file=sys.stderr,
            )
            sys.exit(1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
