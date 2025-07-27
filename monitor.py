import requests
import time
from datetime import datetime
from bs4 import BeautifulSoup
import smtplib
from email.message import EmailMessage

def send_email(subject, body):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = "xpektra7@gmail.com"
    msg["To"] = "ogungbayiimran@gmail.com"
    msg.set_content(body)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login("xpektra7@gmail.com", "xktr dqxo aibp kska")
        smtp.send_message(msg)


url = "https://eportal.oauife.edu.ng"
log_file = "uptime_log.csv"

def log_status(status, info=""):
    with open(log_file, "a") as f:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"{now},{status},{info}\n")

while True:
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print(f"\n[{datetime.now()}] ✅ UP\n")
            log_status("UP")
            url = "https://eportal.oauife.edu.ng/login.php"
            response = requests.get(url)
            soup = BeautifulSoup(response.text, "html.parser")

            # Example: check if 'Login' button or link exists
            option_found = soup.find("option", attrs={"selected": True, "value": "2023"})

            if option_found:
                print("🔐✅ Login option detected!")
                send_email("🔔 Portal Login Available", "The login option for 2023 is now live!")
            else:
                print("🔐❌ Login option not detected!")
        else:
            print(f"[{datetime.now()}] ⚠️ DOWN - Status: {response.status_code}")
            log_status("DOWN", f"Status {response.status_code}")
    except Exception as e:
        print(f"[{datetime.now()}] ❌ DOWN - Error: {e}")
        log_status("DOWN", str(e))

    time.sleep(60)  # wait 5 seconds before the next check





