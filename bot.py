import os
import discord
from discord.ext import commands
from discord import app_commands
from flask import Flask
import threading

# ---------------- KEEP BOT ONLINE ----------------
app = Flask("")

@app.route("/")
def home():
    return "Bot is running!"

def run_web():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    t = threading.Thread(target=run_web)
    t.start()

# ---------------- BOT SETUP ----------------
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# ---------------- CONFIG ----------------
GUILD_ID = 123456789012345678  # ⚠️ PUT YOUR SERVER ID HERE
VERIFIED_ROLE = "Verified"

vouches = {}

# ---------------- EVENTS ----------------
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

    try:
        guild = discord.Object(id=GUILD_ID)
        synced = await tree.sync(guild=guild)
        print(f"Synced {len(synced)} commands.")
    except Exception as e:
        print(e)

# ---------------- BASIC COMMAND ----------------
@bot.command()
async def ping(ctx):
    await ctx.send("🏓 Pong!")

# ---------------- ROLE COMMAND ----------------
@tree.command(name="role", description="Select a role", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(role_name="Role name")
async def role(interaction: discord.Interaction, role_name: str):

    role = discord.utils.get(interaction.guild.roles, name=role_name)

    if role is None:
        await interaction.response.send_message("❌ Role not found.", ephemeral=True)
        return

    await interaction.user.add_roles(role)

    await interaction.response.send_message(
        f"✅ You received the **{role_name}** role.",
        ephemeral=True
    )

# ---------------- VOUCH COMMAND ----------------
@tree.command(name="vouch", description="Vouch for a user", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(user="User you want to vouch")
async def vouch(interaction: discord.Interaction, user: discord.Member):

    verified = discord.utils.get(interaction.user.roles, name=VERIFIED_ROLE)

    if verified is None:
        await interaction.response.send_message(
            "❌ You must be **Verified** to vouch.",
            ephemeral=True
        )
        return

    if user.id == interaction.user.id:
        await interaction.response.send_message(
            "❌ You cannot vouch yourself.",
            ephemeral=True
        )
        return

    if user.id not in vouches:
        vouches[user.id] = []

    if interaction.user.id in vouches[user.id]:
        await interaction.response.send_message(
            "❌ You already vouched this user.",
            ephemeral=True
        )
        return

    vouches[user.id].append(interaction.user.id)

    await interaction.response.send_message(
        f"✅ You vouched for **{user.display_name}**.",
        ephemeral=True
    )

# ---------------- CHECK VOUCHES ----------------
@tree.command(name="vouched_by", description="Check who vouched a user", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(user="User to check")
async def vouched_by(interaction: discord.Interaction, user: discord.Member):

    if user.id not in vouches or len(vouches[user.id]) == 0:
        await interaction.response.send_message(
            "❌ No vouches found.",
            ephemeral=True
        )
        return

    names = []

    for uid in vouches[user.id]:
        member = interaction.guild.get_member(uid)
        if member:
            names.append(member.display_name)

    await interaction.response.send_message(
        f"📜 **{user.display_name}** was vouched by:\n" + "\n".join(names),
        ephemeral=True
    )

# ---------------- START BOT ----------------
keep_alive()

TOKEN = os.getenv("TOKEN")

bot.run(TOKEN)
