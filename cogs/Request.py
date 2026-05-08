from discord.ext import commands
from modals.request_form import RequestForm
import discord

class Request(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    # end

    @discord.app_commands.command()
    async def request(self, interaction: discord.Interaction):
        """Request a piece of media be downloaded to the server."""

        await interaction.response.send_modal(RequestForm())
    # end
# end


async def setup(bot: commands.Bot):
    await bot.add_cog(Request(bot=bot))
# end


if __name__ == "__main__":
    pass
# end
