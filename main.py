import discord
import asyncio
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, BotCommand
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

# Загрузка переменных из .env
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))  # Приведение к int

telegram_bot = Bot(
    token=TELEGRAM_BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

intents = discord.Intents.default()
intents.voice_states = True
intents.guilds = True
intents.members = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'✅ Discord-бот запущен как {client.user}')

async def get_voice_channel_info():
    guild = client.get_guild(GUILD_ID)
    if not guild:
        return "❌ Ошибка: Сервер не найден. Проверьте GUILD_ID."

    report = []
    for channel in guild.voice_channels:
        members_info = []
        for member in channel.members:
            voice_state = member.voice
            if not voice_state:
                members_info.append(member.display_name)
                continue

            is_muted = voice_state.self_mute or voice_state.mute
            status_tags = []
            if is_muted:
                status_tags.append("MUTE")
            if status_tags:
                status_text = " ".join(f"[{tag}]" for tag in status_tags)
                member_info = f"{member.display_name} {status_text}"
            else:
                member_info = member.display_name
            members_info.append(member_info)

        if members_info:
            report.append(
                f"🔊 <b>{channel.name}</b> ({len(members_info)} чел.): " +
                ", ".join(members_info)
            )

    return "\n".join(report) if report else "🔇 В голосовых каналах никого нет."

@dp.message(lambda message: message.text and message.text.startswith('/status'))
async def send_status(message: Message):
    info = await get_voice_channel_info()
    await message.answer(info)

@dp.message(lambda message: message.text and message.text.startswith('/help'))
async def send_help(message: Message):
    commands_text = (
        "📜 <b>Список команд:</b>\n\n"
        "/status - Показать, кто в голосовых каналах Discord\n"
        "/help - Показать список команд\n"
    )
    await message.answer(commands_text, parse_mode=ParseMode.HTML)

async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="status", description="Показать, кто в голосовых каналах"),
        BotCommand(command="help", description="Показать список команд"),
    ]
    await bot.set_my_commands(commands)

async def start_telegram_bot():
    print("✅ Запуск Telegram-бота...")
    await set_commands(telegram_bot)
    await dp.start_polling(telegram_bot)

async def main():
    asyncio.create_task(client.start(DISCORD_BOT_TOKEN))
    await start_telegram_bot()

if __name__ == "__main__":
    asyncio.run(main())
