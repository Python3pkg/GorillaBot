# Copyright (c) 2013 Molly White
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY Kself.ind, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN c.con WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import re, pprint

class Stalker(object):
    def __init__(self):
        self.stalk_dict = dict()
        self.notify_dict = dict()
        self.notify_status = False # Is the bot in the middle of figuring out a notify?
        self.current_nick = '' # Who is the notify set on?
        self.current_sender = '' # Who set the notify?
        self.channel = '' # From where was the notify set?
        self.status = '' # Away, online, offline
        self.codes = []
        self.con = None
        
    def _recv_numcode(self):
        if not self.notify_status:
            return
        if '401' in self.codes:
            # User is offline
            self.con.say('You will be notified when {} comes online.'.format(self.current_nick), self.channel)
            self.status = 'offline'
        elif '301' in self.codes:
            # User is away
            self.con.say('You will be notified when {} returns from away.'.format(self.current_nick), self.channel)
            self.status = 'away'
        else:
            self.con.say('{} is currently online.'.format(self.current_nick), self.channel)
            self.notify_dict[self.current_sender].remove(self.current_nick)
            if len(self.notify_dict[self.current_sender]) == 0:
                del self.notify_dict[self.current_sender]
        self._clear()           
        
    def _clear(self):
        self.notify_status = False # Is the bot in the middle of figuring out a notify?
        self.current_nick = '' # Who is the notify set on?
        self.current_sender = '' # Who set the notify?
        self.channel = '' # From where was the notify set?
        self.status = '' # Away, online, offline
        self.codes = []
        self.con = None
        
    def _update(self, bot):
        self.con = bot.GorillaConnection
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(self.notify_dict)
        nicks = []
        nick_vals = list(self.notify_dict.values())
        for l in nick_vals:
            for nick in l:
                nicks.append(nick)
        nicks = list(set(nicks))
        for i in range(len(nicks)):
            self.current_nick = nicks[i]
            self.con.whois(nicks[i])
            
        
    def notify(self, c, channel, command_type, line):
        self.con = c.con
        self.channel=channel
        user = re.search(r'notify\s(?P<nick>[^\s]+)(?P<extra>.+)?', line)
        if user:
            if user.group('extra'):
                self.con.say("You have used too many parameters. Please only set notification "
                          "on one nick at a time.", channel)
                return
            elif user.group('nick'):
                self.current_nick = user.group('nick')
        else:
            self.con.say("Please specify a nick.", channel)
            return
        self.current_sender = c.get_sender(line)
        if self.current_sender not in self.notify_dict:
            self.notify_dict[self.current_sender] = [self.current_nick]
            self.ind = 0
            self.notify_status = True
        else:
            if self.current_nick in self.notify_dict[self.current_sender]:
                self.con.say("{} is already in your notify list. Did you mean to denotify?".format(self.current_nick), channel)
                return
            else:
                self.notify_dict[self.current_sender].append(self.current_nick)
                self.notify_status = True
        self.con.whois(self.current_nick)