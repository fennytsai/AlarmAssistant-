import os
import requests

from datetime import date

from sheet import (
    get_today_reminders,
    mark_sent
)

# =========================
# Discord Webhook
# =========================

WEBHOOK_URL = os.getenv(
    "DISCORD_WEBHOOK_URL"
)

def send_discord(
    title,
    message
):

    if not WEBHOOK_URL:

        raise Exception(
            "缺少 DISCORD_WEBHOOK_URL"
        )

    response = requests.post(

        WEBHOOK_URL,

        json={

            "embeds": [

                {
                    "title": title,

                    "description": message,

                    "color": 3447003
                }
            ]
        }
    )

    response.raise_for_status()

# =========================
# 今天日期
# =========================

today = date.today().strftime(
    "%Y-%m-%d"
)

print(
    "檢查提醒日期:",
    today
)

# =========================
# 找提醒資料
# =========================

reminders = get_today_reminders(

    today

)

if not reminders:
    print(
        "今天沒有提醒"
    )

else:

    for item in reminders:

        message = f"""
🔔 掛號提醒

👨‍⚕️ 醫師：
{item["doctor"]}

🏥 醫院：
{item["hospital"]}

📌 科別：
{item["dept"]}

📅 看診日期：
{item["appointment_date"]}

🔗 掛號網址：
{item["link"]}

請準備掛號。
"""
        send_discord(

            "掛號提醒",

            message

        )
      
        # 發送成功後

        mark_sent(

            item["row"]

        )

        print(

            "已提醒:",

            item["doctor"],

            item["appointment_date"]

        )
