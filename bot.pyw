import discord
from discord import app_commands
from discord.ext import commands, tasks
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
def check_syntax(filename) -> None:
    try:
        # This function compiles the source into a code object which can be executed
        # It will raise a PyCompileError if there are syntax errors
        py_compile.compile(filename, doraise=True)
        print(f"No syntax errors in {filename}.")
        return
    except py_compile.PyCompileError as e:
        print(f"Syntax error in {filename}: {e}")
        return 1
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
        if check != 1:
            os.execl(sys.executable, sys.executable, 'main.py')
        msg = discord.Embed(description="There was an error...", color=0xFF0000)
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
    user_list = users.replace(" ", "").split(",")  # Corrected from `remove` to `replace`
    successful_users = []
    failed_users = []

    for full_username in user_list:
        try:
            username, discriminator = full_username.split('#')
        except ValueError:
            await interaction.response.send_message("Please provide each username in the format username#discriminator.", ephemeral=True)
            return

        user_found = None
        # Search through all members in all guilds the bot is part of
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

    # Handle initial response if it wasn't already done
    if interaction.response.is_done():
        await interaction.followup.send(f"{success_message}\n{failure_message}", ephemeral=True)
    else:
        await interaction.response.send_message(f"{success_message}\n{failure_message}", ephemeral=True)

    
    raise NotImplementedError
bot.run(TOKEN)
