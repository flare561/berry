import HTMLParser,datetime,re,urllib,json,random,requests;from ircutils import format
 
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
    if event.message[0] not in '*(9&_[{<>},.])-0':
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
    #if event.command.lower() in ["~part", "!part"]:
    #    self.part_channel("#MLAS1", "I'm taking my ball and going home.")

    #testing command, join channel
    #if event.command.lower() in ["~join", "!join"]:
    #    self.join_channel("#MLAS1")

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
                    Authorization="Client-ID d85094527f204d5"
                )).json()[u'data']
        if count > 10:
            count = 10
        ids = ','.join([x[u'id'] for x in random.sample(j,count)])
        self.send_message(
            event.respond,
            u'http://imgur.com/{}'.format(ids).encode('utf-8', 'replace'))

    #feels
    if event.command.lower() in ["~feels", "!feels"]:
        self.send_message(event.respond, 'http://imgur.com/a/PJIsu')

    #help command
    if event.command.lower() in ["~help", "!help"]:
        if len(event.params) <= 0:
            self.send_message(
                event.respond,
                "Currently supported commands: select, flip, yt, g, rande621, newguy, oldguy, randjur, feels, help. For more information on a command type ~help <command>"
            )
        else:
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
                help="Usage: ~help <command> The fuck do you think it does?"
            )
            try:
                response=commands[event.params]
            except:
                response="Invalid argument"
            self.send_message(
                event.respond,
                response
            )