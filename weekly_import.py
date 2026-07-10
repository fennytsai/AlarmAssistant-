from datetime import date, timedelta

from dateutil.relativedelta import relativedelta

from config import DOCTORS

from sheet import (
    appointment_exists,
    add_appointment,
    remove_old_appointments
)

# =========================
# 設定年份範圍
# =========================

today = date.today()

# 每年從 1/1 開始建立

start_date = date(
    today.year,
    1,
    1
)


# 一整年 + 3個月

end_date = (

    start_date
    +
    relativedelta(
        years=1,
        months=3
    )

)

print(
    "匯入範圍:",
    start_date,
    "~",
    end_date
)

# =========================
# 刪除過期資料
# =========================

remove_old_appointments(

    start_date.strftime(
        "%Y-%m-%d"
    )

)

# =========================
# 找星期六
# =========================

current = start_date

while current <= end_date:
  
    # Python:
    # Monday=0
    # Saturday=5

    if current.weekday() == 5:

        print(
            "找到星期六:",
            current
        )

        # =========================
        # 每位星期六醫師
        # =========================

        for doctor in DOCTORS:

            if doctor["weekday"] != 5:
                continue

            exists = appointment_exists(

                current,

                doctor["name"]

            )

            if exists:

                print(

                    "已存在:",
                    current,
                    doctor["name"]

                )

            else:

                add_appointment(

                    appointment_date=current,

                    doctor=doctor["name"],

                    hospital=doctor["hospital"],

                    dept=doctor["dept"],

                    link=doctor["link"]

                )

                print(

                    "新增:",
                    current,
                    doctor["name"]

                )

    current += timedelta(
        days=1
    )
