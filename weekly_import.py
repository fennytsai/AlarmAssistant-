from datetime import date, timedelta

from dateutil.relativedelta import relativedelta


from config import DOCTORS


from sheet import (

    get_existing_appointments,

    add_appointments_batch,

    remove_old_appointments

)



# =========================
# 測試日期
# =========================
#
# 測試時填：
# TEST_DATE = "2026-07-07"
#
# 正式使用：
# TEST_DATE = None
#

TEST_DATE = "2026-07-07"



if TEST_DATE:

    today = date.fromisoformat(
        TEST_DATE
    )

else:

    today = date.today()



print(
    "目前測試日期:",
    today
)



# =========================
# 建立年度範圍
# =========================

start_date = date(

    today.year,

    1,

    1

)


# 一年 + 三個月

end_date = (

    start_date

    +

    relativedelta(

        years=1,

        months=3

    )

    -

    timedelta(days=1)

)



print(

    "匯入範圍:",

    start_date,

    "~",

    end_date

)



# =========================
# 清除過期資料
# =========================

remove_old_appointments(

    start_date.strftime(
        "%Y-%m-%d"
    )

)



# =========================
# 讀取目前 Sheet
# 只讀一次
# =========================

existing = get_existing_appointments()



print(

    "目前已有資料:",

    len(existing)

)



# =========================
# 準備新增資料
# =========================

new_rows = []



current = start_date



while current <= end_date:



    # 星期六

    if current.weekday() == 5:



        print(

            "找到星期六:",

            current

        )



        for doctor in DOCTORS:



            # 只處理星期六醫師

            if doctor["weekday"] != 5:

                continue



            key = (

                current.strftime(
                    "%Y-%m-%d"
                ),

                doctor["name"]

            )



            if key in existing:



                print(

                    "已存在:",

                    current,

                    doctor["name"]

                )



            else:



                print(

                    "準備新增:",

                    current,

                    doctor["name"]

                )



                new_rows.append({


                    "appointment_date":

                        current,


                    "doctor":

                        doctor["name"],


                    "hospital":

                        doctor["hospital"],


                    "dept":

                        doctor["dept"],


                    "link":

                        doctor["link"]


                })



    current += timedelta(days=1)



# =========================
# 一次寫入 Google Sheet
# =========================

if new_rows:


    add_appointments_batch(

        new_rows

    )


    print(

        "新增完成:",

        len(new_rows),

        "筆"

    )


else:


    print(

        "沒有需要新增資料"

    )
