import os
import time
import discord
from discord.ext import commands
from pathlib import Path
from openai import OpenAI

client = OpenAI()

# =========================
# TOKENS
# =========================

TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN not found")

# =========================
# BOT SETUP
# =========================

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# =========================
# ESTADO GLOBAL
# =========================

LAST_INTENT_RESPONSE = {}
LAST_AI_CALL = {}

INTENT_COOLDOWN = 60
AI_COOLDOWN = 60

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
        if all(w in text for w in rules["must_have"]) and any(
            q in text for q in rules["question_words"]
        ):
            return intent
    return None

# =========================
# IA
# =========================

client = OpenAI(api_key=OPENAI_KEY)

def ask_ai(question: str):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a Portuguese teacher for English speakers. "
                    "Explain grammar and usage clearly, with short examples."
                )
            },
            {"role": "user", "content": question}
        ],
        temperature=0.4,
        max_tokens=300
    )
    return response.choices[0].message.content

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

    # ✅ sempre processar comandos
    await bot.process_commands(message)

    # ❌ não rodar IA/detecção em comandos
    if message.content.startswith("!"):
        return

    content = message.content.lower()

    if "?" not in content:
        return

    now = time.time()

    # =========================
    # INTENT DETECTION
    # =========================

    last_intent = LAST_INTENT_RESPONSE.get(message.author.id, 0)
    if now - last_intent >= INTENT_COOLDOWN:
        intent = detect_intent(content)
        if intent:
            LAST_INTENT_RESPONSE[message.author.id] = now
            await message.channel.send(
                f"🤔 This looks like a question about **{intent.replace('_', ' ')}**.\n"
                f"Try: `!explain {intent}`"
            )
            return

    # =========================
    # IA FALLBACK
    # =========================

    if not OPENAI_KEY:
        return

    last_ai = LAST_AI_CALL.get(message.author.id, 0)
    if now - last_ai < AI_COOLDOWN:
        return

    LAST_AI_CALL[message.author.id] = now

    try:
        answer = ask_ai(message.content)
        await message.channel.send(f"🤖 {answer}")
    except Exception:
        await message.channel.send("⚠️ I can't answer right now. Try again later.")

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

    if OPENAI_KEY:
        try:
            answer = ask_ai(question)
            await ctx.send(f"🤖 {answer}")
        except Exception:
            await ctx.send("⚠️ I can't answer right now.")
    else:
        await ctx.send("🤖 I don't have an explanation for this yet.")

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
