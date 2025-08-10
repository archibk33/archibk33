#!/usr/bin/env python3
import os, sys, json, base64, math, datetime as dt, re
from pathlib import Path
import urllib.request

API_BASE = os.getenv("API_BASE_URL", "https://api.wakatime.com/api/v1")
API_KEY  = os.getenv("WAKATIME_API_KEY")
TIME_RANGE = os.getenv("TIME_RANGE", "all_time")  # all_time | last_7_days | last_30_days | last_year
LANG_COUNT = int(os.getenv("LANG_COUNT", "10"))
IGNORED = set(os.getenv("IGNORED_LANGUAGES", "").split())

README_PATH = Path(os.getenv("TARGET_PATH", "README.md"))

MARK_START = "<!-- WAKATIME:START -->"
MARK_END   = "<!-- WAKATIME:END -->"

# Debug information
print(f"Debug: API_BASE = {API_BASE}")
print(f"Debug: API_KEY exists = {API_KEY is not None}")
print(f"Debug: API_KEY length = {len(API_KEY) if API_KEY else 0}")
print(f"Debug: API_KEY first 8 chars = {API_KEY[:8] if API_KEY else 'None'}...")
print(f"Debug: TIME_RANGE = {TIME_RANGE}")
print(f"Debug: LANG_COUNT = {LANG_COUNT}")

if not API_KEY:
    print("❌ ERROR: Missing WAKATIME_API_KEY", file=sys.stderr)
    print("   Please add WAKATIME_API_KEY to your GitHub Secrets", file=sys.stderr)
    sys.exit(1)

# Validate API key format (WakaTime API keys are typically 36 characters)
if len(API_KEY) < 20:
    print(f"⚠️  WARNING: API key seems too short ({len(API_KEY)} chars)")
    print("   WakaTime API keys are typically 36 characters long")
    print("   Make sure you're using the correct API key from https://wakatime.com/settings/api")

# Check if API_BASE is correct
if not API_BASE.startswith("https://api.wakatime.com"):
    print(f"⚠️  WARNING: API_BASE_URL should be https://api.wakatime.com/api/v1, got: {API_BASE}")

def http_get(url: str, headers: dict = None) -> dict:
    print(f"Debug: Making request to {url}")
    print(f"Debug: Headers keys = {list(headers.keys()) if headers else 'None'}")
    print(f"Debug: X-Api-Key length = {len(headers.get('X-Api-Key', '')) if headers else 0}")
    
    req = urllib.request.Request(url, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            print(f"Debug: Response status = {resp.status}")
            print(f"Debug: Response headers = {dict(resp.headers)}")
            data = resp.read().decode("utf-8")
            print(f"Debug: Response data length = {len(data)}")
            return json.loads(data)
    except urllib.error.HTTPError as e:
        print(f"Debug: HTTP Error {e.code}: {e.reason}")
        print(f"Debug: Response headers = {dict(e.headers)}")
        
        # Handle specific WakaTime API error codes
        if e.code == 401:
            print("❌ ERROR 401: Authentication failed!")
            print("   - Check if your WAKATIME_API_KEY is correct")
            print("   - Verify the API key is active at https://wakatime.com/settings/api")
            print("   - Make sure you're using the correct API key (not secret key)")
        elif e.code == 403:
            print("❌ ERROR 403: Forbidden - API key may not have required permissions")
        elif e.code == 429:
            print("❌ ERROR 429: Rate limited - too many requests")
        elif e.code == 500:
            print("❌ ERROR 500: WakaTime server error - try again later")
        
        # Try to read error response
        if e.fp:
            try:
                error_data = e.fp.read().decode("utf-8")
                print(f"Debug: Error response data = {error_data}")
                # Parse WakaTime error response
                try:
                    error_json = json.loads(error_data)
                    if 'errors' in error_json:
                        print(f"Debug: WakaTime errors = {error_json['errors']}")
                    elif 'error' in error_json:
                        print(f"Debug: WakaTime error = {error_json['error']}")
                except json.JSONDecodeError:
                    pass
            except Exception as read_error:
                print(f"Debug: Could not read error response: {read_error}")
        
        raise
    except Exception as e:
        print(f"Debug: Other error: {type(e).__name__}: {e}")
        raise

def human_dhms(total_seconds: int) -> str:
    m, s = divmod(int(total_seconds), 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
    parts = []
    if d: parts.append(f"{d}d")
    if h: parts.append(f"{h}h")
    if m: parts.append(f"{m}m")
    if not parts: parts.append(f"{s}s")
    return " ".join(parts)

# milder mapping; add more if хочешь
LANG_EMOJI = {
    "Java": "☕",
    "JavaScript": "🟨",
    "TypeScript": "🔷",
    "Python": "🐍",
    "CSS": "🎨",
    "HTML": "🧱",
    "Go": "🐹",
    "Rust": "🦀",
    "C": "🔧",
    "C++": "⚙️",
    "C#": "♯",
    "PHP": "🐘",
    "Markdown": "📝",
    "JSON": "📦",
    "YAML": "📑",
    "TOML": "📄",
    "PlantUML": "🌿",
    "HTTP Request": "📡",
    "Properties": "⚙️",
}

# --- fetch stats ---
# https://wakatime.com/developers#stats
# /users/current/stats/{range}
url = f"{API_BASE}/users/current/stats/{TIME_RANGE}?is_including_today=true"
headers = {
    "X-Api-Key": API_KEY,
    "User-Agent": "archibk33-waka-readme"
}

print(f"Debug: Full URL = {url}")
print(f"Debug: Headers keys = {list(headers.keys())}")
print(f"Debug: X-Api-Key length = {len(headers['X-Api-Key'])}")

data = http_get(url, headers)

stats = data.get("data", {})
grand = stats.get("grand_total", {}) or {}
total_text = grand.get("text") or human_dhms(grand.get("total_seconds", 0))
total_secs = int(grand.get("total_seconds", 0))
range_start = stats.get("range", {}).get("start") or stats.get("start")
range_end   = stats.get("range", {}).get("end")   or stats.get("end")

langs = [
    l for l in (stats.get("languages") or [])
    if l.get("name") not in IGNORED
]
# sort & cut
langs.sort(key=lambda x: float(x.get("total_seconds", 0)), reverse=True)
langs = langs[:LANG_COUNT]

def bar(pct: float, width: int = 26) -> str:
    # draw text bar using '▰' and '▱'
    filled = int(round(pct/100.0 * width))
    return "▰"*filled + "▱"*(width - filled)

def line_for_lang(l: dict) -> str:
    name = l.get("name", "Other")
    pct  = float(l.get("percent", 0))
    dur  = l.get("text") or human_dhms(l.get("total_seconds", 0))
    emoji = LANG_EMOJI.get(name, "💻")
    return f"{emoji} **{name}**  {dur}  `{bar(pct)}`  {pct:05.2f} %"

# header date text
def nice_date(s):
    if not s: return None
    try:
        return dt.datetime.fromisoformat(s.replace("Z", "+00:00")).strftime("%d %B %Y")
    except Exception:
        return s

from_txt = nice_date(range_start)
to_txt   = nice_date(range_end)
range_line = f"**From:** {from_txt}  —  **To:** {to_txt}" if from_txt and to_txt else f"**Range:** {TIME_RANGE.replace('_',' ').title()}"

# build markdown block
lines = []
lines.append("## ⏱️ My coding time")
lines.append("")
lines.append(f"{range_line}")
lines.append("")
lines.append(f"**Total Time:** {total_text}")
lines.append("")
for l in langs:
    lines.append(line_for_lang(l))

block = "\n".join(lines).rstrip() + "\n"

# insert/replace in README
if README_PATH.exists():
    content = README_PATH.read_text(encoding="utf-8")
else:
    content = "# archibk33\n\n"

if MARK_START in content and MARK_END in content:
    new_content = re.sub(
        rf"{re.escape(MARK_START)}.*?{re.escape(MARK_END)}",
        f"{MARK_START}\n\n{block}\n{MARK_END}",
        content,
        flags=re.DOTALL
    )
else:
    # append section at the end
    new_content = content.rstrip() + f"\n\n{MARK_START}\n\n{block}\n{MARK_END}\n"

if new_content != content:
    README_PATH.write_text(new_content, encoding="utf-8")
    print("README updated.")
else:
    print("No changes.")
