from discord.ext import commands
from pathvalidate import sanitize_filepath
import os, configparser


def get_config_options(filePath: str) -> list | None:
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


class Video(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    # end

    @commands.group(name="video", invoke_without_command=True)
    async def video(self, ctx: commands.Context):
        """Manages downloaded videos."""
        
        await ctx.send_help(ctx.command)
    # end
# end


async def setup(bot: commands.Bot):
    await bot.add_cog(Video(bot=bot))
# end


if __name__ == "__main__":
    print(get_config('config.ini', "VIDEO PARENT PATH", "path"))
# end 