from dotenv import load_dotenv
import os

load_dotenv()

email = os.environ.get("EMAIL_USER")
password = os.environ.get("EMAIL_PASS")
if not email or not password:
    print("⚠️ Email credentials not found in environment.")
    exit(1)
else:
    print("✅ Email credentials loaded successfully.")