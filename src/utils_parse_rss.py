import feedparser
import json
import os


######################################################################################################################################################
class ParseRSS:
    def __init__(self, logs, podcastdb):
        self.logs = logs
        self.podcastdb = podcastdb

        self.DEBUG = os.getenv("DEBUG")
        if self.DEBUG == '0':
            self.RSS_FEEDS = os.getenv("RSS_FEEDS")
        elif self.DEBUG == '4': # debug mode for pytest
            self.RSS_FEEDS = 'no.json'
        else:
            self.RSS_FEEDS = os.getenv("RSS_FEEDS_TEST")

        self.podcasts = []
        self.feeds = self.parse_json()
        self.parse_feeds()
    

    def parse_json(self):
        prefix = f'[{self.__class__.__name__} | parse_json]'

        try:
            self.logs.logging_msg(f"{prefix} json_file: {self.RSS_FEEDS}", 'DEBUG')

            with open(self.RSS_FEEDS, 'r', encoding='utf-8') as file:
                feeds = json.load(file)
            return feeds
        
        except Exception as e:
            self.logs.logging_msg(f"{prefix} Error: {e}", 'ERROR')
            return []
    

    def parse_feeds(self):
        prefix = f'[{self.__class__.__name__} | parse_feeds]'

        try:
            for podcast in self.feeds:
                self.podcasts.append(ParsePodcast(
                    self.logs,
                    self.podcastdb,
                    podcast["category"],
                    podcast["name"],
                    podcast["rss_feed"],
                    podcast["summarize"]
                ))
        
        except Exception as e:
            self.logs.logging_msg(f"{prefix} Error: {e}", 'ERROR')
    

######################################################################################################################################################
class ParsePodcast:
    def __init__(self, logs, podcastdb, category, name, rss_feed, summarize_text):
        self.logs = logs
        self.podcastdb = podcastdb
        
        self.category = category
        self.name = name
        self.rss_feed = rss_feed
        if summarize_text.lower() == 'true':
            self.summarize = 1
        else:
            self.summarize = 0

        self.parse_podcast()


    def parse_podcast(self):
        prefix = f'[{self.__class__.__name__} | parse_podcast]'

        try:
            self.logs.logging_msg(f"{prefix} feed_rss_url: {self.rss_feed}")

            feed = feedparser.parse(self.rss_feed)

            if feed.bozo:
                raise Exception(f"Failed to parse RSS feed: {feed.bozo_exception}")

            for entry in feed.entries:
                self.logs.logging_msg(f"", 'DEBUG')
                self.logs.logging_msg(f"", 'DEBUG')

                title = entry.get('title', 'No title')

                if 'feeds.acast.com' in self.rss_feed:
                    links = entry.get('links', [])
                    link = next((l['href'] for l in links if l['href'].startswith('https://sphinx.acast.com')), 'No link')
                    self.logs.logging_msg(f"{prefix} 'feeds.acast.com' Podcast Link: {link}", 'DEBUG')
                elif 'feed.ausha.co' in self.rss_feed:
                    link = entry.get('link', 'No link')
                    self.logs.logging_msg(f"{prefix} 'feed.ausha.co' Podcast Link: {link}", 'DEBUG')
                elif 'anchor.fm' in self.rss_feed:
                    link = next((enclosure['url'] for enclosure in entry.get('enclosures', []) if enclosure['url'].startswith('https://')), 'No link')
                    self.logs.logging_msg(f"{prefix} 'anchor.fm' Podcast Link: {link}", 'DEBUG')
                else:
                    link = entry.get('', 'No link')
                    self.logs.logging_msg(f"{prefix} OTHER Podcast Link: {link}", 'WARNING')

                published = entry.get('published', 'No publish date')

                description = entry.get('description', 'No description')
                
                self.logs.logging_msg(f"----------------------------------------------------------------------------------------------------", 'DEBUG')
                self.logs.logging_msg(f"{prefix} Podcast Title: {title}", 'DEBUG')
                self.logs.logging_msg(f"{prefix} Podcast Link: {link}", 'DEBUG')
                self.logs.logging_msg(f"{prefix} Podcast Published Date: {published}", 'DEBUG')
                self.logs.logging_msg(f"{prefix} Podcast Description: {description}", 'DEBUG')
                self.logs.logging_msg(f"----------------------------------------------------------------------------------------------------", 'DEBUG')

                title = title.replace('"', "''")
                link = link.replace('"', "''")
                published = published.replace('"', "''")
                description = description.replace('"', "''")

                self.podcastdb.insert_podcast(self.category, self.name, self.rss_feed, self.summarize, title, link, published, description)

            self.logs.logging_msg(f"{prefix} >> OK <<", 'DEBUG')


        except Exception as e:
            self.logs.logging_msg(f"{prefix} Error: {e}", 'WARNING')