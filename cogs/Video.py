from discord.ext import commands
from os import getcwd
from config_getter_setter import Config
from urllib.parse import urlparse, parse_qs
import re, os, yt_dlp, requests

async def is_valid_video_url(videoUrl: str) -> bool:
    """
    Checks if the given YouTube video url is valid.
    
    Arguments:
        videoUrl (str): Url to validate.

    Returns:
        True if the url is valid or false if not.
    """

    # try:
    #     ydl_opts: yt_dlp._Params = {
    #         "cookiefile": "cookies.txt",
    #         'quiet': True,       # Suppress normal output
    #         'skip_download': True
    #     }

    #     with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    #         info = ydl.extract_info(videoUrl, download=False)
    #         # Check if it's a video (not just a playlist or channel)
    #         if info.get('_type') == 'video' or 'formats' in info:
    #             return True
    #         else:
    #             return False
    # except Exception:
    #     return False

    
    try:
        parsed = urlparse(videoUrl)
    except Exception:
        return False

    # Accept both full and short URLs
    if parsed.netloc not in {
        "www.youtube.com",
        "youtube.com",
        "youtu.be",
    }:
        return False

    # Normalize short URLs
    if parsed.netloc == "youtu.be":
        video_id = parsed.path.lstrip("/")
        if not video_id:
            return False
        url = f"https://www.youtube.com/watch?v={video_id}"
        parsed = urlparse(url)

    # Must be a watch URL with a video id
    if parsed.path != "/watch":
        return False

    if "v" not in parse_qs(parsed.query):
        return False

    try:
        resp = requests.get(
            videoUrl,
            allow_redirects=True,
            headers={
                "User-Agent": "Mozilla/5.0"
            },
        )
    except requests.RequestException:
        return False

    if resp.status_code != 200:
        return False

    final = urlparse(resp.url)

    # YouTube redirects invalid videos to search/home
    if final.path in {"/", "/results", "/oops"}:
        return False

    # Valid videos always end on /watch
    return final.path == "/watch"

# end


async def download_video(videoUrl: str, downloadDir: str, quality: int=360) -> bool:
    """
    Downloads the given YouTube video

    Arguments:
        videoUrl (str): The url of the video you want to download.
        quality (str): The quality to download the given video at e.g. 360p

    Returns:
        True if the video was downloaded or false if there was a problem.
    """

    try:
        with yt_dlp.YoutubeDL(
            {
                "cookiefile": "cookies.txt",
                
                "format": (
                    f"bestvideo[height<={quality}]+bestaudio/"
                    f"best[height<={quality}]"
                ),

                'outtmpl': os.path.join(downloadDir, '%(title)s.%(ext)s'),
            }
        ) as ydl:
            ydl.download([videoUrl])

    except Exception:
        return False
    # end

    return True
# end


class Video(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.configs = Config()
    # end

    @commands.group(name="video", invoke_without_command=True)
    async def video(self, ctx: commands.Context):
        """Manages downloaded videos."""
        
        await ctx.send_help(ctx.command)
    # end

    @video.command(name="download")
    async def video_download(self, ctx: commands.Context, url: str | None=None, quality: str="360p"):
        """
        Downloads a YouTube video at the given url.

        Useage: download <url> [quality]
        
        Arguments:
            url: The url of the video you want to download.
            quality: The quality to download the video at e.g. 360p. Defaults to 360p.
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

        # regex patter to only match video quality format e.g. 1080p
        qualityPattern = re.compile(r"^(144|360|720|1080|1440|2160)p$")
        # make sure quality is valid if given
        if quality is not None and (not bool(qualityPattern.search(quality))):
            await ctx.send("Invalid video quality.")
            return
        # end

        # make sure parent download directoriy still exsit
        if not os.path.exists(self.configs.get_parent_download_path()):
            await ctx.send("Could not find parent download directory.")
            return
        # end

        # create misc. video directory if it doesn't exist
        if not os.path.exists(f"{self.configs.get_parent_download_path()}/Misc."):
            # create misc. videos directory
            os.mkdir(f"{self.configs.get_parent_download_path()}/Misc.")
        # end

        await ctx.send("Downloading video.")

        # try to download video
        try:
            if not await download_video(videoUrl=url, downloadDir=f"{self.configs.get_parent_download_path()}/Misc.", quality=int(quality.rstrip("p"))):
                await ctx.send("Could not download video.")
                return
            # end

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