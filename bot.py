import discord
import asyncio
import configparser
import random
import os.path

#classes ==================================================
class UserCache:
	rolebanned = False
	roles = []
	
#load config ==============================================
def init_config():
	global botConfig
	botConfig = configparser.ConfigParser()
	botConfig['BOT_SETTINGS'] = {'TossRole': 'roleban', 'MinDeleteTime': 8, 'MaxDeleteTime': 12 }
	botConfig['CHANNELS'] = {'ModChat': 'mod-chat', 'QuickDelete': ""}
					
	if os.path.isfile("config.ini"):		 
		botConfig.read("config.ini")
	else:
		with open("config.ini", "w") as configfile:
			botConfig.write(configfile)

	return True;

if not init_config():
	print("Config error.")

#variables ================================================
client = discord.Client()
global quickdelete_list
quickdelete_list = {}
global channel_modchat
global channel_quickdelete
global guild_home
global user_cache
user_cache = dict()

#functions ================================================
def locate_channel(guild, channelName):
	for chan in guild.channels:
		if chan.name == channelName:
			return chan
	return None

def remove_prefix(text, prefix):
	return text[text.startswith(prefix) and len(prefix):]

def apply_config():
	global guild_home
	global channel_modchat;
	global channel_quickdelete
	global roleban
	
	channel_modchat = locate_channel(guild_home, botConfig['CHANNELS']['ModChat']);
	if (channel_modchat == None):
		print("No " + botConfig['CHANNELS']['ModChat'] + " located in " + guild_home.name + ".");
	else:
		print(botConfig['CHANNELS']['ModChat'] + " located.")  
	
	channel_quickdelete = locate_channel(guild_home, botConfig['CHANNELS']['QuickDelete']);
	if (channel_quickdelete == None):
		print("No " + botConfig['CHANNELS']['QuickDelete'] + " located in " + guild_home.name + ".");
	else:
		print(botConfig['CHANNELS']['QuickDelete'] + " located.")
	  
	#find the roleban role
	for role in guild_home.roles:
		if role.name == botConfig['BOT_SETTINGS']['TossRole']:
			roleban = role
			break
	
	return True
#events ===================================================
@client.event
async def on_ready():
	print('logged in'.format(client))
	act = discord.Activity(type=discord.ActivityType.watching, name="for =help")
	await client.change_presence(activity=act)
	
	global guild_home
	guild_home = None
	# This is currently a single server bot, so it breaks after finding the first one, assuming it's only one
	for guild in client.guilds:
		guild_home = guild;
		break;
		
	apply_config()

@client.event
async def on_message(message):
	if message.author == client.user:
		return
	
	global quickdelete_list
	global channel_modchat
	global botConfig
	global roleban
	global user_cache
	
	if message.content.startswith("=ping"):
		await message.channel.send("pong!")
	
	# HELP ========================================================================================
	elif message.content.startswith("=help"):
		await message.channel.send(\
"\n\n__**User commands**__\
\n`=ping` - replies with 'pong!'\
\n`=report` - Send an anonymous report to server staff. It will be deleted from the channel of sending immediately. \
Currently does not support images.\
\n\n__**Mod commands**__\
\n`=toss` - Applies the `roleban` role to mentioned users. Planned to remove other roles in the future. \
Can only be used by users with the manage_roles permission.\
\n`=untoss` - Removes the `roleban` role from mentioned users (and will restore their roles when role \
removal is implemented).\
\n`=timer` - Creates a 3 minute timer, which pings the user when finished. Primarly meant for moderation purposes, \
but can be used by normal users if they have a reason. \
\n`=purge` - Attempts to delete all messages in the channel. Requires manage_messages permission.\
\n`=reload` - Reloads the bot's config file. Requires manage_server permission.\
\n\n__**Passive Features**__\
\nQuickdelete police - The bot will report messages that are deleted too quickly after being \
posted directly to the mod team. If there is no mod channel, the message will instead be reposted \
in the channel it was deleted from.\
\n\n__**Info**__\
\nGithub: https://github.com/cody-p/observer-bot")
								   
	# TOSS ========================================================================================
	elif message.content.startswith('=toss'):
		perms = message.author.permissions_in(message.channel)
		
		# check if sender has permission to toss
		if perms.manage_roles:
			
			#role found
			if roleban:
				for member in message.mentions:
					already_tossed = False
					for role in member.roles:
						if role == roleban:
							already_tossed = True
							break
							
					if not already_tossed:
						try:
							print("Asked to toss " + str(member.id))
							user_cache[member.id] = member.roles
							# The first role is always the everyone role, which can't be removed
							user_cache[member.id].pop(0)
							can_toss = True
							role_names = []
							for role in user_cache[member.id]:
								role_names.append(role.name)
								print(role.name)
								if role.managed:
									can_toss = False
									break
							if can_toss:
								await member.remove_roles(*user_cache[member.id], reason="Rolebanned")
								await member.add_roles(roleban)
								await message.channel.send("**" + member.name + "#" + member.discriminator + "** has been \
rolebanned.\n**ID**: " + str(member.id) + "\n**Roles**: " + str(role_names))
								print("Tossed successfully.")
							else:
								print("Failed to toss because user has integrated roles.")
								await message.channel.send("This user has integrated roles that I can't remove. Deal with them yourself.")
								user_cache.pop(member.id, None)
						except discord.Forbidden:
							print("Failed to toss: error 403 (forbidden)")
							await message.channel.send("I'm not powerful enough to toss this user.")
					else:
						await message.channel.send(member.name + "#" + member.discriminator + " is already rolebanned.")
			#role not found
			else:
				await message.channel.send("No roleban role.")
				
		# no perms
		else:
			await message.channel.send("You need manage_roles to use this command.")
			
	#UNTOSS =======================================================================================
	elif message.content.startswith("=untoss"):
		perms = message.author.permissions_in(message.channel)
		
		# check if sender has permission to toss
		if perms.manage_roles:		
			#role found
			if roleban:
				for member in message.mentions:
					
					print("Asked to untoss " + str(member.id))
					tossed = False
					for role in member.roles:
						if role == roleban:
							tossed = True
							break
					if tossed:
						try:
							if user_cache[member.id] and len(user_cache[member.id]) > 0:
								await member.add_roles(*user_cache[member.id], reason="Unrolebanned")
							await member.remove_roles(roleban)
							role_names = []
							for role in user_cache[member.id]:
								role_names.append(role.name)
							await message.channel.send("**" + member.name + "#" + member.discriminator + "** has been unrolebanned.\
							\n**Roles restored**: " + str(role_names))
							print("Untossed successfully.")
							user_cache.pop(member.id, None)
						except discord.Forbidden:
							print("Failed to untoss: error 403 (forbidden)")
							await message.channel.send("I don't have permission perform this operation.")
					else:
						print("They were already untossed.")
						await message.channel.send(member.name + "#" + member.discriminator + " is not currently rolebanned.")
						
			#role not found
			else:
				await message.channel.send("No roleban role.")
				
		# no perms
		else:
			await message.channel.send("You need manage_roles to use this command.")

	# PURGE =======================================================================================
	elif message.content.startswith("=purge"):
		perms = message.author.permissions_in(message.channel)
		if perms.manage_messages:
			try:
				delete_list = []
				
				#gather message history
				async for message in message.channel.history():
					delete_list.append(message)
					quickdelete_list.pop(message.id, None)
					
				await message.channel.delete_messages(delete_list)
				# send message telling how many were deleted
				await message.channel.send("`" + str(len(delete_list)) + "`", delete_after = 3)
			except discord.Forbidden:
				await message.channel.send("I don't have permission to delete messages.")
		else:
			await message.channel.send("You need manage_messages to use this command.")
		return
	
	# TIMER =======================================================================================
	elif message.content.startswith("=timer"):
		await message.channel.send(":hourglass_flowing_sand:")
		print("set timer")
		await asyncio.sleep(180)
		msg = await message.channel.send(message.author.mention)
		await msg.edit(content=":hourglass:")
	
	# REPORT ======================================================================================
	elif message.content.startswith("=report"):
		await message.delete()
		if channel_modchat != None:
			report_message = "**__REPORT RECEIVED:__**\n\n" + remove_prefix(message.clean_content, "=report")
			await channel_modchat.send(report_message)
		else:
			await message.channel.send("This server currently doesn't accept anonymous reports.")
	
	# RELOAD ======================================================================================
	elif message.content.startswith("=reload"):
		async with message.channel.typing():
			perms = message.author.permissions_in(message.channel)
			if perms.manage_guild:
				if init_config() and apply_config():
					await message.channel.send("Reloaded config!")
				else:
					await message.channel.send("There was an error loading the config.")
			else:
				await message.channel.send("You don't have permission to do that!")
			
	# quickdelete police ==========================================================================
	if not message.author.bot:
		quickdelete_list[message.id] = message
		await asyncio.sleep(random.randint(int(botConfig['BOT_SETTINGS']['MinDeleteTime']), int(botConfig['BOT_SETTINGS']['MaxDeleteTime'])))
		quickdelete_list.pop(message.id, None)

@client.event
async def on_message_delete(message):
	global quickdelete_list
	if message.id in quickdelete_list:
		deletedText = quickdelete_list[message.id]
		descText = deletedText.clean_content
		# add attachments to description
		for attachment in deletedText.attachments:
			descText = descText + "\n<" + attachment.filename + ">"
		#create embed
		deletionEmbed = discord.Embed(description=descText)				
		deletionEmbed.set_author(name=message.author.name + " said...", icon_url=message.author.avatar_url) 
		
		global channel_modchat
		if channel_quickdelete == None:
			deletionEmbed.set_footer(text="This message was automatically re-sent because it was deleted too recently \
			after it was sent. Please ask an administrator if you would like the post removed entirely.")
			await message.channel.send(embed=deletionEmbed)
		else:
			#TODO: add reacts to auto post in original channel
			deletionEmbed.set_footer(text="Quickdelete detected.")
			await channel_modchat.send(embed=deletionEmbed)

#TODO: finish writing DB code
#init
#global userDB
#userDB = sqlite3.connect("./data/users")
#c = conn.cursor()

f=open("./token","r")
token = f.read().strip()
f.close()
client.run(token)

