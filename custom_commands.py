# -*- coding: utf-8 -*-
import functools


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

    def command_lenny(self, event):
        '''Usage: ~lenny Override of default command'''
        self.send_message(event.respond, "Example of an override")
