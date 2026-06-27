from __future__ import annotations

import os
import socket

import uvicorn


def first_free_port(start: int = 8000) -> int:
    port = int(os.getenv("PORT", str(start)))
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            if sock.connect_ex(("127.0.0.1", port)) != 0:
                return port
        print(f"Port {port} is already in use. Trying {port + 1}...")
        port += 1


if __name__ == "__main__":
    selected_port = first_free_port()
    print(f"Starting MedGuard backend on http://127.0.0.1:{selected_port}")
    print(f"Swagger docs: http://127.0.0.1:{selected_port}/docs")
    uvicorn.run("app.main:app", host="127.0.0.1", port=selected_port, reload=True)
