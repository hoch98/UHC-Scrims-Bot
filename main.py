import requests, random
import discord, os
from discord.utils import get
from discord.ext import commands

ranks = {
    "Unranked": [0, 49],
    "Rookie": [50, 99],
    "Iron": [100, 249],
    "Gold": [250, 499],
    "Diamond": [500, 999],
    "Master": [1000, 1999],
    "Legend": [2000, 4999],
    "Grandmaster": [5000, 9999],
    "Godlike": [10000, 24999],
    "Celestial": [25000, 49999],
    "Divine": [50000, 99999],
    "Ascended": [100000, 100000000000000000],
}

user_agents = requests.get("https://gist.githubusercontent.com/pzb/b4b6f57144aea7827ae4/raw/cf847b76a142955b1410c8bcef3aabe221a63db1/user-agents.txt").content.decode("utf-8").split("\n")
user_agents.pop(1000)

def compare(total):
    for prop in ranks.keys():
        if ranks[prop][0] <= total and ranks[prop][1] >= total:
            return prop

def getInfo(name):
    try:
        html = requests.get("https://plancke.io/hypixel/player/stats/"+name, headers={"User-Agent": random.choice(user_agents)}).content.decode("utf-8")
        substr1 = html[html.index("UHC 1v1")+16:html.index("UHC 2v2")].split("</td><td>")
        v1wins = substr1[3].replace(",", "")
        substr2 = html[html.index("UHC 2v2")+16:html.index("UHC 4v4")].split("</td><td>")
        v2wins = substr2[3].replace(",", "")
        substr3 = html[html.index("UHC 4v4")+16:html.index("UHC Deathmatch")].split("</td><td>")
        v3wins = substr3[3].replace(",", "")
        substr4 = html[html.index("UHC Deathmatch")+23:html.index("OP 1v1")].split("</td><td>")
        v4wins = substr4[3].replace(",", "")

        total = int(v1wins)+int(v2wins)+int(v3wins)+int(v4wins)
        division = compare(total)
        discordcut = html[html.index("Discord")+11:len(html)-1]
        discord = html[html.index("Discord")+11:html.index("Discord")+11+discordcut.find("\r\n")-3]
        return 1, [division, discord]
    except ValueError:
        return 0, []

bot = commands.Bot(command_prefix="!", description="UHC Scrims Bot")

@bot.event
async def on_ready():
    print("The UHC Scrims Bot is now up and running!")

@bot.command(name="verify")
async def verify(ctx, arg1):
  print("detected")
  users = []
  with open("userdata.txt", "r") as file:
    content = file.read()
    print(content)
    content = content.split("\n")
    users = content
  tags = []
  for user in users:
    user = user.split("||")
    print(user)
    if len(user) == 3:
      tags.append(user[1])
  print(tags)
  if str(ctx.author) in tags:
    await ctx.send("You are already verified!")
  else:
    success, data = getInfo(str(arg1))
    if success == 0:
      await ctx.send("You haven't linked your discord!")
    else:
      if str(data[1]) == str(ctx.author):
        division = data[0]
        if division != "Unranked":
          role = get(ctx.guild.roles, name=division)
          await ctx.author.add_roles(role)
          await ctx.send("Gave you "+str(division))
          with open("userdata.txt", "a") as file:
            file.write(str(arg1)+"||"+str(data[1])+"||"+str(data[0]))
            file.write("\n")
            file.close()
        await ctx.send("You have succesfully verified!")
      else:
        await ctx.send(str(arg1)+"'s profile is linked to a different Discord account!")

@verify.error
async def verify_error(ctx, error):
  if isinstance(error, commands.MissingRequiredArgument):
    await ctx.send("Correct Syntax: !verify <IGN>")

@bot.command(name="update")
async def update(ctx):
  users = []
  with open("userdata.txt") as file:
    content = file.read()
    content = content.split("\n")
    for c in content:
      users.append(c.split("||"))

  for user in users:
    print(user)
    if len(user) == 3:
      if user[1] == str(ctx.author):
        role = get(ctx.guild.roles, name=user[2].replace("\n", ""))
        await ctx.author.remove_roles(role)
        success, data = getInfo(str(user[0]))
        role = get(ctx.guild.roles, name=data[0])
        await ctx.author.add_roles(role)
        await ctx.send("Updated your role!")
        return True
  await ctx.send("You are not verified!")

bot.run(os.environ.get("key"))
