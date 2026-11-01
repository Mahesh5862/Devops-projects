# **OpsSentry: Linux Change Detection and Incident Investigation System**

> **A Python-based DevOps and security monitoring tool for file integrity checking, Linux authentication-log analysis, and system health monitoring—with a Streamlit dashboard for visibility.**

---

## **1. Problem Statement**

Linux systems host applications, services, configuration files, and user data. Unexpected file changes, unsafe file permissions, repeated failed login attempts, and resource pressure can indicate configuration mistakes or potential security incidents.

When these checks are performed manually, it can be difficult to notice changes consistently, investigate events quickly, and keep monitoring results in one place. Small teams and learners may not have access to a full enterprise monitoring or security information and event management (SIEM) platform.

## **2. Why OpsSentry?**

OpsSentry brings several basic operational and security checks together in one lightweight Python project.

- **Detect file changes:** Compare monitored files with a saved baseline using SHA-256 hashes.
- **Highlight permission risks:** Identify permission changes and world-writable files in the monitored scope.
- **Review authentication activity:** Search supported Linux authentication logs for patterns such as failed logins and invalid users.
- **Check system health:** Capture CPU, memory, and root-disk usage.
- **Keep evidence in reports:** Save results as JSON so they can be reviewed later or displayed in a dashboard.
- **View results visually:** Use Streamlit to see system metrics and file-integrity findings in one interface.
- **Practice DevOps workflows:** Use Git, structured project files, and GitHub Actions if the workflow is included and enabled.

> OpsSentry is a lightweight monitoring and learning tool. It does not replace a production SIEM, endpoint detection platform, or full observability stack.

## **3. Solution Overview**

OpsSentry follows a simple workflow:

1. **Configure** the files and directories to monitor.
2. **Create a baseline** that records the current state of monitored files.
3. **Run checks** to compare current files with the baseline and look for selected authentication-log patterns.
4. **Collect system metrics** such as CPU, memory, and disk usage.
5. **Write reports** to JSON files in the `reports/` directory.
6. **Review findings** through the command line or Streamlit dashboard.
7. **Validate changes** and investigate unexpected events.

### **High-level workflow**

```text
Configuration
     |
     v
Monitored Files + Linux Logs + System Metrics
     |
     v
OpsSentry Python CLI
     |
     +--> File Integrity Checks (SHA-256 / permissions)
     +--> Authentication Log Pattern Checks
     +--> CPU / Memory / Disk Health
     |
     v
JSON Reports
     |
     v
Streamlit Dashboard + Manual Investigation
```

## **4. Key Features**

### **File Integrity Monitoring**
- Records a baseline for configured files.
- Detects added, deleted, or modified files within the monitored scope.
- Uses SHA-256 hashes to help identify content changes.
- Reports permission changes and world-writable files where implemented.

### **Linux Authentication-Log Analysis**
- Searches the configured/supported authentication log for selected text patterns such as failed password attempts, authentication failures, and invalid users.
- Helps surface events for manual review.
- Results depend on the Linux distribution, log location, and the permissions of the account running the tool.

### **System Health Monitoring**
- Captures CPU usage, memory usage, and root filesystem disk usage.
- Saves a snapshot to a JSON report for later review.
- Metrics are point-in-time readings, not continuous monitoring.

### **Dashboard and Reports**
- Displays available health metrics and file-integrity findings in a Streamlit interface.
- Stores results as JSON under `reports/`.
- Makes it easier to review findings without manually opening every report.

## **5. Technology Stack**

| Technology | Purpose |
|---|---|
| **Python** | Main implementation language for the CLI and monitoring logic |
| **psutil** | Collects CPU, memory, and disk usage metrics |
| **Streamlit** | Provides the web-based monitoring dashboard |
| **JSON** | Stores baselines and generated monitoring reports |
| **SHA-256 / `hashlib`** | Helps detect file-content changes |
| **Linux / Ubuntu / WSL** | Provides the operating-system environment and authentication logs |
| **Git and GitHub** | Source control and project hosting |
| **GitHub Actions** | Optional CI checks when the workflow is present and enabled |
| **HTML/CSS via Streamlit** | Dashboard presentation, where applicable |

**Note:** Confirm the dependencies and CI workflow in the actual project before claiming every item is implemented. The core Python standard library may also be used for file traversal, permissions, hashing, and JSON handling.

## **6. Project Structure**

The following is a representative structure. Keep the README aligned with the folders and files actually present in your repository.

```text
devops-projects/
├── README.md
└── 01-OpsSentry/
    ├── README.md
    ├── requirements.txt
    ├── config/
    │   └── monitored_files.txt
    ├── src/
    │   └── opssentry.py
    ├── dashboard/
    │   └── app.py
    ├── data/
    │   └── baseline.json
    ├── lab/
    │   └── important.conf
    ├── reports/
    │   ├── latest_report.json
    │   └── health_report.json
    ├── screenshots/
    │   ├── Screenshot (381).png
    │   └── Screenshot (382).png
    └── .github/
        └── workflows/
            └── opssentry-ci.yml
```

### **What the folders are for**

- `config/` — paths or settings that determine what is monitored.
- `src/` — command-line application and monitoring logic.
- `dashboard/` — Streamlit dashboard code.
- `data/` — saved baseline data used by integrity checks.
- `lab/` — sample files used for safe testing.
- `reports/` — generated JSON output; review before publishing because it may contain sensitive details.
- `screenshots/` — screenshots showing the application or dashboard.
- `.github/workflows/` — GitHub Actions workflow files, if configured.
- `requirements.txt` — Python packages needed to run the project.
- `README.md` — documentation for installation, commands, design, and limitations.

## **7. Installation and Setup**

Run commands from the `01-OpsSentry` directory in Ubuntu/WSL or a compatible Linux environment.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Check which commands are available in the current version:

```bash
python src/opssentry.py --help
```

## **8. Running OpsSentry**

The following are the command names used in this project. If your current CLI version displays different arguments in `--help`, follow that output.

```bash
# Create or refresh the baseline
python src/opssentry.py baseline

# Compare monitored files with the baseline
python src/opssentry.py check

# Analyze supported authentication logs
python src/opssentry.py logs

# Capture system health metrics
python src/opssentry.py health
```

Some log checks may require additional permissions or a compatible log file. Only run monitoring against systems and files you own or are authorized to inspect.

## **9. Launching the Dashboard**

From the project root:

```bash
streamlit run dashboard/app.py
```

Open the URL shown in the terminal. It is commonly:

```text
http://localhost:8501
```

Run the CLI commands first if the dashboard expects JSON reports that do not yet exist.

## **10. Example Use Case**

A system administrator updates a monitored configuration file. During the next integrity check, OpsSentry compares the current file against the saved baseline and reports a change. The administrator reviews whether the change was expected, checks the file's permissions, and inspects relevant authentication-log findings and system health metrics.

This supports investigation; a detected change alone does not prove malicious activity.

## **11. Security and Best Practices**

- Never commit passwords, API keys, access tokens, `.env` files, or private keys.
- Do not publish raw authentication logs or reports containing personal data, internal IP addresses, usernames, or other sensitive details.
- Exclude `.venv/`, `__pycache__/`, and compiled Python files using `.gitignore`.
- Keep sample test files free of real credentials.
- Use least privilege; do not run the whole tool as root unless a specific check requires it.
- Review and test the implementation before using it in production.

Suggested `.gitignore` entries:

```gitignore
**/.venv/
**/__pycache__/
**/*.py[cod]
**/.env
```

## **12. Limitations and Future Improvements**

### Current limitations
- Log detection is pattern-based and can miss events or produce false positives.
- Available authentication logs differ by Linux distribution and system configuration.
- System metrics are snapshots rather than continuous time-series monitoring.
- Integrity checks only cover configured paths and depend on a trustworthy baseline.
- The tool is a learning/demo project, not a replacement for enterprise security or observability products.

### Possible future improvements
- Add configurable alert thresholds and notifications.
- Add scheduled checks using cron or systemd timers.
- Add richer event filtering and timestamps.
- Add charts for historical system-health trends.
- Add tests and stronger validation for malformed or missing reports.
- Add optional integrations with alerting or log-management platforms.

## **13. DevOps Concepts Demonstrated**

- Linux command-line operation and log locations.
- Python scripting and dependency management.
- File integrity and basic operational security checks.
- JSON-based data exchange and reports.
- Dashboarding with Streamlit.
- Git version control and GitHub repository management.
- CI automation with GitHub Actions, if the workflow is present and enabled.
- Documentation and repository hygiene.

## **14. Author**

**Mahesh Pittala**  
GitHub: [Mahesh5862](https://github.com/Mahesh5862)

## **15. License**

No license is specified by this README. Add a `LICENSE` file if you want others to use, modify, and distribute the project under an explicit open-source license.
