
#!/usr/bin/env python3

import hashlib
import json
import psutil
import stat
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
CONFIG_FILE = PROJECT_DIR / "config" / "monitored_files.txt"
BASELINE_FILE = PROJECT_DIR / "data" / "baseline.json"
REPORT_FILE = PROJECT_DIR / "reports" / "latest_report.json"
AUTH_LOG_FILE = Path("/var/log/auth.log")
HEALTH_REPORT_FILE = PROJECT_DIR / "reports" / "health_report.json"


def current_time():
    return datetime.now(timezone.utc).isoformat()


def file_details(path):
    info = path.stat()

    return {
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "permissions": oct(stat.S_IMODE(info.st_mode)),
        "size_bytes": info.st_size,
    }


def monitored_files():
    if not CONFIG_FILE.exists():
        raise FileNotFoundError(
            f"Missing configuration: {CONFIG_FILE}"
        )

    files = {}
    missing_paths = []

    for line in CONFIG_FILE.read_text().splitlines():
        line = line.strip()

        if not line or line.startswith("#"):
            continue

        original_path = PROJECT_DIR / line

        if original_path.is_symlink():
            print(f"WARNING: Skipping symbolic link: {line}")
            continue

        path = original_path.resolve()

        if not path.is_relative_to(PROJECT_DIR):
            raise ValueError(
                f"Path outside project is not allowed: {line}"
            )

        if path.is_file():
            files[path.relative_to(PROJECT_DIR).as_posix()] = path

        elif path.is_dir():
            for item in path.rglob("*"):
                if item.is_symlink():
                    continue

                if item.is_file():
                    resolved = item.resolve()

                    if resolved.is_relative_to(PROJECT_DIR):
                        name = resolved.relative_to(
                            PROJECT_DIR
                        ).as_posix()
                        files[name] = resolved

        else:
            missing_paths.append(line)

    if not files and not missing_paths:
        raise ValueError(
            "No files found in the configured paths."
        )

    return files, missing_paths


def create_baseline():
    files, missing_paths = monitored_files()

    baseline = {
        "created_at": current_time(),
        "files": {}
    }

    for name, path in sorted(files.items()):
        baseline["files"][name] = file_details(path)

    BASELINE_FILE.parent.mkdir(parents=True, exist_ok=True)
    BASELINE_FILE.write_text(json.dumps(baseline, indent=2))

    print("Baseline created successfully.")
    print(f"Files recorded: {len(baseline['files'])}")

    for name in missing_paths:
        print(f"WARNING: Configured path not found: {name}")


def check_files():
    if not BASELINE_FILE.exists():
        raise FileNotFoundError(
            "No baseline found. Run: python src/opssentry.py baseline"
        )

    baseline = json.loads(BASELINE_FILE.read_text())
    previous_files = baseline.get("files", {})

    current_files, missing_paths = monitored_files()
    events = []

    # Detect files deleted since the baseline was created.
    for name in sorted(
        previous_files.keys() - current_files.keys()
    ):
        events.append({
            "time": current_time(),
            "file": name,
            "severity": "HIGH",
            "issue": "File is missing or deleted."
        })

    # Detect configured paths that are missing.
    for name in missing_paths:
        events.append({
            "time": current_time(),
            "file": name,
            "severity": "HIGH",
            "issue": "Configured file or directory is missing."
        })

    # Inspect current files.
    for name, path in sorted(current_files.items()):
        previous = previous_files.get(name)

        if previous is None:
            events.append({
                "time": current_time(),
                "file": name,
                "severity": "MEDIUM",
                "issue": "New file detected; not recorded in baseline."
            })
            continue

        current = file_details(path)

        if current["permissions"] != previous["permissions"]:
            events.append({
                "time": current_time(),
                "file": name,
                "severity": "HIGH",
                "issue": "File permissions have changed.",
                "expected": previous["permissions"],
                "current": current["permissions"]
            })

        if stat.S_IMODE(path.stat().st_mode) & 0o002:
            events.append({
                "time": current_time(),
                "file": name,
                "severity": "HIGH",
                "issue": "File is world-writable.",
                "current": current["permissions"]
            })

        if current["sha256"] != previous["sha256"]:
            events.append({
                "time": current_time(),
                "file": name,
                "severity": "MEDIUM",
                "issue": "File contents have changed."
            })

    report = {
        "checked_at": current_time(),
        "status": "ALERT" if events else "OK",
        "files_checked": len(current_files),
        "issues_detected": len(events),
        "events": events
    }

    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    REPORT_FILE.write_text(json.dumps(report, indent=2))

    print(f"OpsSentry status: {report['status']}")
    print(f"Files checked: {report['files_checked']}")
    print(f"Issues detected: {len(events)}")

    for event in events:
        print(f"\n[{event['severity']}] {event['file']}")
        print(f"Issue: {event['issue']}")

        if "expected" in event:
            print(f"Expected permissions: {event['expected']}")
            print(f"Current permissions: {event['current']}")

    print(f"\nReport saved to: {REPORT_FILE}")


def monitor_logs():
    if not AUTH_LOG_FILE.exists():
        raise FileNotFoundError(
            f"Authentication log not found: {AUTH_LOG_FILE}"
        )

    patterns = (
        "failed password",
        "authentication failure",
        "invalid user",
    )

    matches = []

    with AUTH_LOG_FILE.open("r", errors="replace") as log:
        for line in log:
            lower_line = line.lower()

            # Avoid matching the grep commands used to search logs.
            if "command=/usr/bin/grep" in lower_line:
                continue

            if any(pattern in lower_line for pattern in patterns):
                matches.append(line.rstrip())

    print("OpsSentry Log Monitor")
    print("---------------------")
    print(f"Log source: {AUTH_LOG_FILE}")
    print(f"Matching authentication events: {len(matches)}")

    if matches:
        print("\nRecent matching events:")

        for entry in matches[-20:]:
            print(entry)

        print("\n[MEDIUM] Review these events for possible authentication issues.")
    else:
        print("\nNo matching authentication events found.")


def monitor_health():
    print("OpsSentry System Health Monitor")
    print("--------------------------------")

    cpu_threshold = 80
    memory_threshold = 85
    disk_threshold = 85

    # Measure CPU usage over a one-second interval.
    cpu_usage = psutil.cpu_percent(interval=1)

    # Measure RAM usage.
    memory = psutil.virtual_memory()
    memory_usage = memory.percent

    # Measure disk usage for the Linux root filesystem.
    disk = psutil.disk_usage("/")
    disk_usage = disk.percent

    metrics = {
        "checked_at": current_time(),
        "cpu_usage_percent": cpu_usage,
        "memory_usage_percent": memory_usage,
        "memory_total_bytes": memory.total,
        "memory_available_bytes": memory.available,
        "disk_usage_percent": disk_usage,
        "disk_total_bytes": disk.total,
        "disk_free_bytes": disk.free,
        "thresholds": {
            "cpu_percent": cpu_threshold,
            "memory_percent": memory_threshold,
            "disk_percent": disk_threshold,
        },
        "events": []
    }

    print(f"CPU usage:    {cpu_usage:.1f}%")
    print(f"Memory usage: {memory_usage:.1f}%")
    print(f"Disk usage:   {disk_usage:.1f}%")

    if cpu_usage >= cpu_threshold:
        metrics["events"].append({
            "severity": "HIGH",
            "issue": "High CPU usage detected.",
            "current_percent": cpu_usage
        })

    if memory_usage >= memory_threshold:
        metrics["events"].append({
            "severity": "HIGH",
            "issue": "High memory usage detected.",
            "current_percent": memory_usage
        })

    if disk_usage >= disk_threshold:
        metrics["events"].append({
            "severity": "HIGH",
            "issue": "High disk usage detected.",
            "current_percent": disk_usage
        })

    metrics["status"] = "ALERT" if metrics["events"] else "OK"

    HEALTH_REPORT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    HEALTH_REPORT_FILE.write_text(
        json.dumps(metrics, indent=2)
    )

    if metrics["events"]:
        print("\nHealth alerts:")

        for event in metrics["events"]:
            print(f"[{event['severity']}] {event['issue']}")
    else:
        print("\nNo health threshold alerts detected.")

    print(f"\nSystem health status: {metrics['status']}")
    print(f"Health report saved to: {HEALTH_REPORT_FILE}")


def main():
    valid_commands = {"baseline", "check", "logs", "health"}

    if len(sys.argv) != 2 or sys.argv[1] not in valid_commands:
        print(
            "Usage: python src/opssentry.py "
            "[baseline|check|logs|health]"
        )
        raise SystemExit(1)

    try:
        if sys.argv[1] == "baseline":
            create_baseline()
        elif sys.argv[1] == "check":
            check_files()
        elif sys.argv[1] == "logs":
            monitor_logs()
        elif sys.argv[1] == "health":
            monitor_health()

    except (OSError, ValueError, json.JSONDecodeError) as error:
        raise SystemExit(f"Error: {error}") from error


if __name__ == "__main__":
    main()
