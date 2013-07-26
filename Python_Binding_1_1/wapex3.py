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

import time
start = time.clock()

server = 'http://api.wolframalpha.com/v1/query.jsp'
appid = 'XXXX'
input = 'who are you?'

scantimeout = '3.0'
podtimeout = '4.0'
formattimeout = '8.0'
async = 'False'

waeo = wap.WolframAlphaEngine(appid, server)

waeo.ScanTimeout = scantimeout
waeo.PodTimeout = podtimeout
waeo.FormatTimeout = formattimeout
waeo.Async = async

query = waeo.CreateQuery(input)

#print '***wapex output***', '\n', 'server=' + server + '\n', query

#result = waeo.PerformQuery(query)

waeq = wap.WolframAlphaQuery(input, appid)
waeq.ScanTimeout = scantimeout
waeq.PodTimeout = podtimeout
waeq.FormatTimeout = formattimeout
waeq.Async = async
waeq.ToURL()
waeq.AddPodTitle('')
waeq.AddPodIndex('')
waeq.AddPodScanner('')
waeq.AddPodState('')
waeq.AddAssumption('')

query = waeq.Query

print '***wapex output***', '\n', 'server=' + server + '\n', query

result = waeo.PerformQuery(query)

waeqr = wap.WolframAlphaQueryResult(result)
xmlresult = waeqr.XmlResult
print '\n', type(xmlresult), 'xml=', xmlresult
jsonresult = waeqr.JsonResult()
print '\n', type(jsonresult), 'json=', jsonresult
tree = waeqr.tree
print '\n', type(tree), 'tree=', tree
issuccess = waeqr.IsSuccess()  
print '\n', type(issuccess), 'issuccess=', issuccess
iserror = waeqr.IsError()
print '\n', type(iserror), 'iserror=', iserror
numpods = waeqr.NumPods()
print '\n', type(numpods), 'numpods=', numpods
datatypes = waeqr.DataTypes()
print '\n', type(datatypes), 'datatypes=', datatypes
timedoutscanners = waeqr.TimedoutScanners()
print '\n', type(timedoutscanners), 'timedoutscanners=', timedoutscanners
timing = waeqr.Timing()
print '\n', type(timing), 'timing=', timing
parsetiming = waeqr.ParseTiming()
print '\n', type(parsetiming), 'parsetiming=', parsetiming
error = waeqr.Error()
print '\n', type(error), 'error=', error
errorcode = waeqr.ErrorCode()
print '\n', type(errorcode), 'errorcode=', errorcode
errormessage = waeqr.ErrorMessage()
print '\n', type(errormessage), 'errormessage=', errormessage
pods = waeqr.Pods()
print '\n', type(pods), 'pods=', pods
xmlpods = waeqr.XMLPods()
print '\n', type(xmlpods), 'xmlpods=', xmlpods
assumptions = waeqr.Assumptions()
print '\n', type(assumptions), 'assumptions=', assumptions
warnings = waeqr.Warnings()
print '\n', type(warnings), 'warnings=', warnings
sources = waeqr.Sources()
print '\n', type(sources), 'sources=', sources

for pod in pods:

  waep = wap.Pod(pod)

  iserror = waep.IsError()
  print '\n', type(iserror), 'pod iserror=', iserror
  numsubpods = waep.NumSubpods()
  print '\n', type(numsubpods), 'numsubpods=', numsubpods
  title = waep.Title()
  print '\n', type(title), 'title=', title
  scanner = waep.Scanner()
  print '\n', type(scanner), 'scanner=', scanner
  position = waep.Position()
  print '\n', type(position), 'position=', position
  asynchurl = waep.AsynchURL()
  print '\n', type(asynchurl), 'asynchurl=', asynchurl
  subpods = waep.Subpods()
  print '\n', type(subpods), 'subpods=', subpods
  for subpod in subpods:

    waesp = wap.Subpod(subpod)

    title = waesp.Title()
    print '\n', type(title), 'subpod title=', title

    plaintext = waesp.Plaintext()
    print '\n', type(plaintext), 'plaintext=', plaintext

    img = waesp.Img()
    print '\n', type(img), 'img=', img

  podstates = waep.PodStates()
  print '\n', type(podstates), 'podstates=', podstates
  infos = waep.Infos()
  print '\n', type(infos), 'infos=', infos

for xml in xmlpods:

  waep = wap.Pod(xml)

  asxml = waep.AsXML()
  print '\n', type(asxml), 'pod xml=', asxml

for assumption in assumptions:

  waea = wap.Assumption(assumption)

  atype = waea.Type()
  print '\n', type(atype), 'assumptions type=', atype
  word = waea.Word()
  print '\n', type(word), 'word=', word
  count = waea.Count()
  print '\n', type(count), 'count=', count
  value = waea.Value()
  print '\n', type(value), 'value=', value

stop = time.clock()
print '\n', 'time=', stop - start