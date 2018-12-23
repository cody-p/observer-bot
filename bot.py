import discord
import asyncio
#import sqlite3

client = discord.Client()

global quickdelete_list
quickdelete_list = {}

global channel_modchat
global guild_home

def get_roleban_role(guild):
    for role in guild.roles:
        if role.name == "roleban":
            return role
    return None

def locate_channel(guild, channelName):
    for chan in guild.channels:
        if chan.name == channelName:
            return chan
    return None

def remove_prefix(text, prefix):
    return text[text.startswith(prefix) and len(prefix):]

@client.event
async def on_ready():
    print('logged in'.format(client))
    act = discord.Activity(type=discord.ActivityType.watching, name="everything")
    await client.change_presence(activity=act)
    
    
    global guild_home
    guild_home = None
    # This is currently a single server bot, so it breaks after finding the first one, assuming it's only one
    for guild in client.guilds:
        guild_home = guild;
        break;
        
    global channel_modchat;
    channel_modchat = locate_channel(guild, "mod-chat");
    if (channel_modchat == None):
        print("No mod-chat located in " + guild_home.name + ".");
    else:
        print("mod-chat located.")

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    global quickdelete_list
    global channel_modchat
    
    if message.content.startswith("=ping"):
        await message.channel.send("pong!")
        
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
\n`=timer` - creates a 3 minute timer, which pings the user when finished. Primarly meant for moderation purposes, \
but can be used by normal users if they have a reason. \
\n`=purge` - attempts to delete all messages in the channel. Requires manage_messages permission.\
\n\n__**Passive Features**__\
\nQuickdelete police - The bot will report messages that are deleted too quickly after being \
posted directly to the mod team. If there is no mod channel, the message will instead be reposted \
in the channel it was deleted from.\
\n\n__**Info**__\
\nGithub: https://github.com/cody-p/observer-bot")
                                   
    elif message.content.startswith('=toss'):
        perms = message.author.permissions_in(message.channel)
        
        # check if sender has permission to toss
        if perms.manage_roles:
            
            #find the roleban role
            roleban = get_roleban_role(message.guild)
            
            #role found
            if roleban:
                for member in message.mentions:
                    try:
                        await member.add_roles(roleban)
                        await message.channel.send("**" + member.name + "#" + member.discriminator + "** has been rolebanned.\n**ID**: " + str(member.id))
                    except discord.Forbidden:
                        await message.channel.send("I don't have permission to edit roles for this user!")
                        
            #role not found
            else:
                await message.channel.send("No roleban role.")
                
        # no perms
        else:
            await message.channel.send("You need manage_roles to use this command.")
    elif message.content.startswith("=untoss"):
        perms = message.author.permissions_in(message.channel)
        
        # check if sender has permission to toss
        if perms.manage_roles:
            
            #find the roleban role
            roleban = get_roleban_role(message.guild)
            
            #role found
            if roleban:
                for member in message.mentions:
                    try:
                        await member.remove_roles(roleban)
                        await message.channel.send("**" + member.name + "#" + member.discriminator + "** has been unrolebanned.")
                    except discord.Forbidden:
                        await message.channel.send("I don't have permission to edit roles for this user!")
                        
            #role not found
            else:
                await message.channel.send("No roleban role.")
                
        # no perms
        else:
            await message.channel.send("You need manage_roles to use this command.")

    # PURGE
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
    elif message.content.startswith("=timer"):
        await message.channel.send(":hourglass_flowing_sand:")
        print("set timer")
        await asyncio.sleep(180)
        msg = await message.channel.send(message.author.mention)
        await msg.edit(content=":hourglass:")
    elif message.content.startswith("=report"):
        await message.delete()
        if channel_modchat != None:
            report_message = "**__REPORT RECEIVED:__**\n\n" + remove_prefix(message.clean_content, "=report")
            await channel_modchat.send(report_message)
        else:
            await message.channel.send("This server currently doesn't accept anonymous reports.")
        
    # quickdelete police
    if not message.author.bot:
        quickdelete_list[message.id] = message
        await asyncio.sleep(10)
        quickdelete_list.pop(message.id, None)

@client.event
async def on_message_delete(message):
    global quickdelete_list
    if message.id in quickdelete_list:
        try:
            deletedText = quickdelete_list[message.id]
            descText = deletedText.clean_content
            # add attachments to description
            for attachment in deletedText.attachments:
                descText = descText + "\n<" + attachment.filename + ">"
            #create embed
            deletionEmbed = discord.Embed(description=descText)                
            deletionEmbed.set_author(name=message.author.name + " said...", icon_url=message.author.avatar_url) 
            
            global channel_modchat
            if channel_modchat == None:
                deletionEmbed.set_footer(text="This message was automatically re-sent because it was deleted too recently after it was sent. Please ask an administrator if you would like the post removed entirely.")
                await message.channel.send(embed=deletionEmbed)
            else:
                #TODO: add reacts to auto post in original channel
                deletionEmbed.set_footer(text="Quickdelete detected.")
                await channel_modchat.send(embed=deletionEmbed)
        except:
            await message.channel.send("There was a fucky wucky, asshole.")

#TODO: finish writing DB code
#init
#global userDB
#userDB = sqlite3.connect("./data/users")
#c = conn.cursor()

f=open("./token","r")
token = f.read().strip()
f.close()
client.run(token)

