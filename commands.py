import asyncio
from discord.ext import commands
from discord_slash import cog_ext, SlashContext, ComponentContext
from discord_slash.utils.manage_commands import create_option
from discord_slash.utils.manage_components import (
    create_actionrow,
    create_button,
    ButtonStyle,
)
import os
import aiohttp
from random import choice, shuffle
import discord
from cachetools import TTLCache

search = TTLCache(200, 1800)
vid = TTLCache(200, 1800)
channel = TTLCache(200, 1800)
http = aiohttp.ClientSession()
from humanize import intword

class YouTube(commands.Cog):
    """Youtube Commands"""

    def __init__(self, bot):
        self.bot = bot
        self.cq = {}

    async def search_for(self, query: str):
        if query in search:
            return search[query]

        querystring = {
            "q": query,
            "part": "snippet,id",
            "regionCode": "US",
            "maxResults": "5",
        }

        headers = {
            "x-rapidapi-host": "youtube-v31.p.rapidapi.com",
            "x-rapidapi-key": os.environ["apikey"],
        }

        resp = await http.get(
            "https://youtube-v31.p.rapidapi.com/search",
            headers=headers,
            params=querystring,
        )
        r = await resp.json()
        if resp.status == 400 or resp.status == 500:
            search[query] = r["items"]
        return r

    async def video_info(self, id: str):
        if id in vid:
            return vid[id]

        querystring = {"part": "snippet,statistics,contentDetails", "id": id}

        headers = {
            "x-rapidapi-host": "youtube-v31.p.rapidapi.com",
            "x-rapidapi-key": os.environ["apikey"],
        }

        resp = await http.request(
            "GET",
            "https://youtube-v31.p.rapidapi.com/videos",
            headers=headers,
            params=querystring,
        )
        r = await resp.json()
        vid[id] = r["items"][0]
        return vid[id]

    async def channel_info(self, id: str):
        if id in channel:
            return channel[id]

        querystring = {"part": "snippet,statistics,contentDetails", "id": id}

        headers = {
            "x-rapidapi-host": "youtube-v31.p.rapidapi.com",
            "x-rapidapi-key": os.environ["apikey"],
        }

        resp = await http.request(
            "GET",
            "https://youtube-v31.p.rapidapi.com/channels",
            headers=headers,
            params=querystring,
        )
        r = await resp.json()
        channel[id] = r["items"][0]
        return channel[id]

    @cog_ext.cog_slash(
        name="search",
        description="Search Youtube for your provided keyword",
        options=[create_option("query", "What to search for", str, True)],
    )
    async def search(self, ctx: SlashContext, *, query: str):
        searchdata = await self.search_for(query)
        embed = discord.Embed(color=discord.Color.red())
        embed.set_author(name="Your Search", icon_url=ctx.author.avatar_url)
        for n, res in enumerate(searchdata["items"]):
            embed.add_field(
                name=f"{n+1}. {res['snippet']['title']}"
                + f"- {res['snippet']['channelTitle']}"
                if res["snippet"]["channelTitle"] != res["snippet"]["title"]
                else f"{n+1}. {res['snippet']['title']}",
                value=res["snippet"]["description"] or "No description",
            )
            if res["kind"] == "youtube#channel":
              embed.set_thumbnail(url=res["snippet"]["thumbnails"]["medium"]["url"])
              break
            else:
                embed.set_thumbnail(
                    url=choice(searchdata["items"])["snippet"]["thumbnails"]["medium"][
                        "url"
                    ]
                )
        buttons = [
            create_button(
                style=ButtonStyle.red,
                label=f"Option #{i+1}",
                custom_id=d["id"][list(d["id"])[1]],
            )
            for i, d in enumerate(searchdata["items"])
        ]
        action_row = create_actionrow(*buttons)

        m = await ctx.send(embed=embed, components=[action_row])
        self.cq[m.id] = query

    @commands.Cog.listener()
    async def on_component(self, ctx: ComponentContext):
        if ctx.custom_id == "back":
            searchdata = await self.search_for(self.cq[ctx.origin_message.id])
            embed = discord.Embed(color=discord.Color.red())
            embed.set_author(name="Your Search", icon_url=ctx.author.avatar_url)
            for n, res in enumerate(searchdata["items"]):
                embed.add_field(
                    name=f"{n+1}. {res['snippet']['title']}"
                    + f"- {res['snippet']['channelTitle']}"
                    if res["snippet"]["channelTitle"] != res["snippet"]["title"]
                    else f"{n+1}. {res['snippet']['title']}",
                    value=res["snippet"]["description"] or "No description",
                )
                if res["kind"] == "youtube#channel":
                    embed.set_thumbnail(
                        url=res["snippet"]["thumbnails"]["medium"]["url"]
                    )
                    break

            buttons = [
                create_button(
                    style=ButtonStyle.red,
                    label=f"Option #{i+1}",
                    custom_id=d["id"][list(d["id"])[1]],
                )
                for i, d in enumerate(searchdata["items"])
            ]
            action_row = create_actionrow(*buttons)

            m = await ctx.edit_origin(embed=embed, components=[action_row])
            return

        item = await self.search_for(ctx.custom_id)
        item = item["items"][0]
        embed = discord.Embed(
            description=item["snippet"]["description"] or "No description",
            color=discord.Color.red(),
        )
        embed.set_author(name=item["snippet"]["title"])
        embed.set_thumbnail(url=item["snippet"]["thumbnails"]["medium"]["url"])
        if "video" in item["id"]["kind"]:
            v = await self.video_info(ctx.custom_id)
            vc = intword(v["statistics"]["viewCount"])
            embed.set_footer(
                text=f"👁️ {vc} • 👍 {intword(v['statistics']['likeCount'])} • 💬 {intword(v['statistics']['commentCount'])} • Video by {v['snippet']['channelTitle']}"
            )
            buttons = [
                create_button(
                    style=ButtonStyle.red, label=f"Back", custom_id="back", emoji="⬅️"
                )
            ]
            await ctx.edit_origin(embed=embed, components=[create_actionrow(*buttons)])
        elif "channel" in item["id"]["kind"]:
            v = await self.channel_info(ctx.custom_id)
            vc = intword(v["statistics"]["viewCount"])
            embed.set_footer(
                text=f"👁️ {vc} views • 💓 {intword(v['statistics']['subscriberCount'])} subscribers • ▶️ {intword(v['statistics']['videoCount'])} videos"
            )
            buttons = [
                create_button(
                    style=ButtonStyle.red, label=f"Back", custom_id="back", emoji="⬅️"
                )
            ]
            await ctx.edit_origin(embed=embed, components=[create_actionrow(*buttons)])


def setup(bot):
    bot.add_cog(YouTube(bot))
