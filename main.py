from discord.ext import commands
import discord, asyncio, os


BOT_TOKEN = ""
CHANNEL_ID = 1488359282859708600

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

async def load_extensions(client: commands.Bot):
    """Loads all cogs in the cog folder."""

    for cog in [file[:-3] for file in os.listdir("cogs")[1:]]:
        await client.load_extension(f"cogs.{cog}")
    # end
# end


@bot.event
async def on_ready():
    print("Hello! Ready to go!")
    # get the provided discord channel object
    channel = bot.get_channel(CHANNEL_ID)
    # await channel.send("Hello! Ready to go!")
# end


@bot.command()
async def reload(ctx: commands.Context, arg: str=""):
    """Reloads the given cog or all cogs if none are given."""

    if arg == "":
        # no cog was provided, reload all cogs
        for cog in [file[:-3] for file in os.listdir("cogs")[1:]]:
            await bot.reload_extension(f"cogs.{cog}")
        # end

        # tell the user all cogs were reloaded
        await ctx.send("All cogs reloaded.")

    else:
        try:
            # reload the given cog
            if os.path.exists(f"cogs/{arg}.py"):
                # given cog is valid

                # reload cog
                await bot.reload_extension(f"cogs.{arg}")
                # tell the user the cog was reloaded
                await ctx.send(f"{arg} reloaded.")
            
            else:
                # given cog is not valid

                # tell user the given cog is not valid
                await ctx.send(f"{arg} is not a valid cog.")
            # end

        except commands.ExtensionNotLoaded as e:
            await ctx.send(f"There was an error loading {arg}: {e}")
    # end
# end


if __name__ == "__main__":
    # print(get_channels())
    # start the discord bot
    
    asyncio.run(load_extensions(bot))
    bot.run(BOT_TOKEN)
