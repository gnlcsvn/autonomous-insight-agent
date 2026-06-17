#!/usr/bin/env python3
"""Idempotently add the /insights/ route to the Caddyfile, validate, reload.
Run with sudo:  sudo python3 scripts/install-caddy-route.py
Backs up the Caddyfile first and auto-restores if validation fails, so existing
routes are never left broken.
"""
import subprocess, sys, shutil, datetime, pathlib

CADDY = "/etc/caddy/Caddyfile"
MARK = "handle_path /insights/*"
ANCHOR = "# Default landing page"
BLOCK = """    handle_path /insights/* {
        root * /home/gianluca/projects/insights/public
        file_server
    }

    """

text = pathlib.Path(CADDY).read_text()
if MARK in text:
    print("Route already present; nothing to do.")
    sys.exit(0)
if ANCHOR not in text:
    print("ERROR: anchor not found in Caddyfile; aborting to be safe.", file=sys.stderr)
    sys.exit(1)

new = text.replace(ANCHOR, BLOCK + ANCHOR, 1)
bak = CADDY + ".bak." + datetime.datetime.now().strftime("%Y%m%d%H%M%S")
shutil.copy2(CADDY, bak)
pathlib.Path(CADDY).write_text(new)
print("Backup written:", bak)

v = subprocess.run(["caddy", "validate", "--config", CADDY, "--adapter", "caddyfile"],
                   capture_output=True, text=True)
print(v.stdout.strip())
if v.returncode != 0:
    print(v.stderr.strip(), file=sys.stderr)
    shutil.copy2(bak, CADDY)
    print("Validation FAILED; restored original Caddyfile.", file=sys.stderr)
    sys.exit(1)

r = subprocess.run(["systemctl", "reload", "caddy"], capture_output=True, text=True)
print((r.stdout + r.stderr).strip())
print("OK: /insights/ route added and Caddy reloaded." if r.returncode == 0 else "Reload failed.")
sys.exit(r.returncode)
