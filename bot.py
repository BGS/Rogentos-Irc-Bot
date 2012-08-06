#! /usr/bin/env Python


import socket
import sys
import datetime

from time import sleep

root_admins = ["bgs", "blacknoxis"]

class BotCore:

    def __init__(self, host, port, nick, channel, password=""):
        self.irc_host = host
        self.irc_port = port
        self.irc_nick = nick
        self.irc_channel = channel
        self.joined_channels = []
        self.irc_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.is_connected = False
        self.reconnect = False
        self.command = ""
        self.connect()

    def connect(self):
        self.reconnect = True
        try:
            self.irc_sock.connect (( self.irc_host, self.irc_port))
        except:
            print ("Error: Could not connect to IRC; Host: %s Port: %s" % (self.irc_host, self.irc_port))
            
        print ("Connected to: %s:%s" %(self.irc_host,self.irc_port))

        self.irc_sock.send("USER %s %s %s :This bot belongs to BGS.\n" % (self.irc_nick, self.irc_nick, self.irc_nick))
        self.irc_sock.send("NICK %s\n" % self.irc_nick)
        self.irc_sock.send("JOIN %s\n" % self.irc_channel)
        self.is_connected = True
        self.listen()

    def listen(self):
        while self.is_connected:
            recv = self.irc_sock.recv(4096)
            recv = recv.strip('\n\r')
            print recv
            if str(recv).find ("PING") != -1:
                self.irc_sock.send("PONG :pingis\n")
            if str(recv).find ("JOIN") != -1:
                irc_user_nick = str(recv).split()[0].split('!')[0].split(':')[1]
                channel = str(recv).split()[2]
                if channel == self.irc_channel and irc_user_nick != self.irc_nick:
                    self.send_message_to_channel("""Bine ai venit %s pe canalul %s! \n""" % (irc_user_nick, channel) , channel)

            if str(recv).find ("PRIVMSG") != -1:
                self.irc_user_nick = str(recv).split()[0].split('!')[0].split(':')[1]

                irc_user_message = self.message_to_data(str(recv))

                print ( self.irc_user_nick + ": " + ''.join(irc_user_message))
                try:
                    if (''.join(irc_user_message)[0] == "."):
                        if str(recv).split()[2] == self.irc_nick:
                            self.command = ''.join(irc_user_message)[1:]
                            self.process_command(self.irc_user_nick.lower(), self.irc_channel)
                        else:
                            self.command = ''.join(irc_user_message)[1:]
                            self.process_command(self.irc_user_nick.lower(), ((str(recv)).split()[2]))
                except IndexError:
                    pass 
        if self.reconnect:
            self.connect()

    def message_to_data(self, message):
       data = message.split()
       data = ' '.join(data[3:]).split(':')[1:]
       return data

    def send_message_to_channel(self,message,channel):
        print (( "%s: %s") % (self.irc_nick, message))
        self.irc_sock.send( (("PRIVMSG %s :%s\r\n") % (channel, message)).encode() )
        
    def process_command(self, user, channel):
        if (len(self.command.split()) == 0):
            return
        command = (self.command).lower()
        command = command.split()

        if (user in root_admins):
            if (command[0] == 'help'):
                self.send_message_to_channel("""Available Admin Only Commands:\n""", self.irc_user_nick)
                sleep(0.5)
                self.send_message_to_channel(""".jchs chan1 chan2 chan3 chan4 \n""", self.irc_user_nick)
                sleep(0.5)
                self.send_message_to_channel("""Join speciffied channels.\n""", self.irc_user_nick)
                sleep(0.5)
                self.send_message_to_channel(""".gmsg <message> \n""", self.irc_user_nick)
                sleep(0.5)
                self.send_message_to_channel("""Send a global message to joined channels! \n""", self.irc_user_nick)
                sleep(0.5)
                self.send_message_to_channel(""".say <message>""", self.irc_user_nick)
                sleep(0.5)
                self.send_message_to_channel("""Write message on channel.""", self.irc_user_nick)   

            if (command[0] == "say"):
                self.send_message_to_channel( ' '.join(command[1:]), channel)

            if (command[0] == 'jchs'):
                channels = command[1:]
                for c in channels:
                    self.irc_sock.send("JOIN %s\n" % c)
                    self.joined_channels.append(c)
            if (command[0] == 'gmsg'):
                for c in  self.joined_channels:
                    self.send_message_to_channel( ' '.join(command[1:]), c )
                       
            
        if (command[0] == "hello"):
            self.send_message_to_channel("Hello to you too, %s . Today is :  %s" % (user, datetime.datetime.now().strftime("%Y-%m-%d %H:%M")), channel)
             
        if (command[0] == "help"):
            self.send_message_to_channel("""Available Unprivileged Commands:\n""", self.irc_user_nick)
            self.send_message_to_channel(""".hello""", self.irc_user_nick)
            self.send_message_to_channel("""Say hi!""", self.irc_user_nick)
        if (command[0] == "owner"):
            self.send_message_to_channel("""I belong to %s.""" % root_admins[0] , channel)
             
if __name__ == '__main__':
    BotCore("irc.freenode.net", 6667, "DarthNoxis", "#rogentos-dezvoltare")
