import discord
import asyncio
#import sqlite3

client = discord.Client()

global quickdelete_list
quickdelete_list = {}

def get_roleban_role(guild):
    for role in guild.roles:
        if role.name == "roleban":
            return role
    return None
    
@client.event
async def on_ready():
    print('logged in'.format(client))
    act = discord.Activity(type=discord.ActivityType.watching, name="everything")
    await client.change_presence(activity=act)

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    global quickdelete_list
    if message.content.startswith("=ping"):
        await message.channel.send("pong!")
        
    elif message.content.startswith("=help"):
        await message.channel.send(\
"__**The Observer**__\
\n\n**=ping** - replies with 'pong!'\
\n**=toss** - locks a user in #quarantine\
\n**=untoss** - removes a user from #quarantine\
\n**=timer** - creates a 3 minute timer, used for testing responsiveness in #quarantine\
\n**=purge** - attempts to delete all messages in the channel\
\n\n**Github:** <https://github.com/cody-p/observer-bot>")
                                   
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
                        await message.channel.send("**" + member.name + "#" + member.discriminator + "** has been rolebanned in #" + message.channel.name + " by **" + message.author.name + "**.")
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
                        await message.channel.send("**" + member.name + "#" + member.discriminator + "** has been unrolebanned in #" + message.channel.name + " by **" + message.author.name + "**.")
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
            deletionEmbed.set_footer(text="This message was automatically re-sent because it was deleted too recently after it was sent. Please ask an administrator if you would like the post removed entirely.")
            await message.channel.send(embed=deletionEmbed)
        except:
            await message.channel.send("There was a fucky wucky, asshole.")

#TODO: finish writing DB code
#init
#global userDB
#userDB = sqlite3.connect("./data/users")
#c = conn.cursor()

f=open("./token","r")
token = f.read()
f.close()
client.run(token)

