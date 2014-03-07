"""
Twitter Wizard

Automatic posts to twitter. <filename> is list of posts separated by newline. <interval> is how many hours to wait
between each tweet.

Usage:
  twitter_wizard.py start <filename> <interval> [options]
  twitter_wizard.py validate <filename> [options]

Options:
  -h --help       Show this screen.
  -v --version    Show version.
  -t --test       Do not write to used_tweets, and do not make real tweets. Just print what it would do.
"""

from ztools.docopt import docopt
import os.path, time, logging, sys
from TwitterAPI import TwitterAPI

used_filename="used_tweets"

consumer_key="123abc"
consumer_secret="123abc"
access_token_key="123abc"
access_token_secret="123abc"

def get_logger():
    return logging.getLogger("tweet")

def set_logger():
    logger=get_logger()
    handler=logging.FileHandler("log.txt")
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    handler=logging.StreamHandler(sys.stdout)
    logger.addHandler(handler)

    logger.setLevel(logging.INFO)

    return logger

def make_tweet(tweet):
    if len(tweet)>140:
        get_logger().error("Tweet is too long. Aborted.")
        return

    get_logger().info("Sending tweet.")
    api = TwitterAPI(consumer_key, consumer_secret, access_token_key, access_token_secret)
    r = api.request('statuses/update', {'status':tweet})
    get_logger().info("Status: %s for tweet: %s"%(r.status_code,tweet))

def search_twitter(query):
    r = api.request('search/tweets', {'q':query})
    print("search: %s\nstatus: %s"%(query,r.status_code))
    for item in r.get_iterator():
        print (item)

def get_tweets(filename):
    with open(filename,"r") as f:
        tweets=f.read().split("\n")
    tweets=[tweet+" #edptw14" for tweet in tweets if tweet.strip()]
    tweets=[t for t in tweets if is_valid(t)]

    return tweets

def is_valid(tweet):
    return len(tweet)<=140

def validate(filename):
    tweets=get_tweets(filename)
    success=1
    get_logger().info("Validating tweets.")
    for tweet in tweets:
        if not is_valid(tweet):
            get_logger().warning("Found invalid tweet. Len=%s\n%s"%(len(tweet),tweet))
            success=0
    if success:
        get_logger().info("All tweets are valid!")

def get_used_tweets():
    if not os.path.isfile(used_filename):
        return []

    with open(used_filename,"r") as f:
        used_tweets=set(f.read().split("\n"))
    return used_tweets

def add_used_tweet(tweet):
    with open(used_filename,"a") as f:
        f.write(tweet+"\n")

def tweet_loop(filename,interval,is_test):
    validate(filename)
    get_logger().info("Starting tweet loop. Interval: %s"%interval)

    tweets=get_tweets(filename)
    used_tweets=get_used_tweets()

    while(len(tweets)>0):
        tweet=tweets[0]
        tweets=tweets[1:]

        if tweet not in used_tweets:
            if is_test:
                get_logger().info("TEST tweet: %s"%tweet)
            else:
                add_used_tweet(tweet)
                used_tweets=get_used_tweets()
                make_tweet(tweet)
            get_logger().info("Waiting %s hours."%interval)
            time.sleep(interval*3600)

    get_logger().error("Ran out of new tweets.")

def main(args):
    set_logger()

    if not os.path.isfile(args["<filename>"]):
        get_logger().critical("Not a file: %s"%filename)
        return

    if (args["validate"]):
        validate(args["<filename>"])
        return

    if (args["start"]):
        interval=0
        try:
            interval=float(args["<interval>"])
        except:
            get_logger().critical("Invalid interval: %s"%args["<interval>"])
            return

        if interval<12:
            get_logger().critical("Aborted. You probably don't want to tweet that often. Interval: %s"%interval)
            return

        tweet_loop(args["<filename>"],interval,args["--test"])
        get_logger().info("Done.")

if __name__ == "__main__":
    args = docopt(__doc__, version="0.1")
    main(args)






