#!/usr/bin/env python3
# FORCE UPDATE: Script updated to use 'today' as default time range
# This comment forces GitHub Actions to re-evaluate the script
import os, sys, json, base64, math, datetime as dt, re
from pathlib import Path
import urllib.request

API_BASE = os.getenv("API_BASE_URL", "https://api.wakatime.com/api/v1")
API_KEY  = os.getenv("WAKATIME_API_KEY")
# --- config ---
TIME_RANGE = os.getenv("TIME_RANGE", "today")  # today, last_7_days, last_30_days, all_time
LANG_COUNT = int(os.getenv("LANG_COUNT", "10"))
IGNORED = set(os.getenv("IGNORED_LANGUAGES", "YAML JSON TOML").split())

README_PATH = Path(os.getenv("TARGET_PATH", "README.md"))

MARK_START = "<!-- WAKATIME:START -->"
MARK_END   = "<!-- WAKATIME:END -->"

# ===== DETAILED DEBUG INFORMATION =====
print("=" * 50)
print("🔍 WAKATIME API DEBUG INFORMATION")
print("=" * 50)

print(f"Debug: API_BASE = {API_BASE}")
print(f"Debug: API_KEY exists = {API_KEY is not None}")
print(f"Debug: API_KEY length = {len(API_KEY) if API_KEY else 0}")
print(f"Debug: API_KEY first 8 chars = {API_KEY[:8] if API_KEY else 'None'}...")
print(f"Debug: API_KEY last 4 chars = ...{API_KEY[-4:] if API_KEY and len(API_KEY) >= 4 else 'None'}")
print(f"Debug: TIME_RANGE = {TIME_RANGE}")
print(f"Debug: LANG_COUNT = {LANG_COUNT}")
print(f"Debug: IGNORED_LANGUAGES = {IGNORED}")
print(f"Debug: TARGET_PATH = {README_PATH}")

# Check environment variables
print("\n🔍 Environment Variables Check:")
for key, value in os.environ.items():
    if 'WAKATIME' in key or 'API' in key:
        if 'KEY' in key:
            print(f"  {key} = {'*' * min(len(value), 8)}... (length: {len(value)})")
        else:
            print(f"  {key} = {value}")

if not API_KEY:
    print("\n❌ ERROR: Missing WAKATIME_API_KEY")
    print("   Please add WAKATIME_API_KEY to your GitHub Secrets")
    sys.exit(1)

# Validate API key format (WakaTime API keys are typically 36 characters)
if len(API_KEY) < 20:
    print(f"\n⚠️  WARNING: API key seems too short ({len(API_KEY)} chars)")
    print("   WakaTime API keys are typically 36 characters long")
    print("   Make sure you're using the correct API key from https://wakatime.com/settings/api")
elif len(API_KEY) > 50:
    print(f"\n⚠️  WARNING: API key seems too long ({len(API_KEY)} chars)")
    print("   WakaTime API keys are typically 36 characters long")

# Check if API_BASE is correct
if not API_BASE.startswith("https://api.wakatime.com"):
    print(f"\n⚠️  WARNING: API_BASE_URL should be https://api.wakatime.com/api/v1, got: {API_BASE}")

print("\n" + "=" * 50)

def http_get(url: str, headers: dict = None) -> dict:
    print(f"\n🌐 Making HTTP request:")
    print(f"  URL: {url}")
    print(f"  Headers keys: {list(headers.keys()) if headers else 'None'}")
    print(f"  X-Api-Key length: {len(headers.get('X-Api-Key', '')) if headers else 0}")
    print(f"  User-Agent: {headers.get('User-Agent', 'None') if headers else 'None'}")
    
    req = urllib.request.Request(url, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            print(f"✅ Response received:")
            print(f"  Status: {resp.status}")
            print(f"  Headers: {dict(resp.headers)}")
            data = resp.read().decode("utf-8")
            print(f"  Data length: {len(data)} characters")
            return json.loads(data)
    except urllib.error.HTTPError as e:
        print(f"\n❌ HTTP Error {e.code}: {e.reason}")
        print(f"  URL: {e.url}")
        print(f"  Response headers: {dict(e.headers)}")
        
        # Handle specific WakaTime API error codes
        if e.code == 401:
            print("\n🔐 ERROR 401: Authentication failed!")
            print("   Possible causes:")
            print("   - WAKATIME_API_KEY is incorrect or expired")
            print("   - API key is not active at https://wakatime.com/settings/api")
            print("   - You're using the wrong type of key (secret key instead of API key)")
            print("   - API key has been revoked or deleted")
        elif e.code == 403:
            print("\n🚫 ERROR 403: Forbidden")
            print("   - API key may not have required permissions")
            print("   - Account may be suspended or restricted")
        elif e.code == 429:
            print("\n⏱️  ERROR 429: Rate limited")
            print("   - Too many requests, try again later")
        elif e.code == 500:
            print("\n🖥️  ERROR 500: WakaTime server error")
            print("   - Service unavailable, try again later")
        
        # Try to read error response
        if e.fp:
            try:
                error_data = e.fp.read().decode("utf-8")
                print(f"\n📄 Error response data:")
                print(f"  Raw: {error_data}")
                
                # Parse WakaTime error response
                try:
                    error_json = json.loads(error_data)
                    if 'errors' in error_json:
                        print(f"  Parsed errors: {error_json['errors']}")
                    elif 'error' in error_json:
                        print(f"  Parsed error: {error_json['error']}")
                except json.JSONDecodeError:
                    print("  Could not parse as JSON")
            except Exception as read_error:
                print(f"  Could not read error response: {read_error}")
        
        raise
    except Exception as e:
        print(f"\n💥 Other error: {type(e).__name__}: {e}")
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
url = f"{API_BASE}/users/current/stats/{TIME_RANGE}?is_including_today=true&api_key={API_KEY}"
headers = {
    "User-Agent": "archibk33-waka-readme"
}

print(f"\n📊 Fetching WakaTime stats:")
print(f"  Full URL: {url}")
print(f"  Headers keys: {list(headers.keys())}")
print(f"  API Key length: {len(API_KEY)}")
print(f"  User-Agent: {headers['User-Agent']}")

data = http_get(url, headers)

# Debug: print the structure of the response
print(f"\n🔍 API Response Structure:")
print(f"  Type of 'data': {type(data)}")
print(f"  Keys in 'data': {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
print(f"  Type of 'data.data': {type(data.get('data')) if isinstance(data, dict) else 'N/A'}")

# Extract stats from the response
stats = data.get("data", {}) if isinstance(data, dict) else {}

print(f"  Type of 'stats': {type(stats)}")
print(f"  Keys in 'stats': {list(stats.keys()) if isinstance(stats, dict) else 'Not a dict'}")

if not stats:
    print("❌ No stats data received from API")
    sys.exit(1)

grand = stats.get("grand_total", {}) or {}
total_text = grand.get("text") or human_dhms(grand.get("total_seconds", 0))
total_secs = int(grand.get("total_seconds", 0))

# Fix range extraction - handle both object and string formats
range_obj = stats.get("range", {})
if isinstance(range_obj, dict):
    range_start = range_obj.get("start")
    range_end = range_obj.get("end")
else:
    range_start = stats.get("start")
    range_end = stats.get("end")

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
