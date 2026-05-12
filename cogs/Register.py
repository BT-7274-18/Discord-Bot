import discord
from discord.ext import commands
from modules.config_getter_setter import Config

class Register(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.configs = Config()
    # end

    async def is_valid_user_id(self, userId: int) -> bool:
        """
        Validates the given discord user id

        Arguments:
            userId (int): A discord user id to validate.

        Returns:
            True if the given user Id points to a discord user or false if it's invalid.
        """

        if await self.bot.fetch_user(userId) is None:
            return False
        else:
            return True
        # end
    # end

    @commands.command()
    async def register(self, ctx: commands.Context, member: int | discord.Member):
        """
        Registers the given user as a requester.

        Useage: register <id>

        Arguments:
            id: The user id of the user you want to add as a requester.
        """
        
        userId: int
        displayName: str | int
        if isinstance(member, discord.Member):
            userId = member.id
            displayName = member.name
        else:
            userId = member
            displayName = member
        # end

        # make sure the given user id is valid
        if not await self.is_valid_user_id(userId):
            # the given user id is invalid
            await ctx.send("Invalid user id.")
            return
        # end

        # get the current requesters
        requesters = self.configs.get_requesters()

        # make sure the given user is not already a requester
        if userId in requesters:
            # the given user is already on the requesters list
            await ctx.send(f"{displayName} is already a requester.")
            return
        # end

        # add the given user id to requesters list
        requesters.append(userId)

        # save the new requesters to file
        self.configs.set_requesters(requesters=requesters)

        # send confirmation message
        await ctx.send(f"{displayName} added to requesters list.")
    # end
# end


async def setup(bot: commands.Bot):
    await bot.add_cog(Register(bot=bot))
# end


if __name__ == "__main__":
    pass
# end
