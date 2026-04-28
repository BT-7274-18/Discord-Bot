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

        if not os.path.exists("config.ini"):
            raise FileNotFoundError("No config file found.")
        # end

        self._schema = {
            "PARENT VIDEO PATH":{
                "aliases": ["PARENT VIDEO PATH"],
                "keys": {
                    "path": {
                        "aliases": ["path"],
                        "set function": self.set_parent_download_path,
                        "get function": self.get_parent_download_path
                    }
                }
            },
            "ADMIN": {
                "aliases": ["ADMIN"],
                "keys": {
                    "bot token": {
                        "aliases": ["bot token"],
                        "set function": self.set_bot_token,
                        "get function": self.get_bot_token,
                    },
                    "admins": {
                        "aliases": ["admins"],
                        "set function": self.set_admin_list,
                        "get function": self.get_admin_list
                    }
                }
            }
        }

        # stroing section names in attribute so they can be easily changed 
        # and renamed later if needed
        self._parent_video_path = "PARENT VIDEO PATH"
        self._admin = "ADMIN"

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
        return self._parser.sections()
    # end

    @sync
    def get_section_options(self, section: str):
        return self._parser[section].keys()
    # end

    @sync
    def get_all_options(self) -> list[str]:
        return [option for section in self._parser.sections() for option in self._parser[section].keys()]
    # end
    
    @sync
    def set_parent_download_path(self, value: str):
        self._parser.set(section=self._parent_video_path, option="path", value=value)
    # end

    @sync
    def get_parent_download_path(self) -> str:
        return self._parser.get(section=self._parent_video_path, option="path")
    # end

    @sync
    def set_bot_token(self, value: int):
        self._parser.set(section=self._admin, option="bot token", value=str(value))
    # end

    @sync
    def get_bot_token(self) -> int:
        return int(self._parser.get(section=self._admin, option="bot token"))
    # end

    @sync
    def set_admin_list(self, value: list[int]):
        self._parser.set(section=self._admin, option="admins", value=",".join(str(value)))
    # end
    
    @sync
    def get_admin_list(self) -> list[int]:
        admins = self._parser.get(section=self._admin, option="admins").split(",")

        # remove empty strings and convert non-empty strings to integers
        admins = [int(admin) for admin in admins if admin != ""]

        return admins
    # end    
# end


if __name__ == "__main__":
    config = Config()

    print(config.get_all_options())
# end
