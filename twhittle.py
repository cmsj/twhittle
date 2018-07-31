#!/usr/bin/env python3
"""Whittle your Twittles down to Nittles
This is intended to run permanently somewhere (e.g. Docker) and
delete old tweets.

The Twitter API only lets you enumerate the most recent 200 tweets
you've made, so we will just aim to keep you around 150 tweets"""
import asyncio
import json
import logging
import os
import tweepy

log = None

logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s::%(funcName)s: %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S',
                            level=logging.INFO)

class Twhittle:
    consumer_key = None
    consumer_secret = None
    access_token = None
    access_token_secret = None
    log = None
    auth = None
    api = None

    def __init__(self, consumer_key, consumer_secret, access_token, access_token_secret):
        """Class initialiser"""
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.access_token = access_token
        self.access_token_secret = access_token_secret

        self.log = logging.getLogger("TWhittle::Twitter")

    def login(self):
        """Log in to twitter and return a tweepy API object"""
        self.log.info("Logging in to Twitter")
        self.auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
        self.auth.set_access_token(self.access_token, self.access_token_secret)
        self.api = tweepy.API(self.auth)
        self.log.info("Authenticated as: %s" % self.api.me().screen_name)

    def logout(self):
        self.log.info("Logging out of Twitter")
        if self.api:
            self.api = None
            self.auth = None

    def tweets(self):
        """Fetch the most recent 200 tweets"""
        self.log.info("Fetching most recent tweets")
        return self.api.user_timeline(count=200)

    def trim_tweets(self):
        """Delete any tweets more than 150 tweets old"""
        self.log.info("Looking for tweets to delete")
        if not self.api:
            self.login()
        
        tweets = self.tweets()
        self.log.info("Found %d total tweets" % len(tweets))
        to_delete = tweets[150:]
        self.log.info("Found %d to delete" % len(to_delete))
        for tweet in to_delete:
            self.log.info("Destroying tweet: %s" % tweet.id)
            tweet.destroy()
        
        self.logout()

def main():
    log = logging.getLogger("Twhittle")
    with open(os.getenv("TWHITTLE_CONFIG"), encoding="utf-8") as filep:
        CONFIG = json.load(filep)
        log.info("Configuration loaded")

    loop = asyncio.get_event_loop()
    twhittle = Twhittle(CONFIG["consumer_key"],
                        CONFIG["consumer_secret"],
                        CONFIG["access_token"],
                        CONFIG["access_token_secret"])

    @asyncio.coroutine
    def periodic():
        while True:
            twhittle.trim_tweets()
            yield from asyncio.sleep(3600)
    
    task = asyncio.Task(periodic())

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    except Exception as exp:
        log.exception("Something went wrong", exc_info=exp)
    finally:
        log.info("Twhittle terminated")
        loop.close()

if __name__ == "__main__":
    main()