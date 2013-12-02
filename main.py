import ConfigParser,sys;import traceback;from ircutils import bot
from datetime import tzinfo,timedelta
import time,datetime


class q(bot.SimpleBot):
  def on_any(self,event):
    try:
      event.paramstr=' '.join(event.params)
      event.respond = event.target if event.target != self.nickname else event.source
      if not event.source == self.nickname:
        execfile("body.py")
    except:
      print "ERROR",str(sys.exc_info())
      print traceback.print_tb(sys.exc_info()[2])
  def _prefix(self,*i):
    output=[]
    for x in i:
      output.extend([z+x for z in self.config.prefixes])
    return output


class Config:
    def __init__(self, fileName):
        config = ConfigParser.ConfigParser()
        config.read(fileName)
        self.fileName = fileName


        modified = False
        if config.has_option('DEFAULT', 'debug'):
            self.debug = config.getboolean("DEFAULT", "debug")
        else: 
            self.debug=False
            config.set('DEFAULT', 'debug', self.debug)
            modified = True

        if config.has_option('DEFAULT', 'nick'):
            self.nick = config.get("DEFAULT", "nick")
        else: 
            self.nick = 'BP'
            config.set('DEFAULT', 'nick', self.nick)
            modified = True

        if config.has_option('DEFAULT', 'server'):
            self.server = config.get("DEFAULT", "server")
        else: 
            self.server = 'irc.mlas1.com'
            config.set('DEFAULT', 'server', self.server)
            modified = True

        if config.has_option('DEFAULT', 'channels'):
            self.channels = config.get("DEFAULT", "channels")
        else: 
            self.channels = '#mlas1'
            config.set('DEFAULT', 'channels', self.channels)
            modified = True

        if config.has_option('DEFAULT', 'imgurKey'):
            self.imgurKey = config.get("DEFAULT", "imgurKey")
        else: 
            self.imgurKey = ''
            config.set('DEFAULT', 'imgurKey', self.imgurKey)
            modified = True

        if config.has_option('DEFAULT', 'wolframKey'):
            self.wolframKey = config.get("DEFAULT", "wolframKey")
        else: 
            self.wolframKey = ''
            config.set('DEFAULT', 'wolframKey', self.wolframKey)
            modified = True

        if config.has_option('DEFAULT', 'prefixes'):
            self.prefixes = config.get("DEFAULT", "prefixes").split(',')
        else: 
            self.prefixes = ['~', '!']
            config.set('DEFAULT', 'prefixes', ",".join(self.prefixes))
            modified = True

        if config.has_option('DEFAULT', 'adminhosts'):
            self.adminhosts = config.get("DEFAULT", "adminhosts").split(',')
        else: 
            self.adminhosts = ['Whatever.it.is.Pinkie.Pie.does']
            config.set('DEFAULT', 'adminhosts', ",".join(self.adminhosts))
            modified = True

        if config.has_option('DEFAULT', 'raribot'):
            self.raribot = config.getboolean("DEFAULT", "raribot")
        else: 
            self.raribot=False
            config.set('DEFAULT', 'raribot', self.debug)
            modified = True

        if config.has_option('DEFAULT', 'bannedhosts'):
            self.bannedhosts = config.get("DEFAULT", "bannedhosts").split(',')
        else: 
            self.bannedhosts = []
            config.set('DEFAULT', 'bannedhosts', ",".join(self.bannedhosts))
            modified = True

        if config.has_option('DEFAULT', 'traktKey'):
            self.traktKey = config.get("DEFAULT", "traktKey")
        else: 
            self.traktKey = ''
            config.set('DEFAULT', 'traktKey', self.traktKey)
            modified = True

        if modified:
            with open(self.fileName, "wb") as configFileLocation:
                config.write(configFileLocation)


    def setBannedHosts(self, bannedhosts):
        configFile = ConfigParser.RawConfigParser()
        configFile.read(self.fileName)
        configFile.set("DEFAULT", "bannedhosts", ','.join(bannedhosts))
        with open(self.fileName, "wb") as configFileLocation:
            configFile.write(configFileLocation)

    def getBannedHosts(self):
        configFile = ConfigParser.RawConfigParser()
        configFile.read(self.fileName)
        return configFile.get('DEFAULT', 'bannedhosts').split(',')


if __name__ == "__main__":
  config = Config("config.ini")
  s=q(config.nick);s.connect(config.server, channel=config.channels)
  s.config = config
  s.start()