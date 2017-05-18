# -*- coding: utf-8 -*-
import HTMLParser
import random
import requests
import datetime
import socket
import oembed
import urllib2
import urllib
import threading
import functools
import lxml.html
import lxml.etree as etree
import wikipedia as wiki
import re
import arrow
import string
from urlparse import urlparse

def register(tag, value):
    def wrapped(fn):
        @functools.wraps(fn)
        def wrapped_f(*args, **kwargs):
            return fn(*args, **kwargs)

        setattr(wrapped_f, tag, value)
        return wrapped_f

    return wrapped


def is_str_allowed(str, bannedwords):
    for pattern in bannedwords:
        escapedv = re.escape(pattern)
        escapedv = escapedv.replace('\\*', '.*')
        matches = re.search(escapedv, str)
        if matches:
            return False
    return True


def is_all_str_allowed(strs, bannedwords):
    for str in strs:
        if not is_str_allowed(str, bannedwords):
            return False
    return True


class commands:
    def __init__(self, send_message, send_action, banned_words, config):
        self.send_message = send_message
        self.config = config
        self.send_action = send_action
        self.banned_words = banned_words

    def regex_yt(self, event):
        ytmatch = re.compile(
            "https?:\/\/(?:[0-9A-Z-]+\.)?(?:youtu\.be\/|youtube\.com\S*[^\w\-\s"
            "])([\w\-]{11})(?=[^\w\-]|$)(?![?=&+%\w]*(?:['\"][^<>]*>|<\/a>))[?="
            "&+%\w-]*",
            flags=re.I)
        matches = ytmatch.findall(event.message)
        for x in matches:
            try:
                t = requests.get(
                    'https://www.googleapis.com/youtube/v3/videos',
                    params=dict(
                        part='statistics,contentDetails,snippet',
                        fields='items/snippet/title,'
                        'items/snippet/channelTitle,'
                        'items/contentDetails/duration,'
                        'items/statistics/viewCount,'
                        'items/statistics/likeCount,'
                        'items/statistics/dislikeCount,'
                        'items/snippet/publishedAt',
                        maxResults='1',
                        key=self.config['googleKey'],
                        id=x)).json()['items'][0]

                title = t['snippet']['title']
                uploader = t['snippet']['channelTitle']
                viewcount = t['statistics']['viewCount']
                timediff = arrow.get(t['snippet']['publishedAt']).humanize()
                if 'likeCount' in t['statistics'] and 'dislikeCount' in t['statistics']:
                    likes = float(t['statistics']['likeCount'])
                    dislikes = float(t['statistics']['dislikeCount'])

                    if (dislikes > 0):
                        rating = str(int((likes /
                                          (likes + dislikes)) * 100)) + '%'
                    elif dislikes == 0 and likes == 0:
                        rating = 'unrated'
                    else:
                        rating = "100%"
                else:
                    rating = 'unrated'

                durationregex = re.compile(
                    'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', re.I)
                matches = durationregex.findall(
                    t['contentDetails']['duration'])[0]
                hours = int(matches[0]) if matches[0] != '' else 0
                minutes = int(matches[1]) if matches[1] != '' else 0
                seconds = int(matches[2]) if matches[2] != '' else 0
                duration = str(
                    datetime.timedelta(
                        hours=hours, minutes=minutes, seconds=seconds))

                viewcount = format(int(viewcount), ',')
                self.send_message(event.respond,
                                  u'{} | {} | {} | {} | {} | {}'.format(
                                      title, uploader, viewcount, timediff,
                                      rating, duration).encode(
                                          'utf-8', 'replace'))
            except:
                raise

    def command_yt(self, event):
        '''Usage: ~yt <terms> Used to search youtube with the given terms'''
        try:
            j = requests.get(
                'https://www.googleapis.com/youtube/v3/search',
                params=dict(
                    part='snippet',
                    fields='items/id',
                    safeSearch='none',
                    maxResults='1',
                    key=self.config['googleKey'],
                    q=event.params)).json()
            vidid = j['items'][0]['id']['videoId']

            t = requests.get(
                'https://www.googleapis.com/youtube/v3/videos',
                params=dict(
                    part='statistics,contentDetails,snippet',
                    fields='items/snippet/title,'
                    'items/snippet/channelTitle,'
                    'items/contentDetails/duration,'
                    'items/statistics/viewCount,'
                    'items/statistics/likeCount,'
                    'items/statistics/dislikeCount,'
                    'items/snippet/publishedAt',
                    maxResults='1',
                    key=self.config['googleKey'],
                    id=vidid)).json()['items'][0]

            title = t['snippet']['title']
            uploader = t['snippet']['channelTitle']
            viewcount = t['statistics']['viewCount']
            timediff = arrow.get(t['snippet']['publishedAt']).humanize()

            if 'likeCount' in t['statistics'] and 'dislikeCount' in t['statistics']:
                likes = float(t['statistics']['likeCount'])
                dislikes = float(t['statistics']['dislikeCount'])

                if (dislikes > 0):
                    rating = str(int((likes / (likes + dislikes)) * 100)) + '%'
                else:
                    rating = "100%"
            else:
                rating = 'unrated'

            durationregex = re.compile('PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?',
                                       re.I)
            matches = durationregex.findall(t['contentDetails']['duration'])[0]
            hours = int(matches[0]) if matches[0] != '' else 0
            minutes = int(matches[1]) if matches[1] != '' else 0
            seconds = int(matches[2]) if matches[2] != '' else 0
            duration = str(
                datetime.timedelta(
                    hours=hours, minutes=minutes, seconds=seconds))
            viewcount = format(int(viewcount), ',')

            self.send_message(
                event.respond,
                u'https://youtu.be/{} > {} | {} | {} | {} | {} | {}'.format(
                    vidid, title, uploader, viewcount, timediff, rating,
                    duration).encode('utf-8', 'replace'))

        except:
            self.send_message(event.respond, "No results")
            raise

    def command_g(self, event):
        '''Usage: ~g <terms> Used to search google with the given terms'''
        try:
            t = requests.get(
                'https://www.googleapis.com/customsearch/v1',
                params=dict(
                    q=event.params,
                    cx=self.config['googleengine'],
                    key=self.config['googleKey'],
                    safe='off')).json()
            index = 0
            while (len(t['items']) > index + 1 and not is_all_str_allowed([
                    t['items'][index]['title'], t['items'][index]['link']
            ], self.banned_words)):
                index += 1
            t = t['items'][index]
            self.send_message(event.respond, u'{}: {}'.format(
                t['title'], t['link']).encode('utf-8', 'replace'))
        except:
            self.send_message(event.respond, "No results")
            raise

    @register('nsfw', True)
    def command_rande621(self, event):
        '''Usage: ~rande621 <tags> Used to search e621.net for a random picture with the given tags'''
        try:
            j = requests.get(
                "http://e621.net/post/index.json",
                params=dict(limit="100", tags=event.params)).json()
            if (len(j) > 0):
                try:
                    selection = random.choice(j)
                    if selection['artist'] != []:
                        artist = " & ".join(selection['artist'])
                    else:
                        artist = 'N/A'
                    if selection['rating'] == 'e':
                        rating = 'Explicit'
                    elif selection['rating'] == 's':
                        rating = 'Safe'
                    else:
                        rating = 'Questionable'
                    self.send_message(
                        event.respond,
                        u'http://e621.net/post/show/{0[id]} | Artist(s): {1} | Score: {0[score]} | Rating: {2} | Post Date: {3}'.
                        format(selection, artist, rating,
                               arrow.get(selection['created_at']['s']).format(
                                   'YYYY-MM-DD')).encode('utf-8', 'replace'))
                except:
                    self.send_message(
                        event.respond,
                        "An error occurred while fetching your post.")
            else:
                self.send_message(event.respond, "No Results")
        except:
            self.send_message(event.respond,
                              "An error occurred while fetching your post.")
            raise

    @register('nsfw', True)
    def command_randgel(self, event):
        '''Usage: ~randgel <tags> Used to search gelbooru.com for a random picture with the given tags'''
        try:
            j = requests.get(
                "http://gelbooru.com/index.php",
                params=dict(
                    page="dapi",
                    q="index",
                    json="1",
                    s="post",
                    limit="100",
                    tags=event.params)).json()
            if (len(j) > 0):
                self.send_message(
                    event.respond,
                    u'http://gelbooru.com/index.php?page=post&s=view&id={}'.
                    format(random.choice(j)[u'id']).encode('utf-8', 'replace'))
            else:
                self.send_message(event.respond, "No Results")
        except:
            self.send_message(event.respond,
                              "An error occurred while fetching your post.")
            raise

    @register('nsfw', True)
    def command_clop(self, event):
        '''Usage: ~clop <optional extra tags> Searches e621 for a random image with the tags rating:e and my_little_pony'''
        event.params += ' rating:e my_little_pony'
        self.command_rande621(event)

    def command_randjur(self, event):
        '''Usage: ~randjur <number> Used to post random imgur pictures, from the gallery, <number> defines the number of results with a max of 10'''
        count = 1
        if len(event.params) > 0:
            try:
                count = int(event.params)
            except:
                self.send_message(event.respond, "Could not parse parameter")
                raise
        j = requests.get(
            "https://api.imgur.com/3/gallery.json",
            headers=dict(Authorization="Client-ID " +
                         self.config['imgurKey'])).json()[u'data']
        if count > 10:
            count = 10
        images = ','.join([x[u'id'] for x in random.sample(j, count)])
        album = requests.post(
            'https://api.imgur.com/3/album/',
            headers=dict(Authorization="Client-ID " + self.config['imgurKey']),
            params=dict(ids=images)).json()[u'data'][u'id']
        self.send_message(event.respond,
                          u'http://imgur.com/a/{}'.format(album).encode(
                              'utf-8', 'replace'))

    def command_translate(self, event):
        '''Usage: ~translate <LanguageFrom> <LanguageTo> translates a string of text between languages.'''
        toTrans = event.params.split()
        toTrans[0] = toTrans[0].lower()
        toTrans[1] = toTrans[1].lower()
        langs = {
            'afrikaans': 'af',
            'albanian': 'sq',
            'amharic': 'am',
            'arabic': 'ar',
            'armenian': 'hy',
            'azerbaijan': 'az',
            'bashkir': 'ba',
            'basque': 'eu',
            'belarusian': 'be',
            'bengali': 'bn',
            'bosnian': 'bs',
            'bulgarian': 'bg',
            'catalan': 'ca',
            'cebuano': 'ceb',
            'chinese': 'zh',
            'croatian': 'hr',
            'czech': 'cs',
            'danish': 'da',
            'dutch': 'nl',
            'english': 'en',
            'esperanto': 'eo',
            'estonian': 'et',
            'finnish': 'fi',
            'french': 'fr',
            'galician': 'gl',
            'georgian': 'ka',
            'german': 'de',
            'greek': 'el',
            'gujarati': 'gu',
            'haitian': 'ht',
            'hebrew': 'he',
            'hill mari': 'mrj',
            'hindi': 'hi',
            'hungarian': 'hu',
            'icelandic': 'is',
            'indonesian': 'id',
            'irish': 'ga',
            'italian': 'it',
            'japanese': 'ja',
            'javanese': 'jv',
            'kannada': 'kn',
            'kazakh': 'kk',
            'korean': 'ko',
            'kyrgyz': 'ky',
            'latin': 'la',
            'latvian': 'lv',
            'lithuanian': 'lt',
            'luxembourgish': 'lb',
            'macedonian': 'mk',
            'malagasy': 'mg',
            'malay': 'ms',
            'malayalam': 'ml',
            'maltese': 'mt',
            'maori': 'mi',
            'marathi': 'mr',
            'mari': 'mhr',
            'mongolian': 'mn',
            'nepali': 'ne',
            'norwegian': 'no',
            'papiamento': 'pap',
            'persian': 'fa',
            'polish': 'pl',
            'portuguese': 'pt',
            'punjabi': 'pa',
            'romanian': 'ro',
            'russian': 'ru',
            'scottish': 'gd',
            'serbian': 'sr',
            'sinhala': 'si',
            'slovakian': 'sk',
            'slovenian': 'sl',
            'spanish': 'es',
            'sundanese': 'su',
            'swahili': 'sw',
            'swedish': 'sv',
            'tagalog': 'tl',
            'tajik': 'tg',
            'tamil': 'ta',
            'tatar': 'tt',
            'telugu': 'te',
            'thai': 'th',
            'turkish': 'tr',
            'udmurt': 'udm',
            'ukrainian': 'uk',
            'urdu': 'ur',
            'uzbek': 'uz',
            'vietnamese': 'vi',
            'welsh': 'cy',
            'xhosa': 'xh',
            'yiddish': 'yi'
        }
        key = 'trnsl.1.1.20170403T165802Z.a214e2a67d20b0e6.ad95773f56547cd48cba8ecbd9dd1db0aa056c0f'

        try:
            LangFrom = langs[toTrans[0]] if toTrans[
                0] not in langs.values() else toTrans[0]
            LangTo = langs[toTrans[1]] if toTrans[
                1] not in langs.values() else toTrans[1]
        except:
            self.send_message(event.respond, 'Invalid language!')
            return

        try:
            rep = requests.get(
                "https://translate.yandex.net/api/v1.5/tr.json/translate?key={}&text={}&lang={}-{}&format=plain".
                format(key,
                       urllib.quote_plus(' '.join(toTrans[2:])), LangFrom,
                       LangTo)).json()
            text = ' '.join(rep['text'])
            if len(text) > 397:
                text = text[0:396] + '...'
            self.send_message(event.respond, text.encode('utf-8', 'replace'))
        except:
            self.send_message(
                event.respond,
                'Translation unsuccessful! Maybe the service is down?')

    def command_truerandjur(self, event):
        '''Usage: ~truerandjur <number> Used to post random imgur pictures, from randomly generated IDs, takes a little while to find images so be patient, <number> defines the number of results with a max of 10'''
        count = 1
        if len(event.params) > 0:
            try:
                count = int(event.params)
            except:
                self.send_message(event.respond, "Could not parse parameter")
                raise
        if count > 10:
            count = 10
        # this is gross, why do you let me do this python?

        def findImages(irc, count, respond, clientID):
            images = []
            while len(images) < count:
                randID = ''.join(
                    random.choice(string.ascii_letters + string.digits)
                    for x in range(0, 5))
                j = requests.get(
                    "https://api.imgur.com/3/image/" + randID,
                    headers=dict(
                        Authorization="Client-ID " + clientID)).json()
                if j[u'status'] == 200:
                    images.append(j[u'data'][u'id'])
            album = requests.post(
                'https://api.imgur.com/3/album/',
                headers=dict(Authorization="Client-ID " + clientID),
                params=dict(ids=','.join(images))).json()[u'data'][u'id']
            irc.send_message(respond,
                             u'http://imgur.com/a/{}'.format(album).encode(
                                 'utf-8', 'replace'))

        randjurThread = threading.Thread(
            target=findImages,
            kwargs=dict(
                irc=self,
                count=count,
                respond=event.respond,
                clientID=self.config['imgurKey']))
        randjurThread.start()

    def command_wolf(self, event):
        '''Usage: ~wolf <query> Searches wolfram alpha for your query'''
        try:
            s = requests.get(
                "http://api.wolframalpha.com/v2/query",
                params=dict(
                    input=event.params, appid=self.config['wolframKey'])).text

            x = etree.fromstring(s.encode('UTF-8', 'replace'))
            d = x.xpath('//pod[@primary="true"]/subpod/plaintext')

            results = [
                o.text.replace('\n', '').encode('utf-8', 'replace') for o in d
            ]

            search_url = "http://www.wolframalpha.com/input/?i={}".format(
                urllib.quote(event.params, ''))

            if len(results) < 1:
                responseStr = "No results available, try the query page:"
            else:
                responseStr = '; '.join(results)

            if (len(responseStr) + len(search_url)) > 390:
                responseStr = responseStr[:(390 - len(search_url))] + "..."

            responseStr += " " + search_url

            self.send_message(event.respond, responseStr)
        except:
            self.send_message(event.respond, "Error with the service")
            raise

    def command_weather(self, event):
        '''Usage: ~weather <location> Gets the weather for a location from wolfram alpha'''
        event.params = 'weather ' + event.params
        self.command_wolf(event)

    def command_define(self, event):
        '''Usage: ~define <word> Gets the definition of a word from wolfram alpha'''
        event.params = 'define ' + event.params
        self.command_wolf(event)

    def command_imdb(self, event):
        '''Usage: ~imdb <movie title> Provides basic information of a given movie, if applicable.'''
        t = requests.get(
                    'https://www.googleapis.com/customsearch/v1',
                    params=dict(
                        q='site:imdb.com {}'.format(event.params),
                        cx=self.config['googleengine'],
                        key=self.config['googleKey'],
                        safe='off')).json()
        path = urlparse(t['items'][0]['link']).path
        movie_id = filter(bool, path.split('/'))[-1]
        try:
            resp = requests.get(
                    "http://www.omdbapi.com/?i={}&apikey=b6bc9ea".format(
                        movie_id
                     )).json()
            self.send_message(
                    event.respond,
                    u"Year: {} | IMDB Rating: {} | Metascore Rating: {} | Runtime: {} | Plot: \x031,1{}...\x03 | http://www.imdb.com/title/{}".
                    format(resp['Year'], resp['imdbRating'], resp['Metascore'],
                           resp['Runtime'], resp['Plot'][:199],
                           resp['imdbID']).encode('utf-8', 'replace'))
        except:
            self.send_message(event.respond,
                              "Movie not found! Try checking your spelling?")

    def command_test(self, event):
        '''Usage: ~test Used to verify the bot is responding to messages'''
        possibleAnswers = [
            "Cake, and grief counseling, will be available at the conclusion of the test.",
            "Remember, the Aperture Science Bring Your Daughter to Work Day is the perfect time to have her tested.",
            "As part of an optional test protocol, we are pleased to present an amusing fact: The device is now more valuable than the organs and combined incomes of everyone in *subject hometown here.*",
            "The Enrichment Center promises to always provide a safe testing environment. In dangerous testing environments, the Enrichment Center promises to always provide useful advice. For instance: the floor here will kill you. Try to avoid it.",
            "Due to mandatory scheduled maintenance, the next test is currently unavailable. It has been replaced with a live-fire course designed for military androids. The Enrichment Center apologizes and wishes you the best of luck. ",
            "Well done. Here are the test results: You are a horrible person. I'm serious, that's what it says: \"A horrible person.\" We weren't even testing for that."
        ]
        self.send_message(event.respond, random.choice(possibleAnswers))

    def command_select(self, event):
        '''Usage: ~select <args> Used to select a random word from a given list'''
        if len(event.params) > 0:
            self.send_message(
                event.respond,
                'Select: {}'.format(random.choice(event.params.split(' '))))
        else:
            self.send_message(event.respond, "Invalid parameters. Please include arguements.")

    def command_flip(self, event):
        '''Usage: ~flip Used to flip a coin, responds with heads or tails'''
        self.send_message(event.respond,
                          'Flip: {}'.format(random.choice(['Heads', 'Tails'])))

    def command_gr(self, event):
        '''Usage: ~gr <query> links to the google results for a given query'''
        self.send_message(
            event.respond,
            "http://google.com/#q={}".format(urllib.quote(event.params, '')))

    def command_roll(self, event):
        '''Usage: ~roll <x>d<n> rolls a number, x, of n sided dice, example: ~roll 3d20'''
        strippedparams = ''.join(event.params.split())
        args = strippedparams.split('d')
        try:
            numDice = int(args[0])
        except:
            self.send_message(
                event.respond,
                "Invalid parameters, expected format is <int>d<int> Example: 1d6"
            )
            raise
        try:
            dieSize = int(args[1])
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
                event.respond, "Results: {}".format(', '.join([
                    str(random.randint(1, dieSize)) for x in range(numDice)
                ])))

    def ud(self, event, sort=None):
        try:
            rank = max(1, int(event.params.split('  ')[-1]))
        except ValueError:
            rank = 1
        
        index = rank - 1


        def calc_score(json):
            total = json.get('thumbs_up', 0) + json.get('thumbs_down', 0)
            return ((json.get('thumbs_up', 0) * 100) // total) if total > 0 else 0

        if sort is None:
            sort = calc_score

        try:
            word = event.params.split('  ')[0]
            k = requests.get("http://api.urbandictionary.com/v0/define",
                params = dict(term=word)
            ).json()[u'list']
            k.sort(key=sort, reverse=True)
            k = k[index]
            definition = re.sub(r'[\r\n]', '', k['definition'].encode('UTF-8', 'replace'))
            if (len(definition) > 380):
                definition = "{}...".format(definition[:380])
            response = "#{}: {} | Score: {}/{} {}% | {}".format(
                rank,
                definition,
                k['thumbs_up'],
                k['thumbs_down'],
                str(calc_score(k)),
                k['permalink']
            )
            self.send_message(event.respond, response)
        except:
            self.send_message(event.respond, "An error occurred while fetching your post, or there are no results.")
            raise
    
    def command_ud(self, event):
        '''Usage: ~ud <query>\s\s<int n> Used to search Urban Dictionary for the first (or nth) definition of a word, using flat upvote rank style. Note: a double space is required between parameters'''
        self.ud(event, sort=lambda x: x.get('thumbs_up', 0))


    def command_udr(self, event):
        '''Usage: ~udr <query>\s\s<int n> Used to search Urban Dictionary for the first (or nth) definition of a word, using ratio (upvotes/downvotes) rank style. Note: a double space is required between parameters'''
        self.ud(event)

    def command_isup(self, event):
        '''Usage: ~isup <site> used to check if a given website is up using isup.me'''
        try:
            s = requests.get("http://isup.me/{}".format(event.params)).text
            if "It's just you." in s:
                response = "It's just you! {} is up!".format(event.params)
            else:
                response = "It's not just you! {} looks down from here!".format(
                    event.params)
            self.send_message(event.respond, response)
        except:
            self.send_message(event.respond, "Error with the service")
            raise

    def command_gimg(self, event):
        '''Usage: ~gimg <terms> Used to search google images with the given terms'''
        try:
            t = requests.get(
                'https://www.googleapis.com/customsearch/v1',
                params=dict(
                    q=event.params,
                    cx=self.config['googleengine'],
                    key=self.config['googleKey'],
                    safe='off',
                    searchType='image')).json()
            index = 0
            while (len(t['items']) > index + 1 and not is_all_str_allowed([
                    t['items'][index]['title'], t['items'][index]['link']
            ], self.banned_words)):
                index += 1
            t = t['items'][index]
            self.send_message(event.respond, u'{}: {}'.format(
                t['title'], t['link']).encode('utf-8', 'replace'))
        except:
            self.send_message(event.respond, "No results")
            raise

    def command_rs(self, event):
        '''Usage: ~rs <terms> Used to search for results on reddit, can narrow down to sub or user with /u/<user> or /r/<subreddit>'''
        try:
            query = event.params
            # allow searching by /r/subreddit
            srmatch = re.compile('/(r|u)/(\w+(?:\+\w+)*(?:/\S+)*)', re.I)
            srmatches = srmatch.findall(event.params)
            submatches = [s[1] for s in srmatches if s[0] == 'r']
            usermatches = [s[1] for s in srmatches if s[0] == 'u']
            terms = []
            if len(submatches) > 0:
                terms.append("subreddit:{}".format(submatches[0]))
            if len(usermatches) > 0:
                terms.append("author:{}".format(usermatches[0]))
            if len(terms) > 0:
                query = srmatch.sub("", query)
                query = query.rstrip().lstrip()
            terms.append(query)
            headers = dict()
            headers['User-Agent'] = "Berry Punch IRC Bot"
            j = requests.get(
                'https://www.reddit.com/search.json',
                params=dict(limit="1", q=' '.join(terms)),
                headers=headers).json()[u'data'][u'children']
            if len(j) > 0:
                self.send_message(event.respond,
                                  u'https://reddit.com{} - {}'.format(
                                      j[0][u'data'][u'permalink'],
                                      HTMLParser.HTMLParser().unescape(
                                          j[0][u'data'][u'title'])).encode(
                                              'utf-8', 'replace'))
            else:
                self.send_message(event.respond, 'No results.')
        except:
            self.send_message(
                event.respond,
                'Reddit probably shat itself, try again or whatever.')
            raise

    def regex_e621(self, event):
        e621match = re.compile('https?:\/\/e621\.net\/post\/show\/\d{2,7}',
                               re.I)
        res = e621match.findall(event.message)
        for link in res:
            select = link + '.json'
            selection = requests.get(select).json()
            if selection['artist'] != []:
                artist = " & ".join(selection['artist'])
            else:
                artist = 'N/A'
            if selection['rating'] == 'e':
                rating = 'Explicit'
            elif selection['rating'] == 's':
                rating = 'Safe'
            else:
                rating = 'Questionable'
            self.send_message(
                event.respond,
                u'Artist(s): {1} | Score: {0[score]} | Rating: {2} | Post Date: {3}'.
                format(selection, artist, rating,
                       arrow.get(selection['created_at']['s']).format(
                           'YYYY-MM-DD')).encode('utf-8', 'replace'))

    def regex_reddit(self, event):
        if not event.command.lower()[1:] == 'rs':
            srmatch = re.compile('(?<!\S)/(r|u)/(\w+(?:\+\w+)*(?:/\S+)*)',
                                 re.I)
            srmatches = srmatch.findall(event.message)
            subrootmatches = [
                s[1] for s in srmatches if s[0] == 'r' and '/' not in s[1]
            ]
            suburlmatches = [
                s[1] for s in srmatches if s[0] == 'r' and '/' in s[1]
            ]
            usermatches = [s[1] for s in srmatches if s[0] == 'u']
            links = []
            if len(subrootmatches) > 0:
                links.append(
                    "https://reddit.com/r/{}".format('+'.join(subrootmatches)))
            for link in suburlmatches:
                links.append("https://reddit.com/r/{}".format(link))
            for link in usermatches:
                links.append("https://reddit.com/u/{}".format(link))
            if len(links) > 0:
                self.send_message(event.respond, ' '.join(links))

    def command_dns(self, event):
        '''Usage: ~dns <domain> Used to check which IPs are associated with a DNS listing'''
        try:
            records = socket.getaddrinfo(event.params.split(' ')[0], 80)
            addresses = set([x[4][0] for x in records])
            self.send_message(event.respond, " ".join(addresses))
        except:
            self.send_message(event.respond,
                              "You must give a valid host name to look up")

    def command_trakt(self, event):
        '''Usage: ~trakt <query> Searches trakt for movies, and tv shows'''
        try:
            sess = requests.Session()
            headers = dict()
            headers['Content-Type'] = 'application/json'
            headers['trakt-api-version'] = 2
            headers['trakt-api-key'] = self.config['traktKey']
            sess.headers.update(headers)
            resp = sess.get(
                'https://api-v2launch.trakt.tv/search',
                params=dict(query=event.params, type='movie,show')).json()[0]
            if 'show' in resp:
                apiurl = 'https://api-v2launch.trakt.tv/shows/%s?extended=full' % resp[
                    'show']['ids']['slug']
                url = 'https://trakt.tv/shows/%s' % resp['show']['ids']['slug']
            elif 'movie' in resp:
                apiurl = 'https://api-v2launch.trakt.tv/movies/%s?extended=full' % resp[
                    'movie']['ids']['slug']
                url = 'https://trakt.tv/movies/%s' % resp['movie']['ids'][
                    'slug']
            else:
                self.send_message(event.respond, "No results")
                return
            j = sess.get(apiurl).json()
            out = []
            if 'title' in j:
                out.append(j['title'])
            if 'genres' in j:
                out.append(', '.join(j['genres'][:3]))
            if 'overview' in j:
                out.append(j['overview'][:100] + '...')
            if 'rating' in j:
                out.append(str(j['rating']))
            if 'year' in j:
                out.append(str(j['year']))
            out.append(url)

            self.send_message(event.respond, (' | '.join(out)).encode(
                'utf-8', 'replace'))

        except:
            self.send_message(event.respond, "No results")
            raise

    def command_mal(self, event):
        '''Usage: ~mal <query> Searches My Anime List for a given anime using a custom google search'''
        try:
            t = requests.get(
                'https://www.googleapis.com/customsearch/v1',
                params=dict(
                    q=event.params,
                    cx=self.config['googleengine'],
                    key=self.config['googleKey'],
                    safe='off',
                    siteSearch='myanimelist.net')).json()['items'][0]
            self.send_message(event.respond, u'{}: {}'.format(
                t['title'], t['link']).encode('utf-8', 'replace'))
        except:
            self.send_message(event.respond, "No results")
            raise

    def regex_deviantart(self, event):
        damatch = re.compile(
            '((?:(?:https?|ftp|file)://|www\.|ftp\.)(?:\([-A-Z0-9+&@#/%=~_|$?!:,.]*\)|[-A-Z0-9+&@#/%=~_|$?!:,.])*(?:\([-A-Z0-9+&@#/%=~_|$?!:,.]*\)|[A-Z0-9+&@#/%=~_|$]))',
            re.I)
        damatches = damatch.findall(event.message)
        for x in damatches:
            try:
                consumer = oembed.OEmbedConsumer()
                endpoint = oembed.OEmbedEndpoint(
                    'http://backend.deviantart.com/oembed', [
                        'http://*.deviantart.com/art/*', 'http://fav.me/*',
                        'http://sta.sh/*', 'http://*.deviantart.com/*#/d*'
                    ])
                consumer.addEndpoint(endpoint)
                response = consumer.embed(x).getData()
                out = []
                if 'title' in response:
                    out.append("Title: {}".format(response[u'title']))
                if 'author_name' in response:
                    out.append("Artist: {}".format(response[u'author_name']))
                if 'rating' in response:
                    out.append("Rating: {}".format(response[u'rating']))
                if 'url' in response:
                    out.append("Direct Url: {}".format(response[u'url']))
                self.send_message(event.respond, " | ".join(out).encode(
                    'utf-8', 'replace'))
            except oembed.OEmbedNoEndpoint:
                pass
            except urllib2.HTTPError:
                pass

    def command_wiki(self, event):
        '''Usage: ~wiki <query> Searches wikipedia for a given query'''
        try:
            responseStr = wiki.page(event.params).summary.replace('\n', ' ')
            urllen = 381 - len(wiki.page(event.params).url)
            if len(responseStr) > urllen:
                responseStr = responseStr[:urllen] + "... | " + wiki.page(event.params).url
            self.send_message(event.respond,
                              responseStr.encode('utf-8', 'replace'))
        except wiki.exceptions.DisambiguationError as e:
            responseStr = str(e).replace('\n', ', ')
            urllen = 381 - len(wiki.page(event.params).url)
            if len(responseStr) > urllen:
                responseStr = responseStr[:urllen] + "... | " + wiki.page(event.params).url
            self.send_message(event.respond, responseStr)
        except:
            self.send_message(event.respond, "No results")
            raise

    def command_wimg(self, event):
        '''Usage: ~wimg <query> Links the first image result from wikipedia for a given query'''
        try:
            link = wiki.page(event.params).images[1]
            self.send_message(event.respond,
                link.encode('utf-8', 'replace'))
        except wiki.exceptions.DisambiguationError as e:
            response = str(e).replace('\n', ', ')
            self.send_message(event.respond, response)
        except:
            self.send_message(event.respond, "No results")
            raise

    def command_feels(self, event):
        self.send_message(event.respond,
                          'http://imgur.com/a/PJIsu/layout/blog')

    def command_lenny(self, event):
        self.send_message(event.respond, u'( ͡° ͜ʖ ͡°)'.encode(
            'utf-8', 'replace'))

    def command_derpi(self, event):
        '''Usage: ~derpi <query> Searches derpibooru for a query, tags are comma separated.'''
        sess = requests.Session()
        page = lxml.html.fromstring(
            sess.get('https://derpibooru.org/filters').text)
        authenticitytoken = page.xpath('//meta[@name="csrf-token"]')[0].attrib[
            'content']
        body = dict()
        body['authenticity_token'] = authenticitytoken
        body['_method'] = 'patch'
        sess.post(
            'https://derpibooru.org/filters/select?id=56027',
            data=body,
            headers=dict(Referer='https://derpiboo.ru/filters'))
        if event.params == "":
            event.params = "*"
        results = sess.get(
            'https://derpibooru.org/search.json',
            data=dict(q=event.params)).json()['search']
        if len(results) > 0:
            choice = random.choice(results)
            idNum = choice['id']
            self.send_message(event.respond,
                              ('https://derpibooru.org/%s' % idNum).encode(
                                  "utf-8", "replace"))
        else:
            self.send_message(event.respond, 'No results'.encode(
                "utf-8", "replace"))

    def command_pony(self, event):
        '''Usage: ~pony Gives time until next episode of mlp'''
        now = datetime.datetime.utcnow()
        if True:  # now < datetime.datetime(2015,7,11,15,30):
            days_ahead = 5 - now.weekday()
            if days_ahead < 0 or (days_ahead == 0 and
                                  now.time() > datetime.time(15, 30)):
                days_ahead += 7
            next_episode = datetime.datetime.combine(
                now.date() + datetime.timedelta(days_ahead),
                datetime.time(15, 30))
            time_remaining = (next_episode - now).seconds
            hours, remainder = divmod(time_remaining, 3600)
            minutes, seconds = divmod(remainder, 60)
            self.send_message(
                event.respond,
                "Time until next episode: {} days {} hours {} minutes {} seconds".
                format((next_episode - now).days, hours, minutes, seconds))
        else:
            self.send_message(event.respond,
                              "The show is on hiatus until later this year.")

    def command_fwt(self, event):
        '''Usage: ~fwt <text> repeats text in full width and adds spaces for A E S T H E T I C S'''
        self.send_action(event.respond, (u" ".join([
            unichr(ord(x) + 65248) if 64 < ord(x) < 91 else x
            for x in event.params.upper()
        ])).encode('utf-8', 'replace'))

    @register('nsfw', True)
    def command_furry(self, event):
        '''Usage: ~furry <nick> yiffs them'''
        yiff = random.choice(self.config['yiffs'])
        self.send_action(event.respond, (
            yiff.replace('$target', event.params.strip()).replace(
                '$user', 'pwny').replace('$nick', self.config['nick']).replace(
                    '$channel', event.respond)).encode('utf-8', 'replace'))
