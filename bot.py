import os
import asyncio
import calendar
import json

import discord

from discord.ext import commands

from fastapi import FastAPI

import uvicorn

from datetime import date


from sheet import (
    add_appointment,
    get_active_appointments,
    delete_appointment
)


from config import DOCTORS



# =========================
# FastAPI 防睡眠
# =========================

app = FastAPI()


@app.get("/")
async def home():

    return {

        "status":
        "掛號助理 Bot 運作中"

    }



# =========================
# Discord Bot
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


    @discord.ui.button(

        label="新增",

        style=discord.ButtonStyle.green

    )
    async def add(

        self,

        interaction: discord.Interaction,

        button: discord.ui.Button

    ):


        await interaction.response.send_message(

            "請選擇醫師",

            view=DoctorView(),

            ephemeral=True

        )



    @discord.ui.button(

        label="刪除",

        style=discord.ButtonStyle.red

    )
    async def delete(

        self,

        interaction: discord.Interaction,

        button: discord.ui.Button

    ):


        data = get_active_appointments()


        if not data:


            await interaction.response.send_message(

                "目前沒有掛號資料",

                ephemeral=True

            )

            return



        await interaction.response.send_message(

            "請選擇要刪除的掛號",

            view=DeleteView(data),

            ephemeral=True

        )



# =========================
# 醫師選擇
# =========================


class DoctorView(discord.ui.View):


    def __init__(self):

        super().__init__()



        options=[]


        for doctor in DOCTORS:

            options.append(

                discord.SelectOption(

                    label=doctor["name"]

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

        interaction: discord.Interaction

    ):


        doctor=self.values[0]


        await interaction.response.send_message(

            "請輸入日期，例如 2026-09-05",

            ephemeral=True

        )


        bot.waiting_date = {

            interaction.user.id:

            doctor

        }





# =========================
# 日期輸入
# =========================

bot.waiting_date={}



@bot.event
async def on_message(message):


    if message.author.bot:

        return



    if message.author.id in bot.waiting_date:


        doctor = bot.waiting_date.pop(

            message.author.id

        )


        try:


            appointment_date = date.fromisoformat(

                message.content

            )


            doctor_data = next(

                x for x in DOCTORS

                if x["name"] == doctor

            )


            add_appointment(

                appointment_date,

                doctor_data["name"],

                doctor_data["hospital"],

                doctor_data["dept"],

                doctor_data["link"]

            )


            await message.channel.send(

                f"✅ 已新增\n"
                f"{doctor}\n"
                f"{appointment_date}"

            )


        except Exception as e:


            await message.channel.send(

                f"日期格式錯誤: {e}"

            )


        return



    await bot.process_commands(message)




# =========================
# 刪除功能
# =========================


class DeleteView(discord.ui.View):


    def __init__(self,data):

        super().__init__()


        options=[]


        for item in data:


            options.append(

                discord.SelectOption(

                    label=(

                        f'{item["appointment_date"]} '

                        f'{item["doctor"]}'

                    ),

                    value=str(item["row"])

                )

            )



        self.add_item(

            DeleteSelect(options)

        )





class DeleteSelect(discord.ui.Select):


    def __init__(self,options):

        super().__init__(

            placeholder="選擇刪除資料",

            options=options

        )



    async def callback(

        self,

        interaction: discord.Interaction

    ):


        row=int(self.values[0])


        delete_appointment(row)



        await interaction.response.send_message(

            "✅ 已刪除掛號資料",

            ephemeral=True

        )





# =========================
# 同時啟動 Web + Discord
# =========================


async def main():


    token=os.getenv(

        "DISCORD_BOT_TOKEN"

    )


    if not token:


        print(

            "找不到 DISCORD_BOT_TOKEN"

        )

        return



    config=uvicorn.Config(

        app,

        host="0.0.0.0",

        port=10000

    )


    server=uvicorn.Server(config)



    await asyncio.gather(

        server.serve(),

        bot.start(token)

    )




if __name__=="__main__":


    asyncio.run(main())
