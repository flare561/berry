import sys;import traceback;import json;from ircutils import bot
from datetime import tzinfo,timedelta
import time,datetime,os,commands,custom_commands


class berry(bot.SimpleBot):
  def command_help(self, event):
    '''Usage: ~help <command> The fuck do you think it does?'''
    #Get commands with documentation
    documented_commands = {x[8:]:self.cmds[x].__doc__ for x in self.cmds if self.cmds[x].__doc__ != None
        and ( ( event.respond not in self.config['sfwchans'].split(',') ) or ( not hasattr(self.cmds[x], 'nsfw' ) ) )}

    #If no params, send list of commands
    if len(event.params) < 1:
        self.send_message(event.respond, "Currently supported commands: %s" % ', '.join(documented_commands.keys()))
    #If the param is documented, send the doc string for it
    elif event.params in documented_commands:
        self.send_message(event.respond, documented_commands[event.params])
    #If the param is undocumented, send unsupported
    else:
        self.send_message(event.respond, "Unsupported command")

  

  def on_any(self,event):
    try:
      event.paramstr=' '.join(event.params)
      event.respond = event.target if event.target != self.nickname else event.source
      
      if not event.source == self.nickname:
        if event.command == "INVITE":
          self.join_channel(event.params[0])
        if event.command in ['PRIVMSG']:
          #Reload config and commands.
          if os.stat('config.json').st_mtime > self.lastloadconf or os.stat('commands.py').st_mtime > self.lastloadcommands or os.stat('custom_commands.py').st_mtime > self.lastloadcustomcommands:
            #Reloading
            self.config = loadconf('config.json')
            reload(commands)
            reload(custom_commands)

            #Create objects for commands and custom_commands
            cmd = commands.commands(self.send_message, self.send_action, self.config)
            cust_cmd = custom_commands.custom_commands(self.send_message, self.send_action, self.config)

            #Method to get all callable objects with a given prefix from a given object
            def get_methods(obj, prefix):
              return {x:getattr(obj,x) for x in dir(obj) if x.startswith(prefix) and callable(getattr(obj, x))}

            #Get all regexes from all files, overwriting ones in commands and self with those in custom_commands
            regexes = get_methods(cmd, 'regex_')
            regexes.update(get_methods(self, 'regex_'))
            regexes.update(get_methods(cust_cmd, 'regex_'))

            #Get all commands from all files, overwriting ones in commands and self with those in custom_commands
            cmds = get_methods(cmd, 'command_')
            cmds.update(get_methods(self, 'command_'))
            cmds.update(get_methods(cust_cmd, 'command_'))

            self.cmds = cmds

          event.command=event.message.split(' ')[0]
          try:   event.params=event.message.split(' ',1)[1]
          except:event.params=''

          

          #Execute regexes
          for regex in regexes:
            regexes[regex](event)
          
          #Execute command
          if event.command[0] in self.config['prefixes'].split() and 'command_%s' % event.command[1:].lower() in cmds:
            comm = cmds['command_%s' % event.command[1:].lower()]
            if not ( event.respond in self.config['sfwchans'].split(',') and hasattr(comm, 'nsfw') ):
              comm(event)

    except:
      print "ERROR",str(sys.exc_info())
      print traceback.print_tb(sys.exc_info()[2])

def loadconf(filename):
  if os.path.isfile(filename):
    with open(filename, 'r') as conffile:
      return json.load(conffile)
  else:
    defaultConf=dict(
      debug= False,
      nick= 'Berry',
      server= '127.0.0.1',
      channels= '#bottest',
      imgurKey= '',
      wolframKey= '',
      prefixes= '~ . !',
      traktKey= '',
      googleKey= '',
      googleengine= '015980026967623760357:olr5wqcaob8',
      sfwchans='#channel1,#channel2',
      yiffs=['2furry4me']
    )
    with open(filename, 'w') as conffile:
      json.dump(defaultConf,conffile, sort_keys=True, indent=4, separators=(',',': '))
      return defaultConf

if __name__ == "__main__":
  config = loadconf("config.json")
  s=berry(config['nick'].encode('ascii', 'replace'))
  s.connect(config['server'].encode('ascii', 'replace'), channel=config['channels'].encode('ascii', 'replace'), use_ssl=False)
  s.config = config
  s.lastloadconf = 0
  s.lastloadcommands = 0
  s.lastloadcustomcommands = 0
  print 'starting'
  s.start()
