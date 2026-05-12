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

        # use a list of column headers and items to calculate width of each column
        items = [["Request Id", "Requester Id", "Media Title", "Url", "Created On"]]

        # add each request to output strings
        for request in requests:
            items.append([str(request["requestId"]), str(request['requesterId']), request['mediaTitle'], request['url'], request['createdOn'].strftime("%m-%d-%y")])
        # end

        colWidths = []

        # get the widest item in each column for formatting
        for i in range(len(items[0])):
            colWidths.append(max([len(row[i]) for row in items]))
        # end

        # apply column width formatting to each item
        for i in range(len(colWidths)):
            for row in items:
                row[i] = row[i].ljust(colWidths[i])
            # end
        # end

        # use list of strigns to join later
        outputStrings = []

        # join each row
        for i in range(len(items)):
            outputStrings.append("  ".join(items[i]))
        # end

        # send open requests formatted in a code block
        await ctx.send(f"```{"\n".join(outputStrings)}```")
    # end
# end


async def setup(bot: commands.Bot):
    await bot.add_cog(Request(bot=bot))
# end


if __name__ == "__main__":
    pass
# end
