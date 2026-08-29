<div align="center">

# 🌿 Digital To-Do &amp; Wellness Manager
### *High-Velocity Task Execution Meets Proactive Health & Habit Intelligence*

<br/>

<img src="docs/hero_banner.jpg" alt="Digital To-Do & Wellness Manager Dashboard" width="100%" style="border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.25);" />

<br/>
<br/>

[![CI Pipeline](https://github.com/karnatinikhil-sudo/CSA-0801-Python-programming/actions/workflows/ci.yml/badge.svg)](https://github.com/karnatinikhil-sudo/CSA-0801-Python-programming/actions)
[![Python Version](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-6.1%20%2F%205.1-092E20.svg?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Celery](https://img.shields.io/badge/Celery-5.6%20%2B%20Redis-37814A.svg?logo=celery&logoColor=white)](https://docs.celeryq.dev/)
[![Docker](https://img.shields.io/badge/Docker-Ready%20%2F%20Compose-2496ED.svg?logo=docker&logoColor=white)](docker-compose.yml)
[![Database](https://img.shields.io/badge/Database-MySQL%20%2F%20SQLite3-003B57.svg?logo=sqlite&logoColor=white)]()
[![PWA](https://img.shields.io/badge/PWA-Ready%20%2F%20Offline%20Cache-5A0FC8.svg)]()
[![Tests](https://img.shields.io/badge/Tests-Passing%20(100%25)-brightgreen.svg?logo=pytest&logoColor=white)](tests/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)]()

<br/>

**Digital To-Do & Wellness Manager** is a production-ready, full-stack Python web application designed to solve burnout and cognitive overload in modern workflows. By seamlessly integrating **frictionless natural-language task management** with a **centralized health spotlight** (hydration tracking, medication adherence, and ergonomics reminders), the system ensures productivity never comes at the cost of personal wellbeing.

[Key Features](#-key-features) • [System Architecture](#-system-architecture) • [Live Quickstart](#-quick-start) • [Database Schema](#-database-schema) • [API Matrix](#-api--routes-matrix) • [Author](#-author--maintainer)

</div>

---

## 💡 The Problem & The Solution

| The Problem | How Digital To-Do & Wellness Solves It |
|---|---|
| ⏳ **Friction in Task Capture**: Complex forms with 10 inputs cause users to abandon task tracking. | **⚡ Natural Language Processing**: Type `"Prepare quarterly audit every Friday at 5pm high priority #Finance"` and all fields auto-populate in < 10 seconds. |
| 🪑 **Sedentary Burnout & Neglected Health**: Traditional to-do apps encourage non-stop work without physical health cues. | **💧 Central Wellness Spotlight**: Real-time hydration progress ring, rotating posture/eye-strain breaks, and 1-tap medication logging directly on the main dashboard. |
| 🔔 **Notification Fatigue & Missed Deadlines**: Ignored static notification banners lead to overdue tasks. | **🔊 3-Stage Escalating Audio Reminders**: Gentle 30-min alert $\rightarrow$ Loud synthesized Web Audio chime $\rightarrow$ Persistent overdue warning. |
| 📊 **Lack of Completion Insights**: Users don't know where their time goes. | **📈 Precision Duration Tracking & Chart.js**: Measures exact minutes spent per task with downloadable **PDF & CSV** analytics reports. |

---

## 🌟 Key Features

### 1. ⚡ Ultra-Fast Task Management
- **NLP Input Engine**: Client-side regex & keyword tokenizer that extracts titles, deadlines, repeat schedules (`daily`, `weekly`, `weekdays`), priority tags (`#High`, `#Low`), and categories in real-time.
- **Single-Tap AJAX Toggles**: Check off tasks between `Pending`, `In Progress`, and `Completed` with zero page reloads.
- **Precision Time Tracking**: Tracks exact duration from task creation to completion (e.g., `"Completed in 1h 45m"`), generating velocity metrics.
- **Universal `.ics` Calendar Export**: 1-click download of calendar invites for Google Calendar, Apple Calendar, and Outlook.

### 2. 💧 Proactive Health & Wellness Dashboard
- **Interactive Hydration Ring**: SVG progress ring visualizing daily water consumption against customizable goals (default 8 glasses) with quick `+1 Glass` logging.
- **16+ Rotating Wellness Tips**: Micro-breaks for 20-20-20 eye strain, posture alignment, breathing exercises, and hydration nudges.
- **Medication Adherence Regimen**: Track daily medication doses with 1-tap `Taken` / `Skipped` / `Snooze 15m` actions and a rolling 7-day adherence scorecard.

### 3. 🔔 Background Celery Workers & Alarm Chimes
- **Celery Beat Cron**: Scans approaching task deadlines and medication windows every 60 seconds.
- **Web Audio API Chime**: Client-side audio synthesizer producing a distinct dual-tone chime without external audio file dependencies.
- **Web Push Notifications**: Service Worker integration for system notifications even when the browser tab is idle.

### 4. 📊 Downloadable Reports & Data Visualizations
- **Chart.js Dashboards**: Donut charts for status breakdown, priority distribution bars, and 7-day completion velocity curves.
- **Dynamic PDF Generation**: High-resolution branded reports generated server-side using **ReportLab**.
- **Structured CSV Export**: Instant export of filtered task history for spreadsheet analysis.

### 5. 📱 Progressive Web App (PWA)
- Offline support via Service Worker caching (`sw.js`).
- Standalone app-like windowing on Windows, macOS, Android, and iOS.

---

## 🏛️ System Architecture

```mermaid
flowchart TD
    subgraph Client["💻 Client Browser & Mobile PWA"]
        UI["Bootstrap 5.3 Responsive UI"]
        NLP["Client-Side NLP Task Parser"]
        Audio["Web Audio Synthesizer Chime"]
        SW["Service Worker (PWA Offline Cache)"]
    end

    subgraph Backend["⚙️ Django Web Server"]
        Auth["Django Auth & User Profiles"]
        TaskEngine["Task CRUD & Filter Engine"]
        HealthEngine["Hydration & Medication Tracker"]
        ReportEngine["ReportLab PDF & CSV Generator"]
        CalendarSync["iCalendar .ics / Google OAuth"]
    end

    subgraph Async["⚡ Background Worker (Celery & Redis)"]
        Redis[("Redis Message Broker")]
        CeleryWorker["Celery Asynchronous Worker"]
        CeleryBeat["Celery Beat Task Scheduler (1 min)"]
    end

    subgraph Storage["🗄️ Database Layer"]
        DB[("MySQL / SQLite3 Database")]
    end

    UI --> NLP --> TaskEngine
    UI --> HealthEngine
    UI --> ReportEngine
    UI --> CalendarSync
    TaskEngine --> DB
    HealthEngine --> DB
    Auth --> DB

    CeleryBeat -->|Push Due Reminders| Redis
    Redis -->|Consume Task| CeleryWorker
    CeleryWorker -->|Trigger Push & Chime| UI
```

---

## 🗄️ Database Schema

```mermaid
erDiagram
    User ||--o| UserProfile : has
    User ||--o{ Task : owns
    User ||--o{ Medicine : tracks
    User ||--o{ HydrationLog : logs
    Task ||--o{ TaskTag : categorized_by
    Medicine ||--o{ DoseLog : records
    Task ||--o{ ReminderLog : notifies

    UserProfile {
        int id PK
        int user_id FK
        int daily_water_goal
        int reminder_window_minutes
        string theme_preference
    }

    Task {
        int id PK
        string title
        string priority
        string status
        datetime due_datetime
        int estimated_minutes
        datetime completed_at
    }

    HydrationLog {
        int id PK
        int user_id FK
        date log_date
        int glasses_count
    }

    Medicine {
        int id PK
        string name
        string dosage
        time scheduled_time
    }

    DoseLog {
        int id PK
        int medicine_id FK
        date dose_date
        string status
    }
```

---

## 🚀 Quick Start

### Option A: 🐳 Docker One-Liner (Recommended for Everyone)

Run the entire application with Redis and Celery in a single command:

```bash
git clone https://github.com/karnatinikhil-sudo/CSA-0801-Python-programming.git
cd CSA-0801-Python-programming

docker compose up --build
```
> Open **`http://localhost:8000/`** in your browser!

---

### Option B: 🐍 Local Python Setup

```bash
# 1. Clone repository
git clone https://github.com/karnatinikhil-sudo/CSA-0801-Python-programming.git
cd CSA-0801-Python-programming

# 2. Create virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Initialize database and load seed tips
python manage.py migrate
python manage.py loaddata fixtures/wellness_tips.json

# 5. Start development server
python manage.py runserver
```
> Open **`http://127.0.0.1:8000/`** to interact with the application.

---

## 🔑 Demo Login Credentials

For quick testing without creating a new account:
- **Username**: `demouser_e2e`
- **Password**: `DemoPass123!`

*(You can also click **Sign Up** on the login screen to create a custom profile instantly).*

---

## 🧪 Automated Testing Suite

The repository includes a test suite covering task management, natural language parsing, hydration tracking, medication adherence, reminders, and calendar exports.

```bash
# Run tests with Django test runner
python manage.py test tests/

# Run tests with pytest
pytest -v
```

---

## 📋 API & Routes Matrix

| Endpoint | Method | Description |
|---|---|---|
| `/` | `GET` | Central Dashboard with Hydration Ring, Task KPIs & Wellness Tips |
| `/tasks/` | `GET`, `POST` | Task List View, Filters, and New Task Creation |
| `/tasks/<id>/toggle/` | `POST` | AJAX single-tap task status toggle (`Pending` $\leftrightarrow$ `Completed`) |
| `/tasks/<id>/ics/` | `GET` | Download universal `.ics` calendar file for a specific task |
| `/health/water/increment/` | `POST` | AJAX 1-tap logging of `+1 Glass` of water |
| `/health/medicines/` | `GET`, `POST` | Medication schedule & 7-day adherence scorecard |
| `/health/medicines/<id>/dose/` | `POST` | Record dose status (`taken`, `skipped`, `snoozed`) |
| `/reports/` | `GET` | Performance analytics page with PDF and CSV export links |
| `/reports/pdf/` | `GET` | Generates dynamic ReportLab PDF summary |
| `/reports/csv/` | `GET` | Exports complete task history as CSV |
| `/calendar/settings/` | `GET`, `POST` | Google Calendar OAuth 2.0 synchronization settings |
| `/accounts/profile/` | `GET`, `POST` | User profile, notification preferences & custom water goals |

---

## 🛠️ Technology Stack

```
Frontend:    HTML5 • Vanilla CSS3 • Modern JavaScript (ES6+) • Bootstrap 5.3 • Chart.js
Backend:     Python 3.10-3.14 • Django 6.1 / 5.1 • Django ORM • PyMySQL / SQLite3
Async Jobs:  Celery 5.6 • Redis 7.x • Celery Beat Periodic Scheduler
Reports:     ReportLab PDF Engine • iCalendar Engine • Web Audio API Chimes
DevOps:      Docker • Docker Compose • GitHub Actions CI/CD • PWA Service Workers
```

---

## 🤝 Open Source & Contributing

Contributions, issues, and feature suggestions are always welcome!
1. Fork the repository
2. Create your branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'feat: add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

Please review our [CONTRIBUTING.md](CONTRIBUTING.md) and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

---

## 👨‍💻 Author & Maintainer

<div align="center">

### **Nikhil Karnati**
*Full-Stack Engineer & Python Developer*

[![GitHub](https://img.shields.io/badge/GitHub-karnatinikhil--sudo-181717?style=flat&logo=github)](https://github.com/karnatinikhil-sudo)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?style=flat&logo=linkedin)](https://linkedin.com)
[![Portfolio](https://img.shields.io/badge/Portfolio-Visit%20Site-4F46E5?style=flat&logo=google-chrome&logoColor=white)](https://github.com/karnatinikhil-sudo)

</div>

---

## 📄 License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for more information.