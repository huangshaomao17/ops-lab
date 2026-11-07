#!/usr/bin/env python3
import json
import socket
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone

CHECKS = []

def ok(name, detail=""):
    CHECKS.append({"name": name, "status": "ok", "detail": detail})

def fail(name, detail=""):
    CHECKS.append({"name": name, "status": "fail", "detail": detail})

def check_http(url="http://127.0.0.1:8080/"):
    try:
        with urllib.request.urlopen(url, timeout=3) as r:
            body = r.read().decode("utf-8", errors="replace").strip()
            if r.status == 200 and "ops-lab OK" in body:
                ok("http", f"{r.status} {body}")
            else:
                fail("http", f"{r.status} {body}")
    except Exception as e:
        fail("http", str(e))

def check_tcp(name, host, port):
    try:
        with socket.create_connection((host, port), timeout=3):
            ok(name, f"{host}:{port} open")
    except Exception as e:
        fail(name, str(e))

def check_containers():
    try:
        out = subprocess.check_output(
            ["docker", "compose", "ps", "--format", "json"],
            cwd="/home/%s/ops-lab/compose" % __import__("os").environ.get("USER", ""),
            text=True,
        )
        lines = [json.loads(x) for x in out.strip().splitlines() if x.strip()]
        bad = [c.get("Name") or c.get("Service") for c in lines if c.get("State") != "running"]
        if not lines:
            fail("containers", "no services found")
        elif bad:
            fail("containers", "not running: " + ", ".join(bad))
        else:
            ok("containers", f"{len(lines)} running")
    except Exception as e:
        fail("containers", str(e))

def main():
    check_containers()
    check_http()
    check_tcp("mysql", "127.0.0.1", 3306)
    check_tcp("redis", "127.0.0.1", 6379)
    report = {
        "time": datetime.now(timezone.utc).isoformat(),
        "checks": CHECKS,
        "ok": all(c["status"] == "ok" for c in CHECKS),
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    sys.exit(0 if report["ok"] else 1)

if __name__ == "__main__":
    main()
