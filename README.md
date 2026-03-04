# 🔇 ANTI Hat Sound

External Roblox tool that automatically mutes annoying sounds from specific hats and accessories using memory manipulation. No executor needed.

## How It Works

- Attaches to the running Roblox process externally via [robloxmemoryapi](https://pypi.org/project/robloxmemoryapi/)
- Fetches version-specific memory offsets from [imtheo.lol/Offsets](https://imtheo.lol/Offsets)
- Walks the game's instance tree to find `Sound` objects inside targeted hats
- Sets their `Volume` to `0` directly in memory
- Continuously monitors for newly spawned sounds (e.g. when joining servers or equipping items)

## Blocked Hats

| Hat | Sounds |
|-----|--------|
| 🎩 WitchesBrewHat | Laugh, Laugh2, Laugh3 |
| 🎵 Harmonica | Harm1, Harm2, Harm3, Harm4 |
| 🐔 Chicken Suit | Quack1, Quack2, Quack3, Quack4 |
| 🥤 Bloxycolahat | Quack1, Quack2, Quack3 |

## Setup

```bash
py -m pip install robloxmemoryapi
```

## Usage

1. **Launch Roblox** and open a game (or leave it on the home screen — the script will wait)
2. **Run the script:**
   ```bash
   python anti_audio.py
   ```
3. That's it. Sounds from the blocked hats are automatically muted.

```
  ╔══════════════════════════════════════════╗
  ║     3itx  ANTI  Hat  Sound  Muter       ║
  ╚══════════════════════════════════════════╝

  ✓ Version: version-760d064d05424689
  ✓ Offsets loaded
  ✓ Attached  (PID 76696)
  ✓ In-game  (PlaceId: 7041939546)

  • Monitoring for hat & accessory sounds …

    🔇  Workspace.Player.WitchesBrewHat.Handle.Laugh  →  http://www.roblox.com/asset/?id=62777535
    🔇  Workspace.Player.Bloxycolahat.Handle.Quack1   →  http://www.roblox.com/asset/?id=24113544
```

Press `Ctrl+C` to stop.

## Requirements

- **Windows** (uses direct syscalls for memory access)
- **Python 3.11+**
- **Roblox** running

## Adding More Hats

Edit the `BLOCKED_HATS` set in `anti_audio.py`:

```python
BLOCKED_HATS = {
    "WitchesBrewHat",
    "Harmonica",
    "Chicken Suit",
    "Bloxycolahat",
    "YourNewHatName",  # ← add here
}
```

## Disclaimer

This tool is for personal/educational use. Use at your own risk. Not affiliated with Roblox Corporation.

## Credits

- [robloxmemoryapi](https://github.com/nicholasxuu/robloxmemoryapi) for the memory reading library
- [imtheo.lol](https://imtheo.lol/Offsets) for version-specific offsets
