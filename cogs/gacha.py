import discord
from discord.ext import commands
from tinydb import TinyDB, Query
import random
import os


print("Gacha module loaded, feeling lucky!")
items = TinyDB("items.json")
imagedir = os.getcwd() + "/images/"
starRates = [
	50,
	75,
	89,
	97,
	100
	]

pullCost = 100
class Gacha(commands.Cog):
	def __init__(self,bot):
		self.bot = bot
		random.seed()

	def get_stars(self,num):
		toReturn = ""
		for i in range(0,5):
			if(i < num):
				toReturn += ":star:"
			else:
				toReturn += " - "
		if(num == 6):
			toReturn += ":star:"
		return toReturn


	async def get_pull(self):
		pullNum = random.randint(0,100)
		print(pullNum)
		for i in range(0,len(starRates)):
			if(pullNum <= starRates[i]):
				star = i + 1
				break
		item = Query()
		possibleItems = items.search(item.rarity == star)
		toReturn = possibleItems[random.randint(0,len(possibleItems)-1)]
		return toReturn["name"]

	@commands.command()
	async def rates(self,ctx):
		toSend = "The rates are:\n"
		for r in range(0,len(starRates)):
			if(r == 0):
				toSend += "1 stars: {0}%\n".format(starRates[r])
			else:
				toSend += "{0} stars: {1}%\n".format(r+1,starRates[r] - starRates[r-1])
		await ctx.send(toSend)


	@commands.command()
	async def pull(self,ctx,times=1):
		economy = self.bot.get_cog("Economy")
		inv = self.bot.get_cog("Inventory")

		if(times > 25):
			await ctx.send("Sorry, you cannot pull more than 25 times at once.")
			return

		success = await economy.withdraw(ctx.author,times * pullCost)
		if(success != True):
			await ctx.send("Insufficient llamas.")
			return
		toReturn = []
		returnEmbed = discord.Embed(title="{0.display_name}'s {1} pull attempt.".format(ctx.author,times))

		biggestStar = None
		items = []
		rarest = 0
		for i in range(0,times):
			item = await self.get_pull()
			#toReturn.append()
			rare = inv.get_rarity(item)
			returnEmbed.add_field(name="**{0}**".format(item),value="[{0}]".format(self.get_stars(rare),inline=True))
			if(biggestStar == None):
				biggestStar = item
			elif(rarest < rare):
				biggestStar = item
				rarest = rare
			items.append(item)
		rew = await inv.add_items(ctx.author,items,True)
		returnEmbed.description = "You got :llama:{0} as a bonus.".format(rew)
		returnEmbed.set_thumbnail(url="https://cdn.discordapp.com/avatars/{0.id}/{0.avatar}.png?size=1024".format(ctx.author))
		#returnEmbed.set_image()

		await ctx.send(embed = returnEmbed)
		await inv.summon(ctx,biggestStar)




