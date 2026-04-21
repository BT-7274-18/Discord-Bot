from discord.ext import commands


class Video(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    # end
# end


async def setup(bot: commands.Bot):
    await bot.add_cog(Video(bot=bot))
# end


if __name__ == "__main__":
    pass
# end 