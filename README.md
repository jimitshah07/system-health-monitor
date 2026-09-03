# System Health Monitor

A lightweight, unattended system monitoring tool built in Python — collects live CPU, memory, disk, and network stats, logs them on a schedule, fires alerts (email + Slack) when CPU stays high for a sustained period, and serves a simple live dashboard over HTTP.

Built as a hands-on project to go deep on OS internals, Python, and the fundamentals real cloud/monitoring tools (Datadog, CloudWatch, Zabbix) are built on — not just to produce a script, but to understand *why* each piece works the way it does.

## Features

- **Metrics collection** — CPU, memory, disk, and network I/O via [`psutil`](https://github.com/giampaolo/psutil), reading straight from the OS's own performance counters
- **Persistent logging** — every reading appended to a CSV file, UTC-timestamped, safe for concurrent scheduled runs
- **Unattended scheduling** — runs automatically every 5 minutes via Windows Task Scheduler (equivalent to `cron`/`systemd timer` on Linux), silently via `pythonw.exe`
- **Threshold-based alerting** — flags CPU usage sustained above a threshold across consecutive readings (not just a single spike), reading its own recent history back from the CSV log since each scheduled run is a fresh process with no memory of the last
- **Dual alert channels** — sends a real email (SMTP over Gmail) *and* posts to a Slack channel via an incoming webhook when an alert fires
- **Live dashboard** — a minimal Flask web app renders the most recent logged reading as an HTML page

## Tech stack

Python 3.12 · `psutil` · `smtplib` · `requests` · Flask · Jinja2 · Windows Task Scheduler

## Sample output

**Console output (single run):**
```
[2026-09-03T09:56:22.266612+00:00] CPU 5.5% | Mem 60.6% | Disk 87.2%
OK:CPU ACTING NORMAL :[5.5, 4.9]
```

**CSV log (`system_health_log.csv`):**
```
timestamp,cpu_percent,memory_percent,memory_available_gb,memory_total_gb,disk_percent,disk_free_gb,disk_total_gb,net_sent_mb,net_recv_mb
2026-09-03T09:56:22.266612+00:00,5.5,60.6,6.18,15.68,87.2,33.15,275.02,510.42,905.11
```

**Dashboard (`http://127.0.0.1:5000`):**

_[Add a screenshot here — e.g. `dashboard-screenshot.png` — showing the live page from your browser]_

**Alert (Slack):**

_[Add a screenshot here of the Slack message landing in your channel]_

## Project structure

```
Project 4 System Health Monitor/
├── system_health_monitor_project4.py   # collects stats, logs to CSV, checks thresholds, sends alerts
├── dashboard.py                        # Flask app serving the live dashboard
├── templates/
│   └── dashboard.html                  # Jinja2 template for the dashboard page
└── system_health_log.csv               # generated log file (grows over time)
```

## Setup

1. **Clone the repo**
   ```
   git clone https://github.com/jimitshah07/system-health-monitor.git
   cd system-health-monitor
   ```

2. **Install dependencies**
   ```
   pip install psutil flask requests
   ```

3. **Set environment variables** (never hardcode credentials — see Security notes below)

   | Variable | Purpose |
   |---|---|
   | `EMAIL_ADDRESS` | Gmail address alerts are sent from/to |
   | `EMAIL_APP_PASSWORD` | Gmail [App Password](https://myaccount.google.com/apppasswords) (requires 2-Step Verification) |
   | `SLACK_WEBHOOK_URL` | Incoming webhook URL from your Slack app |

   On Windows: System Properties → Advanced → Environment Variables → add under "User variables", then log off/on for the change to take effect in any already-running session.

4. **Run once manually** to confirm everything works:
   ```
   python system_health_monitor_project4.py
   ```

5. **Schedule it** (Windows Task Scheduler):
   - Program: `pythonw.exe` (windowless — no console flash on each run)
   - Arguments: full path to `system_health_monitor_project4.py`, in quotes
   - Trigger: Daily, repeat every 5 minutes, indefinitely

6. **Run the dashboard**
   ```
   python dashboard.py
   ```
   Then visit `http://127.0.0.1:5000` in a browser.

## How it works

Each scheduled run is a fresh, independent process — it collects one reading, logs it, and exits. Since nothing persists in memory between runs, sustained-threshold detection works by reading back the last few rows from the CSV log itself and checking whether they were *all* over the threshold — the same core idea behind Prometheus's `for: 5m` alerting clause.

## Known limitations

- Flask's built-in development server is used for the dashboard — fine for local/personal use, **not** intended for production traffic (`debug=True` in particular should never be enabled outside a private dev machine, since it exposes an interactive Python console in the browser on error)
- Dashboard shows the most recently *logged* reading (up to 5 minutes stale), not a live-polled value
- File paths are currently Windows-specific (`C:\\` for disk usage) — would need adjusting for Linux/Mac
- CSV grows unbounded over time — no rotation/archiving implemented yet

## Author

Jimit Shah — built as part of a hands-on cloud support / L1-L2 portfolio track, alongside an [L1/L2 troubleshooting runbook project](https://github.com/jimitshah07/l1l2-troubleshooting-runbook).
