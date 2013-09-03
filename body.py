import HTMLParser,re,urllib,json,random,requests,datetime,socket,os,sys,HTMLParser,oembed,urllib2,urllib,threading;from ircutils import format
import xml.etree.ElementTree as ET
import lxml.html

#Invite Responder
if event.command=="INVITE":
    self.join_channel(event.params[0])
 
#AAAAAAAA
if event.command in ['PRIVMSG']:
    #Initialize the event
    event.command=event.message.split(' ')[0]

    if (event.command[:1] == '<' and event.command[-1:] == '>'):
    #if (event.command[-1:] == ':' and event.source == 'S'):
        try: event.command = event.message.split(' ', 2)[1]
        except: event.command = ''
        try: event.params=event.message.split(' ',2)[2]
        except: event.params = ''
    else:
        try:   event.params=event.message.split(' ',1)[1]
        except:event.params=''
     
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
            print x
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
            u'{}, please enjoy the following image albums http://imgur.com/a/F2XQv http://imgur.com/a/wJmdV http://imgur.com/a/wVDx6 http://imgur.com/a/ueAHb http://imgur.com/a/h2xJa http://imgur.com/a/hEuEd'.format(
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
            import random, requests
            images=[]
            foundImages = 0
            while foundImages < count:
                randID = ""
                for x in range(0, 5): 
                    randID += random.choice("1234567890qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM")
                j=requests.get("https://api.imgur.com/3/image/" + randID, headers=dict(Authorization="Client-ID " + clientID)).json()
                if j[u'status'] == 200:
                    foundImages += 1
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
            emote="Usage: ~emote <emote> Used to show an emote in the browser, relies on BPM. Example: ~emote vseyeroll",
            imply="Usage: ~imply <text> Used to imply things.",
            dns="Usage: ~dns <domain> Used to check which IPs are associated with a DNS listing",
            imdb="Usage: ~imdb <film> Used to search IMDB for the listing for a film.",
            implying="Usage: ~implying <implications> turns text green and adds >Implying",
            clop="Usage: ~clop <optional extra tags> Searches e621 for a random image with the tags rating:e and my_little_pony",
            truerandjur="Usage: ~truerandjur <number> Used to post random imgur pictures, from randomly generated IDs, takes a little while to find images so be patient, <number> defines the number of results with a max of 10"
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

    #Wolfram Alpha
    if event.command.lower() in self._prefix('wolf'):
        try:
            s=requests.get("http://api.wolframalpha.com/v2/query", 
                params=dict(
                    input=event.params,
                    appid=self.config.wolframKey
                    )
                ).text
            results =[]
            root = ET.fromstring(s.encode('utf-8', errors='replace'))
            for child in root.findall('pod'):
                if child.attrib.has_key("primary"):
                    if child.attrib["primary"] == 'true':
                        results.append(child.find('subpod').find('plaintext').text.replace('\n', ' '))

            if len(results) < 1:
                responseStr = "No results available, try the query page:"
            else:
                responseStr = '; '.join(results).encode('utf-8', errors='replace')
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
            wait = datetime.datetime(year=airdate.year, month=airdate.month, day=airdate.day, hour=15, minute=30, tzinfo=UTC()) - datetime.datetime.now(LocalTZ())
            
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
    if event.command.lower() in self._prefix('emote'):
        event.params = event.params.split()[0]
        self.send_message(event.respond, 'http:///comeinside.org/emote/{}/'.format(event.params.replace('!', '_excl_').replace(':', '_colon_')))

    if config.autoemote:
        exp = re.compile('(?:\[\]\(/([a-zA-Z0-9-!:]*)(?: ".*")?\))|(?:\\\\([a-zA-Z0-9-!:]*)(?: ".*")?)')
        matches = exp.findall(event.message)
        emotes = []
        emotes.extend([e[1] for e in matches if e[1] != ''])
        emotes.extend([e[0] for e in matches if e[0] != ''])
        response = ""
        for x in emotes:
            response += 'http://comeinside.org/emote/{}/ '.format(x.replace('!', '_excl_').replace(':', '_colon_'))
        self.send_message(event.respond, response.rstrip())


    if event.command.lower() in self._prefix('autoemote'):
        config.autoemote = not config.autoemote
        self.config.setEmote(config.autoemote) 
        self.send_message(event.respond, "Setting auto emote to " + str(config.autoemote))


    #Subreddit links!
    if not event.command.lower() in self._prefix('rs'):
        srmatch=re.compile('(?<!reddit.com)/(r|u)/(\w+(?:\+\w+)*(?:/\S+)*)', re.I)
        srmatches = srmatch.findall(event.message)
        submatches=[s[1] for s in srmatches if s[0] == 'r']
        usermatches=[s[1] for s in srmatches if s[0] == 'u']
        links = []
        if len(submatches) > 0:
            links.append("http://reddit.com/r/{}".format('+'.join(submatches)))
        if len(usermatches) > 0:
            links.append("http://reddit.com/u/{}".format('+'.join(usermatches)))
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
        if event.source in self.config.authorizedUsers and event.params == self.config.password:
            self.quit("My primary function is failure.")
            os.execl(sys.executable, *([sys.executable]+sys.argv))
        else:
            self.send_message(event.respond, "YOU'RE NOT THE BOSS OF ME!")


    #IMDB Search
    if event.command.lower() in self._prefix('imdb'):
        try:
            j=requests.get(
                'http://mymovieapi.com/',
                params=dict(
                    title=event.params,
                    type='json'
                )
            ).json()[0]
            out = []
            if j.has_key('title'): out.append(j['title'])
            if j.has_key('genres'): out.append(', '.join(j['genres'][:3]))
            if j.has_key('actors'): out.append(', '.join(j['actors'][:3]))
            if j.has_key('rating'): out.append(str(j['rating']))
            if j.has_key('year'): out.append(str(j['year']))
            if j.has_key('imdb_url'): out.append(j['imdb_url'])

            try:
                title = j['title']
                tpb = requests.get("http://thepiratebay.sx/search/{}/0/7/0".format(title)).text
                tpbHTML = lxml.html.fromstring(tpb)
                tpbHTML.make_links_absolute("http://thepiratebay.sx")
                links = tpbHTML.iterlinks()
                tpbLink = '';
                while tpbLink == '':
                    currentLink = next(links)[2]
                    if currentLink.startswith("http://thepiratebay.sx/torrent/"):
                        tpbLink = currentLink
                out.append(tpbLink[:tpbLink.rfind('/')+1])
            except:
                pass


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
