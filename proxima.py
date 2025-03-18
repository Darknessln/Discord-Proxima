from discord.ext import commands
import discord
import random
from discord import channel, voice_client
from discord import FFmpegPCMAudio
import time
from datetime import datetime
import pandas as pd
import csv
import qrcode
import change_language, find_recent_message
import os
import encryption
import shutil
import random
import environment_folder
import calendar_
import ast

environment_folder.ensure_data_directories()
environment_folder.check_or_create_log()
with open("token.txt", "r") as  file:
    Token = file.read()
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
script_dir = os.path.dirname(os.path.abspath(__file__))
client = commands.Bot(command_prefix= "-", intents=intents)
print(f"running on:{script_dir}")
happy_emoji = [":grin:", ":kissing_smiling_eyes:", ":heart:", ":white_heart:", ":smiling_face_with_3_hearts:", ":point_right:"]
sad_emoji = [":cry:", ":disappointed_relieved:", ":pleading_face:", ":pensive:", ":persevere:"]
def write_log(message, sender, server, channel, userID, messageID):
    now = datetime.now()
    date = now.strftime("%Y-%m-%d")  # Format the date as YYYY-MM-DD
    time = now.strftime("%H:%M:%S")  # Format the time as HH:MM:SS
    
    # Open the CSV file in append mode ('a')
    with open('log.csv', mode='a', newline='', encoding="utf-8") as file: # encoding="utf-8" for Thai language
        writer = csv.writer(file)

        # Write a row
        writer.writerow([date, time, server, channel, userID, sender, message, messageID])
        file.close()


class LinkToBills(discord.ui.View):
    def __init__(self):
        super().__init__()
        # Add a URL button
        self.add_item(discord.ui.Button(label="Edit Bills", url="https://docs.google.com/spreadsheets/d/1y8rZlKght5j9bNIxx9lbTGQc7CQa_YiUUIHV-CIO2nM/edit?usp=sharing"))


@client.event
async def on_ready():
    print("Proxima is ready")
    try:
        # Sync the commands with Discord (in case you add new commands)
        synced = await client.tree.sync()
        print(f"Synced {len(synced)} command(s).")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

@client.event
async def on_message(message):
    # Write Log.csv
    message_ = str(message.content)
    author_ = str(message.author)
    userID_ = str(message.author.id)
    messageID_ = str(message.id)
    if message.guild is None:
        server_ = 'DM'
        channel_ = 'DM'
    else:
        server_ = str(message.guild.name)
        channel_ = str(message.channel.name)
    if message.attachments:
        attachment_list = []
        for attachment in message.attachments:
            attachment_list.append(attachment.filename)
        message_ = f"attachment = {attachment_list}"
    write_log(message=message_, sender=author_, server=server_, channel=channel_, userID=userID_, messageID=messageID_)

    # Ignore messages from the bot itself
    if message.author == client.user:
        return

    if message.attachments:
        # download_dir = fr'{script_dir}/temp/Data/{message.author.id}'
        download_dir = os.path.join(script_dir, 'temp', 'Data', str(message.author.id))
        os.makedirs(download_dir, exist_ok=True)
        for attachment in message.attachments:
            # file_size = attachment.size / 1024**2
                # Download each attachment
            file_path = os.path.join(download_dir, encryption.encrypt(text=attachment.filename, key=str(message.author.id)))
            print(f"Saved at {file_path}")
            await attachment.save(file_path)
    elif str(message.author.id) in os.listdir(os.path.join(script_dir, 'temp', 'Data')):
        print("deleting")
        try:
            shutil.rmtree(os.path.join(script_dir, 'temp', 'Data', str(message.author.id)))
        except:
            print(f"Empty Folder: " + os.path.join(script_dir, 'temp', 'Data', str(message.author.id)))

    # Language Change function
    if 'แปล' in message.content and message.reference:
        replied_message = await message.channel.fetch_message(message.reference.message_id)

        # Check if English is in the message
        if any(eng in message.content for eng in ['Eng', 'eng', 'english', 'อังกิด', 'อังกฤษ', 'อะงกิด', 'อิ้ง']):
            try:
                await message.channel.send(change_language.language_change_th(replied_message.content))
            except:
                await message.author.send(change_language.language_change_th(replied_message.contents))
            return

        # Translage to Thai key
        try:
            await message.channel.send(change_language.language_change(replied_message.content))
        except:
            await message.author.send(change_language.language_change(replied_message.contents))
            
    # Process the command
    await client.process_commands(message)

# Command ---------------------------------------------------------------------------------------------------------

@client.tree.command(name="qr", description="Generate QR-Code from URL")
async def qr(interaction: discord.Interaction, url: str):
    try:
        qr_path = script_dir + 'qrcode.png'
        img = qrcode.make(url)
        img.save(qr_path)
        await interaction.response.send_message(file=discord.File(qr_path))
    except:
        await interaction.response.send_message("ทำไม่ได้อ่ะค่ะ ขอโทษด้วยนะคะ:sob:", ephemeral=False)

@client.tree.command(name="แปล", description="แก้คำที่ลืมเปลียนภาษาจากข้อความล่าสุด")
async def แปล(interaction: discord.Interaction):
        if interaction.guild and interaction.channel:
            guild_name = interaction.guild.name
            channel_name = interaction.channel.name
            await interaction.response.send_message(change_language.language_change(find_recent_message.find_recent(server=guild_name, channel=channel_name)), ephemeral=False)
        else:
            guild_name = 'DM'
            channel_name = 'DM'
            userID = interaction.user.id
            await interaction.response.send_message(change_language.language_change(find_recent_message.find_recent(server=guild_name, channel=channel_name, userID=userID)), ephemeral=False)

@client.tree.command(name="id", description="ดู User ID ของตัวเอง")
async def id(interaction: discord.Interaction):
    embed = discord.Embed(
    title=f"__{interaction.user.name} ID__: {interaction.user.id}",
    color=discord.Color.orange()
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)

@client.tree.command(name="วันที่", description="แสดงปฏิทิน")
async def วันที่(interaction: discord.Interaction,ปี: int = None, เดือนที่: int = None):
    if เดือนที่ != None:
        if เดือนที่ > 12:
            await interaction.response.send_message(f"1 ปีมีแค่ 12 เดือนนะคะ {random.choice(sad_emoji)}", ephemeral=False)
            return
    if ปี != None:
        if ปี < 1 or ปี > 9999:
            await interaction.response.send_message(f"ขอที่เป็นปีที่ไม่เกิน 4 หลักด้วยค่า {random.choice(sad_emoji)}", ephemeral=False)
            return
    cal = calendar_.month_calendar(year=ปี, month=เดือนที่)

    embed = discord.Embed(
    title=f"__{cal[0]}__ {random.choice(happy_emoji)}",
    description=f"```{cal[1]}```",
    color=discord.Color.orange()
    )
    await interaction.response.send_message(embed=embed, ephemeral=False)

@client.tree.command(name="เปลี่ยนตาราง", description="เปลี่ยนตารางเวลาหรือตารางเรียน")
async def เปลี่ยนตาราง(interaction: discord.Interaction, attachment: discord.Attachment):
        if attachment.content_type.startswith("image"):
            # Save the image locally
            userID = str(interaction.user.id)
            timetable_dir = os.path.join(script_dir, "Data", userID, "Time_Table")
            file_path = os.path.join(timetable_dir, encryption.encrypt(attachment.filename, userID))

            if not os.path.exists(timetable_dir):  # Make folder if does not exist
                os.makedirs(timetable_dir, exist_ok=True)

            if len(os.listdir(timetable_dir)) > 0:
                for i in os.listdir(timetable_dir):
                    file = os.path.join(timetable_dir, i)
                    os.remove(file)  

            await attachment.save(file_path)      
            await interaction.response.send_message(f"เปลี่ยนให้แล้วนะคะ {random.choice(happy_emoji)}", ephemeral=False)
        else:
            await interaction.response.send_message("Please upload an image file.", ephemeral=True)

@client.tree.command(name="ขอตาราง", description="ขอตารางเวลาหรือตารางเรียน")
async def ขอตาราง(interaction: discord.Interaction,):
    UserID = str(interaction.user.id)
    try:
        file_list = os.listdir(os.path.join(script_dir, 'Data', UserID, "Time_Table"))
        # Define the source file and the decrypted destination file path
        source_file = os.path.join(script_dir, 'Data', UserID, "Time_Table", file_list[0])
        decrypted_filename = encryption.decrypt(file_list[0], UserID)
        destination_file = os.path.join(script_dir, 'temp', decrypted_filename)

        # Copy the file to the temp directory with the decrypted name
        shutil.copy(source_file, destination_file)
        await interaction.response.send_message(f"นี่ค่ะ{random.choice(happy_emoji)}", file=discord.File(destination_file))
    except:
        await interaction.response.send_message(f"พี่ยังไม่ส่งตารางมาให้หนูนะคะ {random.choice(sad_emoji)}")
    finally:
        # Remove the temporary file after sending
        try:
            if os.path.exists(destination_file):
                os.remove(destination_file)
        except:
            return

def space(num: int=0):
    return " "*num

import json
def json_url(json_yt, title="", subtractor=0):
    try:
        print(title)
        if title == 'None' or title == None:
             title = f"นี่ค่ะ {random.choice([':sparkling_heart:', ':smiling_face_with_3_hearts:' ':white_heart:', ':heart:'])}"
        result = json.loads(json_yt)
        print(title)
        return f"__{title}__\n<https://www.youtube.com/watch?v={result['docid']}&t={int(float(result['cmt'])) - subtractor}>"
    except:
         return "หนูอ่านไม่ได้อ่ะคะ:sob:"
@client.tree.command(name="ytjson", description="Translate Json script from YouTube to URL with Timestamp and Title")
@discord.app_commands.describe(json_yt="Youtube JSON", title="Optional title", subtractor="Time subtractor in SECOND")
async def YoutubeJson(interaction: discord.Interaction,json_yt: str, title: str = None, subtractor: discord.app_commands.Range[int, 0, None] = 0):
    await interaction.response.send_message(json_url(json_yt, title, subtractor))

@client.tree.command(name="คิดบิล", description="แสดงบิลที่คำนวนแล้วจาก Google Sheet")
async def bills(interaction: discord.Interaction, restarant: str = ""):
        try:
            from billcal import calculate_bill
            embed = discord.Embed(
            title=restarant,
            description=calculate_bill(),
            color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed, view=LinkToBills())
        except:
            await interaction.response.send_message(f"ใส่ข้อมูลให้ครบด้วยนะคะ{random.choice(sad_emoji)}", view=LinkToBills())

@client.tree.command(name="บิล", description="แสดงลิงค์ Google Sheet เพื่อกรอกข้อมูลในการคำนวนบิล")
async def bill_sheet(interaction: discord.Interaction):
        await interaction.response.send_message(f"นี่ค่ะ:point_right:", view=LinkToBills())


from PIL import Image
import pytesseract
# Set the Tesseract executable path based on the OS
if os.name == 'nt':  # Check if it's Windows
    pytesseract.pytesseract.tesseract_cmd = os.path.join(script_dir, 'tess', 'tesseract.exe')
elif os.name == 'posix':  # Check if it's Linux/Ubuntu
    pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'

@client.tree.command(name="imgtext", description="เปลี่ยนรูปเป็นข้อความ")
async def imagetotext(interaction: discord.Interaction, attachment: discord.Attachment):
        if attachment.content_type.startswith("image"):
            # Save the image locally
            file_path = os.path.join(script_dir, 'temp', attachment.filename)
            await attachment.save(file_path)

            embed = discord.Embed(
            title=random.choice(happy_emoji),
            description=f"```{pytesseract.image_to_string(Image.open(file_path))}```",
            color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed)  
            os.remove(file_path)

        else:
            await interaction.response.send_message(f"อัพโหลดรูปด้วยนะคะ{random.choice(sad_emoji)}", ephemeral=True)

client.run(Token)