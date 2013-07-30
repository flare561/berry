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

class Config:
    def __init__(self, fileName):
        config = ConfigParser.ConfigParser()
        config.read(fileName)
        self.debug = config.getboolean("Default", "debug")
        self.nick = config.get("Default", "nick")
        self.server = config.get("Default", "server")
        self.channel = config.get("Default", "channel")
        self.imgurKey = config.get("Default", "imgurKey")
        self.wolframKey = config.get("Default", "wolframKey")
        self.authorizedUsers = config.get("Default", "authorizedUsers").split(',')
        self.password = config.get("Default", "password")


if __name__ == "__main__":
  config = Config("config.ini")
  s=q(config.nick);s.connect(config.server, channel=config.channel)
  s.config = config
  s.start()
