import tweepy
import time
from tweepy import OAuthHandler
from tweepy import API
from tweepy import Stream
from tweepy.streaming import StreamListener

Consumer_Key = 'vGk3JRVlO0YwnzjVBm69fGqJX'
Consumer_Secret = '9T97moIojHnN3rDAcFyv03suJoP4T3KEo15tlYMWK3x0UMRfBl'
Access_Token_Key = '925772963206504448-rBdE0DaVbQ0Ilrij9dGc52w3JWqcGs2'
Access_Token_Secret = 'GEWaDK7TPPDj4ufLDswrajfERduJlHDClowkaQBmlIwYL'

fields = ['created_at', 'coordinates', 'text',
'retweet_count', 'favorite_count', 'hashtags',
'user_id', 'user_mentions', 'user_name', 'user_location',
'user_description', 'user_followers_count', 'user_friends_count']

def process_json(json):
    if json == None:
        return None

    data = dict()
    # geolocation extraction
    if json['coordinates'] != None:
        coords = json['coordinates']['coordinates']
        if coords != None:
            data['coordinates'] = (coords[0], coords[1])
    elif json['geo'] != None:
        if json['geo']['type'] == "Point":
            coords = json['geo']['coordinates']
            if coords != None:
                data['coordinates'] = (coords[0], coords[1])

    # entities extraction
    if json['entities'] != None:
        entities = json['entities']
        if entities['hashtags'] != None:
            hashtags = entities['hashtags']
            hts = []
            for hashtag in hashtags:
                hts.append(hashtag['text'])
            data['hashtags'] = hts

        if entities['user_mentions'] != None:
            user_mentions = entities['user_mentions']
            ums = []
            for um in user_mentions:
                ums.append(um['id'])
            data['user_mentions'] = ums

    # user info extraction
    if json['user'] != None:
        user = json['user']
        for keyword in ['id', 'name', 'location', 'description', 'followers_count', 'friends_count']:
            data['user_' + keyword] = user[keyword]

    # other info extraction
    for field in fields:
        if not field in data:
            data[field] = json[field]

    return data

def preprocess_data(json_data):
    processed_data = []
    for json in json_data:
        process_json(json)
        process_json(json.get('retweeted_status'))
    return processed_data

class TwitterListener(StreamListener):

    def __init__(self, time_limit=60):
        
        self.start_time = time.time()
        self.limit = time_limit
        self.out_file = open('tweets.json', 'a', encoding='utf-8')
        self.processed_data = []
        super(TwitterListener, self).__init__()

    def on_data(self, data):
        if (time.time() - self.start_time) < self.limit:
            self.out_file.write(data)
            process_json(data, self.processed_data)
            self.out_file.write("\n")
            return True
        #self.out_file.write('\n')
        else:
            print("Done")
            print(self.processed_data)
            self.out_file.close()
            return False

    def on_error(self, status):
        print (status)

def print_json(tweet):
    print("-----------------------------------")
    for field in fields:
        print('...' + field + '...')
        print(tweet[field])

if __name__ == '__main__':
    auth = tweepy.OAuthHandler(Consumer_Key,Consumer_Secret)
    auth.set_access_token(Access_Token_Key, Access_Token_Secret)    
    api = tweepy.API(auth)
    results = api.search(q='earthquake', count=5, languages=['en'])
    data_processed = []
    for r in results:
        tweet = process_json(r._json)
        if tweet != None:
            data_processed.append(tweet)
            #print_json(tweet)

        tweet = process_json(r._json.get('retweeted_status'))
        if tweet != None:
            data_processed.append(tweet)
            #print_json(tweet)

keyword = []
    
#twitterStream = Stream(auth, TwitterListener(time_limit=20)) 
#twitterStream.filter(track=keyword, languages=['en'])

