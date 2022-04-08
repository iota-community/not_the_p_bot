import discord
import requests
import json

coin_id = "iota"
url_coin = f"https://api.coingecko.com/api/v3/coins/{coin_id}"

class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as', self.user)

    async def on_message(self, message):
        # don't respond to ourselves
        if message.author == self.user:
            return

        # list of inputs/commands it should listen to
        speccommands = ['p', 'price']
        # let's read the message 
        if message.content.casefold() in str(speccommands).casefold():
            # request response from Coingecko API
            response = requests.get(url_coin)
            
            # load the json to extract the data we are looking for
            iota_prices = json.loads(response.text)

            # fill variables
            marketcaprank = iota_prices["market_cap_rank"]
            currentprice = round(iota_prices["market_data"]["current_price"]["usd"], 4)
            change24hours = round(iota_prices["market_data"]["price_change_percentage_24h"], 1)
            change1hour = round(iota_prices["market_data"]["price_change_percentage_1h_in_currency"]["usd"], 1)
            
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
            embedVar.add_field(name="1h", value=str(change1hour) + "$", inline=True)
            embedVar.add_field(name="24h", value=str(change24hours) + "%", inline=True)
            embedVar.add_field(name="Source", value="Coingecko", inline=False)

            # reply to the input/command with the embed
            await message.channel.send(embed=embedVar)

# load discord intents
intents = discord.Intents.default()
intents.messages = True
client = MyClient(intents=intents)
client.run(INSERTYOURDISCORDBOTTOKENHERE)
