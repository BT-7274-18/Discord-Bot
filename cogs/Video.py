from discord.ext import commands
from pathvalidate import sanitize_filepath
from pytubefix import AsyncYouTube
from os import getcwd


async def is_valid_video_url(videoUrl: str) -> bool:
    """
    Checks if the given YouTube video url is valid.
    
    Arguments:
        videoUrl (str): Url to validate.

    Returns:
        True if the url is valid or false if not.
    """

    # try to fetch video metadata
    try:
        AsyncYouTube(videoUrl)
        return True
    
    except Exception:
        return False
    # end
# end


async def download_video(videoUrl: str) -> bool:
    """
    Downloads the given YouTube video

    Arguments:
        videoUrl (str): The url of the video you want to download.

    Returns:
        True if the video was downloaded or false if there was a problem.
    """

    yt = AsyncYouTube(videoUrl, use_oauth=True, allow_oauth_cache=True)

    streams = await yt.streams()
    stream = streams.filter(progressive=True).get_lowest_resolution()

    if stream is None:
        return False
    # end

    stream.download(getcwd(), stream.title)

    return True
# end


class Video(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    # end

    @commands.group(name="video", invoke_without_command=True)
    async def video(self, ctx: commands.Context):
        """Manages downloaded videos."""
        
        await ctx.send_help(ctx.command)
    # end

    @video.command(name="download")
    async def video_download(self, ctx: commands.Context, url: str | None=None, dir: str | None=None):
        """
        Downloads a YouTube video at the given url.

        Useage: download <url> [dir]
        
        Arguments:
            url: The url of the video you want to download.
            dir: The directory the video should be downloaded to.
        """
    
        # make sure the user provides a url
        if url is None:
            await ctx.send_help(ctx.command)
            return
        # end

        # make sure the given url is valid
        if not await is_valid_video_url(url):
            await ctx.send("Video url is invalid.")
            return
        # end

        await ctx.send("Downloading video.")

        try:
            await download_video(url)

        except Exception as e:
            await ctx.send("Could not download video.")

            print(f"Error downloading video: {e}")
            return
        # end

        await ctx.send("Finished downloading video.")
    # end
# end


async def setup(bot: commands.Bot):
    await bot.add_cog(Video(bot=bot))
# end


if __name__ == "__main__":
    pass
# end 