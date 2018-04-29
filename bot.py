import discord
from discord.ext import commands
import aiohttp, urllib.parse
from datetime import datetime

from config import *
from checks import *

description = """
FrenchMasterSword's bot, provides some cool utilities (just to be sure, it's French)
"""

bot = commands.Bot(command_prefix='.', description=description, pm_help=None)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ; ID : {bot.user.id}')
    print('-----------------------------------------------\n')
    await bot.change_presence(status=3, activity=discord.Game(name='.info | .help'))

@bot.command()
async def info(ctx):
    """Some info about the bot, including an invite link"""
    embed = discord.Embed(title="Frenchie", description=description, color=BLUE)

    embed.add_field(name="Author", value="FrenchMasterSword#9035")
    embed.add_field(name="Server count", value=f"{len(bot.guilds)}")
    embed.add_field(name="Invite", value="[Invite me to your server ! (not yet)](https://google.com)")
    embed.set_footer(text="Coded with ❤ and Python 3")

    await ctx.send(embed=embed)

@bot.command()
async def ping(ctx):
    """Gives you the bot's latency"""
    latency = round(bot.latency * 1000, 2)
    await ctx.send(f':ping_pong: **Pong !** Latency : `{latency} ms`')

@bot.command()
async def weather(ctx, location):
    """Gives you current weather stuff on a given city"""
    async with aiohttp.ClientSession() as client_session:
        async with client_session.get(urllib.parse.quote_plus(weather_url.format(location), safe=';/?:@&=$,><-[]')) as response:
            if response.status == 200:
                data = await response.json()

                temperature = data['main']['temp']
                windSpeed = data['wind']['speed']
                sunrise = str(datetime.utcfromtimestamp(data['sys']['sunrise'])).split(" ")[1]
                sunset = str(datetime.utcfromtimestamp(data['sys']['sunset'])).split(" ")[1]
                humidity = data['main']['humidity']
                pressure = data['main']['pressure']
                city = data['name'].capitalize()
                countryFlag = f':flag_{data["sys"]["country"].lower()}:'

                emb = discord.Embed(title=f"Current weather at {city} {countryFlag} : {data['weather'][0]['description']}", color=BLUE)
                emb.set_thumbnail(url=earth_url)
                emb.add_field(name=":thermometer: Temperature",value=f"{temperature} °C")
                emb.add_field(name=":dash: Wind speed",value=f"{windSpeed} m/s")
                emb.add_field(name=":sunrise_over_mountains: Sunrise",value=f'{sunrise} (UTC)')
                emb.add_field(name=":city_sunset: Sunset",value=f'{sunset} (UTC)')
                emb.add_field(name=":droplet: Humidity",value=f'{humidity} %')
                emb.add_field(name=":cloud: Pressure",value=f'{pressure} hPa')

                emb.set_footer(text="powered by openweathermap.org")
                await ctx.send(embed=emb)
            else:
                await ctx.send("An error occurred. Check your arguments.")

@bot.command(name="run", hidden=True)
async def run_code(ctx, *, text: str):
    """Run code and feedback Output, warnings, errors and performance in more than 40 languages."""
    arg = text.split('|')
    language = arg[0].capitalize()
    code = arg[1][3:-3]

    #code markdown, C++ and C#/F#
    if code.startswith(arg[0]+'\n'):
        code = code[len(arg[0])+1:]
    elif code.startswith("cpp\n"):
        code = code[4:]
    elif code[1:].startswith('sharp\n'):
        code = code[7:]

    rexUrlRequest = rex_url.format(rexLanguageDict[language], code)
    #TODO: add optional compiler args input # INPUT is useless
    #if len(arg) > 2:
    #    if arg[2].startswith('INPUT='):
    #        rexUrlRequest += '&Input=' + arg[2][6:]
    #    if not arg[-1].startswith('INPUT='):
    #        rexUrlRequest += '&CompilerArgs=' + arg[-1]
    if ('&CompilerArgs' not in rexUrlRequest) and (language in rexCompilerDict):
        rexUrlRequest += '&CompilerArgs=' + rexCompilerDict[language]
    #removing bad URL characters
    rexUrlRequest = urllib.parse.quote_plus(rexUrlRequest, safe=';/?:@&=$,><-[]')

    async with aiohttp.ClientSession() as client_session:
        async with client_session.get(rexUrlRequest) as response:
            if response.status == 200:
                donnees = await response.json()

                content = ""
                if donnees['Result']:
                    content += f'```{donnees["Result"]}```'
                if donnees['Warnings']:
                    content += f'```fix\n{donnees["Warnings"]}```'
                if donnees['Errors']:
                    # Red markdown
                    listErrors = donnees['Errors'].split('\n')
                    if len(listErrors) > 1:
                        for line in listErrors:
                            listErrors[listErrors.index(line)] = '-' + line
                    else:
                        listErrors[0] = '-' + listErrors[0]
                    donnees['Errors'] = "diff\n" + "\n".join(listErrors)[:-1]

                    content += f'```{donnees["Errors"]}```'
                if donnees['Stats']:
                    content += f'```{donnees["Stats"]}```'
                if not content:
                    content = "```No output```"
                await ctx.send(content)
            else:
                await ctx.send("An error occurred\nCommand usage : `.run <language>|```<code>```[|INPUT=<input>][|<compiler args>]`")

@bot.command(aliases=['stream', 'listen', 'watch'], hidden=True)
@is_FMS()
async def play(ctx, media='.info | .help'):
    """Update bot presence accordingly to invoke command"""
    # Need URL for streaming
    p_types = {'play': 0, 'stream':1, 'listen': 2, 'watch': 3}
    activity = discord.Activity(name=media, type=p_types[ctx.invoked_with])
    await bot.change_presence(activity=activity)

@bot.command(usage="<location>,[<country code>]", hidden=True)
@is_FMS()
async def kill(ctx):
    await bot.logout()

bot.run(BOT_TOKEN)