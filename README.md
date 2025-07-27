# 🖥️ OAU E-Portal Uptime Monitor

This is a Python-based CLI tool that monitors the uptime of the OAU e-portal and checks for the availability of the login option for a new semester. If available, it sends a notification email.

## 🚀 Features

- Logs portal status every 10 minutes
- Detects when a specific semester login option appears
- Sends Gmail alerts for:
  - Login availability
  - Portal downtime
- Maintains uptime history in a CSV file
- Skips duplicate notifications using persistent flags

## 📦 Requirements

- Python 3.10+
- `requests`, `beautifulsoup4`, `python-dotenv`

Install dependencies:

```bash
pip install -r requirements.txt
````

## 🔐 Setup

1. Create a `.env` file:

```
EMAIL_USER=your-email@gmail.com
EMAIL_PASS=your-app-password
```


2. (Optional) If using GitHub Actions, set `EMAIL_USER` and `EMAIL_PASS` as repository secrets.

## 📂 Output Files

* `uptime_log.csv` — uptime history
* `flags.json` — prevents duplicate email alerts

## 🛠️ Run

```bash
python monitor.py
```

To run in background (Linux):

```bash
nohup python monitor.py &
```

## ☁️ Deployment

Supports GitHub Actions for cloud-based uptime checking.

---

**Made by [Xpektra](https://github.com/Xpektra)** 🎓
