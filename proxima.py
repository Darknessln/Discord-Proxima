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

@client.tree.command(name="list", description="แสดงไฟล์ที่ฝากใว้ทั้งหมด")
async def list(interaction: discord.Interaction):
    try:
        UserID = str(interaction.user.id)
        file_list = os.listdir(os.path.join(script_dir, 'Data', UserID))
        output_list = []
        for i in range(len(file_list)):
            output_list.append(f"[{i+1}]    {encryption.decrypt(file_list[i], UserID)}")

        embed = discord.Embed(
        title=f"__{interaction.user.name}{random.choice(happy_emoji)}__",
        description='\n'.join(output_list),
        color=discord.Color.orange()
        )
        await interaction.response.send_message(embed=embed)
    except:
        await interaction.response.send_message(f"พี่ {interaction.user.name} ยังไม่เคยฝากไฟล์ไว้นะคะ{random.choice(sad_emoji)}")

@client.tree.command(name="ลบไฟล์", description="ลบไฟล์ที่ฝากใว้")
async def ลบไฟล์(interaction: discord.Interaction, เลขไฟล์: int):
    UserID = str(interaction.user.id)
    file_list = os.listdir(os.path.join(script_dir, 'Data', UserID))
    try:
        os.remove(os.path.join(script_dir, 'Data', UserID, file_list[เลขไฟล์-1]))
        await interaction.response.send_message(f"ลบไฟล์ {encryption.decrypt(file_list[เลขไฟล์-1], UserID)} แล้วนะคะ:thumbsup:")
    except:
        await interaction.response.send_message(f"ไม่เจอไฟล์นั้นนะคะ:pleading_face:")

@client.tree.command(name="ขอไฟล์", description="ขอไฟล์ที่ฝากใว้")
async def ขอไฟล์(interaction: discord.Interaction, เลขไฟล์: int):
    UserID = str(interaction.user.id)
    file_list = os.listdir(os.path.join(script_dir, 'Data', UserID))
    try:
        # Define the source file and the decrypted destination file path
        source_file = os.path.join(script_dir, 'Data', UserID, file_list[เลขไฟล์ - 1])
        decrypted_filename = encryption.decrypt(file_list[เลขไฟล์ - 1], UserID)
        destination_file = os.path.join(script_dir, 'temp', decrypted_filename)
        print(destination_file)

        # Copy the file to the temp directory with the decrypted name
        shutil.copy(source_file, destination_file)
        await interaction.response.send_message(f"นี่ค่ะ{random.choice(happy_emoji)}", file=discord.File(os.path.join(script_dir, 'temp', encryption.decrypt(file_list[เลขไฟล์-1], UserID))))
    except:
        await interaction.response.send_message(f"ไม่เจอไฟล์นั้นนะคะ:pleading_face:")
    finally:
        # Remove the temporary file after sending
        if os.path.exists(destination_file):
            os.remove(destination_file)

@client.tree.command(name="ฝาก", description="ฝากไฟล์ใว้ที่ Proxima")
async def ฝาก(interaction: discord.Interaction):
    try:
        path = os.path.join(script_dir, 'temp', 'Data', str(interaction.user.id))
        havefile = os.listdir(path)
        moved_file = []
        remaining = []
        if len(havefile) >= 1:
            dest_dir = os.path.join(script_dir, 'Data', str(interaction.user.id))
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)

            # Iterate over all files in the source directory
            for filename in os.listdir(path):
                src_path = os.path.join(path, filename)
                dest_path = os.path.join(dest_dir, filename)

                # Check if it's a file before moving (ignoring subdirectories)
                if os.path.isfile(src_path):
                    file_size = os.path.getsize(src_path)  / (1024 * 1024)
                    if file_size < 8:
                        shutil.move(src_path, dest_path)
                        print(f"Moved {filename} to {dest_dir}")
                        moved_file.append(":ballot_box_with_check:  " + encryption.decrypt(filename, str(interaction.user.id)))
                    else:
                        os.remove(src_path)
                        remaining.append(":exclamation:  ~~" + encryption.decrypt(filename, str(interaction.user.id)) + "~~")     

        else:
            await interaction.response.send_message(f"พี่ยังไม่ได้ส่งไฟล์มาให้หนูนะคะ{random.choice(sad_emoji)}")
            return

        if len(remaining) < 1:
            embed = discord.Embed(
            title=f"__{interaction.user.name}__",
            description='\n'.join(moved_file),
            color=discord.Color.orange()
            )
            await interaction.response.send_message(f"เพิ่มไฟล์ให้แล้วนะคะ{random.choice(happy_emoji)}", embed=embed)
        else:
            embed = discord.Embed(
            title=f"__{interaction.user.name}__",
            description='\n'.join(moved_file) ,
            color=discord.Color.orange()
            )
            embed.add_field(name=f"**ไฟล์นี้เกิน 8MB นะคะ{random.choice(sad_emoji)}**", value='\n'.join(remaining), inline=False)
            await interaction.response.send_message(f"เพิ่มไฟล์ให้แล้วนะคะ{random.choice(happy_emoji)}", embed=embed)
    except:
        await interaction.response.send_message(f"พี่ยังไม่ได้ส่งไฟล์มาให้หนูนะคะ{random.choice(sad_emoji)}")


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
async def เปลี่ยนตาราง(interaction: discord.Interaction,):
    try:
        userID = str(interaction.user.id)
        timetable_dir = os.path.join(script_dir, "Data", userID, "Time_Table")
        if not os.path.exists(timetable_dir):
            os.makedirs(timetable_dir, exist_ok=True)

        if interaction.guild and interaction.channel:
            guild_name = interaction.guild.name
            channel_name = interaction.channel.name
            attachment = str(find_recent_message.find_recent_attachment(server=guild_name, channel=channel_name, userID=userID))
        else:
            guild_name = 'DM'
            channel_name = 'DM'
            attachment = str(find_recent_message.find_recent_attachment(server=guild_name, channel=channel_name, userID=userID))
        
        attachment = attachment.replace("attachment = ", "")
        attachment = ast.literal_eval(attachment)
        source = os.path.join(script_dir, "temp", "Data", userID, encryption.encrypt(attachment[-1], userID))
        # print(source)
        # print(timetable_dir)
        if len(os.listdir(timetable_dir)) > 0:
            for i in os.listdir(timetable_dir):
                file = os.path.join(timetable_dir, i)
                os.remove(file)
        shutil.move(src=source, dst=os.path.join(timetable_dir, encryption.encrypt(attachment[-1], userID)))
        
        await interaction.response.send_message(f"เปลี่ยนให้แล้วนะคะ {random.choice(happy_emoji)}", ephemeral=False)
    except:
        await interaction.response.send_message(f"พี่ยังไม่ได้ส่งไฟล์ให้หนูนะคะ {random.choice(sad_emoji)}", ephemeral=False)
    


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


@client.tree.command(name="command", description="Command List")
async def command(interaction: discord.Interaction):
    text = f"""
- /ขอตาราง\u200B{space(29)}\u200B:calendar_spiral: ขอตารางเวลา/ตารางเรียนที่บันทึกใว้
- /เปลี่ยนตาราง\u200B{space(22)}\u200B:pencil: เปลี่ยนตารางเวลา/ตารางเรียน
- /qr\u200B{space(42)}\u200B:white_square_button: สร้าง QR Code จากลิงค์
- /แปล\u200B{space(37)}\u200B:keyboard: แก้คำจากการพิมแล้วลืมเปลี่ยนภาษา
- /list\u200B{space(40)}\u200B:dividers: แสดงรายการไฟลที่ฝากใว้ทั้งหมด
- /ฝาก\u200B{space(38)}\u200B:open_file_folder: ฝากไฟล์ใว้ที่ Proxima
- /ขอไฟล์\u200B{space(32)}\u200B:page_facing_up: ขอไฟล์ที่ฝากใว้
- /ลบไฟล์\u200B{space(32)}\u200B:wastebasket: ลบไฟล์ที่ฝากใว้
- /id\u200B{space(42)}\u200B:identification_card: ดู User ID ของตัวเอง
- /วันที่\u200B{space(38)}\u200B:date: แสดงปฎิทิน
"""
    embed = discord.Embed(
    title="__Command__",
    description=text,
    color=discord.Color.orange()
    )
    await interaction.response.send_message(embed=embed)

client.run(Token)