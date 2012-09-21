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
        self.__irc = None

    def register(self):
        """
        4.1.3 User message

        Command:	USER
        Parameters:	<username> <hostname> <servername> <realname>

        4.1.2 Nick message

        Command:	NICK
        Parameters:	<nickname> [ <hopcount> ]
        """
        #TODO: make password generic, and make it work how about!
#        self.__irc.send("PASS grahamtest")
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
        ping_send = "PING %s" % recipient
        self.__irc.send(ping_send + "\r\n")
        print ping_send

    def pong(self, target=":Pong"):
        pong_send = "PONG %s" % target
        self.__irc.send(pong_send + "\r\n")
        print pong_send

    def join(self, channel, password=""):
        """
        4.2.1 Join message

        Command:	JOIN
        Parameters:	<channel>{,<channel>} [<key>{,<key>}]

        Accepts comma separated groups of channels to join and the passwords for those channels
        """
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

    def check_commands(self, data):
        """
        Accepts a string of commands sent to it by IRC server, and operates
        accordingly
        """
        #TODO: Remove debugging message
#        if data.__len__() >= 3 and data == data[3]:
#            if cmd == ":!gtfo":
#                self.send_data("PART " + data[2] + "\n")
#            if cmd == ":!join":
#                if data.__len__() >= 5:
#                    self.join(data[4])
#            if cmd == ":!die":
#                self.quit()
        for line in data.split('\n'):
            if line.find("ERROR") != -1:
                print "Error, disconnecting"
                self.quit()
            elif line[0:4] == "PING":
                self.send_data( "PONG " + line.split()[1] + "\r\n" )
            print "Out of commands! Chillin."
            # This may not be necessary
#            if cmd == "ERROR":
#                if data[1] == ":Closing":
#                    self.quit()

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


#====Connection info====#
server = "irc.utonet.org"
port = 6667
nick = "LonelyBot"
name = "Lonely Island Bot"

#====MAIN====#
bot = IrcBot(server, port, nick, name)
bot.connect_irc()
bot.register()
#bot.join("#LonelyIsland")

#====MAIN LOOP====#
while not bot.should_quit():
    #Receive data from the irc socket
    data = bot.get_data(2048)
    #if length is 0 we got disconnected
    if data.__len__ == 0:
        break
    #Print data received to the console for monitoring
    print data
    #Check to see if there's anything we can do with it :)
    bot.check_commands(data)

bot.quit()
