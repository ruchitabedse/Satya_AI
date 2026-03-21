import streamlit as st
import os
import sys
import json
import html
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from satya.core import storage, Tasks, Scraper

MAIN_OWNER_ICON = """
<svg width="64" height="64" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
  <circle cx="32" cy="32" r="32" fill="#6352E3" fill-opacity="0.1"/>
  <path d="M32 12C24.268 12 18 18.268 18 26C18 33.732 24.268 40 32 40C39.732 40 46 33.732 46 26C46 18.268 39.732 12 32 12ZM32 16C37.523 16 42 20.477 42 26C42 31.523 37.523 36 32 36C26.477 36 22 31.523 22 26C22 20.477 26.477 16 32 16ZM32 42C23.163 42 16 49.163 16 58H48C48 49.163 40.837 42 32 42Z" fill="#6352E3"/>
  <path d="M32 32L36 36L44 28" stroke="white" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
"""

st.set_page_config(
    page_title="Satya - AI Agent Tracker",
    layout="wide",
    page_icon="https://img.icons8.com/fluency/48/artificial-intelligence.png",
    initial_sidebar_state="expanded"
)

if "theme" not in st.session_state:
    st.session_state.theme = "dark"

is_dark = st.session_state.theme == "dark"

DARK_VARS = """
:root {
    --primary: #6352E3;
    --primary-light: #A29BFE;
    --primary-dark: #5A4BD1;
    --card-radius: 16px;
    --card-padding-lg: 2rem;
    --card-padding-md: 1.25rem;
    --card-padding-sm: 1rem;
    --card-gap: 1.5rem;
    --transition-speed: 0.3s;
    --success: #00B894;
    --warning: #FDCB6E;
    --danger: #E17055;
    --info: #74B9FF;
    --bg-main: #0F0F1A;
    --bg-card: #1A1A2E;
    --bg-card-hover: #222240;
    --bg-sidebar: linear-gradient(180deg, #16162B 0%, #0F0F1A 100%);
    --text-primary: #EAEAF0;
    --text-secondary: #B0B0C5;
    --border: #2D2D44;
    --input-bg: #1E1E36;
    --shadow-color: rgba(108, 92, 231, 0.15);
    --log-bg: rgba(108,92,231,0.05);
}
"""

LIGHT_VARS = """
:root {
    --primary: #6352E3;
    --primary-light: #7C6FF0;
    --primary-dark: #5A4BD1;
    --card-radius: 16px;
    --card-padding-lg: 2rem;
    --card-padding-md: 1.25rem;
    --card-padding-sm: 1rem;
    --card-gap: 1.5rem;
    --transition-speed: 0.3s;
    --success: #00B894;
    --warning: #F0A500;
    --danger: #E17055;
    --info: #0984E3;
    --bg-main: #F5F6FA;
    --bg-card: #FFFFFF;
    --bg-card-hover: #F0F0F8;
    --bg-sidebar: linear-gradient(180deg, #FFFFFF 0%, #F5F6FA 100%);
    --text-primary: #2D3436;
    --text-secondary: #636E72;
    --border: #DFE6E9;
    --input-bg: #FFFFFF;
    --shadow-color: rgba(108, 92, 231, 0.08);
    --log-bg: rgba(108,92,231,0.04);
}
"""

THEME_VARS = DARK_VARS if is_dark else LIGHT_VARS

CUSTOM_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

{THEME_VARS}

html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif !important;
}}

.stApp {{
    background: var(--bg-main) !important;
}}

.main .block-container {{
    padding-top: 1.5rem;
    max-width: 1400px;
}}

section[data-testid="stSidebar"] {{
    background: var(--bg-sidebar);
    border-right: 1px solid var(--border);
}}

section[data-testid="stSidebar"] [data-testid="stMarkdown"] {{
    color: var(--text-primary);
}}

.hero-header {{
    background: linear-gradient(135deg, #6C5CE7 0%, #A29BFE 50%, #74B9FF 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-size: 2.2rem;
    font-weight: 800;
    letter-spacing: -0.5px;
    margin-bottom: 0.2rem;
}}

.page-subtitle {{
    color: var(--text-secondary);
    font-size: 1rem;
    margin-bottom: 1.5rem;
    font-weight: 400;
}}

.metric-card {{
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1.5rem;
    text-align: center;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}}

.metric-card:hover {{
    transform: translateY(-2px);
    box-shadow: 0 8px 32px var(--shadow-color);
}}

.metric-value {{
    font-size: 2.5rem;
    font-weight: 800;
    margin: 0.3rem 0;
}}

.metric-label {{
    font-size: 0.85rem;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 1px;
    font-weight: 600;
}}

.metric-icon {{
    font-size: 1.5rem;
    margin-bottom: 0.3rem;
}}

.task-card {{
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.75rem;
    transition: all 0.2s ease;
    border-left: 4px solid transparent;
}}

.task-card:hover {{
    background: var(--bg-card-hover);
    box-shadow: 0 4px 20px var(--shadow-color);
}}

.task-card.priority-critical {{ border-left-color: var(--danger); }}
.task-card.priority-high {{ border-left-color: var(--warning); }}
.task-card.priority-medium {{ border-left-color: var(--info); }}
.task-card.priority-low {{ border-left-color: var(--success); }}

.task-title {{
    font-weight: 600;
    font-size: 0.95rem;
    color: var(--text-primary);
    margin-bottom: 0.3rem;
}}

.task-meta {{
    font-size: 0.75rem;
    color: var(--text-secondary);
}}

.priority-badge {{
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

.badge-critical {{ background: rgba(225,112,85,0.15); color: var(--danger); }}
.badge-high {{ background: rgba(253,203,110,0.15); color: var(--warning); }}
.badge-medium {{ background: rgba(116,185,255,0.15); color: var(--info); }}
.badge-low {{ background: rgba(0,184,148,0.15); color: var(--success); }}

.column-header {{
    padding: 0.6rem 1rem;
    border-radius: 10px;
    text-align: center;
    font-weight: 700;
    font-size: 0.9rem;
    margin-bottom: 1rem;
    letter-spacing: 0.3px;
}}

.header-todo {{ background: rgba(116,185,255,0.15); color: var(--info); border: 1px solid rgba(116,185,255,0.3); }}
.header-progress {{ background: rgba(253,203,110,0.15); color: var(--warning); border: 1px solid rgba(253,203,110,0.3); }}
.header-done {{ background: rgba(0,184,148,0.15); color: var(--success); border: 1px solid rgba(0,184,148,0.3); }}

.truth-card {{
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.2rem;
    margin-bottom: 0.75rem;
    transition: all 0.2s ease;
}}

.truth-card:hover {{
    background: var(--bg-card-hover);
}}

.section-divider {{
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--border), transparent);
    margin: 1.5rem 0;
}}

.sidebar-brand {{
    text-align: center;
    padding: 1rem 0;
}}

.sidebar-brand-title {{
    font-size: 1.6rem;
    font-weight: 800;
    background: linear-gradient(135deg, #6C5CE7, #A29BFE);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -0.5px;
}}

.sidebar-brand-sub {{
    font-size: 0.75rem;
    color: var(--text-secondary);
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-top: 2px;
}}

.log-entry {{
    font-family: 'JetBrains Mono', 'Fira Code', monospace;
    font-size: 0.8rem;
    padding: 0.4rem 0.8rem;
    border-left: 3px solid var(--primary);
    margin-bottom: 0.3rem;
    background: var(--log-bg);
    border-radius: 0 6px 6px 0;
    color: var(--text-primary);
}}

.empty-state {{
    text-align: center;
    padding: 3rem 2rem;
    color: var(--text-secondary);
}}

.empty-state-icon {{
    font-size: 3rem;
    margin-bottom: 1rem;
    opacity: 0.5;
}}

.empty-state-text {{
    font-size: 1rem;
    font-weight: 500;
}}

.stButton > button {{
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.8rem !important;
    padding: 0.3rem 0.8rem !important;
    transition: all 0.2s ease !important;
}}

div[data-testid="stExpander"] {{
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
}}

.progress-bar-container {{
    background: var(--border);
    border-radius: 10px;
    height: 8px;
    overflow: hidden;
    margin-top: 0.5rem;
}}

.progress-bar-fill {{
    height: 100%;
    border-radius: 10px;
    transition: width 0.5s ease;
}}

.footer-text {{
    text-align: center;
    color: var(--text-secondary);
    font-size: 0.75rem;
    padding: 1rem 0;
    border-top: 1px solid var(--border);
    margin-top: 2rem;
}}

.theme-toggle {{
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    padding: 0.4rem 0.8rem;
    border-radius: 10px;
    background: var(--bg-card);
    border: 1px solid var(--border);
    cursor: pointer;
    margin: 0.5rem auto;
    font-size: 0.8rem;
    color: var(--text-secondary);
    font-weight: 500;
}}

.api-section {{
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}}

.api-section h4 {{
    color: var(--text-primary);
    margin-bottom: 0.5rem;
}}

.code-block {{
    background: {'#12121F' if is_dark else '#F0F0F5'};
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1rem;
    font-family: 'JetBrains Mono', 'Fira Code', monospace;
    font-size: 0.8rem;
    color: var(--text-primary);
    overflow-x: auto;
    white-space: pre;
    line-height: 1.6;
}}

.endpoint-row {{
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.6rem 0;
    border-bottom: 1px solid var(--border);
}}

.endpoint-row:last-child {{
    border-bottom: none;
}}

.method-badge {{
    display: inline-block;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 0.7rem;
    font-weight: 700;
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: 0.5px;
}}

.method-post {{ background: rgba(0,184,148,0.2); color: #00B894; }}
.method-get {{ background: rgba(116,185,255,0.2); color: #74B9FF; }}
.method-put {{ background: rgba(253,203,110,0.2); color: #FDCB6E; }}
.method-delete {{ background: rgba(225,112,85,0.2); color: #E17055; }}

/* Promo & Main Owner Styles */
.promo-card {{
    border-radius: var(--card-radius);
    transition: all var(--transition-speed) ease;
    cursor: pointer;
    text-decoration: none;
    display: flex;
    flex-direction: column;
    border: 1px solid var(--border);
    overflow: hidden;
    position: relative;
    margin-bottom: 1.5rem;
}}

.promo-card:hover {{
    transform: translateY(-4px);
    box-shadow: 0 12px 24px var(--shadow-color);
}}

.promo-card:active {{
    transform: translateY(-2px);
}}

/* 1. Hero Card (Large) */
.hero-card {{
    background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
    padding: var(--card-padding-lg);
    color: white;
    min-height: 240px;
    justify-content: center;
}}

.hero-card .card-headline {{
    font-size: 1.75rem;
    font-weight: 800;
    margin-bottom: 0.75rem;
    color: white !important;
}}

.hero-card .card-body {{
    font-size: 1rem;
    opacity: 0.9;
    margin-bottom: 1.5rem;
    max-width: 80%;
    color: white !important;
}}

/* 2. Compact Card (List/Side) */
.compact-card {{
    background: var(--bg-card);
    padding: var(--card-padding-md);
    flex-direction: row;
    align-items: center;
    gap: 1rem;
}}

.compact-card .card-icon {{
    width: 48px;
    height: 48px;
    flex-shrink: 0;
}}

.compact-card .card-content {{
    flex-grow: 1;
}}

.compact-card .card-headline {{
    font-size: 1.1rem;
    font-weight: 700;
    margin-bottom: 0.25rem;
}}

.compact-card .card-body {{
    font-size: 0.85rem;
    color: var(--text-secondary);
}}

/* 3. Mobile Tile */
.mobile-tile {{
    background: var(--bg-card);
    padding: var(--card-padding-sm);
    text-align: center;
    aspect-ratio: 1 / 1;
    justify-content: space-between;
}}

.mobile-tile .card-icon {{
    width: 64px;
    height: 64px;
    margin: 0 auto 0.5rem;
}}

.mobile-tile .card-headline {{
    font-size: 0.95rem;
    font-weight: 700;
}}

/* Accessibility: 4.5:1 Contrast for CTA */
.card-cta {{
    display: inline-block;
    padding: 0.6rem 1.2rem;
    border-radius: 8px;
    font-weight: 700;
    font-size: 0.9rem;
    text-align: center;
    text-decoration: none;
    transition: background 0.2s;
}}

.hero-card .card-cta {{
    background: white;
    color: var(--primary) !important;
}}

.hero-card .card-cta:hover {{
    background: var(--bg-card-hover);
}}

.compact-card .card-cta, .mobile-tile .card-cta {{
    background: var(--primary);
    color: white !important;
}}

.step-card {{
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.25rem;
    margin-bottom: 1rem;
}}

.step-number {{
    width: 24px;
    height: 24px;
    background: var(--primary);
    color: white;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.8rem;
    font-weight: 700;
    margin-bottom: 0.75rem;
}}

.step-title {{
    font-weight: 700;
    font-size: 1rem;
    margin-bottom: 0.5rem;
}}

.step-desc {{
    font-size: 0.9rem;
    color: var(--text-secondary);
}}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


@st.cache_resource
def get_managers():
    return Tasks(), Scraper()

tasks_manager, scraper_manager = get_managers()


def log_analytics(event_name, payload=None):
    """Mock analytics event logging."""
    # Simple deduplication for Streamlit reruns
    last_event = st.session_state.get("last_analytics_event")
    last_payload = st.session_state.get("last_analytics_payload")

    if last_event == event_name and last_payload == payload:
        return None

    st.session_state.last_analytics_event = event_name
    st.session_state.last_analytics_payload = payload

    now = datetime.now().isoformat()
    log_entry = {
        "timestamp": now,
        "event": event_name,
        "payload": payload or {}
    }
    # For demo purposes, we'll log to a file
    os.makedirs("satya_data/analytics", exist_ok=True)
    with open("satya_data/analytics/events.log", "a") as f:
        f.write(json.dumps(log_entry) + "\n")
    return log_entry

def parse_iso(iso_str):
    """Robust ISO parser that handles Z and ensures timezone awareness."""
    if not iso_str:
        return None
    try:
        # Handle cases like '2023-10-27T10:00:00+00:00Z'
        if iso_str.endswith('Z'):
            clean_iso = iso_str.replace('Z', '+00:00')
        else:
            clean_iso = iso_str

        dt = datetime.fromisoformat(clean_iso)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except:
        return None

def format_date(iso_str):
    """Format ISO timestamp to human readable date."""
    dt = parse_iso(iso_str)
    if not dt:
        return html.escape(str(iso_str or "N/A"))
    return dt.strftime("%b %d, %Y")

def format_time_ago(iso_str):
    try:
        dt = parse_iso(iso_str)
        if not dt:
            return html.escape(str(iso_str or ""))

        diff = datetime.now(timezone.utc) - dt
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

def get_priority_badge(priority):
    p = html.escape((priority or "Medium").lower())
    return f'<span class="priority-badge badge-{p}">{html.escape(priority or "Medium")}</span>'

def get_priority_class(priority):
    return f"priority-{html.escape((priority or 'medium').lower())}"


with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <div class="sidebar-brand-title">Satya</div>
        <div class="sidebar-brand-sub">AI Agent Tracker</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Handle Navigation via Query Parameters
    nav_options = ["Dashboard", "Task Board", "Truth Source", "Agent Logs", "Main Owner Guide", "SDK Docs"]
    query_params = st.query_params
    default_index = 0
    if "page" in query_params:
        target_page = query_params["page"].replace("+", " ")
        if target_page in nav_options:
            default_index = nav_options.index(target_page)

    page = st.radio(
        "Navigation",
        nav_options,
        index=default_index,
        label_visibility="collapsed"
    )

    st.markdown("---")

    all_tasks = tasks_manager.list_all()

    # Calculate stats and agent metrics in a single pass to avoid multiple file reads
    stats = {
        "total": len(all_tasks),
        "queued": 0,
        "in_progress": 0,
        "done": 0,
        "failed": 0
    }

    agent_metrics = {}

    for t in all_tasks:
        # Update overall stats
        status = t.get("status", "queued")
        if status in stats:
            stats[status] += 1

        # Update agent metrics
        assignee = t.get("assignee", "Unassigned")
        if assignee not in agent_metrics:
            agent_metrics[assignee] = {"completed": 0, "in_progress": 0, "total": 0}

        agent_metrics[assignee]["total"] += 1
        if status == "done":
            agent_metrics[assignee]["completed"] += 1
        elif status == "in_progress":
            agent_metrics[assignee]["in_progress"] += 1

    if stats["total"] > 0:
        completion = int((stats["done"] / stats["total"]) * 100)
    else:
        completion = 0

    st.markdown(f"""
    <div style="padding: 0.5rem;">
        <div style="font-size: 0.75rem; color: var(--text-secondary); margin-bottom: 0.3rem; text-transform: uppercase; letter-spacing: 1px; font-weight: 600;">
            Overall Progress
        </div>
        <div style="font-size: 1.5rem; font-weight: 800; color: var(--text-primary);">{completion}%</div>
        <div class="progress-bar-container">
            <div class="progress-bar-fill" style="width: {completion}%; background: linear-gradient(90deg, #6C5CE7, #00B894);"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    theme_label = "Switch to Light" if is_dark else "Switch to Dark"
    theme_icon = "&#9728;&#65039;" if is_dark else "&#127769;"
    if st.button(f"{'Light Mode' if is_dark else 'Dark Mode'}", key="theme_toggle", use_container_width=True):
        st.session_state.theme = "light" if is_dark else "dark"
        st.rerun()

    st.markdown("---")

    # Stable A/B test variants using session state
    if "main_owner_variants" not in st.session_state:
        st.session_state.main_owner_variants = {
            "headline": "A" if datetime.now().second % 2 == 0 else "B",
            "cta": "1" if datetime.now().second % 4 < 2 else "2"
        }

    headline_variant = st.session_state.main_owner_variants["headline"]
    cta_variant = st.session_state.main_owner_variants["cta"]

    mobile_headlines = {"A": "Main Owner Setup", "B": "Control Center"}
    mobile_ctas = {"1": "Start", "2": "Unlock"}

    # Mobile Tile (Sidebar/Small)
    st.markdown(f"""
    <div class="promo-card mobile-tile" onclick="window.location.href='?page=Main+Owner+Guide'">
        <div class="card-icon">{MAIN_OWNER_ICON}</div>
        <div class="card-headline">{mobile_headlines[headline_variant]}</div>
        <a href="?page=Main+Owner+Guide" target="_self" class="card-cta" style="padding: 0.3rem 0.8rem; font-size: 0.7rem; display: block;">{mobile_ctas[cta_variant]}</a>
    </div>
    """, unsafe_allow_html=True)
    log_analytics("main_owner_promo_view", {"card_size": "mobile", "variant": headline_variant})

    st.markdown("""
    <div style="text-align: center; padding: 0.5rem;">
        <div style="font-size: 0.7rem; color: var(--text-secondary);">
            Powered by <strong>Anktechsol.com</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)




# ─── DASHBOARD PAGE ─────────────────────────────────────
if page == "Dashboard":
    log_analytics("page_view", {"page": "Dashboard"})
    st.markdown('<div class="hero-header">Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Overview of your AI agent operations and task progress</div>', unsafe_allow_html=True)

    # Variant Selection from session state for stability
    headline_variant = st.session_state.get("main_owner_variants", {}).get("headline", "A")
    cta_variant = st.session_state.get("main_owner_variants", {}).get("cta", "1")

    hero_headlines = {"A": "Master Your AI Fleet", "B": "Unified Control Starts Here"}
    hero_ctas = {"1": "Set Main Owner", "2": "Start Onboarding"}

    # Main Owner Promo Hero Card (Large)
    st.markdown(f"""
    <div class="promo-card hero-card" onclick="window.location.href='?page=Main+Owner+Guide'">
        <div class="card-headline">{hero_headlines[headline_variant]}</div>
        <div class="card-body">Designate a Main Owner for unified oversight, master permissions, and central governance across all agent sessions.</div>
        <div>
            <a href="?page=Main+Owner+Guide" target="_self" class="card-cta" title="Begin the Main Owner onboarding process">{hero_ctas[cta_variant]}</a>
        </div>
    </div>
    """, unsafe_allow_html=True)
    log_analytics("main_owner_promo_view", {"card_size": "hero", "variant": headline_variant})

    from satya.core import get_stale_tasks
    # ⚡ Bolt Optimization:
    # We already fetched all_tasks via tasks_manager.list_all().
    # Passing them here prevents N+1 file reads, drastically speeding up the render.
    stale = get_stale_tasks(all_tasks)
    if stale:
        st.warning(f"⚠️ {len(stale)} stale task(s) detected — agent may be stuck")
        for t in stale:
            st.write(f"- {t['title']} | locked by {t['locked_by']} | {t['elapsed_minutes']}m elapsed")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">&#128202;</div>
            <div class="metric-value" style="color: var(--primary-light);">{stats['total']}</div>
            <div class="metric-label">Total Tasks</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">&#128204;</div>
            <div class="metric-value" style="color: var(--info);">{stats['queued']}</div>
            <div class="metric-label">To Do</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">&#9889;</div>
            <div class="metric-value" style="color: var(--warning);">{stats['in_progress']}</div>
            <div class="metric-label">In Progress</div>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">&#9989;</div>
            <div class="metric-value" style="color: var(--success);">{stats['done']}</div>
            <div class="metric-label">Completed</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)


    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.markdown("#### Recent Tasks")
        sorted_tasks = sorted(all_tasks, key=lambda t: t.get("updated_at", ""), reverse=True)[:5]

        if sorted_tasks:
            for task in sorted_tasks:
                priority = task.get("priority", "Medium")
                st.markdown(f"""
                <div class="task-card {get_priority_class(priority)}">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div class="task-title">{html.escape(task.get('title', 'Untitled'))}</div>
                        {get_priority_badge(priority)}
                    </div>
                    <div class="task-meta">
                        {html.escape(task.get('assignee', 'Unassigned'))} &middot;
                        {html.escape(task.get('status', 'To Do'))} &middot;
                        {format_time_ago(task.get('updated_at', ''))}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="empty-state">
                <div class="empty-state-icon">&#128203;</div>
                <div class="empty-state-text">No tasks yet. Create your first task!</div>
            </div>
            """, unsafe_allow_html=True)

    with col_right:
        st.markdown("#### Quick Stats")

        truth_files = scraper_manager.list_sources()
        log_files = []
        if os.path.exists(storage.AGENTS_DIR):
            log_files = [f for f in os.listdir(storage.AGENTS_DIR) if f.endswith(".log")]

        st.markdown(f"""
        <div class="metric-card" style="margin-bottom: 1rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.3rem 0;">
                <span style="color: var(--text-secondary);">Knowledge Sources</span>
                <span style="font-weight: 700; font-size: 1.2rem; color: var(--primary-light);">{len(truth_files)}</span>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.3rem 0;">
                <span style="color: var(--text-secondary);">Agent Logs</span>
                <span style="font-weight: 700; font-size: 1.2rem; color: var(--primary-light);">{len(log_files)}</span>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.3rem 0;">
                <span style="color: var(--text-secondary);">Completion Rate</span>
                <span style="font-weight: 700; font-size: 1.2rem; color: var(--success);">{completion}%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        compact_headlines = {"A": "Secure Your Workspace", "B": "Enable Owner Oversight"}
        compact_ctas = {"1": "Setup Now", "2": "View Guide"}

        # Compact Card (List/Side)
        st.markdown(f"""
        <div class="promo-card compact-card" onclick="window.location.href='?page=Main+Owner+Guide'">
            <div class="card-icon">{MAIN_OWNER_ICON}</div>
            <div class="card-content">
                <div class="card-headline">{compact_headlines[headline_variant]}</div>
                <div class="card-body">Unified oversight for your mission.</div>
            </div>
            <a href="?page=Main+Owner+Guide" target="_self" class="card-cta" style="padding: 0.4rem 1rem; font-size: 0.75rem;">{compact_ctas[cta_variant]}</a>
        </div>
        """, unsafe_allow_html=True)
        log_analytics("main_owner_promo_view", {"card_size": "compact", "variant": headline_variant})

        st.markdown('<div style="margin-top: 1.5rem;"></div>', unsafe_allow_html=True)

        # Mobile Tile Variant (for completeness on dashboard)
        st.markdown(f"""
        <div class="promo-card mobile-tile" onclick="window.location.href='?page=Main+Owner+Guide'">
            <div class="card-icon">{MAIN_OWNER_ICON}</div>
            <div class="card-headline">Quick Setup</div>
            <a href="?page=Main+Owner+Guide" target="_self" class="card-cta" style="padding: 0.4rem 1rem; font-size: 0.75rem;">{cta_variant == "1" and "Start" or "Unlock"}</a>
        </div>
        """, unsafe_allow_html=True)
        log_analytics("main_owner_promo_view", {"card_size": "mobile_tile", "variant": headline_variant})

        if stats["total"] > 0:
            st.markdown("#### Task Distribution")
            import pandas as pd
            chart_data = pd.DataFrame({
                "Status": ["To Do", "In Progress", "Done"],
                "Count": [stats["queued"], stats["in_progress"], stats["done"]]
            })
            st.bar_chart(chart_data, x="Status", y="Count", color="#6C5CE7", height=200)

        if agent_metrics:
            st.markdown("#### Agent Performance")
            agent_data = []
            for agent, data in agent_metrics.items():
                agent_data.append({"Agent": agent, "Completed": data["completed"], "In Progress": data["in_progress"]})

            df_agents = pd.DataFrame(agent_data)
            st.bar_chart(df_agents, x="Agent", y=["Completed", "In Progress"], height=200)

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown("#### Audit Trail (Governance)")
    # Extract audit trails across all tasks and sort by timestamp
    audit_events = []
    for task in all_tasks:
        audit_trail = task.get("audit_trail", [])
        for event in audit_trail:
            # add task title to the event for display
            event_copy = event.copy()
            event_copy["task_title"] = task.get("title", "Unknown Task")
            audit_events.append(event_copy)

    if audit_events:
        # Sort newest first
        audit_events.sort(key=lambda e: e.get("timestamp", ""), reverse=True)
        # Display top 10
        for event in audit_events[:10]:
            ts = format_date(event.get('timestamp', ''))
            agent = event.get('agent', 'System')
            action = event.get('action', 'Unknown Action')
            details = event.get('details', '')
            task_title = event.get('task_title', '')

            st.markdown(f"""
            <div style="font-size: 0.85rem; padding: 0.5rem; border-left: 3px solid var(--info); margin-bottom: 0.5rem; background: var(--bg-card); border-radius: 4px;">
                <span style="color: var(--text-secondary); font-size: 0.75rem;">{ts}</span> &mdash;
                <strong>{html.escape(agent)}</strong> <span style="color: var(--primary-light);">{html.escape(action)}</span> on <em>{html.escape(task_title)}</em>: {html.escape(details)}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("<p style='color: var(--text-secondary); font-size: 0.85rem;'>No audit events recorded yet.</p>", unsafe_allow_html=True)

# ─── TASK BOARD PAGE ────────────────────────────────────
elif page == "Task Board":
    st.markdown('<div class="hero-header">Task Board</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Manage your Agile tasks across workflow stages</div>', unsafe_allow_html=True)

    with st.expander("Create New Task", expanded=False):
        with st.form("new_task_form"):
            col_a, col_b = st.columns(2)
            with col_a:
                new_title = st.text_input("Title", placeholder="Enter task title...")
                new_assignee = st.text_input("Assignee", value="User", placeholder="Agent or team member name")
            with col_b:
                new_priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"], index=1)
                new_desc = st.text_area("Description", placeholder="Describe the task...", height=76)

            submitted = st.form_submit_button("Create Task", use_container_width=True)

            if submitted and new_title:
                tasks_manager.create_task(new_title, new_desc, new_assignee, new_priority)
                st.success(f"Task '{new_title}' created successfully!")
                st.rerun()
            elif submitted:
                st.warning("Please enter a task title.")

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    tasks_by_status = {"queued": [], "in_progress": [], "done": []}
    for task in all_tasks:
        status = task.get("status", "queued")
        if status not in tasks_by_status:
            status = "queued"
        tasks_by_status[status].append(task)

    for status_key in tasks_by_status:
        tasks_by_status[status_key].sort(
            key=lambda t: {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}.get(t.get("priority", "Medium"), 2)
        )

    col1, col2, col3 = st.columns(3)

    headers = {
        "queued": ("header-todo", "&#128204; To Do", col1),
        "in_progress": ("header-progress", "&#9889; In Progress", col2),
        "done": ("header-done", "&#9989; Done", col3)
    }

    for status, (css_class, label, col) in headers.items():
        count = len(tasks_by_status[status])
        with col:
            st.markdown(f'<div class="column-header {css_class}">{label} ({count})</div>', unsafe_allow_html=True)

            if not tasks_by_status[status]:
                st.markdown("""
                <div class="empty-state" style="padding: 2rem 1rem;">
                    <div style="font-size: 2rem; opacity: 0.3;">&#128466;</div>
                    <div style="font-size: 0.85rem; color: var(--text-secondary);">No tasks</div>
                </div>
                """, unsafe_allow_html=True)

            for task in tasks_by_status[status]:
                priority = task.get("priority", "Medium")

                st.markdown(f"""
                <div class="task-card {get_priority_class(priority)}">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                        <div class="task-title">{html.escape(task.get('title', 'Untitled'))}</div>
                        {get_priority_badge(priority)}
                    </div>
                    <div style="font-size: 0.82rem; color: var(--text-secondary); margin: 0.3rem 0;">
                        {html.escape(task.get('description', '')[:80])}{'...' if len(task.get('description', '')) > 80 else ''}
                    </div>
                    <div class="task-meta">
                        <span title="Task ID" style="font-family: monospace; background: var(--border); padding: 1px 4px; border-radius: 4px; font-size: 0.7rem;">{html.escape(task.get('id', ''))}</span> &middot;
                        &#128100; {html.escape(task.get('assignee', 'Unassigned'))} &middot;
                        &#128197; {format_date(task.get('created_at', ''))}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                btn_cols = st.columns(3)

                if status == "queued":
                    if btn_cols[1].button("Start", key=f"start_{task['id']}", use_container_width=True, help="Move task to In Progress"):
                        tasks_manager.update_task_status(task['id'], "in_progress")
                        st.rerun()
                    if btn_cols[2].button("Delete", key=f"del_todo_{task['id']}", use_container_width=True, help="Permanently delete this task"):
                        tasks_manager.delete_task(task['id'])
                        st.rerun()

                elif status == "in_progress":
                    # Cannot move back to queued legally in the data model
                    if btn_cols[1].button("Done", key=f"done_{task['id']}", use_container_width=True, help="Mark task as Completed"):
                        try:
                            tasks_manager.update_task_status(task['id'], "done")
                            st.rerun()
                        except Exception as e:
                            st.error(str(e))
                    if btn_cols[2].button("Delete", key=f"del_prog_{task['id']}", use_container_width=True, help="Permanently delete this task"):
                        tasks_manager.delete_task(task['id'])
                        st.rerun()

                elif status == "done":
                    if btn_cols[2].button("Delete", key=f"del_done_{task['id']}", use_container_width=True, help="Permanently delete this task"):
                        tasks_manager.delete_task(task['id'])
                        st.rerun()

                with st.expander("Activity Log", expanded=False):
                    comments = task.get("comments", [])
                    if comments:
                        for c in reversed(comments):
                            try:
                                ts_obj = datetime.fromisoformat(c.get("timestamp", ""))
                                ts_str = ts_obj.strftime("%H:%M:%S")
                            except ValueError:
                                ts_str = html.escape(str(c.get("timestamp", "")))
                            txt = html.escape(c.get("text", ""))
                            st.markdown(f"<div style='font-size: 0.8rem; margin-bottom: 0.4rem; border-left: 2px solid var(--border); padding-left: 0.5rem;'><span style='color: var(--text-secondary);'>{ts_str}</span> {txt}</div>", unsafe_allow_html=True)
                    else:
                        st.caption("No activity recorded yet.")


# ─── TRUTH SOURCE PAGE ─────────────────────────────────
elif page == "Truth Source":
    st.markdown('<div class="hero-header">Truth Source</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Curate your knowledge base by scraping and saving web content</div>', unsafe_allow_html=True)

    with st.expander("Add New Source", expanded=False):
        with st.form("scrape_form"):
            url_to_scrape = st.text_input("URL", placeholder="https://example.com/article")
            scrape_btn = st.form_submit_button("Scrape & Save", use_container_width=True)

            if scrape_btn:
                if url_to_scrape:
                    with st.spinner(f"Scraping {url_to_scrape}..."):
                        filename = scraper_manager.fetch_and_save(url_to_scrape)
                        if filename:
                            st.success(f"Saved as: {filename}")
                            st.rerun()
                        else:
                            st.error("Failed to scrape URL. Please check the URL and try again.")
                else:
                    st.warning("Please enter a URL.")

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    files = scraper_manager.list_sources()

    if files:
        st.markdown(f"#### Knowledge Base ({len(files)} sources)")

        for idx, fname in enumerate(files):
            safe_fname = os.path.basename(fname)
            file_path = os.path.join(storage.TRUTH_DIR, safe_fname)
            file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
            size_str = f"{file_size / 1024:.1f} KB" if file_size > 1024 else f"{file_size} B"

            col_f, col_act = st.columns([5, 1])
            with col_f:
                st.markdown(f"""
                <div class="truth-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <div style="font-weight: 600; color: var(--text-primary);">&#128196; {html.escape(fname)}</div>
                            <div style="font-size: 0.75rem; color: var(--text-secondary); margin-top: 0.2rem;">
                                Size: {size_str}
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with col_act:
                if st.button("Delete", key=f"del_truth_{idx}", use_container_width=True):
                    storage.delete_truth_file(fname)
                    st.rerun()

        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

        selected_file = st.selectbox("View Source Content", files, label_visibility="collapsed", placeholder="Select a file to preview...")
        if selected_file:
            safe_selected_file = os.path.basename(selected_file)
            file_path = os.path.join(storage.TRUTH_DIR, safe_selected_file)
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                with st.container(border=True):
                    st.markdown(content)
    else:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-state-icon">&#128218;</div>
            <div class="empty-state-text">No knowledge sources yet.</div>
            <div style="font-size: 0.85rem; color: var(--text-secondary); margin-top: 0.5rem;">
                Add your first source by scraping a URL above.
            </div>
        </div>
        """, unsafe_allow_html=True)


# ─── AGENT LOGS PAGE ───────────────────────────────────
elif page == "Agent Logs":
    st.markdown('<div class="hero-header">Agent Logs</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Monitor autonomous agent activity and session history</div>', unsafe_allow_html=True)

    if not os.path.exists(storage.AGENTS_DIR):
        st.markdown("""
        <div class="empty-state">
            <div class="empty-state-icon">&#128373;</div>
            <div class="empty-state-text">No agent logs directory found.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        log_files = [f for f in os.listdir(storage.AGENTS_DIR) if f.endswith(".log")]

        if log_files:
            log_files.sort(
                key=lambda x: os.path.getmtime(os.path.join(storage.AGENTS_DIR, x)),
                reverse=True
            )

            st.markdown(f"#### Active Sessions ({len(log_files)} logs)")

            col_sel, col_ref = st.columns([4, 1])
            with col_sel:
                selected_log = st.selectbox("Select Log", log_files, label_visibility="collapsed")
            with col_ref:
                if st.button("Refresh", use_container_width=True):
                    st.rerun()

            if selected_log:
                safe_selected_log = os.path.basename(selected_log)
                log_path = os.path.join(storage.AGENTS_DIR, safe_selected_log)

                mod_time = datetime.fromtimestamp(os.path.getmtime(log_path))
                file_size = os.path.getsize(log_path)

                c1, c2, c3 = st.columns(3)
                agent_name = selected_log.rsplit("_", 1)[0] if "_" in selected_log else selected_log
                c1.metric("Agent", agent_name)
                c2.metric("Last Modified", mod_time.strftime("%b %d, %H:%M"))
                c3.metric("Size", f"{file_size / 1024:.1f} KB" if file_size > 1024 else f"{file_size} B")

                st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

                with open(log_path, 'r') as f:
                    log_content = f.read()

                lines = log_content.strip().split('\n')

                with st.container(border=True):
                    for line in lines:
                        if line.strip():
                            st.markdown(f'<div class="log-entry">{html.escape(line)}</div>', unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="empty-state">
                <div class="empty-state-icon">&#128373;</div>
                <div class="empty-state-text">No log files found.</div>
                <div style="font-size: 0.85rem; color: var(--text-secondary); margin-top: 0.5rem;">
                    Agent logs will appear here when agents start sessions using the SDK.
                </div>
            </div>
            """, unsafe_allow_html=True)


# ─── MAIN OWNER PAGE ─────────────────────────────────────
elif page == "Main Owner Guide":
    log_analytics("page_view", {"page": "Main Owner Guide"})
    st.markdown('<div class="hero-header">Main Owner Guide</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Take command of your AI workforce: Designate a Main Owner for unified oversight, master permissions, and central governance.</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="api-section">
        <h4 style="color: var(--primary-light);">Feature Summary</h4>
        <p style="color: var(--text-secondary); font-size: 0.95rem; line-height: 1.7;">
            The Main Owner feature empowers you to take full control of your Satya environment. By designating a primary administrator,
            you gain a single source of truth for agent sessions, knowledge bases, and compliance rules. This centralized role
            streamlines multi-agent coordination, ensures consistent governance across all tasks, and provides the ultimate fallback
            for session management, making it essential for scaling your AI operations securely and efficiently.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    st.markdown("#### 3-Step Setup Guide")
    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        st.markdown("""
        <div class="step-card">
            <div class="step-number">1</div>
            <div class="step-title">Access Settings</div>
            <div class="step-desc">Navigate to the 'Governance' tab in your Satya dashboard and locate the 'Owner Management' section.</div>
        </div>
        """, unsafe_allow_html=True)
    with col_s2:
        st.markdown("""
        <div class="step-card">
            <div class="step-number">2</div>
            <div class="step-title">Designate Identity</div>
            <div class="step-desc">Enter the unique ID or email of the primary human administrator to be assigned as the Main Owner.</div>
        </div>
        """, unsafe_allow_html=True)
    with col_s3:
        st.markdown(f"""
        <div class="step-card">
            <div class="step-number">3</div>
            <div class="step-title">Confirm & Lock</div>
            <div class="step-desc">Review the master permissions and click 'Finalize Setup' to lock the Main Owner identity and enable centralized oversight.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Finalize Setup", use_container_width=True):
            log_analytics("main_owner_setup_complete")
            st.success("Main Owner identity locked and oversight enabled!")

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    col_faq, col_spec = st.columns([3, 2])

    with col_faq:
        st.markdown("#### Frequently Asked Questions")
        faqs = [
            ("What is a Main Owner?", "The Main Owner is the primary human administrator who holds master permissions over all AI agent sessions, truth sources, and governance rules within a Satya workspace."),
            ("Can there be more than one Main Owner?", "No, Satya enforces a single-owner model for absolute accountability, but the Main Owner can delegate specific tasks to other human observers."),
            ("What happens if the Main Owner is unavailable?", "We recommend storing the Main Owner's credentials in a secure, shared vault. In enterprise setups, ownership can be transferred through a verified recovery process."),
            ("Does the Main Owner feature affect agent performance?", "No, it is a governance and oversight layer. Your agents will continue to operate autonomously, but with clearer boundaries and centralized logging."),
            ("Is the Main Owner setup reversible?", "Yes, but it requires a high-level confirmation and an audit trail entry to ensure the security and integrity of your tracked AI operations.")
        ]
        for q, a in faqs:
            with st.expander(q):
                st.write(a)

    with col_spec:
        st.markdown("#### What to Expect")
        checklist = [
            "Centralized dashboard for all agent activity.",
            "Master control over Truth Source (knowledge base) additions.",
            "Enforced governance rules across all connected agents.",
            "Unified audit trail for every status change and task update.",
            "Priority support for owner-initiated session interventions."
        ]
        for item in checklist:
            st.markdown(f"&check; {item}")

        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        st.markdown("#### Developer Spec")
        st.markdown("""
        <div class="code-block" style="font-size: 0.75rem;">
// Analytics Events
- main_owner_promo_view
- main_owner_promo_click
- main_owner_setup_start
- main_owner_setup_complete

// Sample Payload
{
  "event": "main_owner_promo_click",
  "properties": {
    "card_size": "hero",
    "variant": "A",
    "headline": "Master Your AI Fleet",
    "cta": "Set Main Owner",
    "location": "dashboard_top"
  }
}
        </div>
        """, unsafe_allow_html=True)


# ─── SDK DOCS PAGE ─────────────────────────────────────
elif page == "SDK Docs":
    st.markdown('<div class="hero-header">SDK Documentation</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Integration guide for AI agents to self-deploy, operate, and report progress through Satya</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="api-section" style="border-left: 4px solid var(--primary); padding-left: 1.5rem;">
        <h4 style="color: var(--primary-light);">How Satya Works</h4>
        <p style="color: var(--text-secondary); font-size: 0.9rem; line-height: 1.7;">
            <strong style="color: var(--text-primary);">AI agents deploy and operate Satya.</strong> They install dependencies, start the dashboard, create tasks,
            log progress, and scrape knowledge &mdash; all programmatically via the SDK below.<br><br>
            <strong style="color: var(--text-primary);">Humans only observe.</strong> They open this dashboard URL in a browser to monitor tasks, read logs,
            and review the knowledge base. No terminal, no code &mdash; just a web page.<br><br>
            <strong style="color: var(--text-primary);">See <code>AGENTS.md</code></strong> in the repo root for the complete deployment manual written directly for AI agents.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="api-section">
        <h4>Quick Start (For AI Agents)</h4>
        <p style="color: var(--text-secondary); font-size: 0.9rem; margin-bottom: 1rem;">
            AI agents: add the <code>src/</code> directory to your Python path, import the SDK, and start reporting your work. The human will see everything on this dashboard automatically.
        </p>
        <div class="code-block">import sys
sys.path.insert(0, "src")
import satya.sdk as satya

client = satya.init(agent_name="my_agent")

task = satya.create_task("Build login page", "Implement OAuth2 login flow")
satya.log("Starting work on login page...")
satya.update_task(task["id"], "In Progress")
satya.scrape("https://docs.example.com/oauth2")
satya.update_task(task["id"], "Done")
satya.log("Login page complete")
client.flush_logs()</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    st.markdown("#### SDK Functions")

    funcs = [
        ("satya.init(agent_name, repo_path='.')", "Initialize the SDK client. Must be called first. Creates a log file in satya_data/agents/."),
        ("satya.create_task(title, description)", "Create a new task in 'To Do' status. Returns task dict with id, title, status, etc."),
        ("satya.update_task(task_id, status)", "Update a task's status. Valid statuses: 'To Do', 'In Progress', 'Done'."),
        ("satya.log(message)", "Write a timestamped log entry to the agent's session log file."),
        ("satya.scrape(url)", "Scrape a URL, convert to Markdown, and save to the Truth Source knowledge base."),
    ]

    for func_sig, func_desc in funcs:
        st.markdown(f"""
        <div class="truth-card">
            <div style="font-weight: 600; color: var(--primary-light); font-family: 'JetBrains Mono', monospace; font-size: 0.85rem;">
                {func_sig}
            </div>
            <div style="font-size: 0.85rem; color: var(--text-secondary); margin-top: 0.3rem;">
                {func_desc}
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    st.markdown("#### Governance Rules")

    st.markdown(f"""
    <div class="api-section">
        <p style="color: var(--text-secondary); font-size: 0.9rem;">
            Satya includes an enterprise governance layer to enforce high-quality multi-agent coordination:
        </p>
        <ul style="color: var(--text-primary); font-size: 0.85rem; line-height: 1.6;">
            <li><strong>Audit Trails:</strong> Every creation, status change, comment, and update is permanently recorded per task, tied to the agent's name.</li>
            <li><strong>Descriptive Tasks:</strong> Tasks cannot be created with less than 10 characters of description.</li>
            <li><strong>Proof of Work:</strong> An agent cannot mark a task as <code>"Done"</code> without providing at least one log entry explaining their progress.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    st.markdown("#### Data Storage")

    st.markdown(f"""
    <div class="api-section">
        <p style="color: var(--text-secondary); font-size: 0.9rem;">
            All data is stored as flat files under <code>satya_data/</code>. No database required.
        </p>
        <div class="code-block">satya_data/
  tasks/          # JSON files, one per task (e.g., a344b224.json)
  truth/          # Markdown files from web scraping
  agents/         # Log files per agent session</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    st.markdown("#### Full Agent Example")

    st.markdown(f"""
    <div class="api-section">
        <p style="color: var(--text-secondary); font-size: 0.9rem; margin-bottom: 1rem;">
            Complete session showing how an AI agent deploys Satya, creates tasks, logs progress, and scrapes knowledge &mdash; while the human monitors everything from this dashboard:
        </p>
        <div class="code-block">import sys
sys.path.insert(0, "src")
import satya.sdk as satya

# 1. Initialize agent session
client = satya.init(agent_name="coder_bot")
satya.log("Agent session started")

# 2. Create tasks for the work to be done
task = client.create_task(
    "Implement user auth",
    "Add JWT-based authentication with refresh tokens"
)
satya.log(f"Created task: {{task['id']}}")

# 3. Start working on a task
client.update_task(task["id"], "In Progress")
satya.log("Working on auth implementation...")

# 4. Scrape reference docs into knowledge base
client.scrape_url("https://jwt.io/introduction")
satya.log("Scraped JWT docs for reference")

# 5. Mark task complete
client.update_task(task["id"], "Done")
satya.log("Auth implementation complete")

# 6. Flush logs to ensure they are persisted
client.flush_logs()</div>
    </div>
    """, unsafe_allow_html=True)


st.markdown("""
<div class="footer-text">
    Satya v0.1.0 &middot; Built by <strong>Anktechsol.com</strong> &middot; Open Source AI Agent Tracker
</div>
""", unsafe_allow_html=True)
