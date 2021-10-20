import discord
import sqlite3 as sq
import bothelp
import cogs.general as general
import cogs.users as users
import cogs.economy as economy
import cogs.gacha as gacha
import cogs.inventory as inventory
import cogs.sets as sets
from discord.ext import commands
from datetime import datetime


token = "Nzg4MTM1NTY1MTM1NzA4MTgw.X9fGcQ.FxGUIa8vTa0y48GpF4MnUhNKDDY"

imagePath = "D:\\Amazing\\"

bot = commands.Bot(command_prefix=".",case_insesitive=True)
bot.remove_command("help")
bot.add_cog(general.General(bot))
bot.add_cog(users.Users(bot))
bot.add_cog(economy.Economy(bot))
bot.add_cog(gacha.Gacha(bot))
bot.add_cog(inventory.Inventory(bot))
bot.add_cog(sets.Sets(bot))
commandHelp = bothelp.Helper()


@bot.event
async def on_ready():
	print("Bot engaged.  Ready for combat.")


@bot.command()
async def ping(ctx):
	timeDelta = datetime.utcnow() - ctx.message.created_at
	await ctx.channel.send("Pong! Processed in {0}ms.".format(str(timeDelta.microseconds)[:2]))


@bot.command()
async def help(ctx,command=""):
	if(command == ""):
		await ctx.channel.send(embed=commandHelp.get_help())
	else:
		await ctx.channel.send(embed=commandHelp.get_detailed_info(command))

#@bot.event
#async def on_command_error(ctx,err):
#	if(not await bot.get_cog("Users").user_exists(ctx.author.id)):
#		await ctx.channel.send("Please register with !register first.")
#	elif(not isinstance(err,commands.CommandNotFound)):
#		print(err)
#		await ctx.channel.send(embed=commandHelp.get_usage(ctx.command))

@bot.listen()
async def on_message(message):
	if(len(message.content) < 5):
		return
	await bot.get_cog("Economy").calculate_handout(message)

bot.run(token)
