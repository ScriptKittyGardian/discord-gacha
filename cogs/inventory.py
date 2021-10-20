import discord
from discord.ext import commands
from tinydb import TinyDB, Query
from tinydb.operations import set
import os
import math
import re
inventories = TinyDB("useritems.json")
items = TinyDB("items.json")

imagedir = os.getcwd() + "/images/"
maxPerPage = 25
print("Inventory module loaded...  Woah, look at all this stuff.")

starRewards = [
10,
15,
25,
50,
100
]


refinementBonus = [
100,
200,
250,
300,
400,
1000
]



class Inventory(commands.Cog):
	def __init__(self,bot):
		self.bot = bot

	def get_rarity(self,card):
		item = items.search(Query().name == card)[0]
		return item["rarity"]

	async def init_user(self,user):
		q = Query()
		usr = inventories.search(q.id == user.id)
		if(len(usr) != 0):
			return
		inventories.insert({"id" : user.id,"inventory" : {}})

	async def remove_item(self,user,item):
		if(not await self.has_item(user,item)):
			return False
		userItems = inventories.search(Query().id == user.id)[0]["inventory"]
		userItems[item] -= 1
		if(userItems[item] <= 0):
			del userItems[item]
			inventories.update(set("inventory",userItems),Query().id == user.id)
		return True

	async def has_item(self,user,item):
		search = Query()
		try:
			usr = inventories.search(search.id == user.id)
			userInven = usr[0]["inventory"]
		except:
			return 0
		if(userInven.get(item) != None):
			return userInven.get(item)
		return 0

	async def reset_user(self,user):
		q = Query()
		inventories.remove(q.id == user.id)

	async def add_items(self,user,items,rewards=False):
		await self.init_user(user)
		q = Query()
		i = inventories.search(q.id == user.id)
		curItems = i[0]["inventory"]
		curKeys = curItems.keys()
		toReward = 0
		for item in items:
			a = curItems.get(item)
			tempRewards = 0
			if(rewards):
				tempRewards = starRewards[self.get_rarity(item)-1]
			if(a == None):
				curItems[item] = 1
			else:
				curItems[item] = curItems[item] + 1
				#tempRewards *= 4
			toReward += tempRewards
		if(rewards):
			await self.bot.get_cog("Economy").deposit(user,toReward)
		inventories.update(set("inventory",curItems), q.id == user.id)
		return toReward

	async def get_list_page(self,inven,page,embed):
		q = Query()
		invenKeys = await self.get_rarity_list(inven)
		embed.clear_fields()
		g = self.bot.get_cog("Gacha")
		for i in range(page*maxPerPage,(page+1)*maxPerPage):
			if(i < len(invenKeys)):
				curItem = invenKeys[i]
				i = items.search(q.name == curItem)
				item = i[0]
				embed.add_field(name="**{0}**".format(item["name"]),value="[{0}]\nRef Lvl: {1}".format(g.get_stars(item["rarity"]),inven[curItem]-1),inline=True)

		return embed

	async def get_rarity_list(self,inven):
		q = Query()
		invenKeys = list(inven.keys())
		storedRarities = {}
		sortedList = []
		for key in invenKeys:
			result = items.search(q.name == key)
			rarity = result[0]["rarity"]
			storedRarities[key] = rarity
			for k in range(0,len(sortedList) + 1):
				if(k < len(sortedList)):
					if(storedRarities[sortedList[k]] <= rarity):
						sortedList.insert(k,key)
						break
				else:
					sortedList.append(key)


		return sortedList




	@commands.command()
	async def list(self,ctx):
		q = Query()
		usr = inventories.search(q.id == ctx.author.id)
		userInven = usr[0]["inventory"]
		pgNum = 0
		userKeys = list(userInven.keys())
		maxPg = math.floor(len(userKeys)/maxPerPage)
		newEmbed = discord.Embed(title="{0}'s Collection".format(ctx.author.display_name),description="Page {0}/{1}".format(pgNum+1,maxPg+1))
		newEmbed = await self.get_list_page(userInven,pgNum,newEmbed)
		msg = await ctx.send(embed = newEmbed)

		if(maxPg == 0):
			return

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

			if(reaction.emoji == '➡️' and pgNum != maxPg):
				pgNum += 1
			if(reaction.emoji == '⬅️' and pgNum != 0):
				pgNum -= 1
			newEmbed.description = "Page {0}/{1}".format(pgNum+1,maxPg+1)
			newEmbed = await self.get_list_page(userInven,pgNum,newEmbed)
			await msg.edit(embed=newEmbed)


	@commands.command()
	async def completion(self,ctx):
		playerTotals = [0,0,0,0,0,0,0]
		toSend = discord.Embed(title="{0}'s collection progress.".format(ctx.author.display_name))
		toSend.set_thumbnail(url="https://cdn.discordapp.com/avatars/{0.id}/{0.avatar}.png?size=1024".format(ctx.author))
		playerInventory = inventories.search(Query().id == ctx.author.id)[0]["inventory"]
		playerInventory = list(playerInventory.keys())
		for item in playerInventory:
			currentRare = items.search(Query().name == item)[0]["rarity"]
			playerTotals[currentRare] += 1
		for s in range(1,7):
			totalNumber = len(items.search(Query().rarity == s))
			toSend.add_field(name="{0} Star Items:".format(s),value="{0} of {1}".format(playerTotals[s],totalNumber),inline=True)
		await ctx.send(embed=toSend)


	@commands.command()
	async def claimall(self,ctx):
		u = self.bot.get_cog("Users")
		await u.daily(ctx,False)
		q = Query()
		usr = inventories.search(q.id == ctx.author.id)
		userInven = usr[0]["inventory"]
		totalBonus = 0
		eco = self.bot.get_cog("Economy")
		for i in list(userInven.keys()):
			if(userInven[i] > 10):
				rewards = math.floor((userInven[i]-1) / 10)
				userInven[i] -= rewards * 10
				llamas = refinementBonus[self.get_rarity(i) - 1]
				await eco.deposit(ctx.author,llamas * rewards)
				totalBonus += llamas * rewards

		sendEmbed = discord.Embed(title="Refinement Rewards",description="For {0}".format(ctx.author.display_name))
		if(totalBonus == 0):
			sendEmbed.add_field(name="No Rewards to Claim",value="You need 10 refinement level to recieve a bonus.")
		else:
			sendEmbed.add_field(name="Rewards Claimed",value="You got :llama:{0}".format(totalBonus))
		inventories.update(set("inventory",userInven),Query().id == ctx.author.id)
		await ctx.send(embed=sendEmbed)

	@commands.command()
	async def ca(self,ctx):
		await self.claimall(ctx)



	@commands.command()
	async def summon(self,ctx,item):
		s = Query()
		bla = items.search(s.name.search(item,flags=re.IGNORECASE))
		found = False
		for b in bla:
			if(b["name"].lower().startswith(item.lower())):
				if(await self.has_item(ctx.author,b["name"])):
					item = b["name"]
					found = True
					break

		if(not found):
			await ctx.send("You do not have any items that start with '{0}'".format(item))
			return
		num = await self.has_item(ctx.author,item)
		if (num == 0):
			await ctx.send("You do not have that item.")
			return
		g = self.bot.get_cog("Gacha")
		q = Query()
		i = items.search(q.name == item)
		item = i[0]
		newEmbed = discord.Embed(title="{0}'s {1}\n [{2}]".format(ctx.author.display_name,item["name"],g.get_stars(item["rarity"])),description="Refinement level: {0}".format(num - 1))
		print(imagedir + item["image"])
		file = discord.File(imagedir + item["image"])
		newEmbed.set_image(url = "attachment://{0}".format(item["image"]))
		await ctx.send(embed = newEmbed,file=file)


