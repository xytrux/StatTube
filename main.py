from discord.ext import commands
from discord_slash import SlashCommand
import aiohttp
import os
from cachetools import TTLCache
from keep_alive import keep_alive

bot = commands.Bot(command_prefix=commands.when_mentioned_or("s!"))
http = aiohttp.ClientSession()
slash = SlashCommand(
    bot, sync_commands=True, sync_on_cog_reload=True, debug_guild=846429112608620616
)


@bot.event
async def on_ready():
    await slash.sync_all_commands()
    print("Yes!")


search = TTLCache(200, 1800)
keep_alive()
bot.load_extension("jishaku")
bot.load_extension("commands")
bot.run(os.environ["token"])
