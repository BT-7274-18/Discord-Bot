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
            raise FileNotFoundError
        # end

        # stroing section names in attribute so they can be easily changed 
        # and renamed later if needed
        self._parent_video_path = "PARENT VIDEO PATH"
        self._admin = "ADMIN"

        self._parser = configparser.ConfigParser()
        self._parser.read(self.fileName)
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
    def set_admin_list(self, value: list):
        self._parser.set(section=self._admin, option="admins", value=",".join(value))
    # end
    
    @sync
    def get_admin_list(self) -> list:
        admins = self._parser.get(section=self._admin, option="admins").split(",")

        # remove empty strings incase option is empty
        admins = [admin for admin in admins if admin != ""]

        return admins
    # end    
# end


if __name__ == "__main__":
    config = Config()
# end
