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

        # default config options
        defaultConfig = configparser.ConfigParser()
        defaultConfig[self._parent_video_path] = {"path": "YouTube"}
        defaultConfig[self._admin] = {"bot token": "", "admins": "", "requesters": ""}

        # check if a config file exists
        if not os.path.exists(self.fileName):
            # config file does not exist

            # write template config to file
            with open("config.ini", "w") as writer:
                defaultConfig.write(writer)
            # end

        self._parser = configparser.ConfigParser()
        self._parser.read(self.fileName)

        # check for missing sections
        currentSections = self._parser.sections()
        for defaultSection in defaultConfig.sections():
            if not defaultSection in currentSections:
                # section is not in this config file
                
                # add the default section
                self._parser[defaultSection] = defaultConfig[defaultSection]

            else:
                # this section is in the config file

                # make sure all settings are in this section
                for option in defaultConfig[defaultSection].keys():
                    if not option in self._parser[defaultSection].keys():
                        # this setting is not in this section

                        # add this setting to this section
                        self._parser[defaultSection][option] = defaultConfig[defaultSection][option]
                    # end
                # end
            # end
        # end

        # save any changes that may have happened
        with open(self.fileName, "w") as writer:
            self._parser.write(writer)
        # end
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
    def get_sections(self) -> list[str]:
        """Gets all sections in the config file as a list."""
        
        return self._parser.sections()
    # end

    @sync
    def get_requesters(self) -> list[int]:
        """Gets the list of discord users that are allowed to request downloads. Returns list[int]"""

        requesters = self._parser[self._admin]["requesters"]

        return [int(requester) for requester in requesters if not requester == ""]
    # end

    @sync
    def set_requesters(self, requesters: list[int]):
        """
        Updates the list of discords users that are allowed to make download requests.

        Arguments:
            requesters (list[int]): A list of discord id's.
        """

        self._parser.set(self._admin, option="requesters", value=",".join(str(requesters)))
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
        return [int(admin) for admin in admins if admin != ""]
    # end    
# end


if __name__ == "__main__":
    config = Config()

    print(config.get_all_option_names())
    print(config.get_all_option_values())
# end
