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
with open("json_files/badwords.json", 'r') as json_file:
    bad_words = json.load(json_file)
with open("json_files/key.txt", "r") as key_file:
    data = key_file.read()
TOKEN = data
bot = commands.Bot(command_prefix='/', intents=discord.Intents.all())
@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"{len(synced)} commands synced!")
    except Exception as e:
        print(e)
    await asyncio.sleep(10)
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
        msg = discord.(description=f"You are not allowed to perform this action {interaction.user.mention}!", color=0xFF0000)
        await interaction.response.send_message(embed=msg, ephemeral=True)
    else:
        msg = discord.Embed(description="Updating bot...", color=0xFF0000)
        await interaction.response.send_message(embed=msg, ephemeral=True)
        # Restarting the script
        os.execl(sys.executable, sys.executable, 'main.py')
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
bot.run(TOKEN)
