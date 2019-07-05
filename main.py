from __future__ import print_function

import json
import sys
import traceback
import os

from ircutils import bot

import commands
import custom_commands


class berry(bot.SimpleBot):
    def __init__(self, config):
        nick = config['nick'].encode('ascii', 'replace')
        bot.SimpleBot.__init__(self, nick)
        self.config = config
        self.banned_words = set()
        self.checking_for_banned_words = 0

    def send_message(self, to, message):
        try:
            super(berry, self).send_message(to, message.encode('utf-8', 'replace'))
        except UnicodeDecodeError:
            super(berry, self).send_message(to, message.decode('utf-8').encode('utf-8', 'replace'))

    def send_action(self, to, message):
        try:
            super(berry, self).send_action(to, message.encode('utf-8', 'replace'))
        except UnicodeDecodeError:
            super(berry, self).send_action(to, message.decode('utf-8').encode('utf-8', 'replace'))

    def command_help(self, event):
        '''Usage: ~help <command> The fuck do you think it does?'''
        # Get commands with documentation
        documented_commands = {
            x[8:]: self.cmds[x].__doc__
            for x in self.cmds
            if self.cmds[x].__doc__ is not None and
            ((event.respond not in self.config['sfwchans'].split(',')) or
             (not hasattr(self.cmds[x], 'nsfw')))
        }

        # If no params, send list of commands
        if len(event.params) < 1:
            self.send_message(event.respond, "Currently supported commands: %s"
                              % ', '.join(documented_commands.keys()))
        # If the param is documented, send the doc string for it
        elif event.params in documented_commands:
            self.send_message(event.respond, documented_commands[event.params])
        # If the param is undocumented, send unsupported
        else:
            self.send_message(event.respond, "Unsupported command")

    def reload_commands(self):
        # Reloading
        self.config = loadconf('config.json')
        reload(commands)
        reload(custom_commands)
        self.lastloadconf = os.stat('config.json').st_mtime
        self.lastloadcommands = os.stat('commands.py').st_mtime
        self.lastloadcustomcommands = os.stat('custom_commands.py').st_mtime

        # Create objects for commands and custom_commands
        cmd = commands.commands(self.send_message, self.send_action,
                                self.banned_words, self.config)
        cust_cmd = custom_commands.custom_commands(
            self.send_message, self.send_action, self.config)

        # Method to get all callable objects with a given prefix from a given object
        def get_methods(obj, prefix):
            return {
                x: getattr(obj, x)
                for x in dir(obj)
                if x.startswith(prefix) and callable(getattr(obj, x))
            }

        # Get all regexes from all files, overwriting ones in commands and self with those in custom_commands
        self.regexes = get_methods(cmd, 'regex_')
        self.regexes.update(get_methods(self, 'regex_'))
        self.regexes.update(get_methods(cust_cmd, 'regex_'))

        # Get all commands from all files, overwriting ones in commands and self with those in custom_commands
        self.cmds = get_methods(cmd, 'command_')
        self.cmds.update(get_methods(self, 'command_'))
        self.cmds.update(get_methods(cust_cmd, 'command_'))

    def privmsg(self, event):
        # Reload config and commands.
        if os.stat('config.json').st_mtime > self.lastloadconf or os.stat(
                'commands.py').st_mtime > self.lastloadcommands or os.stat(
                    'custom_commands.py'
                ).st_mtime > self.lastloadcustomcommands:
            self.reload_commands()

        event.command = event.message.split(' ')[0]
        try:
            event.params = event.message.split(' ', 1)[1]
        except:
            event.params = ''

        # Execute regexes
        for regex in self.regexes:
            self.regexes[regex](event)

        # Execute command
        if event.command[0] in self.config['prefixes'].split(
        ) and 'command_%s' % event.command[1:].lower() in self.cmds:
            comm = self.cmds['command_%s' % event.command[1:].lower()]
            if not (event.respond in self.config['sfwchans'].split(',') and
                    hasattr(comm, 'nsfw')):
                comm(event)

    def on_any(self, event):
        try:
            event.paramstr = ' '.join(event.params)
            event.respond = event.target if event.target != self.nickname else event.source

            if not event.source == self.nickname:
                if event.command == 'INVITE':
                    self.join_channel(event.params[0])

                # after joining a channel, send mode g command to check for banned words
                if event.command == "RPL_ENDOFNAMES":
                    channel = event.params[0]
                    self.checking_for_banned_words += 1
                    self.execute("MODE", channel, "g")

                # take banned words from server messages
                if is_int(event.command) and self.checking_for_banned_words > 0:
                    if len(
                            event.params
                    ) == 4 and event.params[0] in config['channels'].split(
                            ',') and is_int(event.params[3]):
                        self.banned_words.add(event.params[1])
                    if len(
                            event.params
                    ) == 2 and event.params[1] == 'End of channel spamfilter list':
                        self.checking_for_banned_words -= 1

                # update banned word list when someone uses mode +/-g
                if event.command == 'MODE' and len(event.params) >= 2:
                    if event.params[0] == '+g':
                        self.banned_words.add(event.params[1])
                    if event.params[0] == '-g' and event.params[1] in self.banned_words:
                        self.banned_words.remove(event.params[1])

                if event.command in ['PRIVMSG']:
                    self.privmsg(event)

        except:
            print("ERROR", str(sys.exc_info()))
            print(traceback.print_tb(sys.exc_info()[2]))


def loadconf(filename):
    if os.path.isfile(filename):
        with open(filename, 'r') as conffile:
            return json.load(conffile)
    else:
        defaultConf = dict(
            debug=False,
            nick='Berry',
            server='127.0.0.1',
            channels='#bottest',
            imgurKey='',
            wolframKey='',
            prefixes='~ . !',
            traktKey='',
            googleKey='',
            googleengine='015980026967623760357:olr5wqcaob8',
            sfwchans='#channel1,#channel2',
            yiffs=['2furry4me'])
        with open(filename, 'w') as conffile:
            json.dump(
                defaultConf,
                conffile,
                sort_keys=True,
                indent=4,
                separators=(',', ': '))
            return defaultConf


def is_int(s):
    try:
        int(s)
    except ValueError:
        return False
    return True


if __name__ == "__main__":
    config = loadconf("config.json")
    s = berry(config)
    s.connect(
        config['server'].encode('ascii', 'replace'),
        channel=config['channels'].encode('ascii', 'replace'),
        use_ssl=False)
    s.lastloadconf = 0
    s.lastloadcommands = 0
    s.lastloadcustomcommands = 0
    print('starting')
    s.start()
