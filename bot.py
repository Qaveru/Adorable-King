import asyncio
import json
import logging
import os
import platform
import random
import sys

import aiosqlite
import discord
from discord.ext import commands, tasks
from discord.ext.commands import Bot, Context
from keep_alive import keep_alive
from dotenv import load_dotenv
import datetime

import exceptions

load_dotenv()

if not os.path.isfile(f"{os.path.realpath(os.path.dirname(__file__))}/config.json"):
    sys.exit("'config.json' not found! Please add it and try again.")
else:
    with open(f"{os.path.realpath(os.path.dirname(__file__))}/config.json") as file:
        config = json.load(file)

intents = discord.Intents.all()
intents.messages = True
intents.message_content = True 

async def get_prefix(bot, message):
 if not message.guild:
   return "q."
 else:  
  async with aiosqlite.connect(f"{os.path.realpath(os.path.dirname(__file__))}/database/database.db") as db:
    async with db.cursor() as cursor:
      await cursor.execute("SELECT prefix_id FROM prefixes WHERE server_id=?", (message.guild.id,))
      data = await cursor.fetchone()
      if data:
        return data
      else:
        try:
          await cursor.execute("INSERT INTO prefixes (prefix_id, server_id) VALUES (?, ?)", ("q.", message.guild.id))
          await cursor.execute("SELECT prefix_id FROM prefixes WHERE server_id=?", (message.guild.id))
          data = await cursor.fetchone()
          if data:
            await cursor.execute("UPDATE prefixes SET prefix_id=? WHERE server_id=?", ("q.", message.guild.id))
        except :
          return "q."

bot = Bot(
    command_prefix=get_prefix,
    intents=intents,
    help_command=None,
)


class LoggingFormatter(logging.Formatter):
    # Colors
    black = "\x1b[30m"
    red = "\x1b[31m"
    green = "\x1b[32m"
    yellow = "\x1b[33m"
    blue = "\x1b[34m"
    gray = "\x1b[38m"
    # Styles
    reset = "\x1b[0m"
    bold = "\x1b[1m"

    COLORS = {
        logging.DEBUG: gray + bold,
        logging.INFO: blue + bold,
        logging.WARNING: yellow + bold,
        logging.ERROR: red,
        logging.CRITICAL: red + bold,
    }

    def format(self, record):
        log_color = self.COLORS[record.levelno]
        format = "(black){asctime}(reset) (levelcolor){levelname:<8}(reset) (green){name}(reset) {message}"
        format = format.replace("(black)", self.black + self.bold)
        format = format.replace("(reset)", self.reset)
        format = format.replace("(levelcolor)", log_color)
        format = format.replace("(green)", self.green + self.bold)
        formatter = logging.Formatter(format, "%Y-%m-%d %H:%M:%S", style="{")
        return formatter.format(record)


logger = logging.getLogger("discord_bot")
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setFormatter(LoggingFormatter())
file_handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
file_handler_formatter = logging.Formatter(
    "[{asctime}] [{levelname:<8}] {name}: {message}", "%Y-%m-%d %H:%M:%S", style="{"
)
file_handler.setFormatter(file_handler_formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)
bot.logger = logger


async def init_db():
    async with aiosqlite.connect(
        f"{os.path.realpath(os.path.dirname(__file__))}/database/database.db"
    ) as db:
        with open(
            f"{os.path.realpath(os.path.dirname(__file__))}/database/schema.sql"
        ) as file:
            await db.executescript(file.read())
        await db.commit()


bot.config = config


@bot.event
async def on_ready() -> None:
    bot.logger.info(f"Logged in as {bot.user.name}")
    bot.logger.info(f"discord.py API version: {discord.__version__}")
    bot.logger.info(f"Python version: {platform.python_version()}")
    bot.logger.info(f"Running on: {platform.system()} {platform.release()} ({os.name})")
    bot.logger.info("-------------------")
    status_task.start()
    if config["sync_commands_globally"]:
        bot.logger.info("Syncing commands globally...")
        await bot.tree.sync()

@bot.event
async def on_message(message: discord.Message) -> None:
    if message.author == bot.user or message.author.bot:
        return
    await bot.process_commands(message)


@bot.event
async def on_guild_join(guild):
  async with aiosqlite.connect(f"{os.path.realpath(os.path.dirname(__file__))}/database/database.db") as db:
    async with db.cursor() as cursor:
      await cursor.execute("INSERT INTO prefixes (prefix_id, server_id) VALUES (?, ?)", ('q.', guild.id,))
    await db.commit()


@bot.event
async def on_guild_remove(guild):
  async with aiosqlite.connect(f"{os.path.realpath(os.path.dirname(__file__))}/database/database.db") as db:
    async with db.cursor() as cursor:
      await cursor.execute("SELECT prefix_id FROM prefixes WHERE server_id=?", (guild.id,))
      data = await cursor.fetchone()
      if data:
        await cursor.execute("DELETE FROM prefixes WHERE server_id=?", (guild.id,))
        await cursor.execute("DELETE FROM logs WHERE server_id=?", (guild.id,))
    await db.commit()

@bot.event
async def on_message_edit(before, after):
 if before.author == bot.user or before.author.bot:
        return 
 if not before.guild.id:
   return
 else:  
  async with aiosqlite.connect(f"{os.path.realpath(os.path.dirname(__file__))}/database/database.db") as db:
    async with db.cursor() as cursor:
      await cursor.execute("SELECT channel_id FROM logs WHERE server_id=?", (before.guild.id,))
      data = await cursor.fetchone()
      if data:
        data = int(''.join(map(str, data)))
        logchannel = await bot.fetch_channel(data)
        embed = discord.Embed(description=f"**Сообщение отредактировано в канале** <#{before.channel.id}> \n\n[Нажмите чтобы перейти к сообщению]({before.jump_url})", timestamp=datetime.datetime.now(), color=0x9C84EF)
        embed.add_field(name="**Старое сообщение**", value=f"{before.content}", inline=False)
        embed.add_field(name="**Новое сообщение**", value=f"{after.content}", inline=False)
        embed.set_author(name=before.author, icon_url=before.author.avatar)
        embed.set_footer(text=f"ID Пользователя: {before.author.id}")
        await logchannel.send(embed=embed)
      else:
        return

@bot.event
async def on_message_delete(messages):
 if messages.author == bot.user or messages.author.bot:
        return 
 if not messages.guild.id:
   return
 else:  
  async with aiosqlite.connect(f"{os.path.realpath(os.path.dirname(__file__))}/database/database.db") as db:
    async with db.cursor() as cursor:
      await cursor.execute("SELECT channel_id FROM logs WHERE server_id=?", (messages.guild.id,))
      data = await cursor.fetchone()
      if data:
        data = int(''.join(map(str, data)))
        logchannel = await bot.fetch_channel(data)
        embed = discord.Embed(description=f"**Удалено сообщение, отравленное** {messages.author.mention} **в канале** <#{messages.channel.id}>", timestamp=datetime.datetime.now(), color=0xff5454)
        embed.add_field(name="**Удалённое сообщение**", value=f"{messages.content}", inline=False)
        embed.set_author(name=messages.author, icon_url=messages.author.avatar)
        embed.set_footer(text=f"ID Пользователя: {messages.author.id} | ID Сообщения: {messages.id}")
        await logchannel.send(embed=embed)
      else:
        return

        
@tasks.loop(minutes=1.0)
async def status_task() -> None:
    statuses = ["классные игры!", "/help", "своё удовольствие!"]
    await bot.change_presence(activity=discord.Game(random.choice(statuses)))

@bot.event
async def on_command_completion(context: Context) -> None:
    log = bot.get_channel(1082292716433571840) 
    full_command_name = context.command.qualified_name
    split = full_command_name.split(" ")
    executed_command = str(split[0])
    if context.guild is not None:
        bot.logger.info(
            f"Executed '{executed_command}' command in {context.guild.name} (ID: {context.guild.id}) by {context.author} (ID: {context.author.id})"
        )
    else:
        bot.logger.info(
            f"Executed '{executed_command}' command by {context.author} (ID: {context.author.id}) in DMs"
        )
    if context.guild is not None:
        embed = discord.Embed(description = f"Executed `{executed_command}` command", timestamp=datetime.datetime.now()) 
        embed.add_field(name=f"User: {context.author}", value=f"ID: {context.author.id}")
        embed.add_field(name=f"Guild {context.guild.name}", value=f"ID: {context.guild.id}") 
        await log.send(embed=embed)
    else:
        embed = discord.Embed(description = f"Executed `{executed_command}` command in DMs", timestamp=datetime.datetime.now())
        embed.add_field(name=f"User: {context.author}", value=f"ID: {context.author.id}")
        await log.send(embed=embed)

@bot.event
async def on_command_error(context: Context, error) -> None:
    log = bot.get_channel(1082292716433571840) 
    if isinstance(error, commands.CommandOnCooldown):
        minutes, seconds = divmod(error.retry_after, 60)
        hours, minutes = divmod(minutes, 60)
        hours = hours % 24
        embed = discord.Embed(
            description=f"**Пожалуйста помедленее..** - Вы сможете использовать эту команду через {f'{round(hours)} часов' if round(hours) > 0 else ''} {f'{round(minutes)} минут' if round(minutes) > 0 else ''} {f'{round(seconds)} секунд' if round(seconds) > 0 else ''}.",
            color=0xE02B2B,
        )
        await context.send(embed=embed)
    elif isinstance(error, exceptions.UserBlacklisted):
        embed = discord.Embed(
            description="Извините, но Вы находитесь в чёрном списке и не можете использовать команды!", color=0xE02B2B
        )
        await context.send(embed=embed)
        if context.guild:
            bot.logger.warning(
                f"{context.author} (ID: {context.author.id}) tried to execute a command in the guild {context.guild.name} (ID: {context.guild.id}), but the user is blacklisted from using the bot."
            )
            embed = discord.Embed(title="WARNING", description = "User tried to execute a command in the guild, but the user is blacklised from using the bot.", color=0xff0000, timestamp=datetime.datetime.now())
            embed.add_field(name=f"User: {context.author} ", value=f"ID: {context.author.id}")
            embed.add_field(name=f"Guild: {context.guild.name}", value=f"ID: {context.guild.id}")
            await log.send(embed=embed)
        else:
            bot.logger.warning(
                f"{context.author} (ID: {context.author.id}) tried to execute a command in the bot's DMs, but the user is blacklisted from using the bot."
            )
            embed = discord.Embed(title="WARNING", description="User tried to execute a command in the bot's DMs, but the user is blacklisted from using the bot.", color=0xff0000, timestamp=datetime.datetime.now())
            embed.add_field(name=f"User: {context.author}", value=f"ID: {context.author.id}")
            await log.send(embed=embed)
    elif isinstance(error, exceptions.UserNotOwner):
        embed = discord.Embed(
            description="Ошибка! Эта команда предназначена для владельца!", color=0xE02B2B
        )
        await context.send(embed=embed)
        if context.guild:
            bot.logger.warning(
                f"{context.author} (ID: {context.author.id}) tried to execute an owner only command in the guild {context.guild.name} (ID: {context.guild.id}), but the user is not an owner of the bot."
            )
            embed = discord.Embed(title="WARNING", description= "User tried to execute an owner only command in the guild, but the user is not an owner of the bot.", color=0xffe700, timestamp=datetime.datetime.now())
            embed.add_field(name=f"User: {context.author}", value=f"ID: {context.author.id}")
            embed.add_field(name=f"Guild: {context.guild.name}", value=f"ID: {context.guild.id}")
            await log.send(embed=embed)
        else:
            bot.logger.warning(
                f"{context.author} (ID: {context.author.id}) tried to execute an owner only command in the bot's DMs, but the user is not an owner of the bot."
            )
            embed = discord.Embed(title="WARNING", description="User tried to execute an owner only command in the bot's DMs, but the user is not an owner of the bot.", color=0xffe700, timestamp=datetime.datetime.now())
            embed.add_field(name=f"User: {context.author}", value=f"ID: {context.author.id}")
            await log.send(embed=embed)
    elif isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            description="Извините, но Вы не можете использовать эту команду, у Вас недостаточно прав. Необходимые права: `"
            + ", ".join(error.missing_permissions)
            + "`",
            color=0xE02B2B,
        )
        await context.send(embed=embed)
    elif isinstance(error, commands.BotMissingPermissions):
        embed = discord.Embed(
            description="У меня недостаточно прав чтобы использовать эту команду! Необходимые права: `"
            + ", ".join(error.missing_permissions) + "`",
            color=0xE02B2B,
        )
        await context.send(embed=embed)
    elif isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
            title="Ошибка!",
            description=str(error).capitalize(),
            color=0xE02B2B,
        )
        await context.send(embed=embed)
    else:
        raise error

async def load_cogs() -> None:
    for file in os.listdir(f"{os.path.realpath(os.path.dirname(__file__))}/cogs"):
        if file.endswith(".py"):
            extension = file[:-3]
            try:
                await bot.load_extension(f"cogs.{extension}")
                bot.logger.info(f"Loaded extension '{extension}'")
            except Exception as e:
                exception = f"{type(e).__name__}: {e}"
                bot.logger.error(f"Failed to load extension {extension}\n{exception}")
              
keep_alive()              
asyncio.run(init_db())
asyncio.run(load_cogs())
bot.run(os.getenv("token"))
