# Satya - AI Agent Progress Tracker & Truth Source Manager

## Overview
Satya is an open-source dashboard and SDK for tracking AI agent progress, managing Agile tasks, and curating a "Truth Source" knowledge base via web scraping. All data is persisted locally as JSON/Markdown files.

## Project Architecture

### Directory Structure
```
app.py                    # Main Streamlit application (entry point)
AGENTS.md                 # Instructions for AI agents (deployment & SDK usage)
src/satya/                # Core library
  core/
    __init__.py           # Exports Tasks, Scraper, GitHandler, storage
    storage.py            # File-based storage (JSON/Markdown)
    tasks.py              # Agile task management with priorities
    scraper.py            # Web scraping → Markdown
    git_handler.py        # Git integration (graceful fallback)
  sdk/
    __init__.py           # SDK convenience functions
    client.py             # SatyaClient for agent integration
satya_data/               # Data directory
  tasks/                  # Task JSON files
  truth/                  # Scraped Markdown files
  agents/                 # Agent session logs
.streamlit/config.toml    # Streamlit server config
```

### Key Features
- **Dashboard**: Overview with task stats, completion metrics, charts
- **Task Board**: Kanban-style board with To Do / In Progress / Done columns, priorities, delete
- **Truth Source**: Web scraper that converts pages to Markdown knowledge base
- **Agent Logs**: Monitor autonomous agent sessions in real-time
- **SDK Docs**: In-app documentation for AI agent integration
- **Theme Toggle**: Dark/Light mode switch in sidebar
- **SDK**: Python API for agents (`satya.init()`, `satya.log()`, `satya.create_task()`)

### Tech Stack
- Python 3.11, Streamlit (UI), BeautifulSoup4 + markdownify (scraping), Pandas (data)
- File-based storage (JSON for tasks, Markdown for truth sources, plain text for logs)

### Theme System
- Dark/light theme toggle via sidebar button
- Theme state stored in `st.session_state.theme`
- CSS variables swap between dark and light color palettes

## Running
```
streamlit run app.py --server.port 5000
```

## Recent Changes
- 2026-02-07: Added dark/light theme toggle, SDK Docs page, AGENTS.md with full AI agent deployment instructions
- 2026-02-07: Initial setup with improved UI (dark theme, gradient branding, task priorities, delete functionality, dashboard overview with charts)
