import os
from datetime import datetime
from dateutil.relativedelta import relativedelta

WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

today = datetime.now().date()

# 今天 + 2 個月 = 預計看診日
target_date = today + relativedelta(months=2)

# Python weekday: Monday=0 ... Saturday=5
is_saturday = target_date.weekday() == 5

if is_saturday:
    send_discord_webhook(
        WEBHOOK_URL,
        "中醫針灸預約提醒",
        f"""請準備掛號：

中國醫藥大學 中醫針灸
張哲彬 醫師

📅 看診日期：{target_date:%Y/%m/%d}

🕙 請於今晚 22:30 準時掛號

🔗 https://www.cmuh.cmu.edu.tw/OnlineAppointment/DoctorInfo?flag=second&DocNo=24871&Docname=%E5%BC%B5%E5%93%B2%E5%BD%AC

由 Github Actions 自動觸發"""
    )
