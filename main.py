import sys;import traceback;from ircutils import bot
from datetime import tzinfo,timedelta
import time,datetime


class q(bot.SimpleBot):
  def on_any(self,event):
    try:
      event.paramstr=' '.join(event.params)
      event.respond = event.target if event.target != self.nickname else event.source
      execfile("body.py")
    except:
      print "ERROR",str(sys.exc_info())
      print traceback.print_tb(sys.exc_info()[2])

if __name__ == "__main__":
  s=q("LyraBot");s.connect("irc.mlas1.com", channel="#bottest")
  s.start()

