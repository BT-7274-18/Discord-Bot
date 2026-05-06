from discord.ext import commands
from config_getter_setter import Config
import os, requests
from urllib.parse import urlparse


def is_youtube_channel(url: str) -> bool:
    """
    Verifies that the given url points to a YouTube channel.

    Arguments:
        url (str): A url that points to a YouTube channel.

    Returns:
        True if the url points to a channel or false if not.
    """

    CHANNEL_PREFIXES = (
        "/channel/",
        "/@",
        "/c/",
        "/user/",
    )
    
    try:
            parsed = urlparse(url)
    except Exception:
        return False
    # end

    if parsed.netloc not in {"youtube.com", "www.youtube.com"}:
        return False
    # end

    path = parsed.path.rstrip("/")
    if not path.startswith(CHANNEL_PREFIXES):
        return False
    # end

    try:
        response = requests.get(
            url,
            allow_redirects=True,
            headers={
                # Avoid bot challenges
                "User-Agent": "Mozilla/5.0"
            },
        )
    except requests.RequestException:
        return False
    # end

    # Must be a successful page
    if response.status_code != 200:
        return False
    # end

    final_path = urlparse(response.url).path

    # YouTube redirects invalid channels to search or home
    if final_path.startswith("/results") or final_path == "/":
        return False
    # end

    return final_path.startswith(CHANNEL_PREFIXES)
# end


def get_channels() -> list[str]:
    channels = []

    with open("channels.csv") as reader:
        line = reader.readline()[:-1]

        while line:
            channels.append(line)
            line = reader.readline()[:-1]
        # end
    # end

    return channels
# end


def save_channels(channelsList: list[str]) -> None:
    # write new watch list to file
    with open("channels.csv", "w") as writer:
        writer.write("\n".join(channelsList) + "\n")
    # end
# end


def remove_channel(name: str) -> None:
    """Removes a channel from the watch list with a name matching the given name.

    Args:
        name (str): Name of the channel to remove.
    """

    # get saved channels
    channels = get_channels()
    # remove the channel with the matching name
    channels.pop([channel.split(",")[3] for channel in channels].index(name))

    save_channels(channels)
# end


def add_channel(channelStr: str) -> None:
    """Adds the given channel information to the channel file.

    Args:
        channelStr (str): A string in the format of channelUrl,1OR0,downloadPath,channelName
    """

    # get current list of saved channels
    channels = get_channels()
    # add given channel
    channels.append(channelStr)
    # save new list of channels
    save_channels(channels)
# end


def init_channels():
    """Creates channel list file if it does not exist."""

    # check if channel list file exists
    if not os.path.exists("channels.csv"):
        # channel list file does not exist

        # create empty channel list file
        with open("channels.csv", "w"):
            pass
        # end
    # end
# end


class EditFlags(commands.FlagConverter, prefix='-', delimiter=" "):
    name: str = commands.flag(aliases=["a"], default=None, description="The new name you want to give the channel you're editing.")
    url: str = commands.flag(aliases=["u"], default=None, description="The new channel url you want to give the channel you're editing.")
    notify: bool = commands.flag(aliases=["n"], default=None, description="Either yes or no. If yes a discord message will be sent when this channel uploads a video. If no a message will not be sent.")


class Channel(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__()

        self.bot = bot
        self.illegalCharacters = [",", "/", "\\"]
        self.configs = Config()
        init_channels()
    # end

    def contains_illegal_characters(self, st: str) -> bool:
        """Detects if the given string contains illegal characters.

        Args:
            st (str): The string that will be checked.

        Returns:
            bool: True if an illegal character is found or False if none were found.
        """

        return any(char in st for char in self.illegalCharacters)
    # end

    @commands.group(name="channel", invoke_without_command=True)
    async def channel(self, ctx: commands.Context):
        """Manages channels on the watch list."""
        await ctx.send_help(ctx.command)
    # end

    @channel.command(name="add")
    async def channel_add(self, ctx: commands.Context, 
        channelName: str | None=None,
        channelUrl: str | None=None,
        notify: str | None=None
    ):
        """
        Adds the given channel to the watch list.
        
        Usage: add <name> <url> [-n | --notify]

        Arguments:
            name: Name of the channel being added. (Names with spaces must be wrapped in double quotes "")
            url:  The url of the channel you want to add to the watch list. (Urls with spaces need to be wrapped in double quotes "")
        
        Options:
            -n | --notify: Send discord message when given channel uploads a video.
        """

        # make sure user gives channel name and url
        if channelName is None or channelUrl is None:
            await ctx.send_help(ctx.command)
            return
        # end

        # make sure the given option is correct
        if notify is not None and notify not in ["-n", "--notify"]:
            # user used an unknown command
            await ctx.send_help(ctx.command)
            return
        # end

        # make sure channel name is not already on watch list
        if channelName in [channel.split(",")[3] for channel in get_channels()]:
            await ctx.send(f"{channelName} is already on watch list.")
            return
        # end

        # make sure channel url is not a duplicate
        if channelUrl in [channel.split(",")[0] for channel in get_channels()]:
            await ctx.send(f"A channel with that url is already on the watch list.")
            return
        # end

        # make sure channel name doesn't contain illegal characters
        if self.contains_illegal_characters(channelName):
            await ctx.send(f"Channel name cannot contain any of the following: {" ".join(self.illegalCharacters)}")
            return
        # end

        # make sure parent download path still exists
        if not os.path.exists(self.configs.get_parent_download_path()):
            await ctx.send("Parent download path no longer exists.")
            return
        # end

        # make sure channel url is valid
        if not is_youtube_channel(url=channelUrl):
            await ctx.send("Invalid channel url.")
            return
        # end

        # all checks passed, add channel to watch list
        add_channel(f"{channelUrl},{"0" if notify is None else "1"},{self.configs.get_parent_download_path() + "/" + channelName},{channelName}")

        # create folder for this channel
        os.mkdir(f"{self.configs.get_parent_download_path()}/{channelName}")

        await ctx.send(f"{channelName} was added to the watch list.")
    # end

    @channel.command(name="list")
    async def channel_list(self, ctx: commands.Context, verbose: str | None=None):
        """
        Shows all channel names on the watch list.

        Usage : list [-v | --verbose]
        
        Options:
            -v | --verbose: Shows channel name, url, and notify status.
        """

        channels = get_channels()

        # check if channels list is empty
        if channels == []:
            # channel list is empty

            # tell the user the channel list is empty
            await ctx.send("No channels on watch list.")
            return
        # end
        
        if verbose is None:
            # send a list of only channel names
            await ctx.send(f"```{"\n".join([channel.split(",")[-1] for channel in channels])}```")

        elif verbose in ["-v", "--verbose"]:
            # send a detailed list of channels on the watch list
            # channelName channelUrl Notify: yesNo

            # get channels on the watch list
            displayStrings = []

            nameColWidth = max([len(channel.split(",")[3]) for channel in channels])
            urlColWidth = max([len(channel.split(",")[0]) for channel in channels])

            # format channels for display
            for channel in channels:
                channel = channel.split(",")
                displayStrings.append(f"{channel[3].ljust(nameColWidth)} {channel[0].ljust(urlColWidth)} Notify: {"Yes" if int(channel[1])  else "No"}")
            #end

            # send the detailed list of channels
            await ctx.send(f"```{"\n".join(displayStrings)}```")

        else:
            # user used an unknown option
            await ctx.send_help(ctx.command)
        # end
    # end

    @channel.command(name="edit")
    async def channel_edit(self, ctx: commands.Context, name: str | None=None, *, flags: EditFlags):
        """
        Edits an existing channel on the watch list.

        Usage: edit <name> [options]

        Arguments:
            name: The name of the channel on the watch list you want to edit.

        Options:
            -a | -name <name>:     The new name you want to give the channel you're editing.
            -u | -url <url>:       The new channel url you want to give the channel you're editing.
            -n | -notify <yes-no>: Either yes or no. If yes a discord message will be sent when this channel uploads a video. If no a message will not be sent.
        """

        # get the current list of saved channels
        channels = get_channels()

        # make sure given name is on the watch list
        if name not in [channel.split(",")[3] for channel in channels]:
            await ctx.send(f"{name} is not on the watch list.")
            return
        # end

        # get the channel the user wants to edit
        editChannel = channels[[channel.split(",")[3] for channel in channels].index(name)].split(",")

        # if new channel name is given make sure it contains no illegal characters
        if flags.name is not None and self.contains_illegal_characters(flags.name):
            await ctx.send("New channels names cannot contain the following characters: " + " ".join(self.illegalCharacters))
            return
        # end

        if flags.name is not None:
            editChannel[3] = flags.name
        # end

        if flags.url is not None:
            editChannel[0] = flags.url
        # end

        if flags.notify is not None:
            editChannel[1] = "1" if flags.notify else "0"
        # end

        # update edited channel
        channels[[channel.split(",")[3] for channel in channels].index(name)] = ",".join(editChannel)
        
        # update watch list
        save_channels(channels)

        # tell the user changes took affect
        await ctx.send(f"{name} has been updated.")
    # end

    @channel.command(name="remove")
    async def channel_remove(self, ctx: commands.Context, channelName: str | None=None):
        """
        Removes the given channel from the watch list.

        Usage: remove <name>

        Arguments:
            name: The name of the channel you want to remove.
        """
        
        
        if channelName is None:
            # tell the user needs to give the name of the channel they want to remove
            await ctx.send("Please provide a channel name.")

        elif channelName in [channel.split(",")[3] for channel in get_channels()]:
            # remove the given channel from the watch list
            remove_channel(channelName)
            # tell the user the channel was removed successfully
            await ctx.send(f"Removed {channelName} from the list.")

        else:
            # tell the user the channel they game is not on the watch list
            await ctx.send(f"{channelName} is not on the watch list.")
    # end
# end


async def setup(bot: commands.Bot):
    await bot.add_cog(Channel(bot=bot))
# end


if __name__ == "__main__":
    print("\n".join([channel.split(",")[-1] for channel in get_channels()]))
