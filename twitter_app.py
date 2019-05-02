import socket
import sys
import requests
import requests_oauthlib
import json
import yaml
conf = yaml.safe_load(open('conf/application.yml'))

'''Twitter API Access information'''

ACCESS_TOKEN = conf['twitter_user']['ACCESS_TOKEN']
ACCESS_SECRET = conf['twitter_user']['ACCESS_SECRET']
CONSUMER_KEY = conf['twitter_user']['CONSUMER_KEY']
CONSUMER_SECRET = conf['twitter_user']['CONSUMER_SECRET']

twitter_auth = requests_oauthlib.OAuth1(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_SECRET)


def send_tweets_to_spark(http_resp, tcp_connection):
    for line in http_resp.iter_lines():
        try:
            full_tweet = json.loads(line)
            print("full tweet", full_tweet, '\n')
            tweet_text = str(full_tweet['text'])
            print("Tweet Text: ", tweet_text, 'utf-8')
            print("------------------------------------------", '\n')
            tweet = bytes(tweet_text + "\n", 'utf-8')
            tcp_connection.send(tweet)
        except:
            e = sys.exc_info()[0]
            print("Error: %s" % e)


def get_tweets():
    url = 'https://stream.twitter.com/1.1/statuses/filter.json'
    query_data = [('language', 'en'), ('locations', '-130,-20,100,50'), ('track', '#')]
    #query_data = [('locations', '-130,-20,100,50'), ('track', '#')]
    query_url = url + '?' + '&'.join([str(t[0]) + '=' + str(t[1]) for t in query_data])
    response = requests.get(query_url, auth=twitter_auth, stream=True)
    return response


TCP_IP = "localhost"
TCP_PORT = 9009
conn = None
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)
print("Waiting for TCP connection...")
conn, addr = s.accept()

print("Connected... Starting getting tweets.")
resp = get_tweets()
send_tweets_to_spark(resp, conn)
