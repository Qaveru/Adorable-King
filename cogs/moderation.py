import discord
import asyncio
from discord import app_commands
from discord.ext import commands, tasks
from discord.ext.commands import Context
import datetime
from datetime import date
import os
import aiosqlite


from helpers import checks, db_manager


time = datetime.datetime.now()
today = date.today()

remtime = today.strftime("%d/%m/%Y")    


class Moderation(commands.Cog, name="moderation"):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
      name="setprefix",
      description="Установить собственный префикс для команд на сервере.",
    )
    @commands.check_any(commands.is_owner(), commands.has_permissions(kick_members=True))
    @checks.not_blacklisted()  
    @app_commands.describe(prefix="Введите желаемый префикс.")
    async def setprefix(self, context: Context, prefix) -> None:
      if prefix is None:
        return
      async with aiosqlite.connect(f"{os.path.realpath(os.path.dirname(__file__))}/../database/database.db") as db:
        async with db.cursor() as cursor:
          await cursor.execute("SELECT prefix_id FROM prefixes WHERE server_id=?", (context.guild.id,))
          data = await cursor.fetchone()
          if data:
            await cursor.execute("UPDATE prefixes SET prefix_id=? WHERE server_id=?", (prefix, context.guild.id,))
            embed = discord.Embed(description=f"Новый префикс установлен: `{prefix}`", color=0x9C84EF)
            await context.send(embed=embed)
          else:
            await cursor.execute("INSERT INTO prefixes (prefix_id, server_id) VALUES (?, ?)", ("q.", context.guild.id,))
            await cursor.execute("SELECT prefix_id FROM prefixes WHERE server_id=?", (context.guild.id,))
            data = await cursor.fetchone()
            if data:
              await cursor.execute("UPDATE prefixes SET prefix_id=? WHERE server_id=?", (prefix, context.guild.id,))
              embed = discord.Embed(description=f"Новый префикс установлен: `{prefix}`", color=0x9C84EF)
              await context.send(embed=embed)
            else:
              return
        await db.commit()   
  
    @commands.hybrid_command(
        name="kick",
        description="Выгнать пользователя с сервера.",
    )
    @commands.check_any(commands.is_owner(), commands.has_permissions(kick_members=True))
    @commands.bot_has_permissions(kick_members=True)
    @checks.not_blacklisted()
    @app_commands.describe(
        user="Выберите пользователя из списка или введите его ID.",
        reason="Почему пользователь должен быть выгнан?",
    )
    async def kick(
        self, context: Context, user: discord.User, *, reason: str = "Не указано"
    ) -> None:
        member = context.guild.get_member(user.id) or await context.guild.fetch_member(
            user.id
        )
        if member.guild_permissions.administrator:
            embed = discord.Embed(
                description="Пользователь имеет права администратора.", color=0xE02B2B
            )
            await context.send(embed=embed)
        else:
            try:
                embed = discord.Embed(
                    description=f"*`{member}`* **был выгнан администратором** *`{context.author}`* **по причине:** *`{reason}`*",
                    color=0x9C84EF,
                )
                await context.send(embed=embed)
                try:
                    await member.send(
                      embed = discord.Embed(
                        description=f"**Вы были выгнаны администратором** *`{context.author}`* **с сервера** *`{context.guild.name}`* **по причине:** *`{reason}`*", color=0x9C84EF
                      ))
                except:
                    pass
                await member.kick(reason=reason)
            except:
                embed = discord.Embed(
                    description="Произошла ошибка при попытке выгнать пользователя. Убедитесь что моя роль находится выше пользователя, которого вы хотите выгнать.",
                    color=0xE02B2B,
                )
                await context.send(embed=embed)

    @commands.hybrid_command(
        name="nick",
        description="Сменить никнейм пользователя на сервере.",
    )
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_nicknames=True))
    @commands.bot_has_permissions(manage_nicknames=True)
    @checks.not_blacklisted()
    @app_commands.describe(
        user="Выберите пользователя из списка или введите его ID.",
        nickname="Никнейм, который должен быть установлен.",
    )
    async def nick(
        self, context: Context, user: discord.User, *, nickname: str = None
    ) -> None:
        member = context.guild.get_member(user.id) or await context.guild.fetch_member(
            user.id
        )
        try:
            await member.edit(nick=nickname)
            embed = discord.Embed(
                description=f"Новый никнейм пользователя **{member}** теперь **{nickname}**!",
                color=0x9C84EF,
            )
            await context.send(embed=embed)
        except:
            embed = discord.Embed(
                description="Произошла ошибка при попытке установить никнейм пользователю. Убедитесь что моя роль находится выше пользователя, которому вы пытаетесь установить никнейм.",
                color=0xE02B2B,
            )
            await context.send(embed=embed)

    @commands.hybrid_command(
        name="ban",
        description="Заблокировать пользователя с этого сервера.",
    )
    @commands.check_any(commands.is_owner(), commands.has_permissions(ban_members=True))
    @commands.bot_has_permissions(ban_members=True)
    @checks.not_blacklisted()
    @app_commands.describe(
        user="Выберите пользователя из списка или введите его ID.",
        reason="Почему пользователь должен быть заблокирован?",
    )
    async def ban(
        self, context: Context, user: discord.User, *, reason: str = "Не указано"
    ) -> None:
        member = context.guild.get_member(user.id) or await context.guild.fetch_member(
            user.id
        )
        try:
            if member.guild_permissions.administrator:
                embed = discord.Embed(
                    description="Пользователь имеет права администратора.", color=0xE02B2B
                )
                await context.send(embed=embed)
            else:
                embed = discord.Embed(
                    description=f"*`{user}`* **был заблокирован администратором** *`{context.author}`* **по причине:** *`{reason}`*",
                    color=0x9C84EF,
                )
                await context.send(embed=embed)
                try:
                    await member.send(
                      embed = discord.Embed(
                        description=f"**Вы были заблокированы администратором** *`{context.author}`* **на сервере** *`{context.guild.name}`* **по причине**: *`{reason}`*", 
                       color=0x9C84EF
                      ))
                except:
                    # Couldn't send a message in the private messages of the user
                    pass
                await member.ban(reason=reason)
        except:
            embed = discord.Embed(
                title="Ошибка!",
                description="Произошла ошибка при попытке заблокировать пользователя. Убедитесь что моя роль находится выше пользователя, которого вы пытаетесь заблокировать.",
                color=0xE02B2B,
            )
            await context.send(embed=embed)    

    @commands.hybrid_group(
        name="warning",
        description="Управляние предупреждениями на сервере.",
    )
    @commands.has_permissions(manage_messages=True)
    @checks.not_blacklisted()
    async def warning(self, context: Context) -> None:
        if context.invoked_subcommand is None:
            embed = discord.Embed(
                description="Пожалуйста, укажите подкоманду.\n\n**Подкоманды:**\n`add` - Выдать предупреждение пользователю.\n`remove` - Снять предупреждение с пользователя.\n`list` - Список всех предупреждений пользователя.",
                color=0xE02B2B,
            )
            await context.send(embed=embed)

    @warning.command(
        name="add",
        description="Выдает предупреждение пользователю.",
    )
    @checks.not_blacklisted()
    @commands.has_permissions(manage_messages=True)
    @app_commands.describe(
        user="Выберите пользователя из списка или введите его ID.",
        reason="Почему пользователь должен получить предупреждение?",
    )
    async def warning_add(
        self, context: Context, user: discord.User, *, reason: str = "Не указано"
    ) -> None:
        member = context.guild.get_member(user.id) or await context.guild.fetch_member(
            user.id
        )
        total = await db_manager.add_warn(
            user.id, context.guild.id, context.author.id, reason
        )
        embed = discord.Embed(
            description=f"*`{member}`* **получил предупреждение от администратора** *`{context.author}`* **по причине:** *`{reason}`*",
            color=0x9C84EF,
        )
        embed.add_field(name="Всего предупреждений у пользователя:", value=total)
        await context.send(embed=embed)
        try:
            await member.send(
              embed = discord.Embed(
                description=f"**Вы получили предупреждение от администратора** *`{context.author}`* **на сервере** *`{context.guild.name}`* **по причине:** *`{reason}`*", 
               color=0x9C84EF
              ))
        except:
            # Couldn't send a message in the private messages of the user
            await context.send(
                f"{member.mention}**, Вы получили предупреждение от администратора** *`{context.author}`* **по причине:** *`{reason}`*"
            )

    @warning.command(
        name="remove",
        description="Снять предупреждение с пользователя.",
    )
    @checks.not_blacklisted()
    @commands.has_permissions(manage_messages=True)
    @app_commands.describe(
        user="Выберите пользователя из списка или введите его ID.",
        warn_id="ID предупреждения.",
    )
    async def warning_remove(
        self, context: Context, user: discord.User, warn_id: int
    ) -> None:
        member = context.guild.get_member(user.id) or await context.guild.fetch_member(
            user.id
        )
        total = await db_manager.remove_warn(warn_id, user.id, context.guild.id)
        embed = discord.Embed(
            description=f"**Было снято предупрждение номер** *`#{warn_id}`* **с пользователя** *`{member}`*",
            color=0x9C84EF,
        )
        embed.add_field(name="Всего предупреждений у пользователя:", value=total)
        await context.send(embed=embed)

    @warning.command(
        name="list",
        description="Показать все предупреждения пользователя на сервере.",
    )
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_messages=True))
    @checks.not_blacklisted()
    @app_commands.describe(user="Выберите пользователя из списка или введите его ID.")
    async def warning_list(self, context: Context, user: discord.User):
        warnings_list = await db_manager.get_warnings(user.id, context.guild.id)
        embed = discord.Embed(title=f"Предупреждения пользователя {user}", color=0x9C84EF)
        description = ""
        if len(warnings_list) == 0:
            description = "У этого пользователя нету предупреждений."
        else:
            for warning in warnings_list:
                description += f"• Предупреждение от <@{warning[2]}> Причина: `{warning[3]}` (<t:{warning[4]}>) ID Предупреждения `#{warning[5]}`\n\n"
        embed.description = description
        await context.send(embed=embed)

    @commands.hybrid_command(
        name="purge",
        description="Удалить нужное кол-во сообщений.",
    )
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_messages=True))
    @commands.bot_has_permissions(manage_messages=True)
    @checks.not_blacklisted()
    @app_commands.describe(amount="Введите кол-во сообщений для удаления.")
    async def purge(self, context: Context, amount: int) -> None:
        await context.send(
            "Удаляю сообщения...", delete_after=0.1, ephemeral=True
        )  # Bit of a hacky way to make sure the bot responds to the interaction and doens't get a "Unknown Interaction" response
        purged_messages = await context.channel.purge(limit=amount + 1)
        embed = discord.Embed(
            description=f"**Удалено** `{len(purged_messages)-1}` **соообщений**",
            color=0x9C84EF,
        )
        await context.send(embed=embed, ephemeral=True, delete_after=2)

    @commands.hybrid_command(
        name="hackban",
        description="Блокирует пользователя, даже если он не присутствует на сервере.",
    )
    @commands.check_any(commands.is_owner(), commands.has_permissions(ban_members=True))
    @commands.bot_has_permissions(ban_members=True)
    @checks.not_blacklisted()
    @app_commands.describe(
        user_id="Выберите пользователя из списка или введите его ID.",
        reason="Почему пользователь должен быть заблокирован?.",
    )
    async def hackban(
        self, context: Context, user_id: str, *, reason: str = "Не указано"
    ) -> None:
        try:
            await self.bot.http.ban(user_id, context.guild.id, reason=reason)
            user = self.bot.get_user(int(user_id)) or await self.bot.fetch_user(
                int(user_id)
            )
            embed = discord.Embed(
                description=f"*`{user} (ID: {user_id})`* **был заблокирован администратором** *`{context.author}`* **по причине:** *`{reason}`*",
                color=0x9C84EF,
            )
            await context.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                description="Произошла ошибка при попытке заблокировать пользователя. Убедитесь что ID пользователя, который вы предоставили, принадлежит существующему пользователю.",
                color=0xE02B2B,
            )
            await context.send(embed=embed)

    @commands.hybrid_command(
        name="unban",
        description="Снимает блокировку с пользователя.",
    )
    @commands.check_any(commands.is_owner(), commands.has_permissions(ban_members=True))
    @commands.bot_has_permissions(ban_members=True)
    @checks.not_blacklisted()
    @app_commands.describe(
        user_id="Введите ID пользователя.",
        reason="Почему пользователь должен быть разблокирован?",
    )
    async def unban(
        self, context: Context, user_id: str, *, reason: str = "Не указано"
    ) -> None:
        try:
            await self.bot.http.unban(user_id, context.guild.id, reason=reason)
            user = self.bot.get_user(int(user_id)) or await self.bot.fetch_user(
                int(user_id)
            )
            embed = discord.Embed(
                description=f"*`{user} (ID: {user_id})`* **был разблокирован администратором** *`{context.author}`* **по причине:** *`{reason}`*",
                color=0x9C84EF,
            )
            await context.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                description="Произошла ошибка при попытке разблокировать пользователя. Убедитесь что ID пользователя, который вы предоставили, принадлежит существующему пользователю.",
                color=0xE02B2B,
            )
            await context.send(embed=embed)

    @commands.hybrid_command(
        name="say",
        description="Отправить сообщение от моего имени.",
    )
    @checks.not_blacklisted()
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_messages=True))
    @app_commands.describe(message="Введите сообщение, которое я должен повторить.")
    async def say(self, context: Context, *, message: str) -> None:
         await context.send("ok", delete_after=0.1, ephemeral=True)   
         await context.channel.send(message)
         try:  
          await context.message.delete()
         except:
           pass

    @commands.hybrid_command(
        name="embed",
        description="Отправить сообщение от моего имени в стиле embed.",
    )
    @checks.not_blacklisted()
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_messages=True))
    @app_commands.describe(message="Введите сообщение, которое я должен повторить.")
    async def embed(self, context: Context, *, message: str) -> None:
        embed = discord.Embed(description=message, color=0x9C84EF)
        await context.send("ok", delete_after=0.1, ephemeral=True) 
        await context.channel.send(embed=embed)
        try:
          await context.message.delete()
        except:
            pass

    @commands.hybrid_command(
        name="lock",
        description="Запретить пользователям отправлять сообщения в канале.",
    )
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_channels=True))
    @commands.bot_has_permissions(manage_channels=True)
    @checks.not_blacklisted()
    async def lock(self, context: Context, *, channel: discord.TextChannel) -> None:
        channel = channel or context.channel
        overwrite = channel.overwrites_for(context.guild.default_role)
        overwrite.send_messages = False
        await channel.set_permissions(context.guild.default_role, overwrite=overwrite)
        embed = discord.Embed(description="***Канал закрыт***", color=0x9C84EF)
        await context.send(embed=embed)

    @commands.hybrid_command(
        name="unlock",
        description="Разрешить пользователям отправлять сообщения в канале.",
    )
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_channels=True))
    @commands.bot_has_permissions(manage_channels=True)
    @checks.not_blacklisted()
    async def unlock(self, context: Context, *, channel: discord.TextChannel) -> None:
        channel = channel or context.channel
        overwrite = channel.overwrites_for(context.guild.default_role)
        overwrite.send_messages = True
        await channel.set_permissions(context.guild.default_role, overwrite=overwrite)
        embed = discord.Embed(description="***Канал открыт***", color=0x9C84EF)
        await context.send(embed=embed) 

    @commands.hybrid_command(
        name="dm",
        description="Написать пользователю в личные сообщения от моего имени",
    )
    @checks.not_blacklisted()
    @commands.check_any(commands.is_owner(), commands.has_permissions(ban_members=True))
    @commands.bot_has_permissions(ban_members=True)
    @app_commands.describe(
        user="Выберите пользователя из списка или введите его ID.",
        message="Введите сообщение для отправки",
    )
    async def dm(self, context: Context, user: discord.User, *, message)-> None:
        member = context.guild.get_member(user.id) or await context.guild.fetch_member(
            user.id
        )
        try:
            await context.send("Выполено", ephemeral=True)
            await member.send(message)
        except:
            await context.send("ЛС закрыто", ephemeral=True) 

    @commands.hybrid_command(
        name="dmembed",
        description="Написать пользователю в личные сообщения от моего имени в стиле embed.",
    )
    @commands.check_any(commands.is_owner(), commands.has_permissions(ban_members=True))
    @commands.bot_has_permissions(ban_members=True)
    @checks.not_blacklisted()
    @app_commands.describe(
        user="Выберите пользователя из списка или введите его ID.",
        message="Введите сообщение для отправки",
    )
    async def dmembed(self, context: Context, user: discord.User, *, message)-> None:
        member = context.guild.get_member(user.id) or await context.guild.fetch_member(
            user.id)
        embed = discord.Embed(description=message, color=0x9C84EF)
        try:
            await context.send("Выполено", ephemeral=True)
            await member.send(embed=embed)
        except:
            await context.send("ЛС закрыто", ephemeral=True)

    @commands.hybrid_command(name="setlogchannel", description="Установить канал для истории сообщений")
    @app_commands.describe(channel="Выберите канал или введите его ID.")
    @commands.check_any(commands.is_owner(), commands.has_permissions(administrator=True))
    @checks.not_blacklisted()
    async def setlogchannel(self, context: Context, channel: discord.TextChannel):
      try:
        channel_id = channel or context.channel
        server_id = context.guild.id
        channel_id = discord.utils.get(context.guild.channels, name=channel_id)
        channel_id = channel.id
        id = await db_manager.add_log_channel(channel_id, server_id)
        embed = discord.Embed(description=f"Канал для истории сообщений установлен на <#{id}>", color=0x9C84EF)
        await context.send(embed=embed)
      except:
        embed = discord.Embed(description="Такого канала не существует или у меня нет доступа к каналу.", color=0x9C84EF)
        await context.send(embed=embed)

    @commands.hybrid_command(name="removelogchannel", description="Удалить канал для истории сообщений")
    @commands.check_any(commands.is_owner(), commands.has_permissions(administrator=True))
    async def removelogchannel(self, context: Context):
      server_id = context.guild.id
      await db_manager.remove_log_channel(server_id)
      embed = discord.Embed(description="Канал для истории сообщений удалён.", color=0x9C84EF)
      await context.send(embed=embed)

    @commands.hybrid_command(name="giverole", description="Выдать пользователю роль.")
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_roles=True))
    async def giverole(self, context: Context, user: discord.Member, role: discord.Role):
      try:
        await user.add_roles(role)
        embed = discord.Embed(description=f"Пользователю `{user}` была выдана роль `{role.name}`", color=0x9C84EF)
        await context.send(embed=embed)
      except:
        embed = discord.Embed(description="У меня нет полномочий выдать эту роль или такой роли не существует!", color=0xcf271b)
        await context.send(embed=embed)

    @commands.hybrid_command(name="takerole", description="Забрать роль у пользователя.")
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_roles=True))
    async def takerole(self, context: Context, user: discord.Member, role: discord.Role):
      try:
        await user.remove_roles(role)
        embed = discord.Embed(description=f"Роль `{role.name}` пользователя `{user}` была изъята.", color=0x9C84EF)
        await context.send(embed=embed)
      except:
        embed = discord.Embed(description="У меня нет полномочий забрать эту роль или такой роли не существует!", color=0xcf271b)
        await context.send(embed=embed)
      
async def setup(bot):
    await bot.add_cog(Moderation(bot))
