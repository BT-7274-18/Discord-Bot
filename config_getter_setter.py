import configparser
import os


def sync(func):
    """Updates the parser before getting or setting values and writes changes afterwards."""

    def wrapper(self, *args, **kwargs):
        # update the parser
        self._parser.read("config.ini")

        # call class method
        res = func(self, *args, **kwargs)

        # save changes
        with open("config.ini", "w") as writer:
            self._parser.write(writer)
        # end

        return res
    # end
    return wrapper
# end


class Config:
    def __init__(self):
        self.fileName = "config.ini"
        # stroing section names in attribute so they can be easily changed 
        # and renamed later if needed
        self._parent_video_path = "PARENT VIDEO PATH"
        self._admin = "ADMIN"

        # check if a config file exists
        if not os.path.exists(self.fileName):
            # config file does not exist

            # create a new config file from template
            defaultConfig = configparser.ConfigParser()
            defaultConfig[self._parent_video_path] = {"path": "YouTube"}
            defaultConfig[self._admin] = {"bot token": "", "admins": ""}

            # write template config to file
            with open("config.ini", "w") as writer:
                defaultConfig.write(writer)
            # end
        # end

        self._parser = configparser.ConfigParser()
        self._parser.read(self.fileName)
    # end

    @sync
    def get_setting(self, section: str, setting: str) -> str:
        """
        Get's the value at the given section setting pair.

        Arguments:
            section (str): The name of the section that contains the given setting.
            setting (str): The name of the setting you want the value of.

        Returns:
            The value at the given section setting pair.

        Raises:
            KeyError if the given section or setting names are not in the config file.
        """

        # check if given section is valid
        if section not in self._parser.sections():
            # given section is not valid
            raise KeyError("Invalid section.")
        # end

        # check if given key is valid
        if setting not in self._parser[section].keys():
            # given key is not valid
            raise KeyError("Invalid setting.")
        # end

        # section and key are valid
        return self._parser.get(section=section, option=setting)
    # end

    @sync
    def set_setting(self, section: str, setting: str, value: str):
        """
        Updates a value at the given section setting pair.

        Arguments:
            section (str): The name of the section that contains the setting you want to update.
            setting (str): The name of the setting you want to update.
            value (str): The value you want to change the given setting to.

        Raises:
            KeyError if the given section or setting names are not in the config file.
        """

        # check if given section if valid
        if not section in self._parser.sections():
            # given section is not valid
            raise KeyError("Invalid section.")
        # end

        # check if given setting is valid
        if not setting in self._parser[section].keys():
            # given setting is not valid
            raise KeyError("Invalid setting.")
        # end

        # section and setting pair is valid
        self._parser.set(section=section, option=setting, value=value)
    # end

    @sync
    def get_sections(self) -> list[str]:
        """Gets all sections in the config file as a list."""
        
        return self._parser.sections()
    # end

    @sync
    def get_section_options(self, section: str) -> list[str]:
        """Gets a list of all option names in a section as a list."""

        return list(self._parser[section].keys())
    # end

    @sync
    def get_all_option_names(self) -> list[str]:
        """Gets all option names as a list."""

        return [option for section in self._parser.sections() for option in self._parser[section].keys()]
    # end

    @sync
    def get_all_option_values(self) -> list[str]:
        """Gets all option values as a list."""

        return [self._parser[section][key] for section in self._parser.sections() for key in self._parser[section].keys()]
    # end
    
    @sync
    def set_parent_download_path(self, value: str):
        """
        Sets the parent download path of YouTube videos.

        Arguments:
            value (str): The directory path YouTube videos should be stored.
        """

        self._parser.set(section=self._parent_video_path, option="path", value=value)
    # end

    @sync
    def get_parent_download_path(self) -> str:
        """Gets the current parent download path of YouTube videos."""

        return self._parser.get(section=self._parent_video_path, option="path")
    # end

    @sync
    def set_bot_token(self, value: str):
        """
        Sets the current bot token.

        Arguments:
            value (str): The value to update the bot token option to.
        """

        self._parser.set(section=self._admin, option="bot token", value=value)
    # end

    @sync
    def get_bot_token(self) -> str:
        """Gets the current bot token."""

        return self._parser.get(section=self._admin, option="bot token")
    # end

    @sync
    def set_admin_list(self, value: list[int]):
        """
        Updates the list of admins.

        Arguments:
            value (list[str]): A list of discord user id's.
        """

        self._parser.set(section=self._admin, option="admins", value=",".join(str(value)))
    # end
    
    @sync
    def get_admin_list(self) -> list[int]:
        """Gets the current list of admins as a list of discord user id's."""

        admins = self._parser.get(section=self._admin, option="admins").split(",")

        # remove empty strings and convert non-empty strings to integers
        admins = [int(admin) for admin in admins if admin != ""]

        return admins
    # end    
# end


if __name__ == "__main__":
    config = Config()

    print(config.get_all_option_names())
    print(config.get_all_option_values())
# end
