import random

import aiohttp
import discord
from discord.ext import commands
from discord.ext.commands import Context

from helpers import checks


class Choice(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    @discord.ui.button(label="Орёл", style=discord.ButtonStyle.blurple)
    async def confirm(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        self.value = "Орёл"
        self.stop()

    @discord.ui.button(label="Решка", style=discord.ButtonStyle.blurple)
    async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.value = "Решка"
        self.stop()


class RockPaperScissors(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label="Scissors", description="Вы выбираете ножницы.", emoji="✂"
            ),
            discord.SelectOption(
                label="Rock", description="Вы выбираете камень.", emoji="🪨"
            ),
            discord.SelectOption(
                label="Paper", description="Вы выбираете бумагу.", emoji="🧻"
            ),
        ]
        super().__init__(
            placeholder="Выбирайте...",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        choices = {
            "rock": 0,
            "paper": 1,
            "scissors": 2,
        }
        user_choice = self.values[0].lower()
        user_choice_index = choices[user_choice]

        bot_choice = random.choice(list(choices.keys()))
        bot_choice_index = choices[bot_choice]

        result_embed = discord.Embed(color=0x9C84EF)
        result_embed.set_author(
            name=interaction.user.name, icon_url=interaction.user.avatar.url
        )

        if user_choice_index == bot_choice_index:
            result_embed.description = f"**Ничья!**\nВы выбрали {user_choice} и Я выбрал {bot_choice}."
            result_embed.colour = 0xF59E42
        elif user_choice_index == 0 and bot_choice_index == 2:
            result_embed.description = f"**Вы выиграли!**\nВы выбрали {user_choice} и Я выбрал {bot_choice}."
            result_embed.colour = 0x9C84EF
        elif user_choice_index == 1 and bot_choice_index == 0:
            result_embed.description = f"**Вы выиграли!**\nВы выбрали {user_choice} и Я выбрал {bot_choice}."
            result_embed.colour = 0x9C84EF
        elif user_choice_index == 2 and bot_choice_index == 1:
            result_embed.description = f"**Вы выиграли!**\nВы выбрали {user_choice} и Я выбрал {bot_choice}."
            result_embed.colour = 0x9C84EF
        else:
            result_embed.description = (
                f"**Я выиграл!**\nВы выбрали {user_choice} и Я выбрал {bot_choice}."
            )
            result_embed.colour = 0xE02B2B
        await interaction.response.edit_message(
            embed=result_embed, content=None, view=None
        )


class RockPaperScissorsView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(RockPaperScissors())


class Fun(commands.Cog, name="fun"):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="randomfact", description="Получить случайный факт.")
    @checks.not_blacklisted()
    async def randomfact(self, context: Context) -> None:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://uselessfacts.jsph.pl/random.json?language=en"
            ) as request:
                if request.status == 200:
                    data = await request.json()
                    embed = discord.Embed(description=data["text"], color=0xD75BF4)
                else:
                    embed = discord.Embed(
                        title="Ошибка!",
                        description="Неполадки с API, пожалуйста попробуйте позже",
                        color=0xE02B2B,
                    )
                await context.send(embed=embed)

    @commands.hybrid_command(name="cat", description="Получить случайную картинку котика или кошечки.")
    @checks.not_blacklisted()
    async def cat(self, context: Context) -> None:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://api.thecatapi.com/v1/images/search"
            ) as request:
                if request.status == 200:
                    data = await request.json()
                    embed = discord.Embed(title='Милота! :heart_eyes_cat:', url=data[0]['url'], color=0xD75BF4)
                    embed.set_image(url=data[0]['url'])
                else:
                    embed = discord.Embed(
                        title="Ошибка!",
                        description="Неполадки с API, пожалуйста попробуйте позже",
                        color=0xE02B2B,
                    )
                await context.send(embed=embed)

    @commands.hybrid_command(name="dog", description="Получить случайную картинку пёсика.")
    @checks.not_blacklisted()
    async def dog(self, context: Context) -> None:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://api.thedogapi.com/v1/images/search"
            ) as request:
                if request.status == 200:
                    data = await request.json()
                    embed = discord.Embed(title='Гав! :dog:', url=data[0]['url'], color=0xD75BF4)
                    embed.set_image(url=data[0]['url'])
                else:
                    embed = discord.Embed(
                        title="Ошибка!",
                        description="Неполадки с API, пожалуйста попробуйте позже",
                        color=0xE02B2B,
                    )
                await context.send(embed=embed)

    @commands.hybrid_command(name="bird", description="Получить случайную картинку птички.")
    @checks.not_blacklisted()
    async def bird(self, context: Context) -> None:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://shibe.online/api/birds?count=1&urls=true&httpsUrls=true"
            ) as request:
                if request.status == 200:
                    data = await request.json()
                    embed = discord.Embed(title='Птичка :bird:', url=data[0], color=0xD75BF4)
                    embed.set_image(url=data[0])
                else:
                    embed = discord.Embed(
                        title="Ошибка!",
                        description="Неполадки с API, пожалуйста попробуйте позже",
                        color=0xE02B2B,
                    )
                await context.send(embed=embed)

    @commands.hybrid_command(name="fox", description="Получить случайную картинку лисички.")
    @checks.not_blacklisted()
    async def fox(self, context: Context) -> None:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://randomfox.ca/floof/"
            ) as request:
                if request.status == 200:
                    data = await request.json()
                    embed = discord.Embed(title='Лисичка :fox:', url=data['link'], color=0xD75BF4)
                    embed.set_image(url=data['image'])
                else:
                    embed = discord.Embed(
                        title="Ошибка!",
                        description="Неполадки с API, пожалуйста попробуйте позже",
                        color=0xE02B2B,
                    )
                await context.send(embed=embed)

    @commands.hybrid_command(name="duck", description="Получить случайную картинку уточки.")
    @checks.not_blacklisted()
    async def duck(self, context: Context) -> None:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://random-d.uk/api/v2/random"
            ) as request:
                if request.status == 200:
                    data = await request.json()
                    embed = discord.Embed(title='Кря :duck:', url=data['url'], color=0xD75BF4)
                    embed.set_image(url=data['url'])
                else:
                    embed = discord.Embed(
                        title="Ошибка!",
                        description="Неполадки с API, пожалуйста попробуйте позже",
                        color=0xE02B2B,
                    )
                await context.send(embed=embed)            

    @commands.hybrid_command(
        name="coinflip", description="Подбросить монетку, не забудьте сделать ставку!"
    )
    @checks.not_blacklisted()
    async def coinflip(self, context: Context) -> None:
        buttons = Choice()
        embed = discord.Embed(description="Ты ставишь на что?", color=0x9C84EF)
        message = await context.send(embed=embed, view=buttons)
        await buttons.wait()  # We wait for the user to click a button.
        result = random.choice(["Орёл", "Решка"])
        if buttons.value == result:
            embed = discord.Embed(
                description=f"Верно! Вы выбрали `{buttons.value}` и угадали что это будет `{result}`.",
                color=0x9C84EF,
            )
        else:
            embed = discord.Embed(
                description=f"Ой! Вы выбрали `{buttons.value}`, но не угадали что это будет `{result}`, повезёт в следующий раз!",
                color=0xE02B2B,
            )
        await message.edit(embed=embed, view=None, content=None)

    @commands.hybrid_command(
        name="rps", description="Сыграйте в Камень, Ножницы, Бумага со мной."
    )
    @checks.not_blacklisted()
    async def rock_paper_scissors(self, context: Context) -> None:
        view = RockPaperScissorsView()
        await context.send("Пожалуйста выберите...", view=view)

async def setup(bot):
    await bot.add_cog(Fun(bot))
