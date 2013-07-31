import HTMLParser,re,urllib,json,random,requests,datetime,socket,os,sys;from ircutils import format
import xml.etree.ElementTree as ET
 
#Invite Responder
if event.command=="INVITE":
    self.join_channel(event.params[0])
 
#AAAAAAAA
if event.command in ['PRIVMSG']:
    #Initalise the event
    event.command=event.message.split(' ')[0]
    try:   event.params=event.message.split(' ',1)[1]
    except:event.params=''
     
    #Select Roller
    if event.command in ['~select', '!select'] and len(event.params)>0:
        self.send_message(event.respond,'Select: {}'.format(random.choice(event.params.split(' '))))
 
    #Flip
    if event.command in ['~flip','!flip']:
        self.send_message(event.respond,'Flip: {}'.format(random.choice(['Heads','Tails'])))
         
    #Youtube info fetcher
    ytmatch=re.compile(
        "https?:\/\/(?:[0-9A-Z-]+\.)?(?:youtu\.be\/|youtube\.com\S*[^\w\-\s"
        "])([\w\-]{11})(?=[^\w\-]|$)(?![?=&+%\w]*(?:['\"][^<>]*>|<\/a>))[?="
        "&+%\w-]*",
        flags=re.I)
    matches=ytmatch.findall(event.message)
    for x in matches:
        try:
            j=requests.get(
                'https://gdata.youtube.com/feeds/api/videos/'+x,
                params=dict(
                    v=2,
                    alt="jsonc"
                )
            ).json()[u'data']
            self.send_message(
                event.respond,
                u'{title} | {views:,} | {rating:.0%} | {time}'.format(
                    title  = j['title'],
                    views  = j['viewCount'],
                    rating = j['rating']/5,
                    time   = datetime.timedelta(seconds=j[u'duration'])
                ).encode('utf-8','replace')
            )
        except:
            pass

    #Youtube search
    if event.command.lower() in ['~yt','!yt']:
        try:
            j=requests.get(
                'https://gdata.youtube.com/feeds/api/videos',
                params=dict(
                    {'max-results':1},
                    q  = event.params,
                    v  = 2,
                    alt= "jsonc"
                )
            ).json()[u'data'][u'items'][0]
            self.send_message(
                event.respond,
                u'https://youtu.be/{id} > {title} | {views:,} | {rating:.0%} | {time}'.format(
                    id     = j['id'],
                    title  = j['title'],
                    views  = j['viewCount'],
                    rating = j['rating']/5,
                    time   = datetime.timedelta(seconds=j[u'duration'])
                ).encode('utf-8','replace')
            )
        except:
            print "ERROR\n",traceback.print_tb(sys.exc_info()[2]),"\nERROREND"
            self.send_message(event.respond,"No results")
    
    #Google Search
    if event.command.lower() in ['~g','!g']:
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
    if event.command.lower() in ["~part", "!part"]:
        if self.config.debug:
            self.part_channel("#MLAS1", "I'm taking my ball and going home.")

    #testing command, join channel
    if event.command.lower() in ["~join", "!join"]:
        if self.config.debug:
            self.join_channel("#MLAS1")

    #Random e621
    if event.command.lower() in ["~rande621", "!rande621"]:
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

    #new guy
    if event.command.lower() in ["~newguy", "!newguy", "~oldguy", "!oldguy"]:
        self.send_message(event.respond, 
            u'{}, please enjoy the following image albums http://newguy.mlas1.org http://imgur.com/a/F2XQv http://imgur.com/a/0O33r http://imgur.com/a/wJmdV http://imgur.com/a/wVDx6 http://imgur.com/a/ueAHb http://imgur.com/a/h2xJa http://imgur.com/a/hEuEd'.format(
                event.params
            ).encode('utf-8', 'replace'))

    #Random imgur posts
    if event.command.lower() in ["~randjur", "!randjur"]:
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
        ids = ','.join([x[u'id'] for x in random.sample(j,count)])
        self.send_message(
            event.respond,
            u'http://imgur.com/{}'.format(ids).encode('utf-8', 'replace'))

    #feels
    if event.command.lower() in ["~feels", "!feels"]:
        self.send_message(event.respond, 'http://imgur.com/a/PJIsu/layout/blog')

    #help command
    if event.command.lower() in ["~help", "!help"]:
        commands=dict(
            select="Usage: ~select <args> Used to select a random word from a given list",
            flip="Usage: ~flip Used to flip a coin, responds with heads or tails",
            yt="Usage: ~yt <terms> Used to search youtube with the given terms",
            g="Usage: ~g <terms> Used to search google with the given terms",
            rande621="Usage: ~rande621 <tags> Used to search e621.net for a random picture with the given tags",
            newguy="Usage: ~newguy <nick> If you don't know what this does ask an oldguy to teach you",
            oldguy="Usage: ~oldguy <nick> Reminds us why we came here",
            randjur="Usage: ~randjur <number> Used to post random imgur pictures, <number> defines the number of results with a max of 10",
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
            rs="Usage: ~rs <terms> Used to search for results on reddit, it's simply a google search with the restriction site:reddit.com",
            emote="Usage: ~emote <emote> Used to show an emote in the browser, relies on BPM. Example: ~emote vseyeroll",
            imply="Usage: ~imply <text> Used to imply things.",
            dns="Usage: ~dns <domain> Used to check which IPs are associated with a DNS listing"
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
    if event.command.lower() in ["~wolf", "!wolf"]:
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
    if event.command.lower() in ["~test", "!test"]:
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
    if event.command.lower() in ["~gr", "!gr"]:
        self.send_message(
            event.respond,
            "http://google.com/#q={}".format(urllib.quote(event.params, ''))
            )

    #Dice roll
    if event.command.lower() in ["~roll", "!roll"]:
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
    if event.command.lower() in ["~ud", "!ud"]:
        try:
            j=requests.get("http://api.urbandictionary.com/v0/define",
                params=dict(
                    term=event.params
                )).json()[u'list']
            if (len(j) > 0):
                self.send_message(
                    event.respond,
                    j[0][u'definition'].encode('UTF-8', 'replace')
                    )
            else:
                self.send_message(event.respond, "No Results")
        except:
            self.send_message(event.respond, "An error occurred while fetching your post.")
            raise

    #Time until next pony episode
    if event.command.lower() in ["~pony", "!pony"]:
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
    if event.command.lower() in ["~isup", "!isup"]:
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
    if event.command.lower() in ['~gimg','!gimg']:
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
    if event.command.lower() in ['~rs','!rs']:
        j=requests.get(
            'https://ajax.googleapis.com/ajax/services/search/web',
            params=dict(
                v="1.0",
                q=event.params + " site:reddit.com"
            )
        ).json()[u'responseData'][u'results'][0]
        self.send_message(
            event.respond,
            u'{}: {}'.format(
                HTMLParser.HTMLParser().unescape(j[u'titleNoFormatting']),
                j[u'unescapedUrl']
            ).encode('utf-8','replace')
        )

    #Emotes!
    if event.command.lower() in ["~emote", "!emote"] or (config.autoemote and event.message.startswith('[](/')):
        if event.message.startswith('[](/'):
            event.params = event.message
        if event.params.startswith('[](/'):
            event.params = event.params[4:]
        if ')' in event.params:
            event.params = event.params.split(')')[0]
        event.params = event.params.split()[0]
        parameters = "emote="
        parts = event.params.split('-')
        parameters += parts[0]
        if len(parts) > 1:
            parameters += "&flag=" + parts[1]

        self.send_message(event.respond, 'http://mlas1.com/emotes.html?{}'.format(parameters))

    if event.command.lower() in ["~autoemote", "!autoemote"]:
        config.autoemote = not config.autoemote
        self.config.setEmote(config.autoemote) 
        self.send_message(event.respond, "Setting auto emote to " + str(config.autoemote))


    #Imply
    if event.command.lower() in ["~imply", "!imply"]:
        self.send_message(event.respond, format.color(">" + event.params, format.GREEN))

    #DNS
    if event.command.lower() in ["~dns", "!dns"]:
        try:
            records = socket.getaddrinfo(event.params, 80)
            addresses = set([x[4][0] for x in records])
            self.send_message(event.respond, " ".join(addresses))
        except:
            self.send_message(event.respond, "You must give a valid host name to look up")

    #Reboot
    if event.command.lower() in ["~reboot", "!reboot"]:
        if event.source in self.config.authorizedUsers and event.params == self.config.password:
            self.quit("My primary function is failure.")
            os.execl(sys.executable, *([sys.executable]+sys.argv))
        else:
            self.send_message(event.respond, "YOU'RE NOT THE BOSS OF ME!")

    #dA info fetcher
    #words = "".split() #event.message.split()

    #for x in matches:
    #    try:
    #        j=requests.get(
    #            'http://backend.deviantart.com/oembed',
    #            params=dict(
    #                url=x
    #            )
    #        ).json()[u'data']
    #        self.send_message(
    #            event.respond,
    #            u'{title} | {views:,} | {rating:.0%} | {time}'.format(
    #                title  = j['title'],
    #                views  = j['viewCount'],
    #                rating = j['rating']/5,
    #                time   = datetime.timedelta(seconds=j[u'duration'])
    #            ).encode('utf-8','replace')
    #        )
    #    except:
    #        pass