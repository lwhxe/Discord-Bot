import discord
import ctypes
import platform
from subprocess import Popen, PIPE
import glob
from discord import app_commands
from discord.ext import commands, tasks
import re
import aiohttp
import asyncio
from bs4 import BeautifulSoup
import moviepy.editor as mp
import requests
import openai
import chess
import chess.engine
import chess.pgn
import matplotlib.pyplot as plt
import tempfile
import os
from datetime import datetime
from xml.etree import ElementTree as ET
import time as pytime
import os
import subprocess
import uuid
import json
import logging
from google.oauth2 import service_account
from googleapiclient.discovery import build

logging.basicConfig(level=logging.INFO)

with open("badwords.json", 'r') as json_file:
    bad_words = json.load(json_file)

with open("keys.json", "r+") as file:
    data = json.load(file)
    temalista = data['temalista']
    kursid = data['kursid']  # Load kursid data

TOKEN = data["Bot_token"]
CHANNEL_ID = 1144745209272471622
SERVER_ID = 1144646269743140974

bot = commands.Bot(command_prefix='/', intents=discord.Intents.all())
@bot.event
async def on_ready():
    channel = bot.get_channel(CHANNEL_ID)
    try:
        synced = await bot.tree.sync()
    except Exception as e:
        print(e)
    await asyncio.sleep(10)
    print("\033[2J\033[H", end="", flush=True)
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    channel_name = message.channel.name
    author_name = message.author.name
    content = message.content
    
    log_message = f"Channel: {channel_name}, Author: {author_name}, Message: {content}\n"
    with open('logs.txt', 'a') as log_file:
        log_file.write(log_message)
    message_content = message.content.lower()
    pattern = r'(?:' + '|'.join(re.escape(word) for word in bad_words) + r')'
    if re.search(pattern, message_content):
        await message.delete()
        important_embed = discord.Embed(title="Youuu chicken shit...", description=f"You had to use a bad word like a little baby...{message.author.mention}", color=0xFF0000)
        msg = await message.channel.send(embed=important_embed)
        await asyncio.sleep(5)
        await msg.delete()
    await bot.process_commands(message)

@bot.event
async def on_message_edit(before, after):
    # Ignore the event if the message content hasn't changed or the bot is the author
    if before.content == after.content or after.author == bot.user:
        return

    # Log the edited message
    channel_name = after.channel.name
    author_name = after.author.name
    content = after.content
    
    log_message = f"Edited Message - Channel: {channel_name}, Author: {author_name}, Message: {content}\n"
    with open('logs.txt', 'a') as log_file:
        log_file.write(log_message)
    
    # Check for bad words in the edited message
    message_content = after.content.lower()
    pattern = r'(?:' + '|'.join(re.escape(word) for word in bad_words) + r')'
    if re.search(pattern, message_content):
        await after.delete()
        important_embed = discord.Embed(title="Youuu chicken shit...", description=f"You had to use a bad word like a little baby...{after.author.mention}", color=0xFF0000)
        msg = await after.channel.send(embed=important_embed)
        await asyncio.sleep(5)
        await msg.delete()

    # Process commands if any in the edited message
    await bot.process_commands(after)


@bot.tree.command(name="turnoff", description="Turns off the bot")
async def turnoff(interaction:discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    has_permission = any(role.name == 'ADMIN' or role.name == 'Programmerare' for role in interaction.user.roles)
    if not has_permission:
        embed_denial = discord.Embed(title="Errno13", description=f"You don't have permission to use that command {interaction.user.mention}!", color=0xFF0000)
        await interaction.followup.send(embed=embed_denial, ephemeral=True)
        return
    else:
        embed = discord.Embed(description="Shutting down...", color=0xFF0000)
        await interaction.followup.send(embed=embed, ephemeral=True)
        bot.close()

@bot.tree.command(name = 'lockdown', description = 'Locks down the server until unlocked')
async def lockdown(interaction:discord.Interaction):
    embed_message = discord.Embed(
        title='Lockdown requested',
        description='Attempting Lockdown...',
        color=0xFF0000
    )
    await interaction.response.send_message(embed=embed_message, ephemeral = True)
    ADMIN_ROLE = discord.utils.get(interaction.guild.roles, name='ADMIN')
    if ADMIN_ROLE not in interaction.user.roles:
        canceling_embed = discord.Embed(
            title='Errno13',
            description="You don't have permission to do that!",
            color=0xFF0000
        )
        await interaction.followup.send(embed=canceling_embed, ephemeral = True)
        return
    finished_embed = discord.Embed(
        title = 'Server Locked!',
        description = "To unlock the server you must use the /unlock command.",
        color = 0xFF0000
    )
    # adding the lockdown role to everyone
    lockdown_role = discord.utils.get(interaction.guild.roles, name = 'lockdown')
    for member in interaction.guild.members:
        await member.add_roles(lockdown_role)
    await interaction.followup.send(embed=finished_embed)

@bot.tree.command(name='unlock', description = 'Unlocks the server!')
async def unlock(interaction:discord.Interaction):
    unlocking_embed = discord.Embed(title = 'Unlock requested', description='Unlocking...', color = 0xFF0000)
    await interaction.response.send_message(embed=unlocking_embed, ephemeral = True)
    ADMIN_ROLE = discord.utils.get(interaction.guild.roles, name='ADMIN')
    if ADMIN_ROLE not in interaction.user.roles:
        canceling_embed = discord.Embed(
            title = 'Errno13',
            description="You don't have permission to do that!",
            color=0xFF0000
            )
        canceling_embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/7596/7596460.png")
        await interaction.followup.send(embed=canceling_embed)
        return
    final_embed = discord.Embed(
        title = 'Server Unlocked!',
        description = "The server is now free to use!",
        color=0xFF0000
    )
    # Removing the lockdown role from everyone
    lockdown_role = discord.utils.get(interaction.guild.roles, name='lockdown')
    if lockdown_role:
        for member in interaction.guild.members:
            try:
                await member.remove_roles(lockdown_role)
            except Exception as e:
                print(f"Failed to remove role from {member.name}: {e}")
        await interaction.followup.send(embed=final_embed)
    else:
        print("Lockdown role not found")
@bot.tree.command(name='whois', description="find out different ID's within the server")
@app_commands.describe(item = 'What item ID are you looking for?')
@app_commands.describe(name = 'Name of the user or channel to look for')
async def whois(interaction: discord.Interaction, item: str, name: str = None):
    guild = interaction.guild  # Get the Guild object from the interaction

    if item.lower() == 'users':
        if name:
            user = discord.utils.find(lambda m: m.name == name, guild.members)
            if user:
                await interaction.response.send_message(f"User ID of {name}: {user.id}", ephemeral = True)
            else:
                await interaction.response.send_message(f"No user with the name {name} found.", ephemeral = True)
        else:
            user_ids = {member.name: member.id for member in guild.members}
            await interaction.response.send_message(f"User IDs: {user_ids}", ephemeral = True)

    elif item.lower() == 'channels':
        if name:
            channel = discord.utils.find(lambda c: c.name == name, guild.channels)
            if channel:
                await interaction.response.send_message(f"Channel ID of {name}: {channel.id}", ephemeral = True)
            else:
                await interaction.response.send_message(f"No channel with the name {name} found.", ephemeral = True)
        else:
            channel_ids = {channel.name: channel.id for channel in guild.channels}
            await interaction.response.send_message(f"Channel IDs: {channel_ids}", ephemeral = True)

    elif item.lower() == 'roles':
        if name:
            role = discord.utils.find(lambda r: r.name == name, guild.roles)
            if role:
                await interaction.response.send_message(f"Role ID of {name}: {role.id}", ephemeral=True)
            else:
                await interaction.response.send_message(f"No role with the name {name} found.", ephemeral=True)
        else:
            await interaction.response.send_message("Role name must be specified.", ephemeral=True)

    else:
        await interaction.response.send_message("Invalid item. Choose from 'users', 'channels', or 'roles'.", ephemeral = True)

@bot.tree.command(name='report', description="Reports selected user to the Admins..")
@app_commands.describe(user = "Who would you like to report?")
@app_commands.describe(context = "Describe what made you report selected user..")
async def report(interaction:discord.Interaction, user: str, context:str):
    find_embed = discord.Embed(title = "Sending request", color=0xFF0000)
    await interaction.response.send_message(embed=find_embed, ephemeral = True)
    guild = interaction.guild
    reported_user = discord.utils.find(lambda m: m.name == user, guild.members)
    reporting_user = interaction.user
    reporting_user_id = interaction.user.id
    if reported_user:
        print(f"{reported_user} found!")
        admin_channel = discord.utils.get(guild.text_channels, name='commands')
        if admin_channel:
            print(f"{admin_channel} Channel found!") # Debugging line
            report_message = discord.Embed(title = f"Report from {reporting_user}, against {reported_user}", description = f"Context: {context}", color=0xFF0000)
            await admin_channel.send(embed=report_message)
            confirmation_embed = discord.Embed(title='New report', description = f"<@{reporting_user_id}> 's report against {reported_user} has been sent to the Admins!", color=0xFF0000)
            await interaction.followup.send(embed=confirmation_embed, ephemeral = True)
        else:
            print("Admin channel not found.")
    else:
        print(f"No user with the requested name found.")
        user_unfound = discord.Embed(title = "Errno2", description = f"A user with the name {user} cannot be found... Make sure you're not using their nickname, instead use their username!", ephemeral = True)

@bot.tree.command(name='addbadword', description="This will add a bad word to a list! just separate by a comma! *,*")
@app_commands.describe(badwords="List bad words separated by a comma like this: bad1, bad2...")
async def addbadword(interaction:discord.Interaction, badwords:str):
    embed_prefix = discord.Embed(title="Checking permissions...", color=0xFF0000)
    await interaction.response.send_message(embed=embed_prefix, ephemeral=True)

    has_permission = any(role.name == 'ADMIN' or role.name == 'Programmerare' for role in interaction.user.roles)
    if not has_permission:
        embed_denial = discord.Embed(title="Errno13", description=f"You don't have permission to use that command {interaction.user.mention}!", color=0xFF0000)
        await interaction.followup.send(embed=embed_denial, ephemeral=True)
        return

    first_embed = discord.Embed(title="Adding bad words...", color=0xFF0000)
    cmd_channel = interaction.guild.get_channel(1144648240000675951)
    if interaction.channel == cmd_channel:
        await interaction.followup.send(embed=first_embed)
    else:
        await interaction.followup.send(embed=first_embed, ephemeral=True)

    new_index = badwords.split(', ')
    bad_words.extend(new_index)
    fixed_embed = discord.Embed(title="Added the following words!", description=f"{new_index}", color=0xFF0000)
    await interaction.followup.send(embed=fixed_embed, ephemeral=True)

    with open("badwords.json", 'w') as json_file:
        json.dump(bad_words, json_file, indent=4)

@bot.tree.command(name="purge", description="This will delete the last *specified amount* of messages")
@app_commands.describe(amount="How many?")
async def purge(interaction:discord.Interaction, amount: int):
    await interaction.response.defer(ephemeral=True)#Create if statement here:
    first_embed = discord.Embed(title=f"Attempting deletion of {amount} messages..", color=0xFF0000)
    await interaction.followup.send(embed=first_embed, ephemeral=True)
    try:
        await interaction.channel.purge(limit=amount)
    except Exception as e:
        print(e)
    finished_embed = discord.Embed(title="Deletion complete", description=f"{amount} mesages have been deleted!", color=0xFF0000)
    await interaction.followup.send(embed=finished_embed, ephemeral=True)   


@bot.tree.command(name="bestmove", description="Tells you the best move for the FEN you give it")
@app_commands.describe(fen_string="Enter the FEN string..")
async def bestmove(interaction: discord.Interaction, fen_string: str):
    channel_id = 1167855264578412564
    secondchan_id = 1157762207241744424
    if interaction.channel_id != channel_id and interaction.channel_id != secondchan_id:
        return

    message = await interaction.response.defer()
    await asyncio.sleep(1)
    
    # Initialize engine and analyze the board
    # Keeping this part unchanged as you requested
    board = chess.Board(fen_string)
    engine = chess.engine.SimpleEngine.popen_uci("C:\\Users\\41784\\OneDrive\\Desktop\\chesscalc\\stockfish\\stockfish\\stockfish-windows-x86-64-avx2.exe")
    info = engine.analyse(board, chess.engine.Limit(depth=20))
    best_move = info['pv'][0]
    score = info['score'].relative.score()
    board.push(best_move)
    post_move_FEN = board.fen()
    engine.quit()

    # Create final embed with results
    final_embed = discord.Embed(title=f"Best Move for {interaction.user.name}", color=0xFF0000)
    final_embed.add_field(name="Best Move", value=str(best_move), inline=True)
    final_embed.add_field(name="Score After", value=str(score), inline=True)
    final_embed.add_field(name="FEN String After", value=post_move_FEN, inline=False)

    # Edit the original message with the final results
    await interaction.followup.send(embed=final_embed)
    return


@bot.tree.command(name="tex", description="Turns Latex into math image")
@app_commands.describe(latex_string="Insert the latex you want to turn into math..")
@app_commands.describe(image_size="Changes the image size to fit on the screen.. (multiplicatively)")
async def tex(interaction:discord.Interaction, latex_string: str, image_size: int):
    message = await interaction.response.defer()
    pattern = r'(?:' + '|'.join(re.escape(word) for word in bad_words) + r')'
    if re.search(pattern, interaction.data['options'][0]['value']):
        important_embed = discord.Embed(title="Youuu chicken shit...", description=f"You had to use a bad word like a little baby...{interaction.user.mention}", color=0xFF0000)
        msg = await interaction.followup.send(embed=important_embed)
        return
    if interaction.channel.id == 1144745209272471622:
        return
    try:    
        fig, ax = plt.subplots(figsize=(image_size * 2, image_size))
        fig.patch.set_alpha(0)
        ax.axis('off')
        plt.text(0.5, 0.5, f'${latex_string}$', size=20, ha='center', va='center', color='#d6d6d6')
        plt.axis('off')
    
        # Save the plot to a temporary file
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp:
            plt.savefig(temp.name)
            temp.seek(0)
    
        # Send the image in Discord
        await interaction.followup.send(file=discord.File(fp=temp.name))
    
        # Close the plot and remove the temporary file
        plt.close()
        os.unlink(temp.name)
    except Exception as e:
        print(e)
        print(interaction.data['options'][0]['value'])
        error_embed = discord.Embed(title="Errno4", description=f"Error: {e}", color=0xFF0000)
        error2_embed = discord.Embed(title="Errno exception data", description=f" Prompt : {interaction.data['options'][0]['value']}")
        await interaction.followup.send(embed=error_embed)
        await interaction.followup.send(embed=error2_embed)
        return

@bot.tree.command(name="skolmaten", description="fetches the school food for specified week")
@app_commands.describe(weeknumber="What week of the year are you looking for?")
async def skolmaten(interaction:discord.Interaction, weeknumber: int):
    await interaction.response.defer()
    starttime = pytime.time()
    if interaction.channel.id == 1154812080961093693:
        now = datetime.now()
        _, week_number, _ = now.isocalendar()
        
        offset = weeknumber - week_number
        food_descriptions = fetch_school_food(offset)
        
        if food_descriptions == "Failed to fetch information.":
            await interaction.followup.send("Failed to fetch information.")
            return
        
        formatted_info = format_food_info(fetch_school_food(offset))
        endtime = pytime.time()
        totaltime = endtime - starttime
        formatted_embed = discord.Embed(title=f"SKOLMATEN vecka {weeknumber}", description=f"{formatted_info[12:]}\n\nReceived in {totaltime:.3f} seconds!", color=0x00fff5)
        await interaction.followup.send(embed=formatted_embed)
    else:
        embed = discord.Embed(title="Errno5", description="You cannot use this command here!", color=0xFF0000)
        await interaction.followup.send(embed=embed, ephemeral=True)


def fetch_school_food(offset):
    url = f"https://skolmaten.se/glantanskolan/rss/weeks/?offset={offset}&limit=1"
    response = requests.get(url)
    if response.status_code != 200:
        return "Failed to fetch information."
    
    root = ET.fromstring(response.text)
    food_descriptions = []
    
    for item in root.findall('.//item'):
        description = item.find('description').text
        if description:
            # Keep <br/> tags for later use, remove other HTML tags and CDATA
            clean_description = re.sub(r'<(?!br/?>).*?>', '', description.replace('<![CDATA[', '').replace(']]>', ''))
            food_descriptions.append(clean_description)
            
    return food_descriptions

def format_food_info(food_descriptions):
    formatted = "## SKOLMATEN\n"
    days = ["Måndag", "Tisdag", "Onsdag", "Torsdag", "Fredag"]
    
    for day, description in zip(days, food_descriptions):
        # Splitting each day's food descriptions by <br/> and joining them with new lines
        daily_foods = description.split('<br/>')
        formatted_daily_foods = "\n> ".join(daily_foods)
        
        formatted += f"***{day}***\n> {formatted_daily_foods}\n"
        
    return formatted

# In your main function, use format_food_info to format the food information before sending it

@bot.tree.command(name="ytdlp", description="Sends a downloaded video in the chat")
@app_commands.describe(link="Specify the link to the youtube video.")
async def ytdlp(interaction: discord.Interaction, link: str):
    await interaction.response.defer()
    start_time = pytime.time()
    download_dir = "F:/Rasputin/dist"
    ytdlp_path = "C:/Temp/PATH_stuff/yt-dlp/yt-dlp.exe"
    unique_id = uuid.uuid4()
    unique_filename = f"video_{unique_id}.%(ext)s"
    command = [ytdlp_path, "-f", "bestvideo+bestaudio", "-o", f"{download_dir}/{unique_filename}", link]

    startupinfo = None
    if platform.system() == "Windows":
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE

    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    process = await asyncio.create_subprocess_exec(
        *command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        startupinfo=startupinfo,
        creationflags=subprocess.CREATE_NO_WINDOW if startupinfo else 0
    )

    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        await interaction.followup.send(f"Error downloading video: {stderr.decode()}")
        return

    # Find the downloaded file
    downloaded_file_path = ""
    for file in os.listdir(download_dir):
        if file.startswith(f"video_{unique_id}"):
            downloaded_file_path = os.path.join(download_dir, file)
            break

    if not downloaded_file_path:
        await interaction.followup.send("Downloaded file not found.")
        return

    # Function to check video resolution
    def get_video_resolution(path):
        clip = mp.VideoFileClip(path)
        width, height = clip.size
        clip.close()
        return width, height

    # Resolution check
    loop = asyncio.get_event_loop()
    width, height = await loop.run_in_executor(None, get_video_resolution, downloaded_file_path)

    if height < 720:
        # Send the original downloaded video
        try:
            with open(downloaded_file_path, 'rb') as fp:
                end_time = pytime.time()
                totaltime = end_time - start_time
                embed = discord.Embed(description=f"The time used: {totaltime:.3f} seconds!", color=0x00fff5)
                await interaction.followup.send(file=discord.File(fp, filename=os.path.basename(downloaded_file_path)), embed=embed)
        finally:
            os.remove(downloaded_file_path)
    else:
        # Convert the video
        batch_command = ["conversion.bat", downloaded_file_path]
        batch_startupinfo = None
        if platform.system() == "Windows":
            batch_startupinfo = subprocess.STARTUPINFO()
            batch_startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            batch_startupinfo.wShowWindow = subprocess.SW_HIDE

        process = await asyncio.create_subprocess_exec(
            *batch_command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            startupinfo=batch_startupinfo
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            await interaction.followup.send(f"Error in post-processing: {stderr.decode()}")
            return

        # Handle the converted file
        converted_file_path = f"{download_dir}/video_{unique_id}_converted.mp4"
        if os.path.exists(converted_file_path):
            try:
                with open(converted_file_path, 'rb') as fp:
                    end_time = pytime.time()
                    totaltime = end_time - start_time
                    embed = discord.Embed(description=f"The time used: {totaltime:.3f} seconds!", color=0x00fff5)
                    await interaction.followup.send(file=discord.File(fp, filename=os.path.basename(converted_file_path)), embed=embed)
            finally:
                os.remove(converted_file_path)
                os.remove(downloaded_file_path)
        else:
            await interaction.followup.send("Converted file not found.")

@bot.tree.command(name="sort", description="Sorts any amount of numbers put inside of the command.")
@app_commands.describe(numbers="Write any numbers separated by a comma")
async def sort(interaction: discord.Interaction, numbers: str):
    logging.info("Received sort command.")
    await interaction.response.defer(ephemeral=True)
    logging.info("Interaction deferred.")

    try:
        array = [float(n) for n in numbers.replace(" ", "").split(",")]
        logging.info(f"Converted input to array: {array}")
        sorted_array = quick_sort(array)
        logging.info(f"Array sorted: {sorted_array}")
        embed = discord.Embed(title="Sorted numbers:", description=', '.join(map(str, sorted_array)), color=0xFF0000)
        await interaction.followup.send(embed=embed)
        logging.info("Response sent.")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        message = await interaction.followup.send("An error occurred while processing your request.")
        await asyncio.sleep(5)
        await message.delete()

def quick_sort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quick_sort(left) + middle + quick_sort(right)
bot.run(TOKEN)