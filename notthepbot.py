import discord
import requests
import requests_cache
import json
import threading
import time
import os
from dotenv import load_dotenv
load_dotenv()

## Votes setup
jwt_token = os.getenv('JWT_TOKEN')
participation_event_id = '9e8e1a15c831441797912a86022f5a78fcb70e151e43fe84812d4c7f6eb79a7b'
combined_participation_plugin_url = f"https://chrysalis.naerd.tech/api/plugins/participation/events/{participation_event_id}/status"
head = {'Authorization': 'Bearer {}'.format(jwt_token)}
headers = {'content-type': 'application/json'}

## Coingecko Setup
# chose the token
coin_id = "iota"
# set the URL for the API
coingecko_url_coin = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
# cache API requests to sqlite for 300 seconds
requests_cache.install_cache(cache_name='coingecko_api_cache', expire_after = 300)
# discord channels filtering
discord_channels = [738665041217323068, 997121969969451070]

class ReplyClient(discord.Client):
    # define sleep_switch to zero
    sleep_switch = 0
    # define input/commands to trigger bot
    speccommands = ['p', 'price', 'rice', '🍚']
    votecommands = ['results', '🗳️']

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

        # votes section
        

        vote_response = requests.get(url = combined_participation_plugin_url,headers=head)

        try:
            vote_response_reply = json.loads(vote_response.text)

            response_one_output = vote_response_reply["data"]["questions"][0]["answers"][0]["current"]
            response_two_output = vote_response_reply["data"]["questions"][0]["answers"][1]["current"]
            response_one_formatted = "{:,.0f}".format(response_one_output)
            response_two_formatted = "{:,.0f}".format(response_two_output)
            responses_total = response_one_output + response_two_output
            print(responses_total)
            response_one_percentage = round((response_one_output/responses_total) * 100, 2)
            response_two_percenttage = round((response_two_output/responses_total) * 100, 2)
            print(response_one_percentage)
            print(response_two_percenttage)

         # Catch exception when HORNET node API is down
        except Exception as error_message:
            if message.content.casefold() in self.votecommands and message.channel.id in discord_channels:
                if self.sleep_switch == 0:
                    # Set the sleep_switch to 1 so that the bot only adds reactions instead of posting the embed
                    self.sleep_switch = 1
                    
                    # build embed error message
                    cgapiembedVar=discord.Embed(title = "ERROR MESSAGE", color=0xe01b24)
                    cgapiembedVar.add_field(name="Error type", value="HORNET API is down", inline=True)
                    await message.channel.send(embed=cgapiembedVar)
                    
                    # define a thread for sleeping
                    sleep_thread = threading.Thread(target=self.thread_sleep)
                    
                    # after posting the embed message go to sleep
                    sleep_thread.start()
                else:
                    await message.add_reaction("🪲")
        # let's read the message
        if message.content.casefold() in self.votecommands and message.channel.id in discord_channels:
            # as long as the sleep_switch is off
            if self.sleep_switch == 0:
            # Set the sleep_switch to 1 so that the bot only adds reactions instead of posting the embed
                self.sleep_switch = 1    
                
                embedcolor = 0xff7800
                # build the embed message
                embedVar=discord.Embed(title =  "IOTA vote progress", color = embedcolor)
                embedVar.add_field(name="Vote context", value="Should we incentivize builders and activity on the Shimmer network by increasing the token supply to give the Shimmer Community Treasury DAO and the Tangle Ecosystem Association (TEA) each 10% of the new total supply?", inline=False)
                embedVar.add_field(name="Yes", value=str(response_one_percentage) + " % - " + str(response_one_formatted) + "Ki", inline=True)
                embedVar.add_field(name="No", value=str(response_two_percenttage) + " % - " + str(response_two_formatted) + " Ki", inline=True)
                embedVar.add_field(name="Source", value="NÄRD Tech Node", inline=False)

                # reply to the input/command with the embed
                await message.channel.send(embed=embedVar)
                            
                # define a thread for sleeping
                sleep_thread = threading.Thread(target=self.thread_sleep)
                # after posting the embed message go to sleep
                sleep_thread.start()
                
            # since the sleep_switch is at 1, the bot will only add the reaction to a message and ignore further input/commands    
            else:
                # react to the message
                await message.add_reaction("😠")
        else:
            if message.content.casefold() in self.votecommands and message.channel.id in discord_channels:
            # as long as the sleep_switch is off
                if self.sleep_switch == 0:
                # Set the sleep_switch to 1 so that the bot only adds reactions instead of posting the embed
                    self.sleep_switch = 1    
        ## Coingecko section
        # request response from Coingecko API
        coingecko_response = requests.get(coingecko_url_coin)

        
        try:
            # load the json to extract the data we are looking for
            iota_prices = json.loads(coingecko_response.text)
        
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
                
        
            # nice
            if marketcaprank == 69:
                marketcaprank = "69 (nice!)"
                
        # Catch exception when CoinGecko API is down
        except Exception as error_message:
            if message.content.casefold() in self.speccommands and message.channel.id in discord_channels:
                if self.sleep_switch == 0:
                    # Set the sleep_switch to 1 so that the bot only adds reactions instead of posting the embed
                    self.sleep_switch = 1
                    
                    # build embed error message
                    cgapiembedVar=discord.Embed(title = "ERROR MESSAGE", color=0xe01b24)
                    cgapiembedVar.add_field(name="Error type", value="CoinGecko API is down", inline=True)
                    cgapiembedVar.add_field(name="Info", value="Verify status at https://status.coingecko.com", inline=True)
                    await message.channel.send(embed=cgapiembedVar)
                    
                    # define a thread for sleeping
                    sleep_thread = threading.Thread(target=self.thread_sleep)
                    
                    # after posting the embed message go to sleep
                    sleep_thread.start()
                else:
                    await message.add_reaction("🪲")
            
        # let's read the message
        if message.content.casefold() in self.speccommands and message.channel.id in discord_channels:
            # as long as the sleep_switch is off
            if self.sleep_switch == 0:
            # Set the sleep_switch to 1 so that the bot only adds reactions instead of posting the embed
                self.sleep_switch = 1    
                
                # build the embed message
                embedVar=discord.Embed(title =  str(iota_prices["name"]) + " #" + str(marketcaprank), color = embedcolor)
                embedVar.add_field(name="USD", value=str(currentprice), inline=True)
                embedVar.add_field(name="1h", value=str(change1hour) + "%", inline=True)
                embedVar.add_field(name="24h", value=str(change24hours) + "%", inline=True)
                embedVar.add_field(name="Source", value="Coingecko", inline=False)

                # reply to the input/command with the embed
                await message.channel.send(embed=embedVar)
                # print to the console if we are using the cache
                print ("Used Cache: {0}".format(coingecko_response.from_cache))

                
                # define a thread for sleeping
                sleep_thread = threading.Thread(target=self.thread_sleep)
                # after posting the embed message go to sleep
                sleep_thread.start()
                
            # since the sleep_switch is at 1, the bot will only add the reaction to a message and ignore further input/commands    
            else:
                # react to the message
                await message.add_reaction("😠")
        else:
            if message.content.casefold() in self.votecommands and message.channel.id in discord_channels:
            # as long as the sleep_switch is off
                if self.sleep_switch == 0:
                # Set the sleep_switch to 1 so that the bot only adds reactions instead of posting the embed
                    self.sleep_switch = 1    
    

                
# load discord intents
intents = discord.Intents.default()
intents.messages = True
client = ReplyClient(intents=intents)
discord_bot_token = os.getenv('DISCORD_BOT_TOKEN')
client.run(discord_bot_token)
