import json
import discord
class Helper:

	def __init__(self,prefix=".",file="commandinfo.json"):
		rawfile = open(file)
		self.commandcategories = json.loads(rawfile.read())
		self.prefix = prefix

	#Returns a dictionary object representing a command's help data
	def find_command(self,command):
		for category in self.commandcategories:
			for c in category['commands']:
				print(c['name'])
				if(c['name'].lower() == str(command).lower()):
					return c
		return None

	#Returns an embed containing detailed info on the command
	def get_detailed_info(self,command):
		commandobj = self.find_command(command)
		toReturn = discord.Embed(title="'{0}' Info".format(str(command)))

		if(commandobj == None):
			toReturn.add_field(name="Huh?",value="I don't recognize that command.")
		else:
			toReturn.add_field(name="Description",value=commandobj['helpdetail'])
			toReturn.add_field(name="Usage",value="{0}{1[name]} {1[usage]}".format(self.prefix,commandobj),inline=False)
		return toReturn

	#Returns an embed containing correct usage of the command
	def get_usage(self,command):
		commandobj = self.find_command(command)
		toReturn = discord.Embed(title=str(command) + " Usage",description = "{0}{1[name]} {1[usage]}".format(self.prefix,commandobj))
		return toReturn

	#Returns a formatted list of all commands in a given category object
	def get_category_help(self,category):
		toReturn = ""
		for c in category['commands']:
			toReturn += "**{0[name]} {0[usage]}**\t-\t{0[helptext]}\n".format(c)
		return toReturn

	#Returns an embed contaning all categories, their commands, and their short descriptions
	def get_help(self):
		toReturn = discord.Embed(title="Help",description="For more detailed info on a command, type {0}help <command>".format(self.prefix))
		for category in self.commandcategories:
			toReturn.add_field(name="**{0}**".format(category['name']),value=self.get_category_help(category),inline=False)
		return toReturn
