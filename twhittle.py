#!/usr/bin/env python3
"""Whittle your Twittles down to Nittles
This is intended to run permanently somewhere (e.g. Docker) and
delete old tweets.

The Twitter API only lets you enumerate the most recent 3200 tweets
you've made, so configure this with a number lower than that"""
import asyncio
import json
import logging
import os
import tweepy

log = None

logging.basicConfig(format='%(levelname)s %(name)s::%(funcName)s: %(message)s',
                            level=logging.INFO)

class Twhittle:
    consumer_key = None
    consumer_secret = None
    access_token = None
    access_token_secret = None
    ignore_list = None
    log = None
    auth = None
    api = None

    def __init__(self, consumer_key, consumer_secret, access_token, access_token_secret, ignore_list):
        """Class initialiser"""
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.access_token = access_token
        self.access_token_secret = access_token_secret
        self.ignore_list = ignore_list

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
        """Fetch the most recent tweets"""
        self.log.info("Fetching most recent tweets")
        tweets = self.api.user_timeline(count=200, include_rts=True)
        self.log.info("Started with %d tweets from %d to %d" % (len(tweets), tweets[-1].id, tweets[0].id))
        i = 16 # We're only allowed to fetch 3200 tweets (16 lots of 200)
        while i > 0:
            max_id = tweets[-1].id - 1
            new_tweets = self.api.user_timeline(count=200, max_id=max_id, include_rts=True)
            if not new_tweets:
                self.log.info("Reached the end of the timeline")
                break
            self.log.info("Added %d tweets from %d to %d" % (len(new_tweets), 
                                                             new_tweets[-1].id,
                                                             new_tweets[0].id))
            tweets.extend(new_tweets)
            i = i - 1
        self.log.info("Fetched a total of %d tweets" % len(tweets))
        return tweets

    def trim_tweets(self, max_tweets_keep):
        """Delete any tweets more than max_tweets_keep tweets old"""
        self.log.info("Looking for tweets to delete")
        if not self.api:
            self.login()

        tweets = self.tweets()
        self.log.info("Found %d total tweets" % len(tweets))
        to_delete = tweets[max_tweets_keep:]
        self.log.info("Found %d to delete" % len(to_delete))
        for tweet in to_delete:
            if tweet.id not in self.ignore_list:
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
                        CONFIG["access_token_secret"],
                        CONFIG["ignore_list"])

    @asyncio.coroutine
    def periodic():
        while True:
            try:
                twhittle.trim_tweets(CONFIG["max_tweets_keep"])
            except:
                log.exception("Exception caught")
                asyncio.get_event_loop().stop()
            yield from asyncio.sleep(3600)

    asyncio.Task(periodic())

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
