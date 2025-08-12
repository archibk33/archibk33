#!/usr/bin/env python3
# FORCE UPDATE: Script updated to use 'today' as default time range
# This comment forces GitHub Actions to re-evaluate the script
import os, sys, json, base64, math, datetime as dt, re
from pathlib import Path
import urllib.request

API_BASE = os.getenv("API_BASE_URL", "https://api.wakatime.com/api/v1")
API_KEY  = os.getenv("WAKATIME_API_KEY")
# --- config ---
# TIME_RANGE kept for backwards compatibility but not required for accumulation mode
TIME_RANGE = os.getenv("TIME_RANGE", "today")  # today, last_7_days, last_30_days, all_time
# LANG_COUNT: 0 means show all languages
LANG_COUNT = int(os.getenv("LANG_COUNT", "0"))
IGNORED = set(filter(None, os.getenv("IGNORED_LANGUAGES", "").split()))

README_PATH = Path(os.getenv("TARGET_PATH", "README.md"))
STORE_PATH = Path(os.getenv("STORE_PATH", ".github/waka_store.json"))
BACKFILL_DAYS = int(os.getenv("BACKFILL_DAYS", "0"))  # 0 = выключено

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
print(f"Debug: STORE_PATH = {STORE_PATH}")

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

#############################
# Accumulation mode (free tier friendly)
# - fetch daily summary (yesterday on schedules/early UTC to avoid partial days)
# - store per-day language totals in repo
# - render README from accumulated totals across all stored days
#############################

def determine_summary_date() -> str:
    """Pick which date to fetch from WakaTime.

    Logic:
    - If `SUMMARY_DATE` is provided, use it (debug/manual override).
    - If running on a scheduled workflow (`GITHUB_EVENT_NAME == 'schedule'`) OR
      if current time is in early UTC hours (< 06:00), use yesterday to ensure
      the previous day is fully processed by WakaTime.
    - Otherwise, use today.
    """
    override_date = os.getenv("SUMMARY_DATE")
    if override_date:
        return override_date

    event_name = os.getenv("GITHUB_EVENT_NAME", "")
    try:
        current_hour_utc = dt.datetime.utcnow().hour
    except Exception:
        current_hour_utc = 12

    use_yesterday = event_name == "schedule" or current_hour_utc < 6
    target_date = dt.date.today() - dt.timedelta(days=1 if use_yesterday else 0)
    return target_date.isoformat()

def fetch_today_summary() -> tuple[str, int, list[dict]]:
    # Decide which date to fetch (yesterday for schedules/early UTC)
    date_str = determine_summary_date()
    url = (
        f"{API_BASE}/users/current/summaries?start={date_str}&end={date_str}"
        f"&is_including_today=true&range=1_day&api_key={API_KEY}"
    )
    headers = {"User-Agent": "archibk33-waka-readme"}
    print("\n📊 Fetching WakaTime daily summary:")
    print(f"  Date: {date_str}")
    print(f"  URL: {url}")
    data = http_get(url, headers)
    if not isinstance(data, dict) or not data.get("data"):
        print("❌ No summary data received from API")
        sys.exit(1)
    day = (data.get("data") or [{}])[0]
    # prefer date from API to avoid TZ drift
    range_info = day.get("range") or {}
    api_date = (
        (range_info.get("date") if isinstance(range_info, dict) else None)
        or date_str
    )
    grand = day.get("grand_total", {}) or {}
    total_seconds = int(grand.get("total_seconds", 0))
    languages = day.get("languages") or []
    return api_date, total_seconds, languages


def fetch_range_summaries(start_date: dt.date, end_date: dt.date) -> dict:
    """Fetch summaries for a date range [start_date, end_date].

    Returns mapping: date_iso -> { 'total_seconds': int, 'languages': list[dict] }
    """
    url = (
        f"{API_BASE}/users/current/summaries?start={start_date.isoformat()}&end={end_date.isoformat()}&api_key={API_KEY}"
    )
    headers = {"User-Agent": "archibk33-waka-readme"}
    print("\n📊 Fetching WakaTime range summary:")
    print(f"  Start: {start_date.isoformat()}  End: {end_date.isoformat()}")
    print(f"  URL: {url}")
    data = http_get(url, headers)
    result: dict[str, dict] = {}
    for day in (data.get("data") or []):
        range_info = day.get("range") or {}
        date_iso = (range_info.get("date") if isinstance(range_info, dict) else None)
        if not date_iso:
            continue
        grand = day.get("grand_total", {}) or {}
        total_seconds = int(grand.get("total_seconds", 0))
        languages = day.get("languages") or []
        result[date_iso] = {
            "total_seconds": total_seconds,
            "languages": languages,
        }
    return result


def load_store() -> dict:
    if STORE_PATH.exists():
        try:
            return json.loads(STORE_PATH.read_text(encoding="utf-8"))
        except Exception:
            return {"days": {}}
    return {"days": {}}


def save_store(store: dict) -> None:
    STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STORE_PATH.write_text(json.dumps(store, ensure_ascii=False, indent=2), encoding="utf-8")


def compute_aggregate(store: dict) -> tuple[int, dict]:
    languages_totals: dict[str, float] = {}
    total_seconds = 0
    for day_date, day in store.get("days", {}).items():
        total_seconds += int(day.get("total_seconds", 0))
        for lang, seconds in (day.get("languages", {}) or {}).items():
            languages_totals[lang] = languages_totals.get(lang, 0) + float(seconds)
    return total_seconds, languages_totals


store = load_store()
store.setdefault("days", {})

# Auto-backfill heuristic: если явно не задан BACKFILL_DAYS, но в сторе мало дней,
# подтянем последние 7 дней, чтобы совпасть с дашбордом "Last 7 Days".
auto_backfill_days = 0
if not BACKFILL_DAYS:
    existing_days = list(store.get("days", {}).keys())
    if len(existing_days) < 3:  # практически пусто – сделаем авто-филл
        auto_backfill_days = 7

effective_backfill = BACKFILL_DAYS or auto_backfill_days

if effective_backfill and effective_backfill > 0:
    # Backfill last N days up to the chosen end date
    end_iso = determine_summary_date()
    try:
        end_dt = dt.date.fromisoformat(end_iso)
    except Exception:
        end_dt = dt.date.today()
    start_dt = end_dt - dt.timedelta(days=effective_backfill - 1)
    range_data = fetch_range_summaries(start_dt, end_dt)
    for date_iso, payload in range_data.items():
        lang_map = {}
        for l in (payload.get("languages") or []):
            if l.get("name") and l.get("name") not in IGNORED:
                lang_map[l.get("name")] = float(l.get("total_seconds", 0.0))
        store["days"][date_iso] = {
            "total_seconds": int(payload.get("total_seconds", 0)),
            "languages": lang_map,
        }
else:
    # Single day update (yesterday for schedules/early UTC)
    today_date, today_total_seconds, today_langs = fetch_today_summary()
    store["days"][today_date] = {
        "total_seconds": int(today_total_seconds),
        "languages": {
            l.get("name", "Other"): float(l.get("total_seconds", 0.0)) for l in (today_langs or [])
            if l.get("name") and l.get("name") not in IGNORED
        }
    }

store["updated_at"] = dt.datetime.utcnow().isoformat() + "Z"
save_store(store)

# 3) Compute aggregate from all stored days
agg_total_seconds, agg_lang_totals = compute_aggregate(store)

# Convert to list of dicts like Stats API for rendering
total_secs = int(agg_total_seconds)
total_text = human_dhms(total_secs)
langs = [
    {"name": name, "total_seconds": secs, "percent": (secs / total_secs * 100.0 if total_secs else 0), "text": human_dhms(secs)}
    for name, secs in agg_lang_totals.items() if name not in IGNORED
]
# sort & maybe cut
langs.sort(key=lambda x: float(x.get("total_seconds", 0)), reverse=True)
if LANG_COUNT and LANG_COUNT > 0:
    langs = langs[:LANG_COUNT]

# derive date range from store
all_dates = sorted(store.get("days", {}).keys())
range_start = all_dates[0] if all_dates else today_date
range_end = all_dates[-1] if all_dates else today_date

def bar(pct: float, width: int = 26) -> str:
    # draw text bar using '▰' and '▱'
    filled = int(round(pct/100.0 * width))
    return "▰"*filled + "▱"*(width - filled)

def line_for_lang(l: dict) -> str:
    name = l.get("name", "Other")
    pct  = float(l.get("percent", 0))
    dur  = l.get("text") or human_dhms(l.get("total_seconds", 0))
    emoji = LANG_EMOJI.get(name, "💻")
    # bullet list to гарантировать переносы строк в GitHub Markdown
    return f"- {emoji} **{name}**  {dur}  `{bar(pct)}`  {pct:05.2f} %"

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
