import platform
import random
import os
import aiosqlite

import aiohttp
import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context

from helpers import checks

VISIBLE_COGS = ["general", "fun", "moderation", "music"]

class General(commands.Cog, name="general"):
    def __init__(self, bot):
        self.bot = bot
  
    @commands.hybrid_command(
        name="help", description="Список всех моих команд."
    )
    @checks.not_blacklisted()
    async def help(self, context: Context) -> None:
        if not context.guild:
          servercheck = "Префикс:"
          prefix = "q."
        else:
          servercheck = "Префикс для этого сервера:"
          guild = context.guild.id
          async with aiosqlite.connect(f"{os.path.realpath(os.path.dirname(__file__))}/../database/database.db") as db:
            async with db.cursor() as cursor:
              await cursor.execute('SELECT prefix_id FROM prefixes WHERE server_id=?', (guild,))
              data = await cursor.fetchone()
              prefix = ''.join(data)    
      
        embed = discord.Embed(
            title="Помощь", description="Информация обо мне:", color=0x9C84EF
        )
        embed.add_field(name="Владелец:", value="Qaveru#3999", inline=True)
        embed.add_field(
            name="Версия Python:", value=f"{platform.python_version()}", inline=True
        )
        embed.add_field(
            name=f"{servercheck}",
            value=f"`/` для системных команд\n `{prefix}` для контекстных команд",
            inline=False,
        )
        for i in self.bot.cogs:
            cog = self.bot.get_cog(i.lower())
            commands = cog.get_commands()  
            data = []           
            if cog is None or cog.qualified_name.lower() not in VISIBLE_COGS:
                continue
            for command in commands:
                description = command.description.partition("\n")[0]
                data.append(f"{command.name} - {description}")
            help_text = "\n".join(data)
            embed.add_field(
                name=f"Команды {i.capitalize()}", value=f"```{help_text}```", inline=False
            )
        await context.send(embed=embed)

    @commands.hybrid_command(
        name="serverinfo",
        description="Получить информацию о сервере.",
    )
    @checks.not_blacklisted()
    async def serverinfo(self, context: Context) -> None:
        roles = [role.name for role in context.guild.roles]
        if len(roles) > 50:
            roles = roles[:50]
            roles.append(f">>>> Всего[50/{len(roles)}] ролей")
        roles = ", ".join(roles)

        embed = discord.Embed(
            title=f"{context.guild}", color=0x9C84EF
        )
        if context.guild.icon is not None:
            embed.set_thumbnail(url=context.guild.icon.url)
        embed.add_field(name="Владелец", value=context.guild.owner)
        embed.add_field(name="Пользователей", value=context.guild.member_count)
        embed.add_field(name="ID Сервера", value=context.guild.id)
        embed.add_field(name="Всего \nканалов", value=f"{len(context.guild.channels)}")
        embed.add_field(name="Текстовых каналов", value=f"{len(context.guild.text_channels)}")
        embed.add_field(name="Голосовых каналов", value=f"{len(context.guild.voice_channels)}")
        embed.add_field(name=f"Список Ролей ({len(context.guild.roles)})", value=roles)
        embed.set_footer(text=f"Сервер Создан: {context.guild.created_at}")
        await context.send(embed=embed)

    @commands.hybrid_command(
        name="ping",
        description="Проверить мою задержку.",
    )
    @checks.not_blacklisted()
    async def ping(self, context: Context) -> None:
        embed = discord.Embed(
            title="🏓 Понг!",
            description=f"Моя задержка {round(self.bot.latency * 1000)}мс.",
            color=0x9C84EF,
        )
        await context.send(embed=embed)

    @commands.hybrid_command(
        name="invite",
        description="Пригласить меня к себе на сервер.",
    )
    @checks.not_blacklisted()
    async def invite(self, context: Context) -> None:
        embed = discord.Embed(
            description=f"Пригласите меня нажав [сюда](https://discordapp.com/oauth2/authorize?&client_id={self.bot.config['application_id']}&scope=bot+applications.commands&permissions={self.bot.config['permissions']}).",
            color=0xD75BF4,
        )
        await context.send(embed=embed)

    @commands.hybrid_command(
        name="support",
        description="Получить ссылку на мой сервер, чтобы обратиться за помощью.",
    )
    @checks.not_blacklisted()
    async def support(self, context: Context) -> None:
        embed = discord.Embed(
            description="Получите помощь на моём [сервере](https://discord.gg/a428KzFC9X).",
            color=0xD75BF4,
        )
        await context.send(embed=embed)

    @commands.hybrid_command(
        name="8ball",
        description="Спросить любой вопрос у меня.",
    )
    @checks.not_blacklisted()
    @app_commands.describe(question="Вопрос, который Вы хотите задать.")
    async def eight_ball(self, context: Context, *, question: str) -> None:
        answers = [
            "Это точно.",
            "Вы можете положиться на это.",
            "Без сомнения.",
            "Да, безусловно.",
            "Как я вижу, да.",
            "Вероятно.",
            "Перспектива хорошая.",
            "Да.",
            "Знаки указывают на да.",
            "Ответ туманный, попробуйте еще раз.",
            "Спросите позже.",
            "Сейчас лучше Вам не говорить.",
            "Не могу предсказать сейчас.",
            "Сконцентрируйтесь и спросите позже.",
            "Не рассчитывайте на это.",
            "Мой ответ нет.",
            "Мои источники говорят нет.",
            "Перспектива не очень.",
            "Очень сомнительно.",
        ]
        embed = discord.Embed(
            title="**Мой ответ:**",
            description=f"{random.choice(answers)}",
            color=0x9C84EF,
        )
        embed.set_footer(text=f"Вопрос был: {question}")
        await context.send(embed=embed)

    @commands.hybrid_command(
        name="bitcoin",
        description="Получить нынешную цену биткоина.",
    )
    @checks.not_blacklisted()
    async def bitcoin(self, context: Context) -> None:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://api.coindesk.com/v1/bpi/currentprice/BTC.json"
            ) as request:
                if request.status == 200:
                    data = await request.json(
                        content_type="application/javascript"
                    ) 
                    embed = discord.Embed(
                        title="Цена Биткоина",
                        description=f"Цена биткоина сейчас {data['bpi']['USD']['rate']} долларов",
                        color=0x9C84EF,
                    )
                else:
                    embed = discord.Embed(
                        title="Ошибка!",
                        description="Неполадки с API, пожалуйста попробуйте позже",
                        color=0xE02B2B,
                    )
                await context.send(embed=embed)

async def setup(bot):
    await bot.add_cog(General(bot))
