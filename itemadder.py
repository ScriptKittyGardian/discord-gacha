from tinydb import TinyDB, Query



items = TinyDB("items.json")

while True:
	rarity = int(input("Entry rarity (1-5):"))
	name = str(input("Entry name:"))
	image = input("Entry image name:")
	items.insert({"rarity" : rarity,"name" : name,"image" : image})
