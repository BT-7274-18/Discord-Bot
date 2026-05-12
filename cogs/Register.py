import discord
from discord.ext import commands
from modules.config_getter_setter import Config

class Register(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.configs = Config()
    # end

    def is_valid_user_id(self, userId: int) -> bool:
        """
        Validates the given discord user id

        Arguments:
            userId (int): A discord user id to validate.

        Returns:
            True if the given user Id points to a discord user or false if it's invalid.
        """

        if self.bot.fetch_user(userId) is None:
            return False
        else:
            return False
        # end
    # end

    @commands.command()
    async def register(self, ctx: commands.Context, id: int):
        """
        Registers the given user as a requester.

        Useage: register <id>

        Arguments:
            id: The user id of the user you want to add as a requester.
        """

        # make sure the given user id is valid
        if not self.is_valid_user_id(id):
            # the given user id is invalid
            await ctx.send("Invalid user id.")
            return
        # end

        # get the current requesters
        requesters = self.configs.get_requesters()

        # add the given user id to requesters list
        requesters.append(id)

        # save the new requesters to file
        self.configs.set_requesters(requesters=requesters)

        # send confirmation message
        await ctx.send(f"{id} added to requesters list.")
    # end
# end


async def setup(bot: commands.Bot):
    await bot.add_cog(Register(bot=bot))
# end


if __name__ == "__main__":
    pass
# end
