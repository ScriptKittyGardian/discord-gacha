import discord
from discord.ext import commands
from tinydb import TinyDB, Query
from tinydb.operations import set
import datetime

dailyAmount = 1000
users = TinyDB('users.json')
print("Users module loaded!")

class Users(commands.Cog):
	def __init__(self,bot):
		self.bot = bot


	def user_exists(self,id):
		toSearch = Query()
		results = users.search(toSearch.id == id)
		if(len(results) == 0):
			return False
		else:
			return True

	@commands.command()
	async def register(self,ctx):
		caller = ctx.author
		print("Registered {0}".format(caller))

		if(self.user_exists(caller.id)):
			await ctx.send("{0.mention}, you are already registered.".format(caller))
			return
		users.insert({'id' : caller.id, 'llamas' : 2000, 'lastdaily' : None})
		await ctx.send("{0.mention}, you are now registered.  Welcome to the party!".format(caller))
		
	@commands.command()
	async def daily(self,ctx,admonish=True):
		if(not self.user_exists(ctx.author.id)):
			return
		else:
			e = self.bot.get_cog("Economy")
			c = users.search(Query().id == ctx.author.id)
			lastDaily = c[0]["lastdaily"]
			shouldDeposit = False
			if(lastDaily == None):
				shouldDeposit = True
			else:
				lastDaily = datetime.datetime.strptime(lastDaily,"%d %m %y")
				if(lastDaily.date() < datetime.date.today()):
					shouldDeposit = True
			if(not shouldDeposit):
				if(admonish):
					await ctx.send("You have already claimed your daily today.")
				return
			elif(await e.deposit(ctx.author,dailyAmount)):
				users.update(set("lastdaily",datetime.date.today().strftime("%d %m %y")),Query().id == ctx.author.id)
				await ctx.send("You have claimed your daily bonus of :llama:**{0}**".format(dailyAmount))
			else:
				await ctx.send("Something went wrong!  Make sure you're registered and try again.")




	@commands.command()
	async def reroll(self,ctx):
		caller = ctx.author
		if(not self.user_exists(caller.id)):
			return
		msg = await ctx.send("{0.mention} are you absolutely, totally, 100% sure that you want to reroll your account?  All collected items will be lost.".format(caller))
		await msg.add_reaction('✅')
		await msg.add_reaction('❌')
		shouldDelete = False
		def check(reaction,user):
			if(user == ctx.author):
				if(str(reaction.emoji) == '✅' or str(reaction.emoji) == '❌'):
					return True
		
		reaction,user = await self.bot.wait_for('reaction_add',timeout=60.0,check=check)
		if(str(reaction.emoji) == '✅'):
			toKill = Query()
			users.remove(toKill.id == caller.id)
			inv = self.bot.get_cog("Inventory")
			await inv.reset_user(caller)
			await ctx.send("{0.mention} you have now been reset.".format(caller))
		else:
			await ctx.send("Action cancelled.")

