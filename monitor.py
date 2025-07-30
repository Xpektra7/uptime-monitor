import requests
from datetime import datetime
from bs4 import BeautifulSoup
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
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


if os.environ.get("CI") != "true":
    import notify2
    notify2.init("Uptime Monitor")

    def send_desktop_notification(title, message):
        n = notify2.Notification(title, message)
        n.show()
else:
    def send_desktop_notification(title, message):
        pass  # No-op on CI

send_desktop_notification("🔔 Uptime Monitor", "Running Monitor...")

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
    print(f"[{datetime.now()}] Running monitor...")
    try:
        url = "https://eportal.oauife.edu.ng"
        res = requests.get(url, timeout=10)

        if res.status_code == 200:
            print(f"[{datetime.now()}] ✅ UP")
            log_status("UP")

            # Notify if it was down before
            if flags.get("was_down"):
                send_email("✅ Portal Back Online", "The portal is now back online.")
                send_desktop_notification("✅ Portal Back Online", "The portal is now back online.")
                flags["was_down"] = False
                flags["down_alert_sent"] = False
                save_flags()

            # Login check
            res = requests.get("https://eportal.oauife.edu.ng/login.php")
            soup = BeautifulSoup(res.text, "html.parser")
            login_option = soup.find("option", attrs={"selected": True, "value": "2024"})

            if login_option:
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
            raise Exception(f"Status {res.status_code}")

    except Exception as e:
        print(f"[{datetime.now()}] ❌ DOWN - Error: {e}")
        log_status("DOWN", str(e))
        if not flags["down_alert_sent"]:
            send_email("🔔 Portal Down", "The portal is currently down.")
            send_desktop_notification("🔔 Portal Down", "The OAU e-portal is currently down.")
            flags["down_alert_sent"] = True
        flags["was_down"] = True
        save_flags()



if __name__ == "__main__":
    while True:
        monitor()

        # Continuous running:
        # time.sleep(60)  # Check every 60 seconds

        # For deployment:
        break
