import os
import json
import gspread
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
    return client.open_by_key(
        SHEET_ID
    ).sheet1
# =========================
# 取得全部資料
# (只讀一次)
# =========================
def get_all_data():
    sheet = get_sheet()
    return sheet.get_all_records()
# =========================
# 取得有效掛號
# 給 Discord 刪除使用
# =========================
def get_active_appointments():
    rows = get_all_data()
    result = []
    for index, row in enumerate(rows):
        if str(row["deleted"]).upper() != "TRUE":
            result.append({
                "row": index + 2,
                "appointment_date":
                    row["appointment_date"],
                "doctor":
                    row["doctor"],
                "hospital":
                    row["hospital"],
                "dept":
                    row["dept"]
            })
    return result
# =========================
# 取得已有資料
# 避免重複新增
# =========================
def get_existing_appointments():
    rows = get_all_data()
    result = set()
    for row in rows:
        if str(row["deleted"]).upper() != "TRUE":
            result.add(
                (
                    row["appointment_date"],
                    row["doctor"]
                )
            )
    return result
# =========================
# 批次新增
# =========================
def add_appointments_batch(data):
    if not data:
        return
    sheet = get_sheet()
    rows = []
    for item in data:
        appointment_date = item["appointment_date"]
        remind_date = (
            appointment_date
            -
            relativedelta(months=2)
        )
        rows.append([
            appointment_date.strftime(
                "%Y-%m-%d"
            ),
            remind_date.strftime(
                "%Y-%m-%d"
            ),
            item["doctor"],
            item["hospital"],
            item["dept"],
            item["link"],
            "FALSE",
            "FALSE"
        ])
    sheet.append_rows(rows)
# =========================
# 單筆新增
# Discord 使用
# =========================
def add_appointment(
    appointment_date,
    doctor,
    hospital,
    dept,
    link
):
    add_appointments_batch([
        {
            "appointment_date":
                appointment_date,
            "doctor":
                doctor,
            "hospital":
                hospital,
            "dept":
                dept,
            "link":
                link
        }
    ])
# =========================
# 刪除
# deleted=True
# =========================
def delete_appointment(row_number):
    sheet = get_sheet()
    # H欄
    sheet.update_cell(
        row_number,
        8,
        "TRUE"
    )
# =========================
# 找今天提醒
# =========================
def get_today_reminders(today):
    rows = get_all_data()
    result = []
    for index, row in enumerate(rows):
        if (
            row["remind_date"]
            ==
            today
            and
            str(row["sent"]).upper()
            !=
            "TRUE"
            and
            str(row["deleted"]).upper()
            !=
            "TRUE"
        ):
            result.append({
                "row":
                    index + 2,
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
            })
    return result
# =========================
# 標記已提醒
# =========================
def mark_sent(row_number):
    sheet = get_sheet()
    # G欄
    sheet.update_cell(
        row_number,
        7,
        "TRUE"
    )
# =========================
# 過期資料標記刪除
# =========================
def remove_old_appointments(today):
    sheet = get_sheet()
    rows = sheet.get_all_records()
    update = []
    for index, row in enumerate(rows):
        if (
            row["appointment_date"]
            <
            today
            and
            str(row["deleted"]).upper()
            !=
            "TRUE"
        ):
            update.append(index + 2)
    for row_number in update:
        sheet.update_cell(
            row_number,
            8,
            "TRUE"
        )
