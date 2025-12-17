import os
import time
import discord
from discord.ext import commands
from pathlib import Path

# =========================
# TOKEN
# =========================

TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN not found in environment variables")

# =========================
# BOT SETUP
# =========================

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# =========================
# ESTADO GLOBAL (⚠️ O ERRO ESTAVA AQUI)
# =========================

LAST_INTENT_RESPONSE = {}
COOLDOWN_SECONDS = 60

# =========================
# DIRETÓRIOS
# =========================

CONTENT_DIR = Path("content/pt")
EXPLANATIONS_DIR = Path("explanations")

# =========================
# MAPA DE INTENÇÕES
# =========================

INTENT_KEYWORDS = {
    "accentuation": [
        "accent", "acento", "acentuação"
    ],
    "por_vs_para": [
        "por ou para",
        "por vs para",
        "por e não para",
        "usar por",
        "usar para",
        "difference between por and para",
        "diferença entre por e para"
    ],
    "ser_vs_estar": [
        "ser ou estar",
        "ser vs estar"
    ]
}

# =========================
# HELPERS
# =========================

def detect_intent(text: str):
    text = text.lower()
    for intent, keywords in INTENT_KEYWORDS.items():
        for kw in keywords:
            if kw in text:
                return intent
    return None

# =========================
# EVENTS
# =========================

@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    await bot.process_commands(message)

    content = message.content.lower()

    if "?" not in content:
        return

    now = time.time()
    last_time = LAST_INTENT_RESPONSE.get(message.author.id, 0)

    if now - last_time < COOLDOWN_SECONDS:
        return

    intent = detect_intent(content)
    if intent:
        LAST_INTENT_RESPONSE[message.author.id] = now
        await message.channel.send(
            f"🤔 This looks like a question about **{intent.replace('_', ' ')}**.\n"
            f"Try: `!explain {intent}`"
        )

# =========================
# COMMANDS
# =========================

@bot.command()
async def ask(ctx, *, question: str):
    intent = detect_intent(question)

    if intent:
        await ctx.send(
            f"🤔 This looks like a question about **{intent.replace('_', ' ')}**.\n"
            f"Try: `!explain {intent}`"
        )
        return

    await ctx.send(
        "🤖 I don't have a direct explanation for this yet.\n"
        "Try asking about grammar topics like:\n"
        "`accentuation`, `ser_vs_estar`, `por_vs_para`"
    )

@bot.command()
async def explain(ctx, topic: str):
    file_path = EXPLANATIONS_DIR / f"{topic}.txt"

    if not file_path.exists():
        await ctx.send("❌ Explanation not found.")
        return

    content = file_path.read_text(encoding="utf-8")
    await ctx.send(content[:1900])

# =========================
# RUN
# =========================

bot.run(TOKEN)
