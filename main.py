import os
import time
import discord
from discord.ext import commands
from pathlib import Path

# =========================
# CONFIGURAÇÃO BÁSICA
# =========================

TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN not found in environment variables")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# =========================
# DIRETÓRIOS DE CONTEÚDO
# =========================

CONTENT_DIR = Path("content/pt")
EXPLANATIONS_DIR = Path("explanations")

# =========================
# MAPA DE INTENÇÕES
# =========================

INTENT_KEYWORDS = {
    "accentuation": [
        "accent", "acento", "acentuação", "ô", "ê", "á", "é", "í", "ó", "ú"
    ],
    "por_vs_para": [
        "por ou para",
        "por vs para",
        "difference between por and para",
        "diferença entre por e para"
    ],
    "ser_vs_estar": [
        "ser ou estar",
        "ser vs estar",
        "difference between ser and estar"
    ],
    "verb_tenses": [
        "tempo verbal",
        "verb tense",
        "past tense",
        "present tense",
        "future tense"
    ],
    "gender": [
        "grammatical gender",
        "masculine or feminine",
        "gênero"
    ],
    "false_cognates": [
        "false cognate",
        "false friend",
        "parece inglês"
    ]
}

# =========================
# CONTROLE DE SPAM
# =========================

LAST_INTENT_RESPONSE = {}
COOLDOWN_SECONDS = 60

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
# EVENTOS
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

    QUESTION_TRIGGERS = (
        "why", "what", "when", "how",
        "porque", "por que", "pq", "quando", "como", "qual"
    )

    is_question = (
        "?" in content
        or content.strip().startswith(QUESTION_TRIGGERS)
    )

    if not is_question:
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
# COMANDOS
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
async def topics(ctx):
    if not CONTENT_DIR.exists():
        await ctx.send("❌ Content directory not found.")
        return

    topics = [f.stem for f in CONTENT_DIR.glob("*.txt")]

    if not topics:
        await ctx.send("⚠️ No topics available yet.")
        return

    topic_list = "\n".join(f"- {t}" for t in topics)
    await ctx.send(f"📘 **Portuguese study topics:**\n{topic_list}")

@bot.command()
async def study(ctx, topic: str):
    file_path = CONTENT_DIR / f"{topic}.txt"

    if not file_path.exists():
        await ctx.send("❌ Topic not found.")
        return

    raw_lines = file_path.read_text(encoding="utf-8").splitlines()
    message = f"📖 **{topic.replace('_', ' ').title()} (Portuguese)**\n\n"

    for line in raw_lines:
        if "—" in line:
            pt, en = line.split("—", 1)
            message += f"🇧🇷 **{pt.strip()}**\n🇺🇸 {en.strip()}\n\n"
        elif line.startswith("Pronunciation"):
            message += f"🔊 {line.replace('Pronunciation:', '').strip()}\n\n"
        else:
            message += f"{line}\n"

    await ctx.send(message[:1900])

@bot.command()
async def explain(ctx, topic: str):
    file_path = EXPLANATIONS_DIR / f"{topic}.txt"

    if not file_path.exists():
        await ctx.send(
            "❌ Explanation not found.\n"
            "Try: `!explain accentuation`, `!explain ser_vs_estar`, etc."
        )
        return

    raw_lines = file_path.read_text(encoding="utf-8").splitlines()
    message = f"🧠 **Explanation: {topic.replace('_', ' ').title()}**\n\n"

    for line in raw_lines:
        if not line.strip():
            message += "\n"
        elif line.isupper():
            message += f"📌 **{line}**\n"
        elif line.startswith("EXAMPLE"):
            message += "\n💡 **Example**\n"
        else:
            message += f"{line}\n"

    await ctx.send(message[:1900])

# =========================
# INICIAR BOT
# =========================

bot.run(TOKEN)
