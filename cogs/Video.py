from discord.ext import commands
from pathvalidate import sanitize_filename
from pytubefix import AsyncYouTube
from os import getcwd
import re, ffmpeg, os

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


async def download_video(videoUrl: str, downloadDir: str | None=None, quality: str="360p") -> bool:
    """
    Downloads the given YouTube video

    Arguments:
        videoUrl (str): The url of the video you want to download.
        quality (str): The quality to download the given video at e.g. 360p

    Returns:
        True if the video was downloaded or false if there was a problem.
    """

    # get youtube video object
    yt = AsyncYouTube(videoUrl, use_oauth=True, allow_oauth_cache=True, )

    # get the streams avalible for this video
    streams = await yt.streams()

    # get the video stream for this video
    video = streams.filter(
        adaptive=True,
        res=quality,
        mime_type="video/mp4"
    ).first()
    # get the audio stream for this video
    audio = streams.filter(
        adaptive=True,
        only_audio=True
    ).order_by("abr").desc().first()

    # make sure audio and video were fetched successfully
    if video is None or audio is None:
        return False
    # end

    # get the title of the video
    title = video.title

    # download audio and video streams
    videoPath = video.download(downloadDir if downloadDir is not None else getcwd(), f"{sanitize_filename(title)} video only.mp4")
    audioPath = audio.download(downloadDir if downloadDir is not None else getcwd(), f"{sanitize_filename(title)} audio only.mp4")

    # make sure audio and video files were downloaded
    if videoPath is None or audioPath is None:
        return False

    # merge audio and video files
    try:
        inputVideo = ffmpeg.input(videoPath)
        inputAudio = ffmpeg.input(audioPath)

        ffmpeg.concat(inputVideo, inputAudio, v=1, a=1).output(f"{downloadDir}/{title}.mp4").run(quiet=True)

    except ffmpeg.Error:
        os.remove(videoPath)
        os.remove(audioPath)
        return False
    # end

    # remove temp files
    os.remove(videoPath)
    os.remove(audioPath)

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
    async def video_download(self, ctx: commands.Context, url: str | None=None, dir: str | None=None, quality: str | None=None):
        """
        Downloads a YouTube video at the given url.

        Useage: download <url> [dir] 
        
        Arguments:
            url: The url of the video you want to download.
            dir: The directory the video should be downloaded to.
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

        # make sure download dir is valid if given
        if dir is not None and (not os.path.exists(dir) or not os.path.isdir(dir)):
            await ctx.send("Invalid download directory.")
            return
        # end

        # regex patter to only match video quality format e.g. 1080p
        qualityPattern = re.compile(r"^(144|360|720|1080|1440|2160)p$")
        # make sure quality is valid if given
        if quality is not None and (not bool(qualityPattern.search(quality))):
            await ctx.send("Invalid video quality.")
            return
        # end

        await ctx.send("Downloading video.")

        # try to download video
        try:
            await download_video(videoUrl=url, downloadDir=dir, quality=quality if quality is not None else "360p")

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