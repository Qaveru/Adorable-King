from discord.ext import commands
import re
import asyncio
import random
class Talk(commands.Cog, name="talk"):
    def __init__(self, bot):
        self.bot = bot

  
  
    @commands.Cog.listener()
    async def on_message(self, message): 
     if message.guild:
      if message.guild.id == 1067164049613271141 or message.guild.id == 1076815472030404628 or message.guild.id == 929943183503278081:
       if message.author.id == 1077444289224773752:
         pass
       else:  
        starts = message.content.startswith
        lower = message.content.lower()
        chsend = message.channel.send
        akami = message.author.id == 1077299641776885831
        shelby = message.author.id == 1081303684635439146
        qaveru = message.author.id == 325320123613184021
        subaru = message.author.id == 690182209486848155
        samsa = message.author.id == 620976238391066664
        vaza1 = message.author.id == 619616558917877788
        vaza2 = message.author.id == 1013474912767324291
        nice = ["хорошо", "отлично", "класс", "круто"]
        bad = ["плохо", "не очень", "трудно"]
        
        
          # Здесь 1 команды
        
        if starts("тест") and not akami:
           await chsend("Тест")
        elif lower == "слушаю" and akami:
          await asyncio.sleep(0.5)
          async with message.channel.typing():
            await asyncio.sleep(1)
          await chsend("Вставай на колени!")
          await asyncio.sleep(3)
          async with message.channel.typing():
            await asyncio.sleep(1)
          await chsend("Пожалуйста")
          await asyncio.sleep(6)
          async with message.channel.typing():
            await asyncio.sleep(1)
          await chsend("Для общего развития")
    #    elif lower == "да" and not qaveru:
    #      await asyncio.sleep(1)
    #        await chsend("Пизда")

        elif "любишь" in lower:
          yesno = ["да", "нет"]
          await chsend(random.choice(yesno))

        elif "привет" in lower  and qaveru:
            channel = message.channel
            async with message.channel.typing():
              await asyncio.sleep(0.8)
            await channel.send('Привет, мой любимый создатель! Как ты?')
            def check(message1):
              content = message1.content.lower()
              return message1.channel == channel and message1.author == message.author and any(word in content for word in nice)
            try:
              msg = await self.bot.wait_for('message', check=check, timeout=15.0)
              async with message.channel.typing():
                await asyncio.sleep(0.8)
              await channel.send("Я очень рад это слышать!".format(msg))
              def check(message2):
                content = message2.content.lower()
                question = ["ты", "дела", "тебя"]
                return message2.channel == channel and message2.author == message.author and any(word in content for word in question)
              try:
                msg = await self.bot.wait_for('message', check=check, timeout=15.0)
                async with message.channel.typing():
                  await asyncio.sleep(0.8)
                await channel.send("У меня всё отлично! Развлекаюсь тут и бывает даже слушаю музыку от чего получаю огромное удовольствие!".format(msg))
              except asyncio.exceptions.TimeoutError:
                return
            except asyncio.exceptions.TimeoutError:  
              async with message.channel.typing():
                await asyncio.sleep(0.8)
              await channel.send('Так как твои дела, Кавэру?')
              def check(message2):
                content = message2.content.lower()
                return message2.channel == channel and message2.author == message.author and any(word in content for word in nice)
              try:
                msg = await self.bot.wait_for('message', check=check, timeout=15.0)
                async with message.channel.typing():
                  await asyncio.sleep(0.8)
                await channel.send("Я очень рад это слышать!".format(msg))
              except asyncio.exceptions.TimeoutError:   
                async with message.channel.typing():
                  await asyncio.sleep(0.8)
                await chsend('Не игнорируй, пожалуйста')           

        elif lower == "привет" and subaru:
            channel = message.channel
            async with message.channel.typing():
              await asyncio.sleep(0.8)
            await channel.send('Привет, Субару, как твои дела?')
            def check(message1):
              content = message1.content.lower()
              return message1.channel == channel and message1.author == message.author and any(word in content for word in nice)
            try:
              msg = await self.bot.wait_for('message', check=check, timeout=15.0)
              async with message.channel.typing():
                await asyncio.sleep(0.8)
              await channel.send("Я очень рад это слышать!".format(msg))
            except asyncio.exceptions.TimeoutError:  
              async with message.channel.typing():
                await asyncio.sleep(0.8)
              await channel.send('Так как твои дела, Cубару?')
              def check(message2):
                content = message2.content.lower()
                return message2.channel == channel and message2.author == message.author and any(word in content for word in nice)
              try:
                msg = await self.bot.wait_for('message', check=check, timeout=15.0)
                async with message.channel.typing():
                  await asyncio.sleep(0.8)
                await channel.send("Я очень рад это слышать!".format(msg))
              except asyncio.exceptions.TimeoutError:   
                async with message.channel.typing():
                  await asyncio.sleep(0.8)
                await chsend('Не игнорируй, пожалуйста')

     else:
       pass
  
async def setup(bot):
    await bot.add_cog(Talk(bot))