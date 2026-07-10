import os
import calendar
import discord

from discord.ext import commands
from datetime import date
from config import DOCTORS
from sheet import (
    add_appointment,
    get_active_appointments,
    delete_appointment
)

# =========================
# Discord Bot 初始化
# =========================

intents = discord.Intents.default()

intents.message_content = True

bot = commands.Bot(

    command_prefix="!",

    intents=intents

)

# =========================
# 啟動
# =========================

@bot.event
async def on_ready():

    print(
        f"登入成功: {bot.user}"
    )

# =========================
# !掛號
# =========================
@bot.command()
async def 掛號(ctx):

    await ctx.send(

        "請選擇功能",

        view=MainView()

    )

# =========================
# 主選單
# =========================

class MainView(discord.ui.View):

    def __init__(self):

        super().__init__(
            timeout=180
        )

    @discord.ui.button(

        label="新增",

        style=discord.ButtonStyle.green

    )
    async def add(

        self,

        interaction,

        button

    ):
      
        await interaction.response.send_message(

            "選擇醫師",

            view=DoctorView(),

            ephemeral=True

        )




    @discord.ui.button(

        label="刪除",

        style=discord.ButtonStyle.red

    )
    async def delete(

        self,

        interaction,

        button

    ):

        data = get_active_appointments()

        if not data:

            await interaction.response.send_message(

                "目前沒有可刪除資料",

                ephemeral=True

            )

            return

        await interaction.response.send_message(

            "選擇要刪除的掛號",

            view=DeleteView(data),

            ephemeral=True

        )

# =========================
# 醫師選擇
# =========================

class DoctorView(discord.ui.View):

    def __init__(self):

        super().__init__(
            timeout=180
        )

        options=[]

        for d in DOCTORS:

            options.append(

                discord.SelectOption(

                    label=d["name"],

                    description=d["dept"]

                )

            )

        self.add_item(

            DoctorSelect(options)

        )

class DoctorSelect(discord.ui.Select):

    def __init__(self, options):

        super().__init__(

            placeholder="選擇醫師",

            options=options

        )

    async def callback(

        self,

        interaction

    ):

        doctor = self.values[0]

        await interaction.response.send_message(

            "選擇日期",

            view=DateView(doctor),

            ephemeral=True

        )

# =========================
# 日期選擇
# =========================

class DateView(discord.ui.View):

    def __init__(self, doctor):

        super().__init__(
            timeout=180
        )

        self.doctor = doctor

        today = date.today()

        options=[]

        # 顯示未來90天星期六

        count=0

        day=today

        while count < 15:


            if day.weekday()==5:


                options.append(

                    discord.SelectOption(

                        label=str(day),

                        value=str(day)

                    )

                )

                count+=1


            day = day.fromordinal(

                day.toordinal()+1

            )

        self.add_item(

            DateSelect(

                doctor,

                options

            )

        )

class DateSelect(discord.ui.Select):

    def __init__(

        self,

        doctor,

        options

    ):

        super().__init__(

            placeholder="選擇星期六",

            options=options

        )

        self.doctor=doctor

    async def callback(

        self,

        interaction

    ):

        selected=date.fromisoformat(

            self.values[0]

        )

        info=None

        for d in DOCTORS:

            if d["name"]==self.doctor:

                info=d

                break

        add_appointment(

            selected,

            info["name"],

            info["hospital"],

            info["dept"],

            info["link"]

        )

        await interaction.response.send_message(

            f"✅ 已新增\n{self.doctor}\n{selected}",

            ephemeral=True

        )

# =========================
# 刪除 View
# =========================

class DeleteView(discord.ui.View):

    def __init__(self,data):

        super().__init__(
            timeout=180
        )

        self.add_item(

            DeleteSelect(data)

        )

class DeleteSelect(discord.ui.Select):

    def __init__(self,data):

        self.data=data

        options=[]

        for item in data[:25]:

            options.append(

                discord.SelectOption(

                    label=(

                        f'{item["appointment_date"]} '

                        f'{item["doctor"]}'

                    ),

                    value=str(item["row"])

                )

            )

        super().__init__(

            placeholder="選擇刪除項目",

            options=options

        )

    async def callback(

        self,

        interaction

    ):

        row=int(

            self.values[0]

        )

        delete_appointment(

            row

        )

        await interaction.response.send_message(

            "✅ 已刪除掛號資料",

            ephemeral=True

        )

# =========================
# 啟動 Bot
# =========================

bot.run(
    os.getenv(
        "DISCORD_BOT_TOKEN"
    )
)
