import discord
import datetime
from requests import add_request


class RequestForm(discord.ui.Modal, title="Request Form"):
    mediaTitle = discord.ui.TextInput(label="Media Title", required=True)
    url = discord.ui.TextInput(label="Url", required=True)
    comment = discord.ui.TextInput(label="Comment", required=False)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        interaction.created_at
        add_request(interaction.user.id, self.mediaTitle.value, self.url.value, self.comment.value)

        await interaction.response.send_message("Request submitted.")
    # end
# end
