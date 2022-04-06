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
        speccommands = ['p', 'price']
        if message.content.casefold() in str(speccommands).casefold():
            response = requests.get(url_coin)
            iota_prices = json.loads(response.text)
            marketcaprank = iota_prices["market_cap_rank"]
            currentprice = round(iota_prices["market_data"]["current_price"]["usd"], 4)
            change24hours = round(iota_prices["market_data"]["price_change_percentage_24h"], 1)
            change1hour = round(iota_prices["market_data"]["price_change_percentage_24h"] / 24, 1)
            print (iota_prices["market_cap_rank"])
            embedVar=discord.Embed(title =  str(iota_prices["name"]) + " #" + str(marketcaprank), color = 0xff7800)
            embedVar.add_field(name="USD", value=str(currentprice), inline=True)
            embedVar.add_field(name="1h", value=str(change1hour) + "%", inline=True)
            embedVar.add_field(name="24h", value=str(change24hours) + "%", inline=True)
            embedVar.add_field(name="Source", value="Coingecko", inline=False)
            #print (embedVar)
            #await message.channel.send(iota_prices["market_cap_rank"])
            await message.channel.send(embed=embedVar)

intents = discord.Intents.default()
intents.messages = True
client = MyClient(intents=intents)
client.run(INSERTYOURDISCORDBOTTOKENHERE)
