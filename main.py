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
EXPLANATIONS_DIR = Path("explanations")

INTENT_KEYWORDS = {
    "accentuation": [
        "accent", "acento", "acentuação", "ô", "ê", "á", "é", "í", "ó", "ú"
    ],
    "por_vs_para": [
        "por ou para", "por vs para", "por", "para"
    ],
    "ser_vs_estar": [
        "ser ou estar", "ser vs estar", "ser", "estar"
    ],
    "verb_tenses": [
        "tempo verbal", "tense", "past", "present", "future"
    ],
    "gender": [
        "masculine", "feminine", "gender", "gênero"
    ],
    "false_cognates": [
        "false cognate", "false friend", "parece inglês"
    ]
}

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

@bot.command()
async def explain(ctx, topic: str):
    file_path = EXPLANATIONS_DIR / f"{topic}.txt"

    if not file_path.exists():
        await ctx.send(
            "❌ Explanation not found.\n"
            "Use `!explain accentuation`, `!explain ser_vs_estar`, etc."
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
            message += f"\n💡 **Example**\n"
        else:
            message += f"{line}\n"

    await ctx.send(message[:1900])

if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN not found in environment variables")
    
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    await bot.process_commands(message)

    content = message.content.lower()

    for intent, keywords in INTENT_KEYWORDS.items():
        for kw in keywords:
            if kw in content:
                await message.channel.send(
                    f"🤔 This looks like a question about **{intent.replace('_', ' ')}**.\n"
                    f"Try: `!explain {intent}`"
                )
                return

bot.run(TOKEN)
