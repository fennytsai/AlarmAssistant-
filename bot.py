import discord
from discord.ext import commands
import calendar
import os

# =========================
# 🚀 Bot 初始化
# =========================
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


# =========================
# 🟢 !掛號
# =========================
@bot.command()
async def 掛號(ctx):
    await ctx.send("請選擇操作：", view=MainView())


# =========================
# 🟦 主按鈕
# =========================
class MainView(discord.ui.View):

    @discord.ui.button(label="新增", style=discord.ButtonStyle.green)
    async def add(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("選擇醫生", view=DoctorView(), ephemeral=True)

    @discord.ui.button(label="刪除", style=discord.ButtonStyle.red)
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("刪除功能（未完成）", ephemeral=True)


# =========================
# 🧑‍⚕️ 醫生
# =========================
class DoctorView(discord.ui.View):

    @discord.ui.select(
        placeholder="選擇醫生",
        options=[
            discord.SelectOption(label="張醫生"),
            discord.SelectOption(label="盧醫生")
        ]
    )
    async def select(self, interaction: discord.Interaction, select: discord.ui.Select):

        doctor = select.values[0]

        await interaction.response.send_message(
            f"已選 {doctor}",
            view=YearView(doctor),
            ephemeral=True
        )


# =========================
# 📅 年份
# =========================
class YearView(discord.ui.View):

    def __init__(self, doctor):
        super().__init__()
        self.doctor = doctor

    @discord.ui.select(
        options=[
            discord.SelectOption(label="2026"),
            discord.SelectOption(label="2027")
        ]
    )
    async def select(self, interaction: discord.Interaction, select: discord.ui.Select):

        year = int(select.values[0])

        await interaction.response.send_message(
            f"{self.doctor} {year}",
            view=MonthView(self.doctor, year),
            ephemeral=True
        )


# =========================
# 📆 月份
# =========================
class MonthView(discord.ui.View):

    def __init__(self, doctor, year):
        super().__init__()
        self.doctor = doctor
        self.year = year

    @discord.ui.select(
        options=[discord.SelectOption(label=f"{i}月") for i in range(1, 13)]
    )
    async def select(self, interaction: discord.Interaction, select: discord.ui.Select):

        month = int(select.values[0].replace("月", ""))

        await interaction.response.send_message(
            f"{self.doctor} {self.year}/{month}",
            view=DayView(self.doctor, self.year, month),
            ephemeral=True
        )


# =========================
# 📆 日期
# =========================
class DayView(discord.ui.View):

    def __init__(self, doctor, year, month):
        super().__init__()
        self.doctor = doctor
        self.year = year
        self.month = month

        days = calendar.monthrange(year, month)[1]

        self.add_item(DaySelect(doctor, year, month, days))


class DaySelect(discord.ui.Select):

    def __init__(self, doctor, year, month, days):
        options = [
            discord.SelectOption(label=f"{d}日") for d in range(1, days + 1)
        ]
        super().__init__(placeholder="選擇日期", options=options)

        self.doctor = doctor
        self.year = year
        self.month = month

    async def callback(self, interaction: discord.Interaction):

        day = int(self.values[0].replace("日", ""))

        date_str = f"{self.year}-{self.month:02d}-{day:02d}"

        await interaction.response.send_message(
            f"✅ 已新增提醒：{self.doctor} {date_str}",
            ephemeral=True
        )


# =========================
# 🚀 啟動
# =========================
bot.run(os.getenv("DISCORD_BOT_TOKEN"))
