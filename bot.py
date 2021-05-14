import discord
from discord import guild
from discord.ext import commands
import json

prefixes = ['!']
token = '{insertYourToken}'

client = commands.Bot(command_prefix=prefixes, Intents=discord.Intents.all)

@client.event
async def on_ready():
    print("Shareify is ready!")

@client.event
async def on_message(message):
    message.content = message.content.replace("\'", "\\'").replace('\"', '\\"')
    await client.process_commands(message)

@client.command()
async def share(ctx: commands.context, *args):
    guild_id = str(ctx.guild.id)

    with open('config.json', 'r') as f:
        config = json.load(f)

    if guild_id not in config or not config[guild_id]:
        await ctx.send("Invalid Sharing Channel")
    
    channel = ctx.guild.get_channel(config[guild_id])

    if not channel:
        await ctx.send("Could not find Sharing Channel")
        return

    author = ctx.message.author.mention
    share_message = f"{author} shared something:\n{' '.join(args)}"
    if not ctx.message.attachments:
        await channel.send(share_message)
    else:
        attachment = await ctx.message.attachments[0].to_file()
        await channel.send(share_message, file=attachment)


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

    with open('config.json', 'r') as f:
        config = json.load(f)

    config[guild_id] = channel_id
    with open('config.json', 'w') as f:
        f.write(json.dumps(config, indent=4))
    await ctx.send(f"Sharing channel has been set to: {channel.mention}")
    return
    
client.run(token)