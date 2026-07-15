from discord.ext.commands import Context
from config_getter_setter import Config

config = Config()

def isAdmin(func):
    """Make sure the person using the given command is an admin"""

    async def wrapper(self, *args, **kwargs):
        # get the command context 
        ctx: Context = args[1]

        # get the admin list
        admins = config.get_admin_list()

        # check if the command author is an admin
        if ctx.author.id in admins:
            # the command author is not an admin

            # tell the user they need admin
            await ctx.send("You must be an admin to use this command.")

            # don't call parent function
            return
        # end

        return func(self, *args, **kwargs)
    # end

    return wrapper
# end