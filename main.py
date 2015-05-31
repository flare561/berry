import sys;import traceback;import json;from ircutils import bot
from datetime import tzinfo,timedelta
import time,datetime,os,commands


class berry(bot.SimpleBot):
  def on_any(self,event):
    try:
      event.paramstr=' '.join(event.params)
      event.respond = event.target if event.target != self.nickname else event.source

      if not event.source == self.nickname:
        if event.command == "INVITE":
          self.join_channel(event.params[0])
        if event.command in ['PRIVMSG']:
          #Reload config and commands.
          if os.stat('config.json').st_mtime > self.lastloadconf:
            self.config = loadconf('config.json')
          if os.stat('commands.py').st_mtime > self.lastloadcommands:
            reload(commands)

          event.command=event.message.split(' ')[0]
          try:   event.params=event.message.split(' ',1)[1]
          except:event.params=''
          cmd = commands.commands(self.send_message, self.config)
          for regex in [getattr(cmd,x) for x in dir(cmd) if x.startswith('regex_') and callable(getattr(cmd, x))]:
            regex(event)
          if event.command[0] in self.config['prefixes'].split() and hasattr(cmd, 'command_%s' % event.command[1:].lower()):
            comm = getattr(cmd, 'command_%s' % event.command[1:].lower())
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
    defaultConf={
      'debug': False,
      'nick': 'Berry',
      'server': '127.0.0.1',
      'channels': '#bottest',
      'imgurKey': '',
      'wolframKey': '',
      'prefixes': '~ . !',
      'traktKey': '',
      'googleKey': '',
      'googleengine': '015980026967623760357:olr5wqcaob8',
      'sfwchans': '#channel1,#channel2'
    }
    with open(filename, 'w') as conffile:
      json.dump(defaultConf,conffile, sort_keys=True, indent=4, separators=(',',': '))
      return defaultConf




if __name__ == "__main__":
  config = loadconf("config.json")
  s=berry(config['nick'].encode('ascii', 'replace'))
  s.connect(config['server'].encode('ascii', 'replace'), channel=config['channels'].encode('ascii', 'replace'), use_ssl=False)
  s.config = config
  s.lastloadconf = os.stat('config.json').st_mtime
  s.lastloadcommands = os.stat('commands.py').st_mtime
  print 'starting'
  s.start()
