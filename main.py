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

  def on_join(self,event):
      if (self.firstJoin):
          for channel in self.config.channels[1:]:
              self.join_channel(channel)
      self.firstJoin = False

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
            self.channels = config.get("DEFAULT", "channels").split(',')
        else: 
            self.channels = ['#mlas1']
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
        if config.has_option('DEFAULT', 'authorizedUsers'):
            self.authorizedUsers = config.get("DEFAULT", "authorizedUsers").split(',')
        else: 
            self.authorizedUsers = ['']
            config.set('DEFAULT', 'authorizedUsers', self.authorizedUsers)
            modified = True
        if config.has_option('DEFAULT', 'password'):
            self.password = config.get("DEFAULT", "password")
        else: 
            self.password = ''
            config.set('DEFAULT', 'password', self.password)
            modified = True
        if config.has_option('DEFAULT', 'autoemote'):
            self.autoemote = config.getboolean("DEFAULT", "autoemote")
        else: 
            self.autoemote = True
            config.set('DEFAULT', 'autoemote', self.autoemote)
            modified = True

        if modified:
            with open(self.fileName, "wb") as configFileLocation:
                config.write(configFileLocation)


    def setEmote(self, enabled):
        configFile = ConfigParser.RawConfigParser()
        configFile.read(self.fileName)
        configFile.set("DEFAULT", "autoemote", enabled)
        with open(self.fileName, "wb") as configFileLocation:
            configFile.write(configFileLocation)


if __name__ == "__main__":
  config = Config("config.ini")
  s=q(config.nick);s.connect(config.server, channel=config.channels[0])
  s.firstJoin = True
  s.config = config
  s.start()
