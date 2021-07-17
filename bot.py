import discord
from discord.ext import commands, tasks

import os
from replit import db
import re
from random import choice

from keep_alive import keep_alive
token = os.environ['BOT_TOKEN']

client = commands.Bot(command_prefix="s!", case_insensitive=True, Intents=discord.Intents.all)

statuses = [
    "with s!help",
    "with Slash Commands",
    "with your creations",
    "with sharing channels",
    "with Discord"
]

@tasks.loop(seconds=30)
async def change_status():
    await client.change_presence(activity=discord.Game(choice(statuses)))

@client.event
async def on_ready():
    change_status.start()
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="s!help"))
    print("Shareify is ready!")

@client.event
async def on_message(message):
    if client.user in message.mentions:
        await message.reply("You can type s!help for a list of all commands")
    message.content = message.content.replace("\'", "\\'").replace("\"", "\\\"")
    await client.process_commands(message)

client.remove_command('help')
@client.command()
async def help(ctx: commands.context):
    embed=discord.Embed(title="Shareify Help", description="Use `s!channel` to set a sharing channel, and `s!share` to share your creations!", color=0x7289da)
    embed.add_field(name='\u200b', value='\u200b', inline=False)
    embed.add_field(name="!share", value="Use `s!share <title|link>` and attach a file to share it in the sharing channel.", inline=True)
    embed.add_field(name="s!channel", value="Use `s!channel <#channel>` to set a sharing channel", inline=True)
    embed.add_field(name='\u200b', value='\u200b', inline=False)
    embed.add_field(name="s!help", value="Shows this message", inline=True)
    embed.add_field(name="s!ping", value="Checks the bot's latency", inline=True)
    await ctx.send(embed=embed)

@client.command()
async def share(ctx: commands.context, *args):
    guild_id = str(ctx.guild.id)

    if guild_id not in db:
        await ctx.send("Invalid Sharing Channel")
        return
    
    if not db[guild_id]:
        await ctx.send("Invalid Sharing Channel")
        return

    channel = ctx.guild.get_channel(db[guild_id])

    if not channel:
        await ctx.send("Could not find Sharing Channel")
        return

    author = ctx.message.author  
    input_message = " ".join(args)

    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    if re.findall(regex, ctx.message.content):
        share_message = f"Project by: {author.mention}\n{input_message}"
        if not ctx.message.attachments:
            await channel.send(share_message)
        else:
            attachment = await ctx.message.attachments[0].to_file()
            await channel.send(share_message, file=attachment)
    else:
        embed=discord.Embed(title=f"**{input_message}**")
        embed.set_author(name=f"Project by {author}", icon_url=author.avatar_url)
        if ctx.message.attachments:
            embed.set_image(url=ctx.message.attachments[0].url)
        await channel.send(embed=embed)

@client.command()
async def channel(ctx: commands.context, channel: discord.TextChannel):
    if not ctx.message.author.guild_permissions.manage_channels:
        await ctx.send("You need the 'Manage Channels' permission to use this command.")
        return

    if type(channel) is not discord.TextChannel:
        await ctx.send('Invalid Channel')
        return
    channel_id = channel.id
    guild_id = str(ctx.guild.id)

    db[guild_id] = channel_id
    await ctx.send(f"Sharing channel has been set to: {channel.mention}")
    return

@client.command()
async def ping(ctx):
    await ctx.send(f"Pong! in {round(client.latency * 1000)}ms")

keep_alive()
client.run(token)