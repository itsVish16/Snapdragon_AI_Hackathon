import sys
import os
import argparse
import webbrowser
import threading
import time

try:
    import uvicorn
except ImportError:
    print("Error: uvicorn is not installed. Run `pip install -r requirements.txt`.")
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="SnapFlow AI: Ambient Dictation for Snapdragon HP PCs")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host address (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind (default: 8000)")
    parser.add_argument("--no-browser", action="store_true", help="Do not open browser automatically")
    args = parser.parse_args()

    url = f"http://{args.host}:{args.port}"

    print("=" * 65)
    print("  ⚡ SnapFlow AI — Ambient Dictation & Smart Copilot")
    print("  Target: Snapdragon® X-Powered HP PCs (Hexagon™ NPU 45 TOPS)")
    print("=" * 65)
    print(f"  Web Dashboard: {url}")
    print("  WebSocket:     ws://127.0.0.1:8000/ws/dictate")
    print("  Press Ctrl+C to terminate.")
    print("=" * 65)

    if not args.no_browser:
        def open_browser():
            time.sleep(1.2)
            webbrowser.open(url)
        threading.Thread(target=open_browser, daemon=True).start()

    uvicorn.run("snapflow.web.app:app", host=args.host, port=args.port, log_level="info")


if __name__ == "__main__":
    main()
