import HTMLParser,re,urllib,json,random,requests,datetime,socket,os,sys,HTMLParser,oembed,urllib2,urllib,threading;from ircutils import format
import lxml.etree as etree
import lxml.html

self.bannedhosts=self.config.getBannedHosts()
if hasattr(event, 'host') and (event.host is not None) and (event.host.lower() in [s.lower() for s in self.config.adminhosts]) and hasattr(event, 'message'):
    if event.message.split(' ',1)[0] in self._prefix("banhost"):
        if self.bannedhosts:self.bannedhosts.append(event.message.split(' ',1)[1].lower())
        else:self.bannedhosts=set([event.message.split(' ',1)[1].lower()])
    if event.message.split(' ',1)[0] in self._prefix("unbanhost"):
        if self.bannedhosts:self.bannedhosts.remove(event.message.split(' ',1)[1].lower())
        else:pass
    self.config.setBannedHosts(self.bannedhosts)
if hasattr(self, 'bannedhosts') and hasattr(event, 'host') and (event.host is not None) and event.host.lower() in self.bannedhosts: event.command="NULL"


#Invite Responder
if event.command == "INVITE":
    self.join_channel(event.params[0])
 
#AAAAAAAA
if event.command in ['PRIVMSG']:
    #Initialize the event
    event.command=event.message.split(' ')[0]

    steamNick = False
    if self.config.raribot:
        if event.command[-1:] == ':' and event.source == 'S':
            try: event.command = event.message.split(' ', 2)[1]
            except: event.command = ''
            try: event.params=event.message.split(' ',2)[2]
            except: event.params = ''
        else:
            try:   event.params=event.message.split(' ',1)[1]
            except:event.params=''
    else:
        x=re.compile('^<(.*) ?> ')
        matches=x.findall(event.message)
        if len(matches) > 0:
            event.source = matches[0]
            event.message = x.sub('', event.message)
            event.command = event.message.split(' ')[0]
        try:   event.params=event.message.split(' ',1)[1]
        except:event.params=''

    #substitution
    substmatch=re.compile('(?:\s|^)s/([^/]+)/([^/]+)/?')
    substmatches=substmatch.findall(event.message)
    if len(substmatches) > 0:
        try:
            usernamematch = re.findall('^[a-zA-Z0-9_\-\\\[\]\{}\^`\|]+', event.message)
            if len(usernamematch) > 0 and not event.message[:2].lower() == 's/':
                username = usernamematch[0]
                newmessage = self.lastmessage[username].replace(substmatches[0][0], substmatches[0][1])
                if newmessage != self.lastmessage[username]:
                    self.send_message(event.respond, '{} thinks {} meant to say: "{}"'.format(event.source, username, newmessage))
                else:
                    self.send_message(event.respond, "Couldn't find anything to replace")
            else:
                username = event.source
                newmessage = self.lastmessage[username].replace(substmatches[0][0], substmatches[0][1])
                if newmessage != self.lastmessage[username]:
                    self.send_message(event.respond, '{} meant to say: "{}"'.format(event.source, newmessage))
                else:
                    self.send_message(event.respond, "Couldn't find anything to replace")

        except:
            self.send_message(event.respond, "Couldn't find anything to replace")
            raise

    #required for substitution
    if not hasattr(self, 'lastmessage'):
        self.lastmessage = requests.structures.CaseInsensitiveDict()
    self.lastmessage[event.source]=event.message

    #Select Roller
    if event.command in self._prefix('select') and len(event.params)>0:
        self.send_message(event.respond,'Select: {}'.format(random.choice(event.params.split(' '))))
 
    #Flip
    if event.command in self._prefix('flip'):
        self.send_message(event.respond,'Flip: {}'.format(random.choice(['Heads','Tails'])))
         
    #Youtube info fetcher
    ytmatch=re.compile(
        "https?:\/\/(?:[0-9A-Z-]+\.)?(?:youtu\.be\/|youtube\.com\S*[^\w\-\s"
        "])([\w\-]{11})(?=[^\w\-]|$)(?![?=&+%\w]*(?:['\"][^<>]*>|<\/a>))[?="
        "&+%\w-]*",flags=re.I)
    matches=ytmatch.findall(event.message)
    for x in matches:
        try:
            j=requests.get(
                'https://gdata.youtube.com/feeds/api/videos/'+x,
                params=dict(v=2,alt="jsonc")).json()[u'data']
            out=[]
            if j.has_key('title'):out.append(j['title'])
            if j.has_key('viewCount'):out.append(u'{:,}'.format(j['viewCount']))
            if j.has_key('rating'):out.append(u'{:.0%}'.format(j['rating']/5))
            if j.has_key('duration'):out.append(str(datetime.timedelta(seconds=j[u'duration'])))
            out=u' | '.join(out)
            self.send_message(event.respond,out.encode('utf-8','replace'))
        except:
            print "ERROR\n",traceback.print_tb(sys.exc_info()[2]),"\nERROREND"


    #Youtube search
    if event.command.lower() in self._prefix('yt'):
        try:
            j=requests.get(
                'https://gdata.youtube.com/feeds/api/videos',
                params=dict({'max-results':1},q=event.params,
                    v=2,alt="jsonc")).json()[u'data'][u'items'][0]
            out=[]
            if j.has_key('id'):out.append('https://youtu.be/'+j['id'])
            if j.has_key('title'):out.append(j['title'])
            if j.has_key('viewCount'):out.append(u'{:,}'.format(j['viewCount']))
            if j.has_key('rating'):out.append(u'{:.0%}'.format(j['rating']/5))
            if j.has_key('duration'):out.append(str(datetime.timedelta(seconds=j[u'duration'])))
            out[1:]=[u' | '.join(out[1:])]
            out=' > '.join(out)
            self.send_message(event.respond,out.encode('utf-8','replace'))
        except:
            print "ERROR\n",traceback.print_tb(sys.exc_info()[2]),"\nERROREND"
            self.send_message(event.respond,"No results")
    
    #Google Search
    if event.command.lower() in self._prefix('g'):
        try:
            j=requests.get(
                'https://ajax.googleapis.com/ajax/services/search/web',
                params=dict(
                    v="1.0",
                    q=event.params
                )
            ).json()[u'responseData'][u'results'][0]
            self.send_message(
                event.respond,
                u'{}: {}'.format(
                    HTMLParser.HTMLParser().unescape(j[u'titleNoFormatting']),
                    j[u'unescapedUrl']
                ).encode('utf-8','replace')
            )
        except:
            print "ERROR\n",traceback.print_tb(sys.exc_info()[2]),"\nERROREND"
            self.send_message(event.respond,"No results")

    #testing command, part channel
    if event.command.lower() in self._prefix('part'):
        if self.config.debug:
            self.part_channel("#comeinside", "I'm taking my ball and going home.")

    #testing command, join channel
    if event.command.lower() in self._prefix('join'):
        if self.config.debug:
            self.join_channel("#comeinside")

    #Random e621
    if event.command.lower() in self._prefix('rande621'):
        try:
            j=requests.get("http://e621.net/post/index.json",
                params=dict(
                    limit="100",
                    tags=event.params
                )).json()
            if (len(j) > 0):
                self.send_message(
                    event.respond,
                    u'http://e621.net/post/show/{}'.format(
                        random.choice(j)[u'id']
                    ).encode('utf-8','replace'))
            else:
                self.send_message(event.respond, "No Results")
        except:
            self.send_message(event.respond, "An error occurred while fetching your post.")
            raise


    #Random e621 clop pic
    if event.command.lower() in self._prefix('clop'):
        try:
            j=requests.get("http://e621.net/post/index.json",
                params=dict(
                    limit="100",
                    tags=event.params + " rating:e my_little_pony"
                )).json()
            if (len(j) > 0):
                self.send_message(
                    event.respond,
                    u'http://e621.net/post/show/{}'.format(
                        random.choice(j)[u'id']
                    ).encode('utf-8','replace'))
            else:
                self.send_message(event.respond, "No Results")
        except:
            self.send_message(event.respond, "An error occurred while fetching your post.")
            raise


    #new guy
    if event.command.lower() in self._prefix('newguy','oldguy'):
        self.send_message(event.respond, 
            u'{}, please enjoy the following image albums http://imgur.com/a/NFrRo http://imgur.com/a/F2XQv http://imgur.com/a/wJmdV http://imgur.com/a/wVDx6 http://imgur.com/a/ueAHb http://imgur.com/a/h2xJa http://imgur.com/a/hEuEd http://imgur.com/a/EaBpy'.format(
                event.params
            ).encode('utf-8', 'replace'))

    #Random imgur posts
    if event.command.lower() in self._prefix('randjur'):
        count = 1
        if len(event.params) > 0:
            try:
                count = int(event.params)
            except:
                self.send_message(event.respond, "Could not parse parameter")
                raise
        j=requests.get("https://api.imgur.com/3/gallery.json", 
                headers=dict(
                    Authorization="Client-ID " + self.config.imgurKey
                )).json()[u'data']
        if count > 10:
            count = 10
        images = ','.join([x[u'id'] for x in random.sample(j,count)])
        album=requests.post('https://api.imgur.com/3/album/', 
                headers=dict(
                    Authorization="Client-ID " + self.config.imgurKey), 
                params=dict(
                    ids=images
                )).json()[u'data'][u'id']
        self.send_message(
            event.respond,
            u'http://imgur.com/a/{}'.format(album).encode('utf-8', 'replace'))

    #True random imgur posts
    if event.command.lower() in self._prefix('truerandjur'):
        count = 1
        if len(event.params) > 0:
            try:
                count = int(event.params)
            except:
                self.send_message(event.respond, "Could not parse parameter")
                raise
        if count > 10:
            count = 10
        #this is gross, why do you let me do this python?
        def findImages(irc, count, respond, clientID):
            import random, requests, string
            images=[]
            while len(images) < count:
                randID = ''.join(random.choice(string.ascii_letters+string.digits) for x in range(0,5))
                j=requests.get("https://api.imgur.com/3/image/" + randID, headers=dict(Authorization="Client-ID " + clientID)).json()
                if j[u'status'] == 200:
                    images.append(j[u'data'][u'id'])
            album=requests.post('https://api.imgur.com/3/album/', 
                    headers=dict(
                        Authorization="Client-ID " + clientID), 
                    params=dict(
                        ids=','.join(images)
                    )).json()[u'data'][u'id']
            irc.send_message(
                respond,
                u'http://imgur.com/a/{}'.format(album).encode('utf-8', 'replace'))
        randjurThread = threading.Thread(target=findImages, kwargs=dict(irc=self, count=count, respond=event.respond, clientID=self.config.imgurKey))
        randjurThread.start()

    #feels
    if event.command.lower() in self._prefix('feels'):
        self.send_message(event.respond, 'http://imgur.com/a/PJIsu/layout/blog')

    #help command
    if event.command.lower() in self._prefix('help'):
        commands=dict(
            select="Usage: ~select <args> Used to select a random word from a given list",
            flip="Usage: ~flip Used to flip a coin, responds with heads or tails",
            yt="Usage: ~yt <terms> Used to search youtube with the given terms",
            g="Usage: ~g <terms> Used to search google with the given terms",
            rande621="Usage: ~rande621 <tags> Used to search e621.net for a random picture with the given tags",
            newguy="Usage: ~newguy <nick> If you don't know what this does ask an oldguy to teach you",
            oldguy="Usage: ~oldguy <nick> Reminds us why we came here",
            randjur="Usage: ~randjur <number> Used to post random imgur pictures, from the gallery, <number> defines the number of results with a max of 10",
            feels="Usage: ~feels Just in case",
            help="Usage: ~help <command> The fuck do you think it does?",
            wolf="Usage: ~wolf <query> Searches wolfram alpha for your query",
            test="Usage: ~test Used to verify the bot is responding to messages",
            gr="Usage: ~gr <query> links to the google results for a given query",
            roll="Usage: ~roll <x>d<n> rolls a number, x, of n sided dice, example: ~roll 3d20",
            ud="Usage: ~ud <query> Used to search Urban Dictionary for the first definition of a word",
            pony="Usage: ~pony Used to show the time remaining until the next episode of MLP airs",
            isup="Usage: ~isup <site> used to check if a given website is up using isup.me",
            gimg="Usage: ~gimg <terms> Used to search google images with the given terms",
            rs="Usage: ~rs <terms> Used to search for results on reddit, can narrow down to sub or user with /u/<user> or /r/<subreddit>",
            imply="Usage: ~imply <text> Used to imply things.",
            dns="Usage: ~dns <domain> Used to check which IPs are associated with a DNS listing",
            movie="Usage: ~movie <film> Used to search trakt for the listing for a film.",
            tpb="Usage: ~tpb <query> Used to search the pirate bay for the most seeded entry for a given query.",
            tv="Usage: ~tv <show> Used to search trakt for the listing for a tv show.",
            episode="Usage: ~episode <film> Used to search trakt for the listing for an episode.",
            implying="Usage: ~implying <implications> turns text green and adds >Implying",
            clop="Usage: ~clop <optional extra tags> Searches e621 for a random image with the tags rating:e and my_little_pony",
            truerandjur="Usage: ~truerandjur <number> Used to post random imgur pictures, from randomly generated IDs, takes a little while to find images so be patient, <number> defines the number of results with a max of 10",
            es="Usage: ~es <query> searches for emotes on the PMV. Can be any valid search for BPM. Example: ~es sr:comeinside +pp"
            )
        if len(event.params) <= 0:
            self.send_message(
                event.respond,
                "Currently supported commands: {}. ".format(
                    ', '.join([x for x in commands.keys()])) + 
                "For more information on a command type ~help <command>"
                )
        else:
            
            try:
                response=commands[event.params]
            except:
                response="Invalid argument"
            self.send_message(
                event.respond,
                response
            )

    if event.command.lower() in self._prefix('weather'):
        event.command = self.config.prefixes[0] + 'wolf'
        event.params = 'weather ' + event.params

    #Wolfram Alpha
    if event.command.lower() in self._prefix('wolf'):
        try:
            s=requests.get("http://api.wolframalpha.com/v2/query", 
                params=dict(
                    input=event.params,
                    appid=self.config.wolframKey
                    )
                ).text

            x=etree.fromstring(s.encode('UTF-8', 'replace'))
            d=x.xpath('//pod[@primary="true"]/subpod/plaintext')

            results=[o.text.replace('\n', '').encode('utf-8', 'replace') for o in d]

            if len(results) < 1:
                responseStr = "No results available, try the query page:"
            else:
                responseStr = '; '.join(results)

            if len(responseStr) > 384:
                responseStr = responseStr[:384] + "..."

            responseStr += " http://www.wolframalpha.com/input/?i={}".format(urllib.quote(event.params, ''))

            self.send_message(
                event.respond,
                responseStr
            )
        except:
            self.send_message(
                event.respond,
                "Error with the service"
            )
            raise

    #Test
    if event.command.lower() in self._prefix('test'):
        possibleAnswers=[
            "Cake, and grief counseling, will be available at the conclusion of the test.",
            "Remember, the Aperture Science Bring Your Daughter to Work Day is the perfect time to have her tested.",
            "As part of an optional test protocol, we are pleased to present an amusing fact: The device is now more valuable than the organs and combined incomes of everyone in *subject hometown here.*",
            "The Enrichment Center promises to always provide a safe testing environment. In dangerous testing environments, the Enrichment Center promises to always provide useful advice. For instance: the floor here will kill you. Try to avoid it.",
            "Due to mandatory scheduled maintenance, the next test is currently unavailable. It has been replaced with a live-fire course designed for military androids. The Enrichment Center apologizes and wishes you the best of luck. ",
            "Well done. Here are the test results: You are a horrible person. I'm serious, that's what it says: \"A horrible person.\" We weren't even testing for that."
            ]
        self.send_message(
            event.respond,
            random.choice(possibleAnswers)
            )

    #Google Results
    if event.command.lower() in self._prefix('gr'):
        self.send_message(
            event.respond,
            "http://google.com/#q={}".format(urllib.quote(event.params, ''))
            )

    #Dice roll
    if event.command.lower() in self._prefix('roll'):
        strippedparams=''.join(event.params.split())
        args=strippedparams.split('d')

        try:
            numDice=int(args[0])
        except:
            self.send_message(
            event.respond,
            "Invalid parameters, expected format is <int>d<int> Example: 1d6"
            )
            raise

        try:
            dieSize=int(args[1])
        except:
            self.send_message(
            event.respond,
            "Invalid parameters, expected format is <int>d<int> Example: 1d6"
            )
            raise

        if numDice > 10 or dieSize > 100:
            self.send_message(
            event.respond,
            "The Maximum number of dice is 10, and the maximum number of sides is 100"
            )
        else:
            self.send_message(
            event.respond,
            "Results: {}".format(', '.join([str(random.randint(1,dieSize)) for x in range(numDice)]))
            )

    #Urban Dictionary search
    if event.command.lower() in self._prefix('ud'):
        try:
            j=requests.get("http://api.urbandictionary.com/v0/define",
                params=dict(
                    term=event.params
                )).json()[u'list']
            if (len(j) > 0):
                self.send_message(
                    event.respond,
                    j[0][u'definition'].replace('\r', '').replace('\n', ' ').encode('UTF-8', 'replace')
                    )
            else:
                self.send_message(event.respond, "No Results")
        except:
            self.send_message(event.respond, "An error occurred while fetching your post.")
            raise

    #Time until next pony episode
    if event.command.lower() in self._prefix('pony'):
        class LocalTZ(datetime.tzinfo):
            _unixEpochOrdinal = datetime.datetime.utcfromtimestamp(0).toordinal()

            def dst(self, dt):
                return datetime.timedelta(0)

            def utcoffset(self, dt):
                t = (dt.toordinal() - self._unixEpochOrdinal)*86400 + dt.hour*3600 + dt.minute*60 + dt.second + time.timezone
                utc = datetime.datetime(*time.gmtime(t)[:6])
                local = datetime.datetime(*time.localtime(t)[:6])
                return local - utc

        class UTC(tzinfo):
            """UTC"""
        
            def utcoffset(self, dt):
                return timedelta(0)
        
            def tzname(self, dt):
                return "UTC"
        
            def dst(self, dt):
                return timedelta(0)

        if datetime.datetime.now(LocalTZ()) < datetime.datetime(year=2013, month=11, day=23, hour=15, minute=30, tzinfo=UTC()):
            wait=datetime.datetime(year=2013, month=11, day=23, hour=15, minute=30, tzinfo=UTC()) - datetime.datetime.now(LocalTZ())
        else:
            airdate=datetime.datetime.now(LocalTZ()) + timedelta((12 - datetime.datetime.now(LocalTZ()).weekday()) % 7)
            wait = datetime.datetime(year=airdate.year, month=airdate.month, day=airdate.day, hour=14, minute=30, tzinfo=UTC()) - datetime.datetime.now(LocalTZ())
            
        self.send_message(
            event.respond,
            '{} Days, {} Hours, {} Minutes remaining until the next episode'.format(
                wait.days,
                wait.seconds/3600,
                wait.seconds/60%60
                )
            )

    #isup.me check if website is up
    if event.command.lower() in self._prefix('isup'):
        try:
            s=requests.get("http://isup.me/{}".format(
                event.params
                )).text
            if "It's just you." in s:
                response="It's just you! {} is up!".format(event.params)
            else:
                response="It's not just you! {} looks down from here!".format(event.params)
            self.send_message(
                event.respond,
                response
            )
        except:
            self.send_message(
                event.respond,
                "Error with the service"
            )
            raise

    #Google Image Search
    if event.command.lower() in self._prefix('gimg'):
        try:
            j=requests.get(
                'https://ajax.googleapis.com/ajax/services/search/images',
                params=dict(
                    v="1.0",
                    q=event.params
                )
            ).json()[u'responseData'][u'results'][0]
            self.send_message(
                event.respond,
                u'{}: {}'.format(
                    HTMLParser.HTMLParser().unescape(j[u'titleNoFormatting']),
                    j[u'unescapedUrl']
                ).encode('utf-8','replace')
            )
        except:
            print "ERROR\n",traceback.print_tb(sys.exc_info()[2]),"\nERROREND"
            self.send_message(event.respond, "No results.")

    #Reddit Search
    if event.command.lower() in self._prefix('rs'):
        query=event.params
        #allow searching by /r/subreddit
        srmatch=re.compile('/(r|u)/(\w+(?:\+\w+)*(?:/\S+)*)', re.I)
        srmatches = srmatch.findall(event.params)
        submatches=[s[1] for s in srmatches if s[0] == 'r']
        usermatches=[s[1] for s in srmatches if s[0] == 'u']
        terms = []
        if len(submatches) > 0:
            terms.append("subreddit:{}".format(submatches[0]))
        if len(usermatches) > 0:
            terms.append("author:{}".format(usermatches[0]))
        if len(terms) > 0:
            query=srmatch.sub("", query)
            query=query.rstrip().lstrip()
        terms.append(query)
        j=requests.get(
            'http://www.reddit.com/search.json',
            params=dict(
                limit="1",
                q=' '.join(terms)
            )
        ).json()[u'data'][u'children']
        if len(j) > 0:
            self.send_message(
                event.respond,
                u'http://reddit.com{} - {}'.format(
                    j[0][u'data'][u'permalink'],
                    HTMLParser.HTMLParser().unescape(j[0][u'data'][u'title'])
                ).encode('utf-8','replace')
            )
        else:
            self.send_message(
                event.respond,
                'No results.'
                )

    #Emotes!
    if not self.config.raribot:
        exp = re.compile('(?:\[\]\(/([a-zA-Z0-9-!:]*)(?: ".*")?\))|(?:\\\\\\\\([a-zA-Z0-9-!:]*)(?: ".*")?)')
        matches = exp.findall(event.message)
        emotes = []
        emotes.extend([e[1] for e in matches if e[1] != ''])
        emotes.extend([e[0] for e in matches if e[0] != ''])
        response = ""
        for x in emotes:
            response += 'http://comeinside.org/emote/{}/ '.format(urllib.quote(x))
        self.send_message(event.respond, response.rstrip())

    if event.command.lower() in self._prefix('es') and not self.config.raribot:
        self.send_message(event.respond, 'http://comeinside.org/emote/#{} '.format(urllib.quote(event.params)))

    #Subreddit links!
    if not event.command.lower() in self._prefix('rs'):
        srmatch=re.compile('(?<!\S)/(r|u)/(\w+(?:\+\w+)*(?:/\S+)*)', re.I)
        srmatches = srmatch.findall(event.message)
        subrootmatches=[s[1] for s in srmatches if s[0] == 'r' and not '/' in s[1]]
        suburlmatches=[s[1] for s in srmatches if s[0] == 'r' and '/' in s[1]]
        usermatches=[s[1] for s in srmatches if s[0] == 'u']
        links = []
        if len(subrootmatches) > 0:
            links.append("http://reddit.com/r/{}".format('+'.join(subrootmatches)))
        for link in suburlmatches:
            links.append("http://reddit.com/r/{}".format(link))
        for link in usermatches:
            links.append("http://reddit.com/u/{}".format(link))
        if len(links) > 0:
            self.send_message(event.respond, ' '.join(links))

    #Imply
    if event.command.lower() in self._prefix('imply'):
        self.send_message(event.respond, format.color(">" + event.params, format.GREEN))

    #DNS
    if event.command.lower() in self._prefix('dns'):
        try:
            records = socket.getaddrinfo(event.params.split(' ')[0], 80)
            addresses = set([x[4][0] for x in records])
            self.send_message(event.respond, " ".join(addresses))
        except:
            self.send_message(event.respond, "You must give a valid host name to look up")

    #Reboot
    if event.command.lower() in self._prefix('reboot'):
        if event.host in self.config.adminhosts:
            self.quit("My primary function is failure.")
            os.execl(sys.executable, *([sys.executable]+sys.argv))
        else:
            self.send_message(event.respond, "YOU'RE NOT THE BOSS OF ME!")


    #Movie Search
    if event.command.lower() in self._prefix('movie'):
        try:
            j=requests.get(
                'http://api.trakt.tv/search/movies.json/{}/{}'.format(self.config.traktKey, event.params), 
                headers={"User-Agent": 'Berry Punch IRC Bot'}
            ).json()[0]


            movieid = ''
            if j.has_key('imdb_id') and j['imdb_id'] != '': 
                movieid = j['imdb_id']
            else: 
                if j.has_key('tvdb_id'): 
                    movieid = j['tvdb_id']
            if movieid == '':
                raise Exception('No results')

            j=requests.get(
                'http://api.trakt.tv/movie/summary.json/{}/{}'.format(self.config.traktKey, movieid),
                headers={"User-Agent": 'Berry Punch IRC Bot'}
            ).json()

            out = []
            if j.has_key('title'): out.append(j['title'])
            if j.has_key('genres'): out.append(', '.join(j['genres'][:3]))
            if j.has_key('people'):
               if j['people'].has_key('actors'):
                  out.append(', '.join([s['name'] for s in j['people']['actors'][:3]]))
            if j.has_key('overview'): out.append(j['overview'][:100] + '...')
            if j.has_key('ratings'):
               if j['ratings'].has_key('percentage'): 
                   out.append(str(j['ratings']['percentage']) + '%')
            if j.has_key('year'): out.append(str(j['year']))
            if j.has_key('url'): out.append(j['url'])


            self.send_message(
                event.respond,
                (' | '.join(out)).encode('utf-8','replace')
            )
        except:
            self.send_message(
                event.respond,
                "Could not find the specified film, please try again."
            )
            raise

    #TV Show Search
    if event.command.lower() in self._prefix('tv'):
        try:
            j=requests.get(
                'http://api.trakt.tv/search/shows.json/{}/{}'.format(self.config.traktKey, event.params), 
                headers={"User-Agent": 'Berry Punch IRC Bot'}
            ).json()[0]


            showid = ''
            if j.has_key('imdb_id') and j['imdb_id'] != '': 
                showid = j['imdb_id']
            else: 
                if j.has_key('tvdb_id'): 
                    showid = j['tvdb_id']
            if showid == '':
                raise Exception('No results')

            j=requests.get(
                'http://api.trakt.tv/show/summary.json/{}/{}'.format(self.config.traktKey, showid),
                headers={"User-Agent": 'Berry Punch IRC Bot'}
            ).json()

            out = []
            if j.has_key('title'): out.append(j['title'])
            if j.has_key('genres'): out.append(', '.join(j['genres'][:3]))
            if j.has_key('people'):
               if j['people'].has_key('actors'):
                  out.append(', '.join([s['name'] for s in j['people']['actors'][:3]]))
            if j.has_key('overview'): out.append(j['overview'][:100] + '...')
            if j.has_key('ratings'):
               if j['ratings'].has_key('percentage'): 
                   out.append(str(j['ratings']['percentage']) + '%')
            if j.has_key('year'): out.append(str(j['year']))
            if j.has_key('url'): out.append(j['url'])


            self.send_message(
                event.respond,
                (' | '.join(out)).encode('utf-8','replace')
            )
        except:
            self.send_message(
                event.respond,
                "Could not find the specified film, please try again."
            )
            raise

    #TV Episode Search
    if event.command.lower() in self._prefix('episode'):
        try:
            j=requests.get(
                'http://api.trakt.tv/search/episodes.json/{}/{}'.format(self.config.traktKey, event.params), 
                headers={"User-Agent": 'Berry Punch IRC Bot'}
            ).json()[0]


            showid = ''
            if j.has_key('show'):
                if j['show'].has_key('imdb_id') and j['show']['imdb_id'] != '': 
                    showid = j['show']['imdb_id']
                else: 
                    if j['show'].has_key('tvdb_id'): 
                        showid = j['show']['tvdb_id']
            if showid == '':
                raise Exception('No results')

            season = ''
            episode = ''
            if j.has_key('episode'):
                if j['episode'].has_key('season'): 
                    season = j['episode']['season']
                if j['episode'].has_key('episode'): 
                    episode = j['episode']['episode']
            if season == '' or episode == '':
                raise Exception('No results')

            j=requests.get(
                'http://api.trakt.tv/show/episode/summary.json/{}/{}/{}/{}'.format(self.config.traktKey, showid, season, episode),
                headers={"User-Agent": 'Berry Punch IRC Bot'}
            ).json()

            out = []
            if j.has_key('show'):
                if j['show'].has_key('title'): out.append(j['show']['title'])
                if j['show'].has_key('genres'): out.append(', '.join(j['show']['genres'][:3]))
            if j.has_key('episode'):
                if j['episode'].has_key('title'): out.append(j['episode']['title'])
                if j['episode'].has_key('season'): out.append("Season " + str(j['episode']['season']))
                if j['episode'].has_key('number'): out.append("Episode " + str(j['episode']['number']))
                if j['episode'].has_key('overview'): out.append(j['episode']['overview'][:100] + '...')
                if j['episode'].has_key('ratings'):
                   if j['episode']['ratings'].has_key('percentage'): 
                       out.append(str(j['episode']['ratings']['percentage']) + '%')
                if j['episode'].has_key('url'): out.append(j['episode']['url'])


            self.send_message(
                event.respond,
                (' | '.join(out)).encode('utf-8','replace')
            )
        except:
            self.send_message(
                event.respond,
                "Could not find the specified episode, please try again."
            )
            raise

    #IMDB Search
    if event.command.lower() in self._prefix('tpb'):
        try:
            tpb = requests.get("http://thepiratebay.sx/search/{}/0/7/0".format(event.params)).text
            tpbHTML = lxml.html.fromstring(tpb)
            tpbHTML.make_links_absolute("http://thepiratebay.sx")
            links = tpbHTML.iterlinks()
            tpbLink = ''
            while tpbLink == '':
                currentLink = next(links)[2]
                if currentLink.startswith("http://thepiratebay.sx/torrent/"):
                    tpbLink = currentLink
            self.send_message(event.respond, tpbLink[:tpbLink.rfind('/')+1])
        except:
            self.send_message(event.respond, "No results, or TPB is down")

    #Bullshit ensues, MAL is now an alias for a google search.
    if event.command.lower() in self._prefix('mal'):
        try:
            j=requests.get(
                'https://ajax.googleapis.com/ajax/services/search/web',
                params=dict(
                    v="1.0",
                    q=event.params + " site:myanimelist.net"
                )
            ).json()[u'responseData'][u'results'][0]
            self.send_message(
                event.respond,
                u'{}: {}'.format(
                    HTMLParser.HTMLParser().unescape(j[u'titleNoFormatting']),
                    j[u'unescapedUrl']
                ).encode('utf-8','replace')
            )
        except:
            print "ERROR\n",traceback.print_tb(sys.exc_info()[2]),"\nERROREND"
            self.send_message(event.respond,"No results")

    #Implying
    if event.command.lower() in self._prefix('implying'):
        self.send_message(event.respond, format.color(">Implying " + event.params, format.GREEN))

    #dA info fetcher
    damatch=re.compile('((?:(?:https?|ftp|file)://|www\.|ftp\.)(?:\([-A-Z0-9+&@#/%=~_|$?!:,.]*\)|[-A-Z0-9+&@#/%=~_|$?!:,.])*(?:\([-A-Z0-9+&@#/%=~_|$?!:,.]*\)|[A-Z0-9+&@#/%=~_|$]))', re.I)
    damatches = damatch.findall(event.message)
    for x in damatches:
        try:
            consumer = oembed.OEmbedConsumer()
            endpoint = oembed.OEmbedEndpoint('http://backend.deviantart.com/oembed', ['http://*.deviantart.com/art/*', 'http://fav.me/*', 'http://sta.sh/*', 'http://*.deviantart.com/*#/d*'])
            consumer.addEndpoint(endpoint)
            response = consumer.embed(x).getData()
            out=[]
            if response.has_key(u'title'): out.append("Title: {}".format(response[u'title']))
            if response.has_key(u'author_name'): out.append("Artist: {}".format(response[u'author_name']))
            if response.has_key(u'rating'): 
                out.append("Rating: {}".format(response[u'rating']))
                if response.has_key(u'url'): out.append("Direct Url: {}".format(response[u'url']))
            self.send_message(
                event.respond,
                " | ".join(out).encode('utf-8','replace')
                )
        except oembed.OEmbedNoEndpoint:
            pass
        except urllib2.HTTPError:
            pass
