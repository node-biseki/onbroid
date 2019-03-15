import discord
from discord.ext import commands
from googletrans import Translator
import re
import aiohttp
import async_timeout
import lxml.html

#got bot's token
with open('../bot.txt') as f:
    token = f.readline()

weblio = 'https://ejje.weblio.jp/content/'
client = discord.Client()
session = aiohttp.ClientSession()

#language dict
lang = {
    'cn':'zh-cn',
    'ko':'ko',
    'en':'en',
    'ja':'ja'
    }

alphanum = re.compile(r'^[a-zA-Z0-9]+$')
def isenword(word):
    return bool(alphanum.match(word))

#scraping
async def fetch(session, url):
    levels = []
    with async_timeout.timeout(10):
        async with session.get(url) as resp:
            html = await resp.text()
            root = lxml.html.fromstring(html)
            contents = root.cssselect('meta[name="twitter:description"]')[0].attrib['content']
            level = root.cssselect('span.learning-level-row span')
            for a in level:
                levels.append(a.text)
            return [contents, ' '.join(levels)]

#translation and make embeds
async def trans(content_list):
    tolang = 'ja'
    t = Translator()
    content = []

    #processing '-'
    for index in content_list:
        if index[0] == '-':
            tolang = lang[index[1:].lower()]
            continue
        content.append(index)
    contents = ' '.join(content)

    #whether ues weblio or google
    if len(content) == 1 and isenword(contents) and tolang == 'ja':
        url = weblio + contents
        data = await fetch(session, url)
        translate, level = data[0], data[1]

        if translate == '1087万語収録！weblio辞書で英語学習':
            translate = '{}って何？'.format(contents)
        if not level:
            level = 'noob level'
    else:
        translate = t.translate(contents, dest=tolang).text
        level = 'pro level'

    embed = discord.Embed(title='**->** '+contents, description=translate, color=16738740)
    embed.set_footer(text=level)
    return embed

@client.event
async def on_message(message):
    try:
        if message.content.startswith('*'):
            content_list = message.content[1:].split()
            reply = await trans(content_list)
            await message.channel.send(embed=reply)
    except:
        pass

client.run(token)
