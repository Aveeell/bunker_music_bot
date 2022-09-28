import discord
import config
from bot_token import TOKEN
from discord.ext import commands
from youtube_dl import YoutubeDL


bot = commands.Bot(command_prefix='!')
query = []


async def check_domains(src):
    for i in config.DOMAINS:
        if src.startswith(i):
            return True
    return False


def play_next(context, songs_query):
    print('PLAY_NEXT')
    if len(songs_query) != 0:
        voice = discord.utils.get(bot.voice_clients, guild=context.guild)
        with YoutubeDL(config.YOUTUBE_OPTIONS) as youtube_download:
            try:
                info = youtube_download.extract_info(songs_query[0], download=False)
            except:
                info = youtube_download.extract_info(songs_query[0], download=False)
        url = info['formats'][0]['url']
        if len(songs_query) != 0:
            songs_query.pop(0)
        voice.play(discord.FFmpegPCMAudio(source=url, **config.FFMPEG_OPTIONS), after=lambda x: play_next(context, songs_query))


@bot.event
async def on_ready():
    print('bot online')


@bot.command()
async def play(context, command=None):
    author = context.author
    if command is None:
        name_channel = author.voice.channel.name
        voice_channel = discord.utils.get(context.guild.voice_channels, name=name_channel)
    else:
        params = command.split(' ')
    if len(params) == 1:
        src = params[0]
        name_channel = author.voice.channel.name
        voice_channel = discord.utils.get(context.guild.voice_channels, name=name_channel)
    else:
        await context.channel.send('invalid command')
        return

    voice = discord.utils.get(bot.voice_clients, guild=context.guild)
    if voice is None:
        await voice_channel.connect()
        voice = discord.utils.get(bot.voice_clients, guild=context.guild)

    if src is None:
        pass
    elif src.startswith('http'):
        if await check_domains(src) is False:
            await context.channel.send(f'{author.mention}, invalid link')
            return

        with YoutubeDL(config.YOUTUBE_OPTIONS) as youtube_download:
            info = youtube_download.extract_info(src, download=False)
        url = info['formats'][0]['url']
        voice.play(discord.FFmpegPCMAudio(source=url, **config.FFMPEG_OPTIONS), after=lambda x: play_next(context, query))


@bot.command()
async def skip(context):
    print('SKIP')
    global query
    voice = discord.utils.get(bot.voice_clients, guild=context.guild)
    if len(query) != 0:
        if voice.is_playing():
            voice.stop()
            play_next(context, query)
        else:
            play_next(context, query)
    else:
        await context.channel.send(f'{context.author.mention}, no more songs in playlist')



@bot.command()
async def leave(context):
    voice = discord.utils.get(bot.voice_clients, guild=context.guild)
    if voice.is_connected():
        await voice.disconnect()
    else:
        await context.channel.send(f'{context.author.mention}, bot already stopped')


@bot.command()
async def pause(context):
    voice = discord.utils.get(bot.voice_clients, guild=context.guild)
    if voice.is_playing():
        voice.pause()
    else:
        await context.channel.send(f'{context.author.mention}, bot already paused')


@bot.command()
async def resume(context):
    voice = discord.utils.get(bot.voice_clients, guild=context.guild)
    if voice.is_paused():
        voice.resume()
    else:
        await context.channel.send(f'{context.author.mention}, bot already played')


@bot.command()
async def stop(context):
    voice = discord.utils.get(bot.voice_clients, guild=context.guild)
    if voice.is_playing() or voice.is_pause():
        voice.stop()
    else:
        await context.channel.send(f'{context.author.mention}, bot already paused')


@bot.command()
async def add(context, command):
    query.append(command.split(' ')[0])
    print(query)
    await context.channel.send(f'{context.author.mention}, song added to playlist')


@bot.command()
async def stream(context, *, arg):
    voice_channel = await context.message.author.voice.channel.connect()
    with YoutubeDL(config.YOUTUBE_OPTIONS) as ydl:
        if 'https://' in arg:
            info = ydl.extract_info(arg, download=False)
        else:
            info = ydl.extract_info(f"ytsearch:{arg}", download=False)['entries'][0]

    url = info['formats'][0]['url']

    voice_channel.play(discord.FFmpegPCMAudio(source=url, **config.FFMPEG_OPTIONS))


bot.run(TOKEN)

'''
если не работает ffmpeg, то в папку, где лежат скрипты питона (.../Python/Python39/Scripts) нужно докинуть экзешники
из папки ffmpeg/bin (https://ffmpeg.org/download.html) 
'''