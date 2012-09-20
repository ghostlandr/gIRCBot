#!/usr/bin/env python
########################################
#                                      #
#          IRC Bot Skeleton            #
#           by den5e. 2012             #
#                                      #
########################################

import socket
import time


class IrcBot(object):

    def __init__(self, server, port, nick, full_name):
        self.server = server
        self.port = port
        self.nick = nick
        self.full_name = full_name
        self.botQuit = False
        self.irc = None

    def register(self):
        """
        4.1.3 User message

        Command:	USER
        Parameters:	<username> <hostname> <servername> <realname>

        4.1.2 Nick message

        Command:	NICK
        Parameters:	<nickname> [ <hopcount> ]
        """
        #TODO: make password generic
#        self.irc.send("PASS grahamtest")
        self.irc.send("USER " + self.nick + " " + self.nick +
                      " " + self.server + " :" + self.full_name)
        self.irc.send("NICK " + self.nick)

    def connect_irc(self):
        self.irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.irc.connect((self.server, self.port))

    def ping(self, recipient):
        self.irc.send("PING %s\n" % recipient)

    def pong(self):
        self.irc.send("PONG " + self.nick + "\n")

    def join(self, channel, password=""):
        """
        4.2.1 Join message

        Command:	JOIN
        Parameters:	<channel>{,<channel>} [<key>{,<key>}]

        Accepts comma separated groups of channels to join and the passwords for those channels
        """
        self.irc.send("JOIN " + channel + " " + password + "\n")

    def send_raw_data(self, data):
        self.irc.send(data)

    def quit(self, channel=None, msg=None):
        if msg != None:
            self.send_message(channel, msg)

        self.send_raw_data("QUIT" + "\n")
        self.botQuit = True
        self.irc.close()

    def send_message(self, receiver, message):
        """
        4.4.1 Private messages

        Command:	PRIVMSG
        Parameters:	<receiver>{,<receiver>} <text to be sent>

        PRIVMSG is used to send private messages between users. <receiver>
         is the nickname of the receiver of the message. <receiver> can also
         be a list of names or channels separated with commas.
        """
        self.irc.send("PRIVMSG " + receiver + " :" + message)

    def check_commands(self, data):
        """
        Accepts a list [] of commands sent to it by IRC server, and operates
        accordingly
        """
        print data
        for cmd in data:
            if data.__len__() >= 3 and cmd == data[3]:
                if cmd == ":!gtfo":
                    self.send_raw_data("PART " + data[2] + "\n")
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
        data = self.irc.recv(buffer_size)
        data = data.rstrip("\r\n")

        return data

#====Check for commands====#
#def CheckCmds(data):
#    for cmd in data:
#        if data.__len__() >= 3 and cmd == data[3]:
#            if cmd == ":!gtfo":
#                SendRawData("PART "+ data[2] + "\n")
#            if cmd == ":!join":
#                if data.__len__() >= 5:
#                    Join(data[4], "Pickeeeee")
#            if cmd == ":!die":
#                Quit()
#
#        if cmd == "PING":
#            SendPing()

#====Register USER and NICK====#
#def register():
#    irc.send("USER "+ nick + " " + nick + " " + nick + " :irc bot\n")
#    irc.send("NICK "+ nick +"\n")

#====Ping,Pong====#
#def SendPing():
#    irc.send("PING :Pong\n")

#====Send a message, PRIVMSG====#
#def SendMessage(chan, message):
#    irc.send("PRIVMSG "+ chan +" :"+ message +"\n")

#====Join channel,optional: Send a message====#
#def Join(chan, msg=None):
#    irc.send("JOIN "+ chan +"\n")
#    if msg != None:
#        SendMessage(chan, msg)

#====Send Raw IRC Commands====#        
#def SendRawData(data):
#    irc.send(data)

#====Quit====#
#def Quit(chan=None, msg=None):
#    if msg != None:
#        Send(chan, msg)
#
#    SendRawData("QUIT" + "\n")
#    global botQuit
#    botQuit = True

    


#====Connection info====#
server = "irc.utonet.org"
port = 6667
nick = "LonelyBot"

#====MAIN====#
bot = IrcBot("irc.utonet.org", 6667, "LonelyBot", "Lonely Island Bot")
#irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#irc.connect((server, port))
bot.connect_irc()
bot.register()
bot.join("#LonelyIsland")
#register()
#Join('#LonelyIsland')

#====MAIN LOOP====#
while bot.should_quit != True:
#    data = irc.recv(2048)
#    data = data.strip('\n\r')
    data = bot.get_data(4096)
    bot.check_commands(data.split(" "))
    print(data)
    time.sleep(10)