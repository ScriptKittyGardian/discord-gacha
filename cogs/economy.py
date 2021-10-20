import discord
from discord.ext import commands
from tinydb import TinyDB, Query
from tinydb.operations import subtract, add
import random
users = TinyDB('users.json')
print("Economy module loaded, kaching!")


handoutChance = 5
handoutAmount = 50
class Economy(commands.Cog):
	def __init__(self,bot):
		self.bot = bot
		random.seed()
	
	async def get_balance(self,user):
		toSearch = Query()
		results = users.search(toSearch.id == user.id)
		if(len(results) == 0):
			return 0
		else:
			return results[0]['llamas']

	@commands.command()
	async def balance(self,ctx):
		caller = ctx.author
		economy = self.bot.get_cog('Economy')

		u = self.bot.get_cog("Users")
		if(u.user_exists(caller.id) != True):
			await u.register(ctx)

		bal =  await self.get_balance(caller)
		toReturn = discord.Embed(title="{0}".format(caller.display_name))
		toReturn.add_field(name="Llama Balance",value=":llama:{0}".format(bal))
		await ctx.send(embed=toReturn)

	@commands.command()
	async def bal(self,ctx):
		await self.balance(ctx)

	async def calculate_handout(self,message):
		caller = message.author
		u = self.bot.get_cog("Users")
		if(u.user_exists(caller.id) == True):
			if(random.randint(0,100) < handoutChance):
				await self.deposit(caller,handoutAmount)
				await message.channel.send("Congratulations {0.mention} you got {1} free llamas.".format(caller,handoutAmount))

	async def withdraw(self,user,amount):
		bal = await self.get_balance(user)
		print("Testing for {0}".format(amount))
		print(bal)
		if(bal < amount):
			return False
		u = Query()
		users.update(subtract('llamas',amount), u.id == user.id)
		return True

	async def deposit(self,user,amount):
		users.update(add('llamas',amount), Query().id == user.id)
		return True