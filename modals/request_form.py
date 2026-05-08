import discord


class RequestForm(discord.ui.Modal, title="Request Form"):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.add_item(discord.ui.TextInput(label="Media Title"))
        self.add_item(discord.ui.TextInput(label="Url", default="Url to media information."))
        self.add_item(discord.ui.TextInput(label="Comment"))