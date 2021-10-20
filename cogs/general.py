import discord
from discord.ext import commands
from tinydb import TinyDB, Query


print("General module loaded!")
class General(commands.Cog):
	def __init__(self,bot):
		self.bot = bot
		
	@commands.command()
	async def hellothere(self,ctx):
		await ctx.send("General Kenobe!")
