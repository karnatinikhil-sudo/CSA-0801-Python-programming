<div align="center">

# 🌿 Digital To-Do &amp; Wellness Manager
### Full-Stack Task Management & Active Health Tracking Web Application

[![Python Version](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-6.1%20%2F%205.1-092E20.svg?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Celery](https://img.shields.io/badge/Celery-5.6%20%2B%20Redis-37814A.svg?logo=celery&logoColor=white)](https://docs.celeryq.dev/)
[![Database](https://img.shields.io/badge/Database-MySQL%20%2F%20SQLite3-003B57.svg?logo=sqlite&logoColor=white)]()
[![PWA](https://img.shields.io/badge/PWA-Ready%20%2F%20Offline%20Cache-5A0FC8.svg)]()
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

*A production-ready full-stack Python web application that combines streamlined task execution with proactive health monitoring, hydration tracking, medication adherence regimens, background Celery notifications, and visual analytics dashboards.*

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
├── manage.py                              # Django CLI management script
├── requirements.txt                       # Full Python dependencies
├── .env.example                           # Sample environment configuration
├── .gitignore                             # Git ignore rules
├── LICENSE                                # MIT License
└── README.md                              # Complete documentation
```

---

## 🚀 Quick Start Guide

### 1. Clone the Repository
```bash
git clone https://github.com/karnatinikhil-sudo/CSA-0801-Python-programming.git
cd CSA-0801-Python-programming
```

### 2. Set Up Virtual Environment & Dependencies
```bash
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

### 3. Run Database Migrations & Seed Data
```bash
python manage.py migrate
python manage.py loaddata fixtures/wellness_tips.json
```

### 4. Create Superuser (Optional)
```bash
python manage.py createsuperuser
```

### 5. Launch the Development Server
```bash
python manage.py runserver
```
Open **`http://127.0.0.1:8000/`** in your browser!

### 6. (Optional) Run Celery Background Worker & Beat
```bash
# Terminal 1: Celery Worker
celery -A core worker -l info

# Terminal 2: Celery Beat Scheduler
celery -A core beat -l info
```
*(Note: If Redis is not running locally, setting `CELERY_TASK_ALWAYS_EAGER = True` in `.env` executes background tasks synchronously).*

---

## 🧪 Running Automated Tests

Run the test suite across all modules:

```bash
# Run tests with Django test runner:
python manage.py test tests/

# Or using pytest:
pytest
```

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

Developed by **Nikhil Karnati**.