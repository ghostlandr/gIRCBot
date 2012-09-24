

from ircbot import IrcBot

# Set up your connection
server = "irc.utonet.org"
port = 6667
buffer_size = 2048

# Set up your bot
nick = "LonelyBot"
name = "Lonely Island Bot"
# this is important because you don't want any random to be sending some of the commands to the bot
# this is a list of names
admin_nicks = ["Tenotitwan", "TenotitwanWork"]
# a list of chat rooms to join
chat_rooms = ["#LonelyIsland"]

# Create new instance of bot, connect to designated server, grab some data
bot = IrcBot(server, port, nick, name, admin_nicks)
bot.connect_irc()
bot.register()
data = bot.get_data(buffer_size)

# Get connected to the server
#TODO: Find a way to make this a lot better
while bot.search_history("Logon News") is not True:
    bot.check_commands(data)
    data = bot.get_data(buffer_size)

# Connect to your chat room(s)
for room in chat_rooms:
    bot.join(room)

#====MAIN LOOP====#
while 1:
    #Receive data from the irc socket
    data = bot.get_data(buffer_size)
    #if length is 0 we got disconnected
    if data.__len__ == 0:
        break
        #Check to see if there's anything we can do with it :)
    bot.check_commands(data)

# Disconnect for good
bot.quit()
