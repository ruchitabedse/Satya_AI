import html
from datetime import datetime, timezone, timedelta

def format_time_ago(iso_str):
    try:
        clean_iso = iso_str or ""
        if clean_iso.endswith('Z'):
            clean_iso = clean_iso[:-1]
            if not ('+' in clean_iso or '-' in clean_iso.split('T')[-1]):
                clean_iso += '+00:00'
        dt = datetime.fromisoformat(clean_iso)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        diff = now - dt
        seconds = int(diff.total_seconds())
        if seconds < 0:
            return "Just now"
        if seconds < 60:
            return f"{seconds}s ago"
        if seconds < 3600:
            return f"{seconds // 60}m ago"
        if seconds < 86400:
            return f"{seconds // 3600}h ago"
        if diff.days < 30:
            return f"{diff.days}d ago"
        if diff.days < 365:
            return f"{diff.days // 30}mo ago"
        return f"{diff.days // 365}y ago"
    except:
        return html.escape(str(iso_str or ""))

now = datetime.now(timezone.utc)
test_cases = [
    (now.isoformat(), "Just now or Xs ago"),
    ((now - timedelta(seconds=30)).isoformat(), "30s ago"),
    ((now - timedelta(minutes=5)).isoformat(), "5m ago"),
    ((now - timedelta(hours=2)).isoformat(), "2h ago"),
    ((now - timedelta(days=10)).isoformat(), "10d ago"),
    ((now - timedelta(days=60)).isoformat(), "2mo ago"),
    ((now - timedelta(days=400)).isoformat(), "1y ago"),
    ("invalid", "invalid"),
    (None, "")
]

for iso, expected in test_cases:
    print(f"ISO: {iso} -> Result: {format_time_ago(iso)} (Expected: {expected})")
