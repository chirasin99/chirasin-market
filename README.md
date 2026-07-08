IQ Option Trend Paint Arrow Bot (demo-first)
=========================================

Summary
-------
Minimal Python bot that connects to IQ Option (demo) and acts on the EMA arrow signals you provided. The project defaults to simulation mode for safety; enable real demo trades by setting `LIVE_MODE=1` in your environment and supplying credentials.

Setup
-----
1. Create a virtualenv and activate it.

```bash
python -m venv .venv
.\.venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Copy `config.example.json` to `config.json` and fill your `email` and `password`. Alternatively set `IQ_EMAIL` and `IQ_PASSWORD` env vars.

Usage
-----
Simulation (default):

```bash
python bot_iqoption.py
```

Enable demo-mode trading (still NOT real-money):

Windows PowerShell:
```powershell
$env:IQ_EMAIL = "you@example.com"
$env:IQ_PASSWORD = "yourpassword"
$env:LIVE_MODE = "1"
python bot_iqoption.py
```

Warnings
--------
- Trading carries risk. Test thoroughly on demo accounts before enabling any live or real-money automation.
- This script uses an unofficial API client and is provided as example code only.
