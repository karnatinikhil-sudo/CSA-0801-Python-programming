<div align="center">

# 🌿 Digital To-Do &amp; Wellness Manager
### Full-Stack Task Execution & Active Health Tracking Web Application

[![CI Pipeline](https://github.com/karnatinikhil-sudo/CSA-0801-Python-programming/actions/workflows/ci.yml/badge.svg)](https://github.com/karnatinikhil-sudo/CSA-0801-Python-programming/actions)
[![Python Version](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-6.1%20%2F%205.1-092E20.svg?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Celery](https://img.shields.io/badge/Celery-5.6%20%2B%20Redis-37814A.svg?logo=celery&logoColor=white)](https://docs.celeryq.dev/)
[![Docker](https://img.shields.io/badge/Docker-Ready%20%2F%20Compose-2496ED.svg?logo=docker&logoColor=white)]()
[![PWA](https://img.shields.io/badge/PWA-Ready%20%2F%20Offline%20Cache-5A0FC8.svg)]()
[![Open Source Love](https://badges.frapsoft.com/os/v1/open-source.svg?v=103)](https://github.com/karnatinikhil-sudo/CSA-0801-Python-programming)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

*A modern, open-source full-stack Python web application designed for everyone. It bridges high-velocity task management with active health monitoring, hydration tracking, medication adherence regimens, background Celery notifications, and visual analytics dashboards.*

</div>

---

## 🌟 Key Application Features

### 1. ⚡ Task Input & Execution Module
- **Ultra-Fast Task Creation (< 10 seconds)**: Streamlined single-input with auto-focus, sensible defaults, and natural language understanding (e.g. typing `"Submit quarterly audit every Friday at 5pm high priority #Work"` auto-populates due date, time, priority, and category).
- **Single-Tap Checkbox Toggle**: Toggle tasks between Pending, In Progress, and Completed instantly via AJAX without page reloads.
- **Precision Time Tracking**: Tracks duration from creation/start to completion (e.g., `"Completed in 2h 15m"` or `"In progress for 45m"`), feeding into completion velocity trend graphs.
- **Inline Plain-Language Validation**: Friendly, human-readable guidance preventing invalid dates or negative intervals.

### 2. 💧 Health & Wellness Module (Central Dashboard Spotlight)
- **Central Placement**: Positioned prominently in the middle of the dashboard so users are reminded to care for their physical & mental wellbeing every time they review tasks.
- **Hydration Tracker**: Real-time water tracker with a progress ring, daily goals (default 8 glasses), active work hours filter, and 1-tap `+1 Glass` quick logging.
- **Rotating Wellness Tips Pool**: 16+ actionable micro-tips covering posture adjustments, 20-20-20 eye strain breaks, deep breathing exercises, and stretching routines.
- **Medication Tracker & Adherence**: Track multiple medications with independent schedules, 1-tap `Taken` / `Skipped` / `Snooze 15m` responses, and 7-day adherence scorecard (e.g. `"You've taken 6 of 7 doses this week (86%)"`).
- **Adaptive UI**: For users with no active medications, the health card cleanly displays hydration and wellness tips with zero clutter.

### 3. 🔔 Background Jobs & Escalating Reminders
- **Celery + Redis Engine**: Background worker automatically scans approaching task deadlines and medication schedules every minute.
- **3-Stage Escalating Alerts**:
  - **Stage 1 (Gentle)**: Friendly notification 30 minutes before the due time.
  - **Stage 2 (Urgent)**: Loud audible chime and high-priority browser push alert at deadline.
  - **Stage 3 (Overdue)**: Persistent visual warning when past due time.
- **Alarm-Style Web Push & Audio Chimes**: Web Audio API alarm sound synthesizer chime for urgent alerts and medication doses.

### 4. 📊 Dashboard & Downloadable Reports
- **Visual KPI Metric Cards**: Total Tasks, Pending, Completed, Overdue, Average Completion Time, and Hydration Level.
- **Chart.js Analytics**: Donut chart for status breakdown, Bar chart for priority distribution, and 7-day completion velocity graph.
- **Exportable Reports**: Filterable task history with downloadable **CSV** and **PDF** reports (generated dynamically via ReportLab).

### 5. 📅 Calendar & Alarm Integration
- **Universal `.ics` Export**: 1-tap "Add to Calendar" for individual tasks, full task archives, or medication schedules.
- **Google Calendar OAuth Sync**: Push events directly to Google Calendar.
- **Two-Way Conflict Awareness**: Flags overlapping schedule conflicts before saving a task.

### 6. 📱 Progressive Web App (PWA) Support
- Fully installable on Android, iOS, and Desktop with offline caching via Service Worker (`sw.js`).

---

## 🛠️ Tech Stack & Architecture

- **Backend**: Python 3.10+ / Django 6.1 & 5.1
- **Database**: MySQL (Production PyMySQL driver) / SQLite3 (Zero-setup local development)
- **Background Worker & Broker**: Celery 5.6 + Redis
- **Frontend**: HTML5, Vanilla CSS3, Modern JavaScript (ES6+), Bootstrap 5.3, Bootstrap Icons, Chart.js
- **Calendar & Reports**: iCalendar, ReportLab, Web Audio API
- **Authentication**: Django Auth (Custom UserProfile, Email / Username login, Password Reset)

---

## 🏛️ Project Directory Structure

```
CSA-0801-Python-programming/
├── .github/                               # GitHub Actions CI & Issue Templates
│   ├── workflows/ci.yml                   # Automated Multi-Python Matrix CI Pipeline
│   └── ISSUE_TEMPLATE/                    # Bug report & Feature request templates
├── apps/                                  # Django Pluggable Applications
│   ├── accounts/                          # User authentication, profiles, & preferences
│   ├── calendar_sync/                     # iCalendar (.ics) exports, Google Calendar sync
│   ├── dashboard/                         # Central dashboard, Chart.js stats, & KPI views
│   ├── health/                            # Hydration logging, medication schedules, wellness tips
│   ├── reminders/                         # Celery periodic jobs, push notifications, chimes
│   └── tasks/                             # Task CRUD, tags, filters, NLP parsing, & ICS exports
├── core/                                  # Project Configuration & Settings
│   ├── settings.py                        # Django configuration (SQLite/MySQL dual support)
│   ├── urls.py                            # Root URL routing
│   ├── celery.py                          # Celery application & beat scheduler setup
│   ├── wsgi.py / asgi.py                  # Web server gateway interfaces
│   └── __init__.py                        # Core package initialization
├── fixtures/                              # Seed datasets
│   └── wellness_tips.json                 # Initial wellness & hydration tips pool
├── static/                                # Static assets
│   ├── css/style.css                      # Custom theme, animations & responsive styles
│   ├── icons/                             # PWA application icons (192x192, 512x512)
│   ├── js/app.js                          # AJAX toggles, Web Audio chime, NLP parser
│   ├── js/charts.js                       # Chart.js analytics graphs
│   ├── js/sw.js                           # Service worker for offline PWA
│   └── manifest.json                      # Web App Manifest
├── templates/                             # HTML5 Django Templates
│   ├── accounts/                          # Login, signup, password reset, profile
│   ├── base.html                          # Root master layout
│   ├── calendar_sync/                     # Google Calendar sync settings
│   ├── components/                        # Navbars, PWA banners, audio notifications
│   ├── dashboard/                         # Dashboard & downloadable reports
│   ├── health/                            # Hydration & medication management
│   ├── offline.html                       # PWA offline fallback template
│   └── tasks/                             # Task lists, quick-add modal, filters
├── tests/                                 # Automated Test Suite
│   ├── test_calendar_sync.py              # Calendar export & sync tests
│   ├── test_health.py                     # Hydration & medication tests
│   ├── test_reminders.py                  # Reminder & Celery task tests
│   └── test_tasks.py                      # Task CRUD & NLP parser tests
├── Dockerfile                             # Production Docker Container
├── docker-compose.yml                     # 1-Command Multi-Service Compose Setup
├── manage.py                              # Django CLI management script
├── requirements.txt                       # Full Python dependencies
├── .env.example                           # Sample environment configuration
├── CONTRIBUTING.md                        # Open-source contribution guidelines
├── CODE_OF_CONDUCT.md                     # Contributor Code of Conduct
├── SECURITY.md                            # Security policy
├── LICENSE                                # MIT License
└── README.md                              # Complete documentation
```

---

## 🚀 Quick Start Guide

### Option A: 🐳 Run with Docker (Recommended for Anyone)
The easiest way for anyone to run the full application with Redis & Celery:

```bash
# 1. Clone the repository
git clone https://github.com/karnatinikhil-sudo/CSA-0801-Python-programming.git
cd CSA-0801-Python-programming

# 2. Start all services in 1 command
docker compose up --build
```
Open **`http://localhost:8000/`** in your browser!

---

### Option B: 🐍 Run Locally with Python

#### 1. Clone & Set Up Virtual Environment
```bash
git clone https://github.com/karnatinikhil-sudo/CSA-0801-Python-programming.git
cd CSA-0801-Python-programming

python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

#### 2. Run Database Migrations & Seed Data
```bash
python manage.py migrate
python manage.py loaddata fixtures/wellness_tips.json
```

#### 3. Launch the Server
```bash
python manage.py runserver
```
Visit **`http://127.0.0.1:8000/`** to get started!

---

## 🧪 Running Automated Tests

```bash
# Run tests with Django test runner:
python manage.py test tests/

# Or using pytest:
pytest
```

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!
Check out the [CONTRIBUTING.md](CONTRIBUTING.md) guide and feel free to submit a Pull Request.

---

## 📄 License

This project is open source and available to everyone under the **[MIT License](LICENSE)**.

Maintained by **[Nikhil Karnati](https://github.com/karnatinikhil-sudo)**.