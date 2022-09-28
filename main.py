import discord
import yt_dlp
import os
import config
from discord.ext import commands
from youtube_dl import YoutubeDL

YDL_OPTIONS = {
    'format': 'worstaudio/best',
    'noplaylist': 'False',
    'simulate': 'True',
    'preferredquality': '192',
    'preferredcodec': 'mp3',
    'key': 'FFmpegExtractAudio',
}
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',
}
youtube_options = {
    'format': 'worstaudio/best',
    'postprocessors': [
        {
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }
    ],
}
bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print('bot online')

@bot.command()
async def stream(context, *, arg):
    voice_channel = await context.message.author.voice.channel.connect()
    with YoutubeDL(YDL_OPTIONS) as ydl:
        if 'https://' in arg:
            info = ydl.extract_info(arg, download=False)
        else:
            info = ydl.extract_info(f"ytsearch:{arg}", download=False)['entries'][0]

    url = info['formats'][0]['url']

    voice_channel.play(discord.FFmpegPCMAudio(source=url, **FFMPEG_OPTIONS))

server = server_id = name_channel = None

domains = ['https://www.youtube.com/', 'http://www.youtube.com/', 'https://youtu.be/', 'http://youtu.be/']

async def check_domains(src):
    for i in domains:
        if src.startswith(i):
            return True
    return False

def connect_and_play(context, voice_channel, src):
    voice = discord.utils.get(bot.voice_clients, guild=context.guild)
    if voice is None:
        await voice_channel.connect()
        voice = discord.utils.get(bot.voice_clients, guild=context.guild)

    if src is None:
        pass
    elif src.startswith('http'):
        if await check_domains(src) is False:
            await context.channel.send(f'{context.author.mention}, invalid link')
            return

        with YoutubeDL(youtube_options) as youtube_download:
            info = youtube_download.extract_info(src, download=False)
        url = info['formats'][0]['url']
        # print(info)
        voice.play(discord.FFmpegPCMAudio(source=url))

@bot.command()
async def play(context, *, command=None):
    global server, server_id, name_channel
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
        print('len(params) == 1')
    elif len(params) == 3:
        server_id = params[0]
        voice_id = params[1]
        src = params[2]
        try:
            server_id = int(server_id)
            voice_id = int(voice_id)
        except:
            await context.channel.send(f'{author.mention}, id server/voice should be integer')
            return
        print('len(params) == 3')
        server = bot.get_guild(server_id)
        voice_channel = discord.utils.get(server.voice_channels, id=voice_id)
    else:
        await context.channel.send('invalid command')
        return
    connect_and_play(context, src, voice_channel)
    # voice = discord.utils.get(bot.voice_clients, guild=context.guild)
    # if voice is None:
    #     await voice_channel.connect()
    #     voice = discord.utils.get(bot.voice_clients, guild=context.guild)
    #
    # if src is None:
    #     pass
    # elif src.startswith('http'):
    #     if await check_domains(src) is False:
    #         await context.channel.send(f'{author.mention}, invalid link')
    #         return
    #
    #     with YoutubeDL(youtube_options) as youtube_download:
    #         info = youtube_download.extract_info(src, download=False)
    #     url = info['formats'][0]['url']
    #     # print(info)
    #     voice.play(discord.FFmpegPCMAudio(source=url))

#C:\Development\PyCharm\bunker_music\ffmpeg\bin
#!play https://www.youtube.com/watch?v=tL25rbnvM4o


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


bot.run(config.TOKEN)

'''
если не работает ffmpeg, то в папку, где лежат скрипты питона (.../Python/Python39/Scripts) нужно докинуть экзешники
из папки ffmpeg/bin (https://ffmpeg.org/download.html) 
'''