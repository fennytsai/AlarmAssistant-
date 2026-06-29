import os
import requests
from datetime import datetime
from zoneinfo import ZoneInfo
from dateutil.relativedelta import relativedelta

WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")


def send_discord_webhook(webhook_url, title, message):
    if not webhook_url:
        raise ValueError("DISCORD_WEBHOOK_URL 沒有設定")

    requests.post(webhook_url, json={
        "embeds": [
            {
                "title": title,
                "description": message,
                "color": 3447003
            }
        ]
    })


today = datetime.now(ZoneInfo("Asia/Taipei")).date()
target_date = today + relativedelta(months=2)

if target_date.weekday() == 5:
    send_discord_webhook(
        WEBHOOK_URL,
        "中醫針灸預約提醒",
        f"""請準備掛號：

中國醫藥大學 中醫針灸
張哲彬 醫師

📅 看診日期：{target_date:%Y/%m/%d}

🕙 請於今晚 22:30 準時掛號

🔗 https://www.cmuh.cmu.edu.tw/OnlineAppointment/DoctorInfo?flag=second&DocNo=24871&Docname=%E5%BC%B5%E5%93%B2%E5%BD%AC

由 GitHub Actions 自動觸發"""
    )
