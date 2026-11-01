
import json
from pathlib import Path

import streamlit as st

PROJECT_DIR = Path(__file__).resolve().parent.parent
HEALTH_REPORT = PROJECT_DIR / "reports" / "health_report.json"
FILE_REPORT = PROJECT_DIR / "reports" / "latest_report.json"

st.set_page_config(
    page_title="OpsSentry",
    page_icon="🛡️",
    layout="wide",
)

st.title("🛡️ OpsSentry")
st.caption("Linux System Monitoring & Incident Investigation")

def load_report(path):
    if not path.exists():
        return None

    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return None

health = load_report(HEALTH_REPORT)
file_report = load_report(FILE_REPORT)

st.subheader("System Health")

if health is None:
    st.info("No health report found. Run: python src/opssentry.py health")
else:
    cpu = health.get("cpu_usage_percent", 0)
    memory = health.get("memory_usage_percent", 0)
    disk = health.get("disk_usage_percent", 0)

    col1, col2, col3 = st.columns(3)

    col1.metric("CPU Usage", f"{cpu:.1f}%")
    col2.metric("Memory Usage", f"{memory:.1f}%")
    col3.metric("Disk Usage", f"{disk:.1f}%")

    st.write("CPU utilization")
    st.progress(min(max(int(cpu), 0), 100))

    st.write("Memory utilization")
    st.progress(min(max(int(memory), 0), 100))

    st.write("Disk utilization")
    st.progress(min(max(int(disk), 0), 100))

    st.write("Health Status:", health.get("status", "UNKNOWN"))

st.divider()
st.subheader("File Integrity Monitoring")

if file_report is None:
    st.info("No file report found. Run: python src/opssentry.py check")
else:
    col1, col2, col3 = st.columns(3)

    col1.metric("Status", file_report.get("status", "UNKNOWN"))
    col2.metric("Files Checked", file_report.get("files_checked", 0))
    col3.metric("Issues Detected", file_report.get("issues_detected", 0))

    events = file_report.get("events", [])

    if events:
        st.warning("File integrity issues detected")
        st.dataframe(events, use_container_width=True)
    else:
        st.success("No file integrity issues detected")

st.caption("Data is read from OpsSentry JSON reports.")
st.caption("Run your CLI monitoring commands to update the reports.")
