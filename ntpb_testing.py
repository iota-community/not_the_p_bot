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
voting_enabled = 1
jwt_token = os.getenv('JWT_TOKEN')
participation_event_id = '9e8e1a15c831441797912a86022f5a78fcb70e151e43fe84812d4c7f6eb79a7b'
combined_participation_plugin_url = f"https://chrysalis.naerd.tech/api/plugins/participation/events/{participation_event_id}/status"
head = {'Authorization': 'Bearer {}'.format(jwt_token)}
headers = {'content-type': 'application/json'}

## Coingecko Setup
# IOTA token
coin_id_iota = "iota"
coin_id_shimmer = "shimmer"
# set the URL for the API
coingecko_url_iota = f"https://api.coingecko.com/api/v3/coins/{coin_id_iota}"
coingecko_url_shimmer = f"htts://api.coingecko.com/api/v3/coins/{coin_id_shimmer}"

# cache API requests to sqlite for 300 seconds
requests_cache.install_cache(cache_name='api_cache', expire_after = 300)

# discord channels filtering
discord_channels = [738665041217323068] # Discord channel enabled for replies

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

        # Votes section
        if message.content.casefold() in self.votecommands and message.channel.id in discord_channels:
            if voting_enabled == 1:
                print("voting is enabled")
                try:
                    vote_response = requests.get(url = combined_participation_plugin_url,headers=head)

                # Catch exception when HORNET node API is down
                except requests.exceptions.InvalidSchema as error:
                      
                    if self.sleep_switch == 0:
                        
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
                        # react to the message
                        await message.add_reaction("😠")

                else:
                    vote_response_reply = json.loads(vote_response.text)
                    
                    # Get results of two options from the node API
                    response_one_output = vote_response_reply["data"]["questions"][0]["answers"][0]["current"]
                    response_two_output = vote_response_reply["data"]["questions"][0]["answers"][1]["current"]
                    # Format results
                    response_one_formatted = "{:,.0f}".format(response_one_output)
                    response_two_formatted = "{:,.0f}".format(response_two_output)
                    
                    # Caluclate percentage P = V/T * 100
                    responses_total = response_one_output + response_two_output
                    
                    response_one_percentage = round((response_one_output/responses_total) * 100, 2)
                    response_two_percenttage = round((response_two_output/responses_total) * 100, 2)
                
                    # let's read the message
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
                        # print to the console if we are using the cache
                        print ("Used Cache: {0}".format(vote_response.from_cache))            
                        
                        # define a thread for sleeping
                        sleep_thread = threading.Thread(target=self.thread_sleep)
                        # after posting the embed message go to sleep
                        sleep_thread.start()
                        
                    # since the sleep_switch is at 1, the bot will only add the reaction to a message and ignore further input/commands    
                    else:
                        # react to the message
                        await message.add_reaction("😠")
            else:
                if self.sleep_switch == 0:
                    # Set the sleep_switch to 1 so that the bot only adds reactions instead of posting the embed
                    self.sleep_switch = 1
                    
                    # build embed error message
                    cgapiembedVar=discord.Embed(title = "INFORMATION", color=0xe01b24)
                    cgapiembedVar.add_field(name="Vote tracking: ", value="NOT enabled", inline=True)
                    await message.channel.send(embed=cgapiembedVar)
                    
                    # define a thread for sleeping
                    sleep_thread = threading.Thread(target=self.thread_sleep)
                        
                    # after posting the embed message go to sleep
                    sleep_thread.start()
                else:
                        # react to the message
                        await message.add_reaction("😠")
                
        ## Coingecko section
        
        if message.content.casefold() in self.speccommands and message.channel.id in discord_channels:    
            try:
                # request response from Coingecko API
                coingecko_response_iota = requests.get(coingecko_url_iota)
                # coingecko_response_shimmer = requests.get(coingecko_url_shimmer)
            # Catch exception when CoinGecko API is down
            except Exception as error_message:
                
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
            
            else:
                # load the json to extract the data we are looking for
                prices_iota = json.loads(coingecko_response_iota.text)
                # prices_shimmer = json.loads(coingecko_response_iota.text)
            
                # fill variables
                marketcaprank_iota = prices_iota["market_cap_rank"]
                currentprice_iota = round(prices_iota["market_data"]["current_price"]["usd"], 4)
                change24hours_iota = round(prices_iota["market_data"]["price_change_percentage_24h"], 1)
                change1hour_iota = round(prices_iota["market_data"]["price_change_percentage_1h_in_currency"]["usd"], 2)
                
                # change color of the embed based on the value of the change1hour variable
                if change1hour_iota >= 0:
                    if change1hour_iota == 0:
                        embedcolor = 0xff7800
                    else:
                        embedcolor = 0x33d17a
                else:
                    embedcolor = 0xe01b24
                    
            
                # IOTA nice
                if marketcaprank_iota == 69:
                    marketcaprank_iota = "69 (nice!)"
                
                # # Shimmer nice
                # if marketcaprank_shimmer == 69:
                #     marketcaprank_shimmer = "69 (nice!)"
                    
                
                # let's read the message
                if message.content.casefold() in self.speccommands and message.channel.id in discord_channels:
                    # as long as the sleep_switch is off
                    if self.sleep_switch == 0:
                    # Set the sleep_switch to 1 so that the bot only adds reactions instead of posting the embed
                        self.sleep_switch = 1    
                        
                        # build the embed message
                        # IOTA section
                        embedVar_iota = discord.Embed(title =  str(prices_iota["name"]) + " #" + str(marketcaprank_iota), color = embedcolor)
                        embedVar_iota.add_field(name = "USD", value = str(currentprice_iota), inline=True)
                        embedVar_iota.add_field(name = "1h", value = str(change1hour_iota) + "%", inline=True)
                        embedVar_iota.add_field(name = "24h", value = str(change24hours_iota) + "%", inline=True)
                        embedVar_iota.add_field(name="Source", value="Coingecko", inline=False)

                        # Shimmer section
                        # uncomment once Shimmer is listed on Coingecko
                        # embedVar_iota = discord.Embed(title = str(prices_shimmer["name"]) + " #" + str(marketcaprank_shimmer))
                        # embedVar_shimmer.add_field(name = "USD", value = str(currentprice_shimmer), inline=True)
                        # embedVar_shimmer.add_field(name = "1h", value = str(change1hour_shimmer) + "%", inline=True)
                        # embedVar_shimmer.add_field(name = "24h", value = str(change24hours_shimmer) + "%", inline=True)
                        # embedVar_shimmer.add_field(name="Source", value="Coingecko", inline=False)

                        # Delete this section once Shimmer is listed on Coingecko
                        embedVar_shimmer = discord.Embed(title = "Shimmer #1 in our hearts", color = embedcolor)
                        embedVar_shimmer.add_field(name = "USD", value = "0", inline=True)
                        embedVar_shimmer.add_field(name = "1h", value = "0" + "%", inline=True)
                        embedVar_shimmer.add_field(name = "24h", value = "0" + "%", inline=True)
                        embedVar_shimmer.add_field(name="Source", value="NO MARKET DATA AVAILABLE", inline=False)

                        # Stop delete

                        

                        # reply to the input/command with the embed
                        await message.channel.send(embed=embedVar_iota)
                        await message.channel.send(embed=embedVar_shimmer)

                        # print to the console if we are using the cache
                        print ("Used Cache: {0}".format(coingecko_response_iota.from_cache))
                        # print ("Used Cache: {0}".format(coingecko_response_shimmer.from_cache))

                        
                        # define a thread for sleeping
                        sleep_thread = threading.Thread(target=self.thread_sleep)
                        # after posting the embed message go to sleep
                        sleep_thread.start()
                        
                    # since the sleep_switch is at 1, the bot will only add the reaction to a message and ignore further input/commands    
                    else:
                        # react to the message
                        await message.add_reaction("😠")
    

                
# load discord intents
intents = discord.Intents.default()
intents.messages = True
client = ReplyClient(intents=intents)
discord_bot_token = os.getenv('DISCORD_BOT_TOKEN')
client.run(discord_bot_token)
