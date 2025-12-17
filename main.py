import os
import discord
from discord.ext import commands

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")

@bot.command()
async def ask(ctx, *, question: str):
    await ctx.send(
        "🤖 I'm still learning!\n\n"
        "You asked:\n"
        f"**{question}**\n\n"
        "I'll answer shortly."
    )

bot.run(TOKEN)
