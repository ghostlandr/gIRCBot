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

import socket, time

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
        __channels - a list containing all the channels the bot is (or will be) connected to - private
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
        self.__greetings = ["Hello", "Hi", "Sup", "G'day", "Morning", "Evening", "Mornin'", "Evenin'", "Afternoon"]

    def channel_list(self):
        return self.__channels

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
                      " " + self.server + " :" + self.full_name)
        self.send_data("NICK " + self.nick)

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
        self.send_data(ping_send)

    def pong(self, target=":Pong"):
        """
        Responds to a ping
        """
        pong_send = "PONG %s" % target
        print pong_send
        self.send_data(pong_send)

    def join(self, channel, password=""):
        """
        4.2.1 Join message

        Command:	JOIN
        Parameters:	<channel>{,<channel>} [<key>{,<key>}]

        Accepts comma separated groups of channels to join and the passwords for those channels
        """
        self.__channels.append(channel.lower())
        self.__irc.send("JOIN " + channel + " " + password)

    def send_data(self, data):
        """
        Sends raw - though properly terminated - data to the socket.
        """
        if data is not None:
            self.__irc.send(data + "\r\n")

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
            self.send_data("QUIT " + channel + " :" + msg)
        elif channel is not None:
            self.send_data("QUIT " + channel)
        else:
            self.send_data("QUIT")
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
        self.send_data("PRIVMSG " + receiver + " :" + message)

    def is_admin(self, user_nick):
        """
        Checks if the nick passed in is on the "masters" list. Some commands require
        a nickname to have "administrative" privileges
        """
        return user_nick in self.master

    def _get_sender_nick(self, line):
        return line[1:line.find("!")]

    def cmd_list(self, chat_room):
        self.send_message(chat_room, "Okay, here's what I can do:")
        self.send_message(chat_room, "1. !math - Type !math [operand] [operator] [operand] and"
                                     " I'll print the result! No brackets or fancy stuff please.")
        self.send_message(chat_room, "Well, I guess that's it for now actually.")

    def _dialogue(self, line):
        """
        Accepts a line from the chat that contains PRIVMSG. This means that there should
        be some response from the bot to the people in the server or to a specific person.
        This method contains a lot of logic, thus it is broken out from check_commands
        """
        chat_nick = self._get_sender_nick(line)
        chat_string = line.split(" ")
        chat_room = chat_string[2]

        if "#" not in chat_room:
            # private messaging, check what they want us to do
            if chat_nick in self.master:
                # follow more accordingly to admins
                if "!admin_list" in line:
                    self.send_message(chat_nick, "Admins are: %s" % " / ".join(self.master))
                elif "!add_admin" in line:
                    # this commands syntax: !add_admin [admin_nick]
                    new_admin = chat_string[4]
                    if new_admin not in self.master:
                        self.master.append(new_admin)
                        self.send_message(chat_nick, "%s is now an administrator" % new_admin)
                    else:
                        self.send_message(chat_nick, "%s is already an admin!" % new_admin)
            else:
                # regular person who is PMing us
                pass #not sure what to do here yet
        elif chat_room in self.__channels:
            # we're in a channel, start checking for commands
            if ":!gtfo" in line:
                if chat_nick in self.master:
                    self.send_message(chat_room, "Yes %s, I will leave %s" % (chat_nick, chat_room))
                    self.quit(chat_room, "I've been ordered out!")
                else:
                    self.deny_command(chat_room, chat_nick)
            elif ":!cmds" in line:
                self.cmd_list(chat_room)
            elif ":!quit" in line:
                if chat_nick in self.master:
                    self.send_message(chat_room, "Yes %s, I will leave %s" % (chat_nick, chat_room))
                    self.quit(chat_room, "I've been ordered out!")
                else:
                    self.deny_command(chat_room, chat_nick)
            elif ":!math" in line:
                message = ""
                try:
                    message = self.do_math(line)
                except ZeroDivisionError:
                    message = "Ha, you wanted me to divide by zero didn't you!"
                except ValueError:
                    message = "I can only accept numeric input (obviously)"
                self.send_message(chat_room, message)
            elif chat_string[1] == "JOIN":
                if chat_nick is self.nick:
                    self.send_message(chat_room[2:], "Greetings all, I am here!")
                else:
                    self.send_message(chat_room[2:], "Greetings %s and welcome to the %s channel!" % (chat_nick, chat_room[2:]))
            elif chat_string[1] == "PART":
                self.send_message(chat_room, "See you later, %s" % chat_nick)
            elif self.nick.lower() in line.lower():
                #If they are addressing the bot, try to do something
                for greeting in self.__greetings:
                    if greeting.lower() in line.lower():
                        #TODO: Randomize the greetings
                        self.send_message(chat_room, "Hello to you too, %s" % chat_nick)
                        break
                #TODO: Add farewells!!

    def do_math(self, line):
        """
        do_math expects a command like !math [operand] [operator] [operand], ex: !math 2 * 2
        """
#        chat_nick = self._get_sender_nick(line)
        operand1 = float(line.split(" ")[4])
        operator = line.split(" ")[5]
        operand2 = float(line.split(" ")[6])
        result = 0
        if operator is "*" or operator is "x":
            result = operand1 * operand2
        elif operator is "/" or operator is "\\":
            result = operand1 / operand2
        elif operator is "+":
            result = operand1 + operand2
        elif operator is "-":
            result = operand1 - operand2

        return "%s %s %s = %s" % (operand1, operator, operand2, result)

    def deny_command(self, reply_to, chat_nick):
        """
        When someone who is not the bots master attempts to run what is considered an "admin command" (example:
        having the bot quit), it will deny that command.
        """
        self.send_message(reply_to, "You're not my master, %s!" % chat_nick)

    def check_commands(self, data):
        """
        Accepts a string of commands sent to it by IRC server, and operates
        accordingly
        """
        nothings = 0
        self.__history.append(data)
        print data
        for line in data.split('\r\n'):
            if "ERROR" in line:
                print "Error, disconnecting"
                #TODO: think of some reconnection logic here
                self.quit()
            elif "PRIVMSG" in line or "JOIN" in line or "PART" in line:
                # this is a message from a human, process it in a separate method to save space here
                self._dialogue(line)
            elif line[0:4] == "PING":
                self.pong(line.split()[1])
            else:
                nothings += 1

        if nothings is not 0:
            print "Nothing to do with %s lines" % nothings

    def search_history(self, query):
        for line in self.__history:
            if query in line:
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
        while "\r\n" not in data:
            data += self.__receive_data(buffer_size)
        return data.strip('\r\n')

# Set up your connection
server = "irc.utonet.org"
port = 6667
buffer_size = 4096

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
bot.check_commands(data)

# Get connected to the server
#TODO: Find a way to make this a lot better
while bot.search_history("Logon News") is not True:
    data = bot.get_data(buffer_size)
    bot.check_commands(data)

#time.sleep(20)

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
