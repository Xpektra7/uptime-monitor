import requests
from datetime import datetime
from bs4 import BeautifulSoup
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
import notify2  # Add this import
import os
import json
from pathlib import Path

# Ensure logs directory exists
os.makedirs("logs", exist_ok=True)

# Load environment variables
load_dotenv()
email = os.environ.get("EMAIL_USER")
password = os.environ.get("EMAIL_PASS")

# Email sending
def send_email(subject, body):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = email
    msg["To"] = "ogungbayiimran@gmail.com"
    msg.set_content(body)
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(email, password)
        smtp.send_message(msg)

# Desktop notifications


def send_desktop_notification(title, message):
    notify2.init("Uptime Monitor")
    n = notify2.Notification(title, message)
    n.show()

# Flags
flags_file = Path("flags.json")
flags = {"login_alert_sent": False, "down_alert_sent": False}

if flags_file.exists():
    try:
        with open(flags_file, "r") as f:
            content = f.read().strip()
            if content:
                flags.update(json.loads(content))
    except Exception:
        print("⚠️ Warning: flags.json is invalid. Resetting flags.")

def save_flags():
    with open(flags_file, "w") as f:
        json.dump(flags, f)

# Uptime logging
log_file = "logs/uptime_log.csv"
def log_status(status, info=""):
    with open(log_file, "a") as f:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"{now},{status},{info}\n")

# Monitor loop
def monitor():
    print(f"[{datetime.now()}] Starting monitor...")
    try:
        url = "https://eportal.oauife.edu.ng"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print(f"\n[{datetime.now()}] ✅ UP\n")
            log_status("UP")
            flags["down_alert_sent"] = False
            save_flags()

            # Check login option
            response = requests.get("https://eportal.oauife.edu.ng/login.php")
            soup = BeautifulSoup(response.text, "html.parser")
            option_found = soup.find("option", attrs={"selected": True, "value": "2024"})

            if option_found:
                print("🔐✅ Login option detected!")
                if not flags["login_alert_sent"]:
                    send_email("🔔 Portal Login Available", "The login option for 2024 is now live!")
                    send_desktop_notification("🔔 Portal Login Available", "The login option for 2024 is now live!")
                    flags["login_alert_sent"] = True
                    save_flags()
            else:
                print("🔐❌ Login option not detected!")
                flags["login_alert_sent"] = False
                save_flags()

        else:
            print(f"[{datetime.now()}] ⚠️ DOWN - Status: {response.status_code}")
            log_status("DOWN", f"Status {response.status_code}")
            if not flags["down_alert_sent"]:
                send_email("🔔 Portal Down", "The portal is currently down.")
                flags["down_alert_sent"] = True
                save_flags()

    except Exception as e:
        print(f"[{datetime.now()}] ❌ DOWN - Error: {e}")
        log_status("DOWN", str(e))
        if not flags["down_alert_sent"]:
            send_email("🔔 Portal Down", "The portal is currently down.")
            flags["down_alert_sent"] = True
            save_flags()

if __name__ == "__main__":
    while True:
        monitor()
        # Uncomment the line below to run the monitor only once
        break
        # If you want to run the monitor continuously, keep the while loop
        # If you want to run the monitor only once, uncomment the break statement above
        # and comment out the while loop.