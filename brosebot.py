
# -*- coding: utf-8 -*-
#pip3 install: Pillow, asyncio, discord.py

from datetime import datetime
from PIL import Image
import PIL.ImageOps
from random import randint
from time import sleep
import discord,asyncio,os
from discord.ext import commands, tasks
import re
from datetime import datetime
import requests

intents = discord.Intents.all()
intents.messages = True

bot = commands.Bot(command_prefix="!", intents=intents)
allowed_mentions = discord.AllowedMentions(everyone = True)

#Pulls environment variables from docker container for sensitive data
designatedChannel = os.environ['CHANNEL_ID']
userID = os.environ['USER_ID']
botToken = os.environ['BOT_TOKEN']

phrases = ["In-house tonight?", "Man fuck you", "bruh", "yo dap me up for that", "ya peel me?", "na ur beat for that", "lick my nuts", 
"half hour power", "I’m boutta morb", "HONK SHOOOOOO", "aye throw on Rxknephew", "^^^ thats beat", "y'all are beat", "bangball anyone?", 
"peep Brussy and Co. rq", "peep Not the Boys rq", "slover?", "نشط: يدخل Jax في Evasion ، وهو موقف دفاعي ، لمدة ثانيتين ، مما يتسبب في تفادي جميع الهجمات الأساسية غير البرجية ضده طوال المدة. يحصل Jax أيضًا على تقليل الضرر بنسبة 25٪ ، مما يقلل الضرر من جميع قدرات منطقة التأثير التي يتم الحصول عليها من أبطال البطل. يمكن إعادة صياغة Counter Strike بعد ثانية واحدة ، ويتم ذلك تلقائيًا بعد انتهاء المدة. RECAST: يلحق Jax ضررًا جسديًا لجميع الأعداء القريبين ، ويزيد بنسبة 20٪ لكل هجوم يتم تفاديه ، وزيادة تصل إلى 100٪ ، ويصعقهم الصاعقة لمدة ثانية واحدة."]

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    avatar.start()
    quote.start()

@tasks.loop(hours=0) #Alternates setting the next loops delay and sending a message to ensure that logs are lined up with actual message times
async def quote():
    if quote.current_loop % 2 == 0: #Ignores the first loop so that the timer matches with printout
        timer = randint(360,1440) #Randomizes time until next quote in minutes
        quote.change_interval(minutes=timer) #Sets the time until the next quote
        current_time = datetime.now().strftime("%H:%M:%S")
        #print(current_time + " | Next quote in " + str(timer) + " seconds (" + str(quote.current_loop) +")")
        print(current_time + " | Next quote in " + str(timer//60) + " hours and " + str(timer%60) + " minutes")
    else:
        channel = bot.get_channel(int(designatedChannel)) #Set to the desired channel, current: Social in Team Jersey 701174432126861436
        phrase = randint(0,len(phrases)-1)
        if phrase == 0:
            chance = randint(1,30)
            if chance == 1:
                await channel.send(content = "@everyone " + phrases[phrase], allowed_mentions=allowed_mentions)
        await channel.send(phrases[phrase])
        quote.change_interval(minutes=0)
    

@tasks.loop(hours=4) #Outage may cause a http 503 error causing the bot to not update pfp until restarted, add an exception to retry after an hour
async def avatar():
    user = await bot.fetch_user(userID) #Brose discord ID
    pfp = requests.get(user.avatar_url, stream=True)

    image = Image.open(pfp.raw)
    if image.mode == 'RGBA':
        r,g,b,a = image.split()
        rgb_image = Image.merge('RGB', (r,g,b))

        inverted_image = PIL.ImageOps.invert(rgb_image)

        r2,g2,b2 = inverted_image.split()

        final_transparent_image = Image.merge('RGBA', (r2,g2,b2,a))

        final_transparent_image.save('inv_img.png')
    elif image.mode == 'P':
        image = image.convert('RGB')
        inverted_image = PIL.ImageOps.invert(image)
        inverted_image.save('inv_img.png')
    else:
        inverted_image = PIL.ImageOps.invert(image)
        inverted_image.save('inv_img.png')

    pfp_path = "inv_img.png"
    with open(pfp_path, "rb") as pfp:
        await bot.user.edit(avatar=pfp.read())
    current_time = datetime.now().strftime("%H:%M:%S")
    print(current_time + " | Got Brose's PFP")

    #await ctx.reply(file=discord.File(pfp_path)) #Sends a reply in the chat with the inverted pfp, should be removed after adding a timer to check for Brose's pfp. Needs ctx to reply if added back
    
@bot.event
async def on_message(message):
    channel = bot.get_channel(designatedChannel) #Set to the desired channel, current: Social in Team Jersey
    
    #Makes sure the message contains mentions before processing
    if message.mentions == 0:
        return
    #Using Regex to find the number of total mentions in a message while making sure that there is only 1 unique mention using message.mentions, with 4 or more total mentions
    if message.author != bot.user and len(message.mentions) == 1 and len(re.findall(r"[@]\w{18,19}", message.content)) > 3:
        #Copies the original message(including text), using the same number of mentions
        await channel.send(message.content)


bot.run(botToken)
