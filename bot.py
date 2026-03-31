import os
import discord
from discord.ext import commands
from discord import app_commands

# ---------------- TOKEN ----------------
TOKEN = os.getenv("TOKEN")  # Make sure you set this in Render environment variables

# ---------------- INTENTS ----------------
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # Required for role management

# ---------------- BOT SETUP ----------------
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# Staff role names
STAFF_ROLES = ["👑- Godfather", "Father"]

# Vouch dictionary (in-memory storage)
vouches = {}  # {user_id: [vouched_by_user_ids]}

# ---------- EVENTS ----------
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    try:
        synced = await tree.sync()
        print(f"Synced {len(synced)} slash commands.")
    except Exception as e:
        print(e)

# ---------- COMMANDS ----------
@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

# Slash command: role selection
@tree.command(name="role", description="Select a role")
@app_commands.describe(role_name="The role you want")
async def role(interaction: discord.Interaction, role_name: str):
    role = discord.utils.get(interaction.guild.roles, name=role_name)
    if role is None:
        await interaction.response.send_message(f"Role `{role_name}` not found.", ephemeral=True)
        return
    await interaction.user.add_roles(role)
    await interaction.response.send_message(f"You have been given the `{role_name}` role!", ephemeral=True)

# Slash command: vouch someone
@tree.command(name="vouch", description="Vouch for a verified user")
@app_commands.describe(user="The user you want to vouch for")
async def vouch(interaction: discord.Interaction, user: discord.Member):
    verified_roles = ["Verified"]  # Change to your verified role names
    if not any(role.name in verified_roles for role in interaction.user.roles):
        await interaction.response.send_message("You must be verified to vouch!", ephemeral=True)
        return
    
    if user.id == interaction.user.id:
        await interaction.response.send_message("You cannot vouch for yourself!", ephemeral=True)
        return
    
    if user.id not in vouches:
        vouches[user.id] = []
    if interaction.user.id in vouches[user.id]:
        await interaction.response.send_message("You already vouched for this user.", ephemeral=True)
        return
    
    vouches[user.id].append(interaction.user.id)
    await interaction.response.send_message(f"You vouched for {user.display_name}!", ephemeral=True)

# Slash command: check who vouched for a user
@tree.command(name="vouched_by", description="See who vouched for a user")
@app_commands.describe(user="The user to check")
async def vouched_by(interaction: discord.Interaction, user: discord.Member):
    vouched_list = vouches.get(user.id, [])
    if not vouched_list:
        await interaction.response.send_message(f"{user.display_name} has no vouches yet.", ephemeral=True)
        return
    names = [interaction.guild.get_member(uid).display_name for uid in vouched_list]
    await interaction.response.send_message(f"{user.display_name} was vouched by: {', '.join(names)}", ephemeral=True)

# ---------- RUN BOT ----------
bot.run(TOKEN)
