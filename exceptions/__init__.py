from discord.ext import commands


class UserBlacklisted(commands.CheckFailure):

    def __init__(self, message="Пользователь в чёрном списке!"):
        self.message = message
        super().__init__(self.message)


class UserNotOwner(commands.CheckFailure):

    def __init__(self, message="Пользователь не владелец бота!"):
        self.message = message
        super().__init__(self.message)
