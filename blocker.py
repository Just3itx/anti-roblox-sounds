"""
3itx ANTI Hat Sound — External Roblox Hat/Accessory Sound Muter
Automatically mutes sounds from hats and accessories using robloxmemoryapi.
"""

import json
import re
import subprocess
import sys
import time
import urllib.request
import urllib.error

from robloxmemoryapi import RobloxGameClient

# ── Config ───────────────────────────────────────────────────────────────────
SCAN_INTERVAL = 2
OFFSETS_URL = "https://imtheo.lol/Offsets"


BLOCKED_HATS = {
    "WitchesBrewHat",
    "Harmonica",
    "Chicken Suit",
    "Bloxycolahat",
}
_ID_RE = re.compile(r"\d+")


# ── Terminal UI helpers ──────────────────────────────────────────────────────

def banner():
    print()
    print("Thanks for using 3itx ANTI Hat Sound!")
    print()


def status(msg, symbol="•"):
    print(f"  {symbol} {msg}", flush=True)


def success(msg):
    status(msg, "✓")


def warn(msg):
    status(msg, "!")


def muted_line(name, sound_id):
    print(f"    🔇  {name}  →  {sound_id}", flush=True)


# ── Version & Offsets ────────────────────────────────────────────────────────

def get_roblox_version() -> str | None:
    try:
        out = subprocess.check_output(
            ["wmic", "process", "where", "name='RobloxPlayerBeta.exe'",
             "get", "ExecutablePath", "/value"],
            text=True, stderr=subprocess.DEVNULL,
        )
        for line in out.splitlines():
            if "ExecutablePath=" in line:
                for part in line.split("=", 1)[1].replace("/", "\\").split("\\"):
                    if part.lower().startswith("version-"):
                        return part
    except Exception:
        pass
    return None


def fetch_offsets(version: str) -> dict | None:
    url = f"{OFFSETS_URL}/{version}/Offsets.json"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        resp = urllib.request.urlopen(req, timeout=10)
        data = json.loads(resp.read().decode())
        if isinstance(data, dict) and "error" in data:
            return None
        if isinstance(data, dict) and "Offsets" in data:
            return data["Offsets"]
    except Exception:
        pass
    return None


# ── Raw Sound Reader (version-specific offsets) ──────────────────────────────

class SoundRW:
    """Read SoundId and write Volume using raw memory offsets."""

    def __init__(self, mem, offsets: dict):
        self.mem = mem
        self._sound = offsets["Sound"]

    def read_sound_id(self, addr: int) -> str:
        return self.mem.read_string(addr, self._sound["SoundId"])

    def read_volume(self, addr: int) -> float:
        return self.mem.read_float(addr, self._sound["Volume"])

    def write_volume(self, addr: int, value: float):
        self.mem.write_float(addr + self._sound["Volume"], value)


# ── Detection helpers ────────────────────────────────────────────────────────

def is_in_blocked_hat(inst) -> bool:
    """Walk parents to check if this Sound is inside one of the blocked hats."""
    try:
        cur = inst.Parent
        for _ in range(10):
            if cur is None:
                return False
            name = cur.Name
            if name in BLOCKED_HATS:
                return True
            cn = cur.ClassName
            if cn in ("Workspace", "DataModel"):
                return False
            cur = cur.Parent
    except Exception:
        pass
    return False


# ── Scan ─────────────────────────────────────────────────────────────────────

def scan_and_mute(srw: SoundRW, root, muted: set) -> int:
    count = 0
    try:
        descendants = root.GetDescendants()
    except Exception:
        return 0

    for inst in descendants:
        try:
            if inst.ClassName != "Sound":
                continue
        except Exception:
            continue

        if not is_in_blocked_hat(inst):
            continue

        try:
            full_name = inst.GetFullName()
        except Exception:
            full_name = f"sound_{inst.raw_address:#x}"

        if full_name in muted:
            continue

        addr = inst.raw_address
        try:
            vol = srw.read_volume(addr)
            if vol > 0:
                srw.write_volume(addr, 0.0)
                sid = ""
                try:
                    sid = srw.read_sound_id(addr)
                except Exception:
                    pass
                muted_line(full_name, sid)
                muted.add(full_name)
                count += 1
        except Exception:
            pass

    return count


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    banner()

    # Version
    status("Detecting Roblox version …")
    version = get_roblox_version()
    if not version:
        warn("Roblox not found — make sure it's running.")
        sys.exit(1)
    success(f"Version: {version}")

    # Offsets
    status("Loading offsets …")
    offsets = fetch_offsets(version)
    if not offsets:
        warn(f"Offsets unavailable for {version}")
        sys.exit(1)
    success("Offsets loaded")

    # Attach
    status("Attaching to Roblox …")
    client = RobloxGameClient(allow_write=True)
    if client.failed:
        warn("Failed to attach — is Roblox running?")
        sys.exit(1)

    game = client.DataModel
    srw = SoundRW(client.memory_module, offsets)
    success(f"Attached  (PID {client.pid})")

    # Wait for game
    if game.is_lua_app():
        status("Waiting for you to join a game …")
        while game.is_lua_app():
            time.sleep(1)
    success(f"In-game  (PlaceId: {game.PlaceId})")

    print()
    status("Monitoring for hat & accessory sounds …")
    print()

    # Refresh callback
    muted: set[str] = set()

    def on_refresh(_dm):
        nonlocal muted
        muted.clear()

    game.bind_to_refresh(on_refresh)

    # Scan loop
    try:
        while True:
            if game.is_lua_app():
                time.sleep(SCAN_INTERVAL)
                continue

            try:
                ws = game.Workspace
                if ws:
                    scan_and_mute(srw, ws, muted)
            except Exception:
                pass

            try:
                ps = game.Players
                if ps:
                    scan_and_mute(srw, ps, muted)
            except Exception:
                pass

            time.sleep(SCAN_INTERVAL)

    except KeyboardInterrupt:
        pass
    finally:
        client.close()
        print()
        print("  Thank you for using 3itx ANTI Hat Sound. Enjoy!")
        print()


if __name__ == "__main__":
    main()
