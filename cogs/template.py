import discord
from discord.ext import commands
from discord.ext.commands import Context, Bot
from discord import app_commands

from helpers import checks

access_token = 'KSWEYZd3vLuwazHEVwoDV1EcVFjeRezDogvUvG7xz3b6vsDI-EYAtKmvxT7F5HPt'

class Template(commands.Cog, name="template"):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="testcommand",
        description="This is a testing command that does nothing.",
    )
    @checks.not_blacklisted()
    @checks.is_owner()
    async def testcommand(self, context: Context):
        pass
  
async def setup(bot):
    await bot.add_cog(Template(bot))
