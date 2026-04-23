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
    Gets the config at the given file, section, and key.

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


def get_list_config(filePath: str, section: str, key: str) -> list[str] | None:
    """
    Gets the list config at the given file, section, and key

    Arguments:
        filePath (str): The file path to the config file.
        section (str): The name of the section the given key is located.
        key (str): The name of the key whose value you want to get.

    Returns:
        A list of values in the key or none if there was an error reading the file.
    """

    configs = get_config(filePath=filePath, section=section, key=key)

    # check if the config was read successfully
    if configs is None:
        # config was not read successfully
        return None
    # end

    # split the config into a string
    configs = configs.split(",")

    # remove any empty strings
    configs = [config for config in configs if config != ""]

    return configs
# end


def validate_schema(template: configparser.ConfigParser, fileName: str) -> bool:
    """
    Validates the given ini file against the given config object to make sure the schemas match.

    Arguments:
        template (configparser.ConfigParser): The template config to varify against.
        fileName (str): The name of the ini file to varify the schema.

    Returns:
        True if the schemas match or false if they don't match.
    """

    # check if test file exists
    if not os.path.exists(fileName):
        # test file does not exist
        return False
    # end

    # import test config file
    testConfig = configparser.ConfigParser()
    testConfig.read(fileName)

    # check if all sections match
    if template.sections() != testConfig.sections():
        # all sections don't match
        return False
    # end

    # check if keys match
    for section in template.sections():
        if template[section].keys() != testConfig[section].keys():
            #  keys for this section don't match match
            return False
        # end
    # end

    # all checks passed
    # config schemas match
    return True
# end


class Settings(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        self.defaultConfig = configparser.ConfigParser()
        self.defaultConfig["PARENT VIDEO PATH"] = {"path": "YouTube"}
        self.defaultConfig["ADMIN"] = {"bot token": "", "admins": ""}

        # if config file doesn't exists create one using template
        if not os.path.exists("config.ini"):
            with open("config.ini", "w") as writer:
                self.defaultConfig.write(writer)
            # end
        # end
    # end

    async def is_valid_user_id(self, userId: int) -> bool:
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
        except discord.NotFound or discord.HTTPException:
            # the id was not valid
            return False
        # end
    # end

    async def get_user_by_id(self, userId: int) -> discord.User | None:
        """
        Fetches a user account by id.

        Arguments:
            userid (str): The user id of the user you want to get.

        Returns:
            A discord user object or none if the user is invalid or could not be reached.
        """

        try:
            return await self.bot.fetch_user(userId)

        except discord.NotFound or discord.HTTPException:
            return None
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
    async def settings_set(self, ctx: commands.Context, settingSection: str | None=None, setting: str | None=None, value: str | None=None):
        """
        Updates the given setting with the given value.

        Useage: set <section> <setting> <value>

        Arguments:
            section: The settings section that contains the option you want to change.
            setting: The name of the setting to change.
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
        if settingSection == "PARENT VIDEO PATH" and setting == "path":
            # user wants to change the parent path where videos are downloaded to

            # make sure the given dirpath is valid
            if value != sanitize_filepath(value):
                # given file path is not valid
                await ctx.send("File path is not valid.")
                return
            # end

            # update the path setting
            update_config("config.ini", "PARENT VIDEO PATH", "path", value=value)

            await ctx.send("path was updated to " + value)

        # make sure the user can't edit the admins list through the settings command
        elif settingSection == "ADMIN" and setting == "admins":
            # user is trying to update the admins list using the settings command

            # tell the user they need to use the admins command to update the admins list
            await ctx.send("You can only change this setting using the !admins commands.")
            return

        else:
            if update_config("config.ini", settingSection, setting, value=value):
                await ctx.send(f"{settingSection} {setting} updated to {value}.")
            else:
                await ctx.send("Invalid config parameters.")
            # end
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

    @settings.command(name="export")
    async def settings_export(self, ctx: commands.Context):
        """Exports the config file."""
    
        # check if the config file exists
        if not os.path.exists("config.ini"):
            await ctx.send("Config file could not be found.")
            return
        # end

        # send the config file to the user
        await ctx.author.send(file=discord.File("config.ini"))
        await ctx.send("Config file was sent in a DM.")
    # end

    @settings.command(name="import")
    async def settings_import(self, ctx: commands.Context):
        """Imports the given config file."""
    
        # check if the user uploaded a file
        if not ctx.message.attachments:
            # the user did not upload any files
            await ctx.send_help(ctx.command)
            return
        # end

        # try to download the given file
        try:
            # open a temp config file
            with open("temp_config.ini", "wb") as writer:
                # download first attachment
                await ctx.message.attachments[0].save(writer)
            # end

            # check if config schemas match
            if not validate_schema(self.defaultConfig, "temp_config.ini"):
                # schemas don't match, reject given config file
                os.remove("temp_config.ini")
                await ctx.send("Config schema doesn't match. Setings not imported.")
                return
            # end

            # config schemas match. Override config file with given file
            os.remove("config.ini")
            os.rename("temp_config.ini", "config.ini")

            await ctx.send("Settings imported.")

        except Exception as e:
            await ctx.send(f"Failed to save {ctx.message.attachments[0].filename} because of an error: {e}")
        # end
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
            profile: A mention or user ID to add to the admins list.
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
        if not await self.is_valid_user_id(int(memberId)):
            await ctx.send(f"{memberName} is not a valid user.")
            return
        # end

        # get the current admins list
        admins = get_list_config("config.ini", "ADMIN", "admins")

        # make sure config file was read successfully
        if admins is None:
            # config file was not read successfully

            # tell the user the command failed
            await ctx.send(f"Failed to add {memberName} to the admins list. Could not read config file.")
            return
        # end

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
            # failed to update the config file
            await ctx.send(f"Failed to add {memberName} to the admins list.")
            return
        # end
    # end

    @admins.command(name="remove")
    async def admins_remove(self, ctx: commands.Context, userId: int | None=None):
        """
        Removes a profile from the admins list.
        
        Usage: remove <id>

        Arguments:
            id: The user id to remove from the admins list.
        """
    
        # check if an id was given
        if userId is None:
            await ctx.send_help(ctx.command)
        # end

        # get the list of admins
        admins = get_list_config("config.ini", "ADMIN", "admins")

        # check if config was read successfully
        if admins is None:
            # config file was not not read
            await ctx.send("There was an error reading the config file.")
            return
        # end

        # check if given id is in the admins list
        if not str(userId) in admins:
            # the given user is not on the admins list
            await ctx.send("This user is not on the admins list.")
            return
        # end

        # remove given user form the admins list
        admins.remove(str(userId))
        await ctx.send(f"{userId} was removed from the admins list.")
    # end

    @admins.command(name="list")
    async def admins_list(self, ctx: commands.Context):
        """Lists lists everyone on the admin list."""
    
        # get the admins list from config file
        admins = get_list_config("config.ini", "ADMIN", "admins")
        # admins is a list of user ids

        # check if admins list was read successfully
        if admins is None:
            # config file was not read form successully
            await ctx.send("There was an error reading the config file.")
            return
        # end

        # check if admins list is empty
        if len(admins) == 0:
            # the admins list is empty

            # tell the user there are no registered admins
            await ctx.send("There is no one on the admins list.")
            return
        # end

        # fetch the user object of each admin
        users = [await self.get_user_by_id(int(admin)) for admin in admins]
        # get the length of the longest user name for formatting
        colWidth = max([len(user.display_name) for user in users if user is not None])

        # display the list of admins
        displayString = []
        for i in range(len(admins)):
            # declare user variable to make type checker calm down
            user = users[i]

            # check if user was fetched successfully
            if user is None:
                # user was not fetched
                displayString.append(f"{i} Error fetching user with id: {admins[i]}")
                continue
            # end

            # add addmin user information to display string list
            displayString.append(f"{user.display_name.ljust(colWidth)} ID: {admins[i]}")
        # end

        # display admins list
        await ctx.send(f"# Admins\n```{"\n".join(displayString)}```")
    # end
# end


async def setup(bot: commands.Bot):
    await bot.add_cog(Settings(bot=bot))
# end


if __name__ == "__main__":
    print(list("[1, 2, 3, 4]"))
# end