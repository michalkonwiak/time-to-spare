"""Run the API and Vite locally; terminate both when either exits or on Ctrl+C."""

import os
import signal
import subprocess
import sys
import time
from contextlib import suppress
from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    api_port = os.environ.get("TTS_API_PORT", "8000")
    web_port = os.environ.get("TTS_WEB_PORT", "5173")
    environment = {**os.environ, "API_TARGET": f"http://127.0.0.1:{api_port}"}
    commands = [
        (
            [
                sys.executable,
                "-m",
                "uvicorn",
                "time_to_spare.http.app:create_app",
                "--factory",
                "--host",
                "127.0.0.1",
                "--port",
                api_port,
            ],
            root,
        ),
        (["npm", "run", "dev", "--", "--port", web_port], root / "apps/web"),
    ]
    processes: list[subprocess.Popen[bytes]] = []
    try:
        for command, cwd in commands:
            processes.append(
                subprocess.Popen(command, cwd=cwd, env=environment, start_new_session=True)
            )
        while all(process.poll() is None for process in processes):
            time.sleep(0.2)
        raise SystemExit(next(p.returncode for p in processes if p.returncode is not None))
    except KeyboardInterrupt:
        pass
    finally:
        for process in processes:
            # npm starts a child process; terminate the group to avoid orphaned Vite servers.
            with suppress(ProcessLookupError):
                os.killpg(process.pid, signal.SIGTERM)
        for process in processes:
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()


if __name__ == "__main__":
    main()
