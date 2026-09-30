#!/usr/bin/env python3
"""Safely hold a local dev server for external browser QA."""

from __future__ import annotations

import argparse
import http.client
import os
import signal
import socket
import subprocess
import sys
import threading
import time
from urllib.parse import urlsplit


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True, help="Local HTTP readiness URL, e.g. http://127.0.0.1:5173/")
    parser.add_argument("--timeout", type=float, default=45, help="Startup timeout in seconds")
    parser.add_argument("--grace", type=float, default=4, help="Shutdown grace period in seconds")
    parser.add_argument("command", nargs=argparse.REMAINDER, help="Server argv after --")
    args = parser.parse_args()
    if args.command and args.command[0] == "--":
        args.command = args.command[1:]
    if not args.command:
        parser.error("provide the server command after --")
    if args.timeout <= 0 or args.grace <= 0:
        parser.error("--timeout and --grace must be positive")
    parsed = urlsplit(args.url)
    if parsed.scheme != "http" or parsed.hostname not in {"localhost", "127.0.0.1", "::1"}:
        parser.error("--url must use http:// and a loopback host")
    if parsed.username or parsed.password or parsed.fragment:
        parser.error("credentials and URL fragments are not allowed in --url")
    args.parsed_url = parsed
    return args


def probe(url, timeout: float) -> tuple[bool, int | None]:
    parsed = urlsplit(url)
    port = parsed.port or 80
    path = parsed.path or "/"
    if parsed.query:
        path += "?" + parsed.query
    connection = http.client.HTTPConnection(parsed.hostname, port, timeout=timeout)
    try:
        connection.request("GET", path, headers={"Connection": "close"})
        response = connection.getresponse()
        status = response.status
        response.close()
        return True, status
    except (OSError, http.client.HTTPException, TimeoutError):
        return False, None
    finally:
        connection.close()


def port_is_open(host: str, port: int, timeout: float = 1) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def group_exists(pgid: int) -> bool:
    try:
        os.killpg(pgid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def stop_owned_group(process: subprocess.Popen, grace: float) -> None:
    pgid = process.pid  # start_new_session=True makes this the private process-group id.
    if group_exists(pgid):
        try:
            os.killpg(pgid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        deadline = time.monotonic() + grace
        while group_exists(pgid) and time.monotonic() < deadline:
            time.sleep(0.1)
        if group_exists(pgid):
            try:
                os.killpg(pgid, signal.SIGKILL)
            except ProcessLookupError:
                pass
    try:
        process.wait(timeout=grace + 1)
    except subprocess.TimeoutExpired:
        pass


def main() -> int:
    args = parse_args()
    parsed = args.parsed_url
    host = parsed.hostname
    port = parsed.port or 80
    reachable, status = probe(args.url, timeout=1)
    if reachable:
        print(f"Reusing existing local HTTP service (status {status}) at {args.url}; it will not be stopped.")
        return 0
    if port_is_open(host, port):
        print(f"Port {port} is occupied but readiness URL did not answer; refusing to start or stop anything.", file=sys.stderr)
        return 2

    try:
        process = subprocess.Popen(args.command, start_new_session=True)
    except OSError as exc:
        print(f"Could not start server: {exc}", file=sys.stderr)
        return 1

    stop_requested = threading.Event()
    previous_sigterm = signal.signal(signal.SIGTERM, lambda *_: stop_requested.set())
    try:
        deadline = time.monotonic() + args.timeout
        while time.monotonic() < deadline and not stop_requested.is_set():
            if process.poll() is not None:
                print(f"Server command exited early with status {process.returncode}.", file=sys.stderr)
                return process.returncode or 1
            reachable, status = probe(args.url, timeout=1)
            if reachable and status is not None and 200 <= status < 400:
                print(f"Started owned server (pid {process.pid}) at {args.url}.", flush=True)
                break
            time.sleep(0.25)
        else:
            print(f"Server did not become ready at {args.url} within {args.timeout:g}s.", file=sys.stderr)
            return 1

        while not stop_requested.wait(0.25):
            if process.poll() is not None:
                return process.returncode or 0
        return 0
    except KeyboardInterrupt:
        return 0
    finally:
        signal.signal(signal.SIGTERM, previous_sigterm)
        stop_owned_group(process, args.grace)


if __name__ == "__main__":
    raise SystemExit(main())
