from discord.ext import commands
import discord
from asyncio import TimeoutError
from typing import Any
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


def update_config(filePath:str, section: str, key: str, value) -> bool:
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


def get_config(filePath: str, section: str, key: str) -> str | None:
    """
    Update or create a key-value pair in a given section of an INI file.

    Arguments:
        filePath (str): The file path to the config file.
        section (str): The name of the section the given key is located.
        key (str): The name of the key whose value you want to get.

    Returns:
        The value of the key or none if there was an error reading the file.
    """

    config = configparser.ConfigParser()

    # Read existing file if it exists else return false
    if os.path.exists(filePath):
        config.read(filePath)

    else:
        return None
    # end
    # value = config.get(section, key)
    # return value if value is not None else ""
    return config.get(section, key)
# end


class Settings(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        self.defaultConfig = configparser.ConfigParser()
        self.defaultConfig["PARENT VIDEO PATH"] = {"path": "YouTube"}
        self.defaultConfig["ADMIN"] = {"bot token": "", "admins": ""}

        # if config file doesn't exists create on using template
        if not os.path.exists("config.ini"):
            with open("config.ini", "w") as writer:
                self.defaultConfig.write(writer)
            # end
        # end
    # end

    async def validate_user_id(self, userId: int) -> bool:
        """
        Validates the given discord user ID.

        Arguments:
            userId (int): The discord user id you want to validate
        
        Returns:
            True if the given discord user id points to a discord account or false if not.
        """

        try:
            # try to fetch a discord user using the given id
            user = await self.bot.fetch_user(userId)

            print(user.display_name)

            # the id was valid
            return True
        except discord.NotFound:
            # the id was not valid
            return False
        except discord.HTTPException:
            # there was an error in the fetch process
            return False
        # end
    # end

    @commands.group(name="settings", invoke_without_command=True)
    async def settings(self, ctx: commands.Context):
        """Manages settings."""
        await ctx.send_help(ctx.command)
    # end

    @settings.command(name="reset")
    async def settings_reset(self, ctx: commands.Context):
        """Resets the config file to its default values."""
    
        # ask the user if they're sure they want to rest the configs
        await ctx.send("Are you sure you want to reset the configs?\nThis will reset all settings to their default value. (y/n)")

        def check(msg: discord.Message) -> bool:
            return msg.author == ctx.author and msg.channel == ctx.channel and msg.content.lower() in ('yes', 'y', 'true', 't', '1', 'enable', 'on', 'no', 'n', 'false', 'f', '0', 'disable', 'off')
        # end

        try:
            # get users respones
            msg = await self.bot.wait_for("message", check=check)

            # determine if the user is sure or not
            if msg.content.lower() in ('yes', 'y', 'true', 't', '1', 'enable', 'on'):
                # the user wants to reset configs

                # make a copies of important settings
                admins = get_config("config.ini", "ADMIN", "admins")
                botToken = get_config("config.ini", "ADMIN", "bot token")

                if admins is None or botToken is None:
                    # admin settings could not be backed up don't reset settings
                    await ctx.send("Admin settings back up failed. Reset canceled.")

                    return
                # end

                # add admin settings to default configs
                self.defaultConfig["ADMIN"]["admins"] = str(admins)
                self.defaultConfig["ADMIN"]["bot token"] = botToken

                # reset the config file
                with open("config.ini", "w") as writer:

                    # reset config file
                    self.defaultConfig.write(writer)
                # end

                # tell the user the config was reset
                await ctx.send("Config settings reset.")

            else:
                # user entered somthing other than a yes

                # cancel config reset
                await ctx.send("Reset canceled")
            # end

        except TimeoutError:
            # user did not respond
            await ctx.send("Settings not reset. Took too long to respond.") 
        # end
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

        # get the length of the option with the longest name
        colWidth = max([len(key) for section in configs.sections() for key in configs[section]])

        # add each section and option to the list to format later
        for section in configs.sections():
            # add section title
            configStrings.append(f"[{section}]")
            for key in configs[section]:
                # add option value pairs
                configStrings.append(f"{key.ljust(colWidth)} {configs[section][key]}")
                #                           ^ Format option name so that all option values are aligned
            # end
        # end
        await ctx.send("```\n" + "\n".join(configStrings) + "\n```")
    
        # await ctx.send(f"```{"\n".join([f"{col1.ljust(max([len(item[0]) for item in data]), ".")} {col2}" for col1, col2 in data])}```")
    # end

    @commands.group(name="admins", invoke_without_command=True)
    async def admins(self, ctx: commands.Context):
        """Handels admin related settings."""
        await ctx.send_help(ctx.command)
    # end
    
    @admins.command(name="add")
    async def admins_add(self, ctx: commands.Context, member: discord.Member | int | None=None):
        """
        Adds a profile to the admins list.
        
        Usage: add <profile>

        Arguments:
            profile: The discord profile or user ID to add to the admins list.
        """

        # make sure the user gives a member to add to the admins list
        if member is None:
            await ctx.send_help(ctx.command)
            return
        # end

        memberName = ""
        memberId = ""
        if isinstance(member, int):
            memberName = str(member)
            memberId = str(member)

        else:
            memberName = member.display_name
            memberId = str(member.id)

        # check if the given user is valid
        if not await self.validate_user_id(int(memberId)):
            await ctx.send(f"{memberName} is not a valid user.")
            return
        # end

        # get the current admins list
        admins = get_config("config.ini", "ADMIN", "admins")

        # make sure config file was read successfully
        if admins is None:
            # config file was not read successfully

            # tell the user the command failed
            await ctx.send(f"Failed to add {memberName} to the admins list. Could not read config file.")
            return

        # parse string from config file
        admins = admins.split(",")

        # remove empty strings from admin list
        admins = [item for item in admins if item != ""]

        # make sure the given member is not a duplicate
        if memberId in admins:
            # given member is already on the admin list

            # tell the user the given member is already an admin
            await ctx.send(f"{memberName} is already an admin.")
            return
        # end

        # add the given members id to the admin list
        admins.append(memberId)

        # update the config changes with the new admins list
        if update_config("config.ini", "ADMIN", "admins", ",".join(admins)):
            # config was updated successfully 

            # tell the user the changes were made successfully
            await ctx.send(f"{memberName} has been added to the admins list.")

        else:
            # failed to update the donfig file
            await ctx.send(f"Failed to add {memberName} to the admins list.")
            return
        # end
    # end

    @admins.command(name="remove")
    async def admins_remove(self, ctx: commands.Context, member):
        """
        Removes a profile from the admins list.
        
        Usage: remove <profile>

        Arguments:
            profile: The discord profile to remove from the admins list.
        """
    
        pass
    # end

    @admins.command(name="list")
    async def admins_list(self, ctx: commands.Context):
        """Lists all profiles on the admin list."""
    
        pass
    # end
# end


async def setup(bot: commands.Bot):
    await bot.add_cog(Settings(bot=bot))
# end


if __name__ == "__main__":
    print(list("[1, 2, 3, 4]"))
# end