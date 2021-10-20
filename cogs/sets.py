import discord
from discord.ext import commands
from tinydb import TinyDB, Query
import json
import math

setsPerPage = 10
class Sets(commands.Cog):
	def __init__(self,bot):
		self.bot = bot
		rawfile = open("sets.json")
		self.setData = json.loads(rawfile.read())
		print("Set module loaded.")



	async def get_completion(self,set,user):
		userNum = 0
		inv = self.bot.get_cog("Inventory")
		for i in set["items"]:
			if(await inv.has_item(user,i)):
				userNum += 1
		return userNum



	async def populate_set_list(self,user,embed,pageNum):
		embed.clear_fields()
		for i in range(pageNum*setsPerPage, (pageNum+1) * setsPerPage):
			if(i >= len(self.setData)):
				break
			currentSet = self.setData[i]
			embed.add_field(name=currentSet["name"],value="{0} of {1}".format(await self.get_completion(currentSet,user),len(currentSet["items"])))
		return embed

	async def find_set(self,to_find):
		for s in self.setData:
			if(s["name"].lower().startswith(to_find.lower())):
				return s
		return None


	@commands.command()
	async def setdetail(self,ctx,sett):
		caller = ctx.author
		refSet = await self.find_set(sett)
		gacha = self.bot.get_cog("Gacha")
		inventory = self.bot.get_cog("Inventory")
		if(refSet is None):
			await ctx.send("Couldn't find a set that starts with '{0}'".format(sett))
			return
		newEmbed = discord.Embed(title=refSet["name"],description="You have {0} out of {1} cards in this set.".format(await self.get_completion(refSet,caller),len(refSet["items"])))
		for card in refSet["items"]:
			b = ""
			if(await inventory.has_item(caller,card)):
				b = "**"
			newEmbed.add_field(name="{0} {1}{0}".format(b,card),value="[{0}]".format(gacha.get_stars(inventory.get_rarity(card))))
		await ctx.send(embed=newEmbed)

	@commands.command()
	async def exchange(self,ctx,sett):
		caller = ctx.author
		refSet = await self.find_set(sett)
		gacha = self.bot.get_cog("Gacha")
		inventory = self.bot.get_cog("Inventory")
		eco = self.bot.get_cog("Economy")
		if(refSet is None):
			await ctx.send("Couldn't find a set that starts with '{0}'".format(sett))
			return
		if(await self.get_completion(refSet,caller) != len(refSet["items"])):
			await ctx.send("You haven't completed that set!")
			return
		newEmbed = discord.Embed(title="Exchange Confirmation")
		toLose = ""
		for i in refSet["items"]:
			toLose += "1x {0}\n".format(i)
		toGet = ":llama:{0}\n{2}\n[{1}]".format(refSet["reward"],gacha.get_stars(6),refSet["rewardcard"])
		newEmbed.add_field(name="**You will lose:**",value=toLose)
		newEmbed.add_field(name="**You will get:**",value=toGet)

		msg = await ctx.send("{0.mention} please confirm the action.".format(caller),embed=newEmbed)
		await msg.add_reaction('✅')
		await msg.add_reaction('❌')
		def check(reaction,user):
			if(user == ctx.author):
				if(str(reaction.emoji) == '✅' or str(reaction.emoji) == '❌'):
					return True
		
		reaction,user = await self.bot.wait_for('reaction_add',timeout=60.0,check=check)
		if(str(reaction.emoji) == '✅'):
			await eco.deposit(caller,refSet["reward"])
			await inventory.add_items(caller,[refSet["rewardcard"]])
			for i in refSet["items"]:
				await inventory.remove_item(caller,i)
			await ctx.send("Exchange success!")
		else:
			await ctx.send("Action cancelled.")



	@commands.command()
	async def sets(self,ctx):
		totalSets = len(self.setData)
		print(len(self.setData))
		curPage = 0
		maxPage = math.floor(totalSets/setsPerPage)
		print(totalSets/setsPerPage)
		returnEmbed = discord.Embed(title="Available Sets",description="Page {0}/{1}".format(curPage+1,maxPage+1))
		returnEmbed = await self.populate_set_list(ctx.author,returnEmbed,curPage)
		msg = await ctx.send(embed=returnEmbed)
		await msg.add_reaction('⬅️')
		await msg.add_reaction('➡️')
		def check(reaction,user):
			if(user == ctx.author):
				if(str(reaction.emoji) == '➡️' or str(reaction.emoji) == '⬅️'):
					return True	
					
		while(True):
			try:
				reaction,user = await self.bot.wait_for('reaction_add',timeout=60.0,check=check)
			except:
				return

			if(reaction.emoji == '➡️' and curPage != maxPage):
				curPage += 1
			if(reaction.emoji == '⬅️' and curPage != 0):
				curPage -= 1
			returnEmbed.description = "Page {0}/{1}".format(curPage+1,maxPage+1)
			returnEmbed = await self.populate_set_list(ctx.author,returnEmbed,curPage)
			await msg.edit(embed=returnEmbed)	






