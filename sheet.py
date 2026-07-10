import os
import json
import gspread

from datetime import datetime
from dateutil.relativedelta import relativedelta
from google.oauth2.service_account import Credentials

# =========================
# Google Sheet 設定
# =========================

SHEET_ID = "1-vTfyVwgQU3ZodQ4WODNeo7PXPfK5FgC8JDyV-8p_os"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets"
]

# =========================
# 連線 Google Sheet
# =========================

def get_sheet():
    json_key = os.getenv(
        "GOOGLE_CREDENTIALS_JSON"
    )

    if not json_key:
        raise Exception(
            "缺少 GOOGLE_CREDENTIALS_JSON"
        )

    credentials = Credentials.from_service_account_info(
        json.loads(json_key),
        scopes=SCOPES
    )

    client = gspread.authorize(
        credentials
    )

    sheet = client.open_by_key(
        SHEET_ID
    ).sheet1

    return sheet

# =========================
# 新增資料
# =========================

def add_appointment(
    appointment_date,
    doctor,
    hospital,
    dept,
    link
):

    sheet = get_sheet()

    remind_date = (
        appointment_date
        -
        relativedelta(months=2)
    )

    sheet.append_row(
        [
            appointment_date.strftime("%Y-%m-%d"),
            remind_date.strftime("%Y-%m-%d"),
            doctor,
            hospital,
            dept,
            link,
            "FALSE",
            "FALSE"
        ]
    )

# =========================
# 檢查是否存在
# =========================

def appointment_exists(
    appointment_date,
    doctor
):

    sheet = get_sheet()
    rows = sheet.get_all_records()
    
    date_str = appointment_date.strftime(
        "%Y-%m-%d"
    )

    for row in rows:
        if (
            row["appointment_date"]
            == date_str

            and

            row["doctor"]
            == doctor

            and

            str(row["deleted"]).upper()
            == "FALSE"
        ):
            return True

    return False

# =========================
# 查詢有效資料
# =========================

def get_active_appointments():
    
    sheet = get_sheet()

    rows = sheet.get_all_records()

    result = []

    for index,row in enumerate(rows):
        
        if str(
            row["deleted"]
        ).upper() == "FALSE":

            result.append(
                {

                    "row": index + 2,

                    "appointment_date":
                    row["appointment_date"],

                    "doctor":
                    row["doctor"],

                    "hospital":
                    row["hospital"],

                    "dept":
                    row["dept"]
                }
            )
    return result

# =========================
# Discord 刪除
# =========================

def delete_appointment(row_number):
    sheet = get_sheet()

    # H欄 deleted

    sheet.update_cell(

        row_number,

        8,

        "TRUE"

    )

# =========================
# 找今天提醒
# =========================

def get_today_reminders(today):

    sheet = get_sheet()

    rows = sheet.get_all_records()

    result=[]

    for index,row in enumerate(rows):

        if (

            row["remind_date"]

            == today

            and

            str(row["sent"]).upper()

            == "FALSE"

            and

            str(row["deleted"]).upper()

            == "FALSE"

        ):
            
            result.append(

                {

                    "row":index+2,

                    "appointment_date":
                    row["appointment_date"],

                    "doctor":
                    row["doctor"],

                    "hospital":
                    row["hospital"],

                    "dept":
                    row["dept"],

                    "link":
                    row["link"]
                }
            )

    return result

# =========================
# 標記提醒完成
# =========================

def mark_sent(row_number):
    
    sheet=get_sheet()

    # G欄 sent

    sheet.update_cell(

        row_number,

        7,

        "TRUE"

    )

# =========================
# 清除過期資料
# =========================

def remove_old_appointments(today):

    sheet=get_sheet()

    rows=sheet.get_all_records()

    for index,row in enumerate(rows):

        if (

            row["appointment_date"]

            <

            today

            and

            str(row["deleted"]).upper()

            == "FALSE"

        ):
            
            sheet.update_cell(

                index+2,

                8,

                "TRUE"

            )
