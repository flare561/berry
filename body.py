import random
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
                j[u'titleNoFormatting'],
                j[u'unescapedUrl']
            ).encode('utf-8','replace')
        )

    #if event.command.lower() in ["~part", "!part"]:
    #    self.part_channel("#MLAS1", "I'm taking my ball and going home.")

    #if event.command.lower() in ["~join", "!join"]:
    #    self.join_channel("#MLAS1")

    if event.command.lower() in ["~rande621", "!rande621"]:
        j=requests.get("http://e621.net/post/index.json",
                       params=dict(limit="100", tags=event.params)).json()
        resultCount = len(j)
        if (resultCount > 0):
            self.send_message(event.respond, u'http://e621.net/post/show/{}'.format(j[random.randint(0,resultCount)][u'id']).encode('utf-8','replace'))
        else:
            self.send_message(event.respond, "No Results")
    
    if event.command.lower() in ["~newguy", "!newguy"]:
        self.send_message(event.respond, u'{}, please enjoy the following image albums http://newguy.mlas1.org http://imgur.com/a/F2XQv http://imgur.com/a/0O33r http://imgur.com/a/wJmdV http://imgur.com/a/wVDx6 http://imgur.com/a/ueAHb http://imgur.com/a/h2xJa http://imgur.com/a/hEuEd'.format(
                            event.params).encode('utf-8', 'replace'))
