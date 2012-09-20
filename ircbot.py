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

    """

    def __init__(self, server, port, nick, full_name):
        self.server = server
        self.port = port
        self.nick = nick
        self.full_name = full_name
        self.botQuit = False
        self._irc = None

    def register(self):
        """
        4.1.3 User message

        Command:	USER
        Parameters:	<username> <hostname> <servername> <realname>

        4.1.2 Nick message

        Command:	NICK
        Parameters:	<nickname> [ <hopcount> ]
        """
        #TODO: make password generic, and make it work how about
#        self._irc.send("PASS grahamtest")
        self.send_data("USER " + self.nick + " " + self.nick +
                      " " + self.server + " :" + self.full_name)
        self.send_data("NICK " + self.nick)

    def connect_irc(self):
        """
        Connects to the IRC server specified in the constructor. socket.connect uses a tuple containing the server
        and port info.
        """
        self._irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._irc.connect((self.server, self.port))

    def ping(self, recipient):
        self._irc.send("PING %s\n" % recipient)

    def pong(self):
        self._irc.send("PONG " + self.nick + "\n")

    def join(self, channel, password=""):
        """
        4.2.1 Join message

        Command:	JOIN
        Parameters:	<channel>{,<channel>} [<key>{,<key>}]

        Accepts comma separated groups of channels to join and the passwords for those channels
        """
        self._irc.send("JOIN " + channel + " " + password + "\n")

    def send_data(self, data):
        """
        Sends raw data to the socket.
        """
        self._irc.send(data)

    def receive_data(self, buffer_size=4096):
        """
        Gets raw data from the socket
        """
        return self._irc.recv(buffer_size)

    def quit(self, channel=None, msg=None):
        if msg != None:
            self.send_message(channel, msg)

        self.send_data("QUIT" + "\n")
        self.botQuit = True
        # close connection
        self._irc.close()

    def send_message(self, receiver, message):
        """
        4.4.1 Private messages

        Command:	PRIVMSG
        Parameters:	<receiver>{,<receiver>} <text to be sent>

        PRIVMSG is used to send private messages between users. <receiver>
         is the nickname of the receiver of the message. <receiver> can also
         be a list of names or channels separated with commas.
        """
        self._irc.send("PRIVMSG " + receiver + " :" + message)

    def check_commands(self, data):
        """
        Accepts a list [] of commands sent to it by IRC server, and operates
        accordingly
        """
        #TODO: Remove debugging message
        #print data
        for cmd in data:
            if data.__len__() >= 3 and cmd == data[3]:
                if cmd == ":!gtfo":
                    self.send_data("PART " + data[2] + "\n")
                if cmd == ":!join":
                    if data.__len__() >= 5:
                        self.join(data[4])
                if cmd == ":!die":
                    self.quit()

            if cmd == "PING":
                self.pong()

            if cmd == "ERROR":
                if data[1] == ":Closing":
                    self.quit()

    def should_quit(self):
        return self.botQuit

    def get_data(self, buffer_size=4096):
        """
        Gets data from the socket. This needs to occur as often as possible, because "data" can be anything from
        server messages to chat messages and beyond. This method takes in the data as a string from the socket
        and returns it to the calling party.
        """
        data = self.receive_data(buffer_size)
        data = data.rstrip("\r\n")
        return data



#====Connection info====#
server = "irc.utonet.org"
port = 6667
nick = "LonelyBot"
name = "Lonely Island Bot"

#====MAIN====#
bot = IrcBot(server, port, nick, name)
bot.connect_irc()
bot.register()
bot.join("#LonelyIsland")

#====MAIN LOOP====#
while not bot.should_quit():
    try:
        #Receive data from the irc socket
        data = bot.get_data()
        #Print data received for debugging
        print(data)
        #Check to see if there's anything we can do with it :)
        bot.check_commands(data.split(" "))
    except IOError:
        bot.quit()

