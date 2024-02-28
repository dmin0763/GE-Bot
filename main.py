import os
import discord
import requests
import json
from discord.ext import commands


intents = discord.Intents.all()
intents.messages = True
bot = commands.Bot(command_prefix='$', intents=intents)




#Download an updated JSON to parse info
print("Updating Databases...")
rs3 = requests.get("https://chisel.weirdgloop.org/gazproj/gazbot/rs_dump.json", allow_redirects=False)
open('rs3_dump.json', 'wb').write(rs3.content)
rs3.close()
osrs = requests.get("https://chisel.weirdgloop.org/gazproj/gazbot/os_dump.json", allow_redirects=False)
open('osrs_dump.json', 'wb').write(osrs.content)
osrs.close()
print("Done.")


def getAlchProfits(margin, version):
  result = ""
  goal = margin
  file = ""
  if version == "RS3":
      file = "rs3_dump.json"
  elif version == "OSRS":
      file = "osrs_dump.json"
  with open(file, 'r') as data:
      data = json.load(data)
      nat_price = data['561']['last']  # Grabbing Nature rune price using its ID
      result = result + (f"Nature Runes in {version} are currently: {format (nat_price, ',d')} gp.\n")
      result = result + (f"Listing all items in {version} with a High Alchemy profit of at least {format (goal, ',d')}:\n\n")
      try:
          for i in data:
              # Filter out non-alchables
              try:
                  Halch = data[i]['highalch']
              except KeyError:
                  Halch = -100
              # Filter out non-tradeables
              try:
                  price = data[i]['last']
              except KeyError:
                  price = -100

              if Halch != -100 and price != -100:
                  profit = ((Halch - price) - nat_price)

              #Filter out items whose alch profits don't meet the goal
              if Halch != -100 and price != -100 and profit >= goal:
                  # Name
                  try:
                      name = data[i]['name']
                  except KeyError:
                      print("Cannot Fetch Name.")

                  # Price
                  try:
                      price = data[i]['last']
                  except KeyError:
                      print("Cannot Fetch Price.")

                  # Trade Limit
                  try:
                    limit = data[i]['limit']
                  except KeyError:
                      print("Cannot Fetch Limit.")
                  # Volume
                  try:
                    volume = data[i]['volume']
                  except KeyError:
                      print("Cannot Fetch Trade Volume.")

                  temp = (f"**{name}**\nLast Price: {format (price, ',d')}\nHigh Alch Value: {format (Halch, ',d')}\nTrade Limit: {format (limit, ',d')}\nTrade Volume: {format (volume, ',d')}\nHigh Alch Profit: {format (profit, ',d')}\n\n")
                  result = result + temp
      except TypeError:
        result = result + "End of List.\n\n"

  
  return result



@bot.command()
async def alch(ctx, arg1, arg2):
  print(await bot.fetch_user(ctx.author.id))
  if arg1 and arg2:
        one = arg1
        two = arg2
  else:
        ctx.send("Incorrect input. Enter '$alch rs3' or '$alch osrs', followed by the desired profit per alch.")
        return

  version = str(one).upper()
  if (version != "RS3" and version != "OSRS"):
        await ctx.send("Incorrect input. Enter '$alch rs3' or '$alch osrs', followed by the desired profit per alch.")
        return
  elif version == "RS3" or version == "OSRS":
        try:
            margin = int(two)
            if margin <= 0:
                await ctx.send("Desired profit must be at least 1gp.")
                return
        except ValueError:
            await ctx.send("Incorrect input. Enter '$alch Rs3' or '$alch osrs', followed by the desired profit per alch.")
            return

        await ctx.send(getAlchProfits(margin, version))
        
          

@bot.command()
async def commands(ctx):
    user = await bot.fetch_user(ctx.author.id)
    await user.send("Commands: \n\n"
                   "$alch (**rs3**/**osrs**) (**amount**):\n"
                   "Lists all items in chosen version with a High Alch profit greater than or equal to a specified amount. Cannot be 0 or negative.\n\n"
                   "$commands:\n"
                   "View this message again.")
    return


with open("config.json", "r") as jsonfile:
    data = json.load(jsonfile)
    print("Read successful")
print(data)
bot.run(os.getenv("TOKEN"))
