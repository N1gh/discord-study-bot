import os
import discord
from discord.ext import commands
from pathlib import Path

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

CONTENT_DIR = Path("content/pt")

@bot.command()
async def topics(ctx):
    if not CONTENT_DIR.exists():
        await ctx.send("❌ Conteúdo não encontrado.")
        return

    topics = [f.stem for f in CONTENT_DIR.glob("*.txt")]

    if not topics:
        await ctx.send("⚠️ No topics available yet.")
        return

    topic_list = "\n".join(f"- {t}" for t in topics)
    await ctx.send(f"📘 Portuguese study topics:\n{topic_list}")

@bot.command()
async def study(ctx, topic: str):
    file_path = CONTENT_DIR / f"{topic}.txt"
    if not file_path.exists():
        await ctx.send("❌ Topic not found.")
        return

    raw_lines = file_path.read_text(encoding="utf-8").splitlines()
    message = f"📖 **{topic.replace('_', ' ').title()} (Portuguese)**\n\n"

    i = 0
    while i < len(raw_lines):
        line = raw_lines[i]

        if "—" in line:
            pt, en = line.split("—")
            message += f"🇧🇷 **{pt.strip()}**\n🇺🇸 {en.strip()}\n"
        elif line.startswith("Pronunciation"):
            message += f"🔊 {line.replace('Pronunciation:', '').strip()}\n\n"

        i += 1

    await ctx.send(message[:1900])

if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN not found in environment variables")

bot.run(TOKEN)
