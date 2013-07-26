#!/usr/bin/env python
#
# Copyright 2009 Derik Pereira. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

'''An example that provides a python interface to walpha'''

__author__ = 'derik66@gmail.com'
__version__ = '1.1-devel'

import urllib2

url = 'http://derik-wa.appspot.com/walpha'
data = 'content=who are you?'

result = urllib2.urlopen(url, data)
jsonr = result.read()

print jsonr