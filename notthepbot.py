import discord
import requests
import requests_cache
import json
import threading
import time

# chose the token
coin_id = "iota"
# set the URL for the API
url_coin = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
# cache API requests to sqlite for 300 seconds
requests_cache.install_cache(cache_name='coingecko_api_cache', expire_after = 300)
# discord channels filtering
discord_channels = [738665041217323068, 960905086882680833]

class ReplyClient(discord.Client):
    # define sleep_switch to zero
    sleep_switch = 0
    # define input/commands to trigger bot
    speccommands = ['p', 'price']

    # define sleep period, during this time the embed will not be posted to Discord
    def thread_sleep(self):
        # sleep for N seconds
        time.sleep(10)
        self.sleep_switch = 0

    # print to console that we logged in
    async def on_ready(self):
        print('Logged on as', self.user)

    # the discord function
    async def on_message(self, message):
        # don't respond to ourselves
        if message.author == self.user:
            return
        # as long as the sleep_switch is off
        if self.sleep_switch == 0:
            # list of inputs/commands it should listen to
            
            # let's read the message
            if message.content.casefold() in self.speccommands and message.channel.id in discord_channels:
 
                # request response from Coingecko API
                response = requests.get(url_coin)

                # load the json to extract the data we are looking for
                iota_prices = json.loads(response.text)

                # fill variables
                marketcaprank = iota_prices["market_cap_rank"]
                currentprice = round(iota_prices["market_data"]["current_price"]["usd"], 4)
                change24hours = round(iota_prices["market_data"]["price_change_percentage_24h"], 1)
                change1hour = round(iota_prices["market_data"]["price_change_percentage_1h_in_currency"]["usd"], 2)

                # change color of the embed based on the value of the change1hour variable
                if change1hour >= 0:
                    if change1hour == 0:
                        embedcolor = 0xff7800
                    else:
                        embedcolor = 0x33d17a
                else:
                    embedcolor = 0xe01b24
                
                # build the embed message
                embedVar=discord.Embed(title =  str(iota_prices["name"]) + " #" + str(marketcaprank), color = embedcolor)
                embedVar.add_field(name="USD", value=str(currentprice), inline=True)
                embedVar.add_field(name="1h", value=str(change1hour) + "%", inline=True)
                embedVar.add_field(name="24h", value=str(change24hours) + "%", inline=True)
                embedVar.add_field(name="Source", value="Coingecko", inline=False)

                # reply to the input/command with the embed
                await message.channel.send(embed=embedVar)
                # print to the console if we are using the cache
                print ("Used Cache: {0}".format(response.from_cache))
                # Set the sleep_switch to 1 so that the bot only adds reactions instead of posting the embed
                self.sleep_switch = 1
                
            # define a thread for sleeping
            sleep_thread = threading.Thread(target=self.thread_sleep)
            # after posting the embed message go to sleep
            sleep_thread.start()
        # since the sleep_switch is at 1, the bot will only add the reaction to a message and ignore further input/commands    
        else:
            # let's read the message
            if message.content.casefold() in self.speccommands and message.channel.id in discord_channels:
                # react to the message
                await message.add_reaction("😒")
    

                
# load discord intents
intents = discord.Intents.default()
intents.messages = True
client = ReplyClient(intents=intents)
client.run(INSERTYOURDISCORDBOTTOKENHERE)
