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

'''An example that provides a python interface to the wap library'''

__author__ = 'derik66@gmail.com'
__version__ = '1.1-devel'

import wap

#url = 'http://preview.wolframalpha.com/api/v1/query.jsp'
#url = 'http://preview.wolframalpha.com/api/v1/validatequery.jsp'
#url = 'http://api.wolframalpha.com/v1/query.jsp'
#url = 'http://api.wolframalpha.com/v1/validatequery.jsp'

server = 'http://api.wolframalpha.com/v1/query.jsp'
appid = 'XXXX'
input = 'who are you?'

waeo = wap.WolframAlphaEngine(appid, server)
query = waeo.CreateQuery(input)
result = waeo.PerformQuery(query)
waeqr = wap.WolframAlphaQueryResult(result)
jsonresult = waeqr.JsonResult()

print jsonresult