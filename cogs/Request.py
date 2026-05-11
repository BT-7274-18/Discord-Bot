from discord.ext import commands
from modals.request_form import RequestForm
from modules.requests import get_requests
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
    # end

    @commands.group(name="requests", invoke_without_command=True)
    async def requests(self, ctx: commands.Context):
        """Handels media download requests."""
        await ctx.send_help(ctx.command)
    # end
    
    @requests.command(name="list")
    async def requests_list(self, ctx: commands.Context):
        """List all unfullfilled download requests."""
    
        # get all requests from file
        requests = get_requests()

        # check if there are no open requests
        if requests == []:
            # there are no open requests
            await ctx.send("There are no open requests.")
            return
        # end

        # use a list to format strings later
        outputStrings = [" ".join(list(requests[0].keys()))]

        # add each request to output strings
        for request in requests:
            outputStrings.append(f"{request['requesterId']} {request['mediaTitle']} {request['url']} {request['comment']} {request['createdOn']}")
        # end

        # send open requests formatted in a code block
        await ctx.send(f"```{"\n".join(outputStrings)}```")
    # end
# end


async def setup(bot: commands.Bot):
    await bot.add_cog(Request(bot=bot))
# end


if __name__ == "__main__":
    requests = get_requests()

    outputStrings = [" ".join(list(requests[0].keys()))]
# end
