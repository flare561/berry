# -*- coding: utf-8 -*-
import HTMLParser,re,json,random,requests,datetime,socket,os,sys,oembed,urllib2,urllib,threading,urlparse,sys,traceback,time,datetime,os,commands,functools,lxml.html
from ircutils import format
import lxml.etree as etree
import wikipedia as wiki
from time import strftime
from datetime import tzinfo,timedelta

def register(tag, value):
    def wrapped(fn):
        @functools.wraps(fn)
        def wrapped_f(*args, **kwargs):
            return fn(*args, **kwargs)
        setattr(wrapped_f, tag, value)
        return wrapped_f
    return wrapped

class custom_commands:
    def __init__(self, send_message, send_action, config):
        self.send_message = send_message
        self.config = config
        self.send_action = send_action
    
    def command_example(self, event):
        self.send_message(event.respond, "Example custom command")

    def command_lenny(self,event):
        '''Usage: ~lenny Override of default command'''
        self.send_message(event.respond, "Example of an override")