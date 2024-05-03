import discord
from discord import app_commands
from discord.ext import commands, tasks
import subprocess
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import re
import asyncio
import time as pytime
import json
import os
import sys
import requests
import py_compile
with open("json_files/badwords.json", 'r') as json_file:
    bad_words = json.load(json_file)
with open("json_files/key.txt", "r") as key_file:
    data = key_file.read()
TOKEN = data
bot = commands.Bot(command_prefix='/', intents=discord.Intents.all())
def check_syntax(filename):
    try:
        # This will compile the source into a code object that can be executed; raise an exception on syntax errors
        py_compile.compile(filename, doraise=True)
        print(f"No syntax errors in {filename}.")
        return None  # Explicitly returning None for clarity
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"Syntax error or other issue in {filename}: {error_details}")
        return error_details  # Returning detailed traceback information
async def fetch_all_members(bot, guild_id):
    guild = bot.get_guild(guild_id)
    if guild is not None:
        await guild.chunk()  # This ensures all members are loaded
        return guild.members  # Returns a list of Member objects
    else:
        print("Guild not found. Ensure the bot is part of the guild and the ID is correct.")
        return None
def download_video(url, download_path, format_specifier='best'):
    # Command to download the video in the specified format to the given path
    subprocess.run(['yt-dlp', '-f', format_specifier, '-o', download_path, url])
def get_file_size(file_path):
    # Get the size of the file in megabytes
    return os.path.getsize(file_path) / (1024 * 1024)
@bot.event
async def on_ready():
    try:
        # Sync registered commands with the current commands in code.
        # This updates any changes and removes commands not present in the code.
        synced = await bot.tree.sync()

        # Fetch all registered commands from Discord
        registered_commands = await bot.tree.fetch_commands()

        # Compare registered commands with the bot's current commands
        current_command_names = {cmd.name for cmd in bot.tree.get_commands()}
        stale_commands = [cmd for cmd in registered_commands if cmd.name not in current_command_names]

        # Remove commands that are no longer defined in the bot's code
        for cmd in stale_commands:
            await bot.tree.remove_command(cmd.name, type=cmd.type)
            print(f"Removed stale command: {cmd.name}")

        print(f"{len(synced)} commands synced!")

    except Exception as e:
        print(f"Error during command sync or removal: {e}")
@bot.event
async def on_message(message) -> None:
    if message.author == bot.user:
        return
    channel_name = message.channel.name
    if channel_name == "announcements":
        await message.delete()
        return
    author_name = message.author.name
    content = message.content
    print(f"{author_name}{message.author.discriminator} in {channel_name} sent: {content}")
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
async def on_message_edit(before, after) -> None:
    if before.content == after.content or after.author == bot.user:
        return
    if message.channel.name == "announcements":
        if message.author.id != 594947855278538783:
            await message.delete()
            return
    message_content = after.content.lower()
    pattern = r'(?:' + '|'.join(re.escape(word) for word in bad_words) + r')'
    if re.search(pattern, message_content):
        await after.delete()
        important_embed = discord.Embed(title="Youuu chicken shit...", description=f"You had to use a bad word like a little baby...{after.author.mention}", color=0xFF0000)
        msg = await after.channel.send(embed=important_embed)
        await asyncio.sleep(5)
        await msg.delete()
    await bot.process_commands(after)
@bot.tree.command(name="update", description="Reinitialize the bots sequence...")
async def update(interaction: discord.Interaction) -> None:
    # Checking if the user has the ADMIN role
    admin_role = discord.utils.find(lambda r: r.name == 'ADMIN', interaction.user.roles)
    if not admin_role:
        msg = discord.Embed(description=f"You are not allowed to perform this action {interaction.user.mention}!", color=0xFF0000)
        await interaction.response.send_message(embed=msg, ephemeral=True)
    else:
        msg = discord.Embed(description="Updating bot...", color=0xFF0000)
        await interaction.response.send_message(embed=msg, ephemeral=True)
        # Restarting the script
        check = check_syntax("main.py")
        if check == 0:
            os.execl(sys.executable, sys.executable, 'main.py')
        msg = discord.Embed(description=f"There was an error\n{check}", color=0xFF0000)
        await interaction.followup.send(embed=msg, ephemeral=True)
        return
@bot.tree.command(name="upgrade", description="Pull from github...")
async def upgrade(interaction: discord.Interaction) -> None:
    admin_role = discord.utils.find(lambda r: r.name =="ADMIN", interaction.user.roles)
    if not admin_role:
        msg = discord.Embed(description=f"You are not allowed to perform this action {interaction.user.mention}!", color=0xFF0000)
        await interaction.response.send_message(embed=msg, ephemeral=True)
    else:
        msg = discord.Embed(description="Upgrading bot...", color=0xFF0000)
        await interaction.response.send_message(embed=msg, ephemeral=True)
        response = requests.get("https://raw.githubusercontent.com/lwhxe/Discord-Bot/main/bot.pyw")
        print(response.text)
        if response.status_code == 200:
            with open("main.py", "w") as file:
                file.write(response.text)
            print("file downloaded successfully.")
        else:
            print("Failed to download file.", response.status_code)
            return
        msg = discord.Embed(description="Bot upgraded.", color=0xFF0000)
        await interaction.followup.send(embed=msg, ephemeral=True)
@bot.tree.command(name="notify", description="Sends custom message to users.")
@app_commands.describe(content="What do you want to send?")
@app_commands.describe(users="Who do you want to send this to?")
async def notify(interaction: discord.Interaction, content: str, users: str):
    await interaction.response.defer(ephemeral=True)  # Correctly defer the response
    successful_users = []
    failed_users = []

    if users == "all":
        members = await fetch_all_members(bot, 1205978381741596684)  # Await the async call
        for user in members:
            try:
                await user.send(content)
                successful_users.append(f"{user.name}#{user.discriminator}")
            except Exception as e:
                failed_users.append(f"{user.name}#{user.discriminator}: {str(e)}")
    else:
        user_list = users.replace(" ", "").split(",")
        for full_username in user_list:
            try:
                username, discriminator = full_username.split('#')
            except ValueError:
                await interaction.followup.send("Please provide each username in the format username#discriminator.", ephemeral=True)
                return

            user_found = None
            for guild in bot.guilds:
                user_found = discord.utils.find(lambda m: m.name == username and m.discriminator == discriminator, guild.members)
                if user_found:
                    break

            if user_found:
                try:
                    await user_found.send(content)
                    successful_users.append(f"{username}#{discriminator}")
                except Exception as e:
                    failed_users.append(f"{username}#{discriminator}: {str(e)}")
            else:
                failed_users.append(f"{username}#{discriminator}: User not found")

    if successful_users:
        success_message = "Message sent to: " + ", ".join(successful_users)
    else:
        success_message = "No messages were sent."

    if failed_users:
        failure_message = "Failed to send to: " + ", ".join(failed_users)
    else:
        failure_message = "All messages were successfully sent."

    # Send a follow-up message after handling initial response
    await interaction.followup.send(f"{success_message}\n{failure_message}", ephemeral=True)
@bot.tree.command(name="yt_dlp", description="Downloads video from internet.")
@app_commands.describe(url="What URL are you downloading from?")
@app_commands.describe(format_specifiers="Yt-dlp needs some format specifiers from you.")
@app_commands.describe(filename="What do you want the file to be called?")
async def yt_dlp(interaction: discord.Interaction, url: str, format_specifiers: str, filename: str):
    raise NotImplementedError
bot.run(TOKEN)
