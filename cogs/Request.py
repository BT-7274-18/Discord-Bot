from discord.ext import commands
from modals.request_form import RequestForm
import discord, os

class Request(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        # check for requests file
        if not os.path.exists("requests.csv"):
            # requests file does not exist

            # create requests file
            with open("requests.csv", "w"):
                pass
            # end
        # end
    # end

    @discord.app_commands.command()
    async def request(self, interaction: discord.Interaction):
        """Request a piece of media be downloaded to the server."""

        await interaction.response.send_modal(RequestForm())

        interaction.followup
    # end
# end


async def setup(bot: commands.Bot):
    await bot.add_cog(Request(bot=bot))
# end


if __name__ == "__main__":
    pass
# end
