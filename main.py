

from ircbot import IrcBot

# Set up your connection
server = raw_input("Enter the name of your server: ")
port = raw_input("Which port to use? (most commonly it is 6667, leave this blank to use that) ")
if port is "":
    port = 6667
buffer_size = raw_input("What size of buffer do you want to take from the socket? 2048 or 4096 are most common, leave blank for 4096: ")
if buffer_size is "":
    buffer_size = 4096

# Personalize your bot
nick = raw_input("What is your bot's name? ")
name = raw_input("What is its full name? ")
# this is important because you don't want any random to be sending some of the commands to the bot
# this is a list of names
print "Name some administrators (type 'done' to finish):"
admin_add = raw_input("> ")
admin_nicks = []
while admin_add is not "done":
    admin_nicks.append(admin_add)
    admin_add = raw_input("Alright, any more?\n>")

# a list of chat rooms to join
print "Name some chat rooms to join (including #; type 'done' to finish):"
room_add = raw_input("> ")
chat_rooms = []
while room_add is not "done":
    chat_rooms.append(room_add)
    room_add = raw_input("Alright, any more?\n>")

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
