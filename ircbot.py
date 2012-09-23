#!/usr/bin/env python
########################################
#                                      #
#           gIRCBot                    #
#        by Graham Holtslander         #
#                                      #
#            adapted from:             #
#          IRC Bot Skeleton            #
#           by den5e. 2012             #
#                                      #
########################################

import socket
import time


class IrcBot(object):
    #TODO: Class __doc__ notes
    """
    IRCBot that can connect to an IRC server using an address and port.
    The IRCBot has many methods and variables to help you out, discussed in their respective doc notes
    """

    def __init__(self, server, port, nick, full_name, admin_nick):
        """
        server - the server to connect to (ex: irc.utonet.org)
        port - the port of the server to join (almost always 6667)
        nick - the nick the bot will have, and what it can be addressed by
        master - a user (or users) who has "admin" control over the bot
        full_name - only used for the server join process really
        botQuit - whether or not the bot should quit/leave the server
        __irc - the socket that is connected to the server - private
        __channels - a list containing all the channels the bot is connected to - private
        __history - a list of every line that the bot has read in from the socket
        """
        self.server = server
        self.port = port
        self.nick = nick
        self.master = admin_nick
        self.full_name = full_name
        self.botQuit = False
        self.__irc = None
        self.__channels = []
        self.__history = []

    def register(self):
        """
        4.1.3 User message

        Command:	USER
        Parameters:	<username> <hostname> <servername> <realname>

        4.1.2 Nick message

        Command:	NICK
        Parameters:	<nickname> [ <hopcount> ]
        """
        self.send_data("USER " + self.nick + " " + self.nick +
                      " " + self.server + " :" + self.full_name + "\r\n")
        self.send_data("NICK " + self.nick + "\r\n")

    def connect_irc(self):
        """
        Connects to the IRC server specified in the constructor. socket.connect uses a tuple containing the server
        and port info.
        """
        self.__irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__irc.connect((self.server, self.port))

    def ping(self, recipient):
        """
        Sends a ping to the recipient
        """
        ping_send = "PING %s" % recipient
        print ping_send
        self.__irc.send(ping_send + "\r\n")

    def pong(self, target=":Pong"):
        """
        Responds to a ping
        """
        pong_send = "PONG %s" % target
        print pong_send
        self.__irc.send(pong_send + "\r\n")

    def join(self, channel, password=""):
        """
        4.2.1 Join message

        Command:	JOIN
        Parameters:	<channel>{,<channel>} [<key>{,<key>}]

        Accepts comma separated groups of channels to join and the passwords for those channels
        """
        self.__channels.append(channel)
        self.__irc.send("JOIN " + channel + " " + password + "\r\n")

    def send_data(self, data):
        """
        Sends raw data to the socket.
        """
        self.__irc.send(data)

    def __receive_data(self, buffer_size=4096):
        """
        Gets raw data from the socket
        """
        data = self.__irc.recv(buffer_size)
        while data.find('\r\n') == -1:
            data += self.__irc.recv(buffer_size)

        return data

    def quit(self, channel=None, msg=None):
        """
        This method can accomplish a few things. 1) Quit a channel and give a message as to why you're quitting,
        2) Quit a channel without a message, and 3) quit the server altogether
        """
        if msg is not None and channel is not None:
            self.send_data("QUIT " + channel + " :" + msg + "\r\n")
        elif channel is not None:
            self.send_data("QUIT " + channel + "\r\n")
        else:
            self.send_data("QUIT" + "\r\n")
            self.botQuit = True
        # close connection
            self.__irc.close()

    def send_message(self, receiver, message):
        """
        4.4.1 Private messages

        Command:	PRIVMSG
        Parameters:	<receiver>{,<receiver>} <text to be sent>

        PRIVMSG is used to send private messages between users. <receiver>
         is the nickname of the receiver of the message. <receiver> can also
         be a list of names or channels separated with commas.
        """
        self.__irc.send("PRIVMSG " + receiver + " :" + message)

    def is_admin(self, user_nick):
        """
        Checks if the nick passed in is on the "masters" list. Some commands require
        a nickname to have "administrative" privileges
        """
        return user_nick in self.master

    def _dialogue(self, line):
        """
        Accepts a line from the chat that contains PRIVMSG. This means that there should
        be some response from the bot to the people in the server or to a specific person.
        This method contains a lot of logic, thus it is broken out from check_commands
        """
        if line.split(' ')[2] in self.__channels:
            # we're in a channel, start checking for commands
            if line.find("!quit"):


    def check_commands(self, data):
        """
        Accepts a string of commands sent to it by IRC server, and operates
        accordingly
        """
        nothings = 0
        self.__history.append(data)
        print data
        for line in data.split('\n'):
            if "ERROR" in line:
                print "Error, disconnecting"
                #TODO: think of some reconnection logic here
                self.quit()
            elif "PRIVMSG" in line:
                self._dialogue(line)
            elif line[0:4] == "PING":
                self.pong(line.split()[1])
            else:
                nothings += 1

        if nothings is not 0:
            print "Nothing to do with %s lines" % nothings

    def search_history(self, query):
        for line in self.__history:
            if line.find(query) != -1:
                return True

    def should_quit(self):
        return self.botQuit

    def get_data(self, buffer_size=4096):
        """
        Gets data from the socket. This needs to occur as often as possible, because "data" can be anything from
        server messages to chat messages and beyond. This method takes in the data as a string from the socket
        and returns it to the calling party.
        """
        data = self.__receive_data(buffer_size)
        return data.strip('\r\n')


# Set up your connection
server = "irc.utonet.org"
port = 6667
buffer_size = 2048

# Set up your bot
nick = "LonelyBot"
name = "Lonely Island Bot"
# this is important because you don't want any random to be sending some of the commands to the bot
# this is a list of names (eventually)
admin_nick = ["Tenotitwan", "TenotitwanWork"]
# if more than one person should have admin powers, make the above line look like this:
chat_room = "#LonelyIsland"
#chat_room2 = "#LonelyIslandAttackers"
# etc.

# Create new instance of bot, connect to designated server, grab some data
bot = IrcBot(server, port, nick, name, admin_nick)
bot.connect_irc()
bot.register()
data = bot.get_data(buffer_size)

# Get connected to the server
#TODO: Find a way to make this a lot better
while bot.search_history("Welcome to UtoNet") is not True:
    bot.check_commands(data)
    data = bot.get_data(buffer_size)

# Connect to your chat room(s)
bot.join(chat_room)
# if you have more rooms to join:
print "Getting here?"
#bot.join(chat_room2)
# etc.

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
