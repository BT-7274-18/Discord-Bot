from discord.ext import commands
from pathvalidate import sanitize_filepath
import configparser, os


def get_config_options(filePath: str) -> list | None:
    """
    Gets all the options from the config as a list.

    Arguments:
        filePath (str): The name of the config file.

    Returns:
        A list of all config options or None if an error occured.
    """

    # make sure config file exists
    if not os.path.isfile(filePath):
        print(f"Error: File '{filePath}' not found.")
        return None
    # end

    # create config parser
    config = configparser.ConfigParser()

    # safely parse config file
    try:
        config.read(filePath)

    # handle parsing error
    except configparser.Error as e:
        print(f"Error reading config file: {e}")
        return None
    # end

    # make sure there are sections to read
    if not config.sections():
        print("No sections found in the configuration file.")
        return None
    # end

    # return all config option names
    return [option for section in config.sections() for option, _ in config.items(section)]
# end


def get_all_config(filePath: str) -> configparser.ConfigParser | None:
    """
    Gets a config options as a config parse object or None if file could not be read.

    Arguments:
        filePath (str): Name of the config file to read.

    Returns:
        Config parser object or None if config file could not be read.
    """

    # create parser object
    config = configparser.ConfigParser()
    # read config file
    config.read(filePath)

    # return parser object or none if file could not be read
    return config if config is not None else None
# end


def update_config(filePath, section, key, value) -> bool:
    """
    Update or create a key-value pair in a given section of an INI file.

    Arguments:
        filePath (str): The file path to the config file.
        section (str): The name of the section the given key is located.
        key (str): The name of the key you want to update.

    Returns:
        True if the file was updated successfully or false if there was an error along the way.
    """

    config = configparser.ConfigParser()

    # Read existing file if it exists else return false
    if os.path.exists(filePath):
        config.read(filePath)

    else:
        return False
    # end

    # return false if config does not have the given section
    if not config.has_section(section):
        return False
    # end

    # Set the value
    config.set(section, key, str(value))  # Always store as string

    # Write changes back to file
    try:
        with open(filePath, 'w') as configfile:
            config.write(configfile)
        # end

        print(f"Updated [{section}] {key} = {value} in {filePath}")

        # config was updated successfully return true
        return True
    
    except OSError as e:
        print(f"Error writing to file: {e}")
        # there was an error writing to config file return false
        return False
    # end
# end


def get_config(filePath, section, key):
    """
    Update or create a key-value pair in a given section of an INI file.

    Arguments:
        filePath (str): The file path to the config file.
        section (str): The name of the section the given key is located.
        key (str): The name of the key you want to update.

    Returns:
        True if the file was updated successfully or false if there was an error along the way.
    """

    config = configparser.ConfigParser()

    # Read existing file if it exists else return false
    if os.path.exists(filePath):
        config.read(filePath)

    else:
        return False
    # end

    return config.get(section, key)


class Settings(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    # end

    @commands.group(name="settings", invoke_without_command=True)
    async def settings(self, ctx: commands.Context):
        """Manages settings."""
        await ctx.send_help(ctx.command)
    # end

    @settings.command(name="set")
    async def settings_set(self, ctx: commands.Context, setting: str | None=None, settingSection: str | None=None, value: str | None=None):
        """
        Updates the given setting with the given value.

        Useage: set <option> <value>

        Arguments:
            setting: The name of the setting to change.
            section: The settings section that contains the option you want to change.
            value:  The value to update the setting to.
        """
        
        # make sure both command arguments are given
        if setting is None or value is None or settingSection is None:
            # one or both arguments were not given
            await ctx.send_help(ctx.command)
            return
        # end
        
        # get a list of config options
        configOptions = get_config_options("config.ini")
        # make sure the config file could be reached
        if configOptions is None:
            # config file could not be reach
            await ctx.send("Command not executed. Could not reach config file.")
            return
        # end

        # make sure the given command is valid
        if not setting in configOptions:
            # given command is not valid
            await ctx.send(f"{setting} is not a valid setting.")
            return
        # end

        # determine which setting is being changed
        if setting == "path":
            # user wants to change the parent path where videos are downloaded to

            # make sure the given dirpath is valid
            if value != sanitize_filepath(value):
                # given file path is not valid
                await ctx.send("File path is not valid.")
                return
            # end

            # update the path setting
            update_config("config.ini", "PARENT VIDEO PATH", "path", value=value)

            await ctx.send("Parent video file path was updated to " + value)
        # end
    # end

    @settings.command(name="list")
    async def settings_list(self, ctx: commands.Context):
        """Lists available settings."""

        configStrings = []
        configs = get_all_config("config.ini")

        # check if settings file was read successfully
        if configs is None:
            await ctx.send("Could not read settings file.")
            return
        # end

        colWidth = max([len(key) for section in configs.sections() for key in configs[section]])

        for section in configs.sections():
            configStrings.append(f"[{section}]")
            for key in configs[section]:
                configStrings.append(f"{key.ljust(colWidth)} {configs[section][key]}")
            # end
        # end
        await ctx.send("```\n" + "\n".join(configStrings) + "\n```")
    
        # await ctx.send(f"```{"\n".join([f"{col1.ljust(max([len(item[0]) for item in data]), ".")} {col2}" for col1, col2 in data])}```")
    # end
# end


async def setup(bot: commands.Bot):
    await bot.add_cog(Settings(bot=bot))
# end


if __name__ == "__main__":
    configs = get_all_config("config.ini")

    if configs is not None:
        colWidth = max([len(key) for section in configs.sections() for key in configs[section]])
        print("```\n" + "\n".join([f"{key.ljust(colWidth)} {configs[section][key]}" for section in configs.sections() for key in configs[section]]) + "\n```")
    # end
# end