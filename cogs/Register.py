import discord
from discord.ext import commands

class Register(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    # end

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # ignore messages from the bot itself
        if message.author == self.bot.user:
            # incoming message is from the bot
            return
        # end

        # make sure the incoming message is a DM
        if not isinstance(message.channel, discord.DMChannel):
            # this is not a dm channel
            return
        # end

        await message.channel.send("Responding to non-command dm.")

        # make sure commands can still be sent in DMs
        await self.bot.process_commands(message)
    # end
# end


async def setup(bot: commands.Bot):
    await bot.add_cog(Register(bot=bot))
# end


if __name__ == "__main__":
    pass
# end
