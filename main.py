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

INTENT_PATTERNS = {
    "por_vs_para": {
        "must_have": ["por", "para"],
        "question_words": ["usar", "diferença", "difference", "when", "porque", "por que"]
    },
    "ser_vs_estar": {
        "must_have": ["ser", "estar"],
        "question_words": ["usar", "difference", "when", "qual", "porque"]
    },
    "accentuation": {
        "must_have": ["acento", "accent", "ô", "ê", "á", "é", "í", "ó", "ú"],
        "question_words": ["porque", "why", "por que"]
    }
}

# =========================
# HELPERS
# =========================

def detect_intent(text: str):
    text = text.lower()

    for intent, rules in INTENT_PATTERNS.items():
        must_have = rules["must_have"]
        question_words = rules["question_words"]

        if all(word in text for word in must_have) and any(
            qw in text for qw in question_words
        ):
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

    # ✅ Sempre permitir comandos
    await bot.process_commands(message)

    # 🚫 Não rodar detecção automática em comandos
    if message.content.startswith("!"):
        return

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
