"""Serves the static site and accepts lead submissions.

Leads always go to Render logs (line-prefixed LEAD) and to leads.jsonl on disk.
If SMTP env vars are set, each lead is also emailed:
  LEAD_EMAIL_TO, SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS
"""
import json
import os
import pathlib
import smtplib
import time
from email.message import EmailMessage

from flask import Flask, request, send_from_directory

ROOT = pathlib.Path(__file__).resolve().parent
PUB = ROOT / "public"
LEADS = ROOT / "leads.jsonl"

app = Flask(__name__)


@app.post("/api/lead")
def lead():
    data = {k: request.form.get(k, "")[:2000] for k in
            ("subject", "name", "email", "phone", "zip", "project_type", "details")}
    data["ts"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    line = json.dumps(data)
    print(f"LEAD {line}", flush=True)
    with open(LEADS, "a") as f:
        f.write(line + "\n")
    _maybe_email(data)
    return {"ok": True}


def _maybe_email(data):
    to = os.environ.get("LEAD_EMAIL_TO")
    host = os.environ.get("SMTP_HOST")
    if not (to and host):
        return
    try:
        msg = EmailMessage()
        msg["Subject"] = f"Lead: {data['subject'] or data['project_type']}"
        msg["From"] = os.environ.get("SMTP_USER", "leads@localhost")
        msg["To"] = to
        msg.set_content("\n".join(f"{k}: {v}" for k, v in data.items()))
        with smtplib.SMTP(host, int(os.environ.get("SMTP_PORT", "587"))) as s:
            s.starttls()
            s.login(os.environ["SMTP_USER"], os.environ["SMTP_PASS"])
            s.send_message(msg)
    except Exception as e:  # a failed email must never lose the lead
        print(f"LEAD_EMAIL_ERROR {e}", flush=True)


@app.get("/")
@app.get("/<path:path>")
def static_site(path="index.html"):
    full = PUB / path
    if full.is_dir() or path.endswith("/"):
        path = path.rstrip("/") + "/index.html"
    if not (PUB / path).exists() and not path.endswith(".html"):
        candidate = path + "/index.html"
        if (PUB / candidate).exists():
            path = candidate
    if not (PUB / path).exists():
        return send_from_directory(PUB, "index.html"), 404
    return send_from_directory(PUB, path)


if __name__ == "__main__":
    app.run(port=int(os.environ.get("PORT", "8018")))
