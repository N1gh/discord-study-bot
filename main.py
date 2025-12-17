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

from pathlib import Path

CONTENT_DIR = Path("content/pt")

@bot.command()
async def topics(ctx):
    if not CONTENT_DIR.exists():
        await ctx.send("❌ Conteúdo não encontrado.")
        return

    topics = [f.stem for f in CONTENT_DIR.glob("*.txt")]
    topic_list = "\n".join(f"- {t}" for t in topics)

    await ctx.send(f"📘 Portuguese study topics:\n{topic_list}")


@bot.command()
async def study(ctx, topic: str):
    file_path = CONTENT_DIR / f"{topic}.txt"
    if not file_path.exists():
        await ctx.send("❌ Topic not found.")
        return

    content = file_path.read_text(encoding="utf-8")
    await ctx.send(
        f"📖 **{topic.replace('_', ' ').title()} (Portuguese)**\n\n{content}"
    )

bot.run(TOKEN)
