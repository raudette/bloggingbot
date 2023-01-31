from mastodon import Mastodon
from dotenv import load_dotenv
import os
import json
import openai
import tweepy
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-ni", "--noninteractive", help="Don't ask for confirmation to post", action='store_true')
args = parser.parse_args()


load_dotenv()
postrootfolder=str(os.getenv("POST_ROOT_FOLDER"))
openai.api_key = os.getenv("OPENAI_API_KEY")
site_url=str(os.getenv("SITE_URL"))

#open current working file
filename="./currentarticle/prompt.json"
f = open(filename)
data = json.load(f)
identifier=data['identifier']

#get get title, build out post url
filename="./draft/" + identifier + "/" + identifier + ".json"
post_url=site_url +"post/"+ identifier + "/" + identifier + "/"

f = open(filename)
data = json.load(f)
title=data['title']

openai.api_key = os.getenv("OPENAI_API_KEY")

tweetprompt="Write a tweet introducing a blog post titled: "+title
print(tweetprompt)

response = openai.Completion.create(
  model="text-davinci-003",
  prompt=tweetprompt,
  temperature=0.7,
  max_tokens=60,
  top_p=1,
  frequency_penalty=0,
  presence_penalty=1
)

intro = response.choices[0].text.strip().replace('"','')

endoffirstparagraph=0
if "#" in intro:
    firsthashtagpos = intro.index("#")
    toot=intro[0:firsthashtagpos]+"\n"+post_url+"\n"+intro[firsthashtagpos:]
else:
    toot=intro+"\n"+post_url

print("\n\nToot:\n")
print(toot)
print("Length: "+str(len(toot)))

if len(toot)>280:
    print(len(toot))
    print("Too long for twitter")
    quit()

if args.noninteractive==False:
  print("\n\nPost to Mastodon and Twitter? y/n")
  proceed = input()
  if "n" in proceed:
    quit()
    
mastodon_access_token = os.getenv("MASTODON_ACCESS_TOKEN")
mastodon_url = os.getenv("MASTODON_URL")

if len(mastodon_access_token)>5:
  print("Posting to Mastodon")
  mastodon = Mastodon(access_token = mastodon_access_token,api_base_url = mastodon_url)
  mastodon.toot(toot)

twitter_consumer_key = os.getenv("TWITTER_CONSUMER_KEY")
twitter_consumer_secret = os.getenv("TWITTER_CONSUMER_SECRET")
twitter_access_token = os.getenv("TWITTER_ACCESS_TOKEN")
twitter_access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

if len(twitter_consumer_key)>5:
  print("Posting to Twitter")
  # Authenticate to Twitter
  auth = tweepy.OAuthHandler(twitter_consumer_key, 
      twitter_consumer_secret)
  auth.set_access_token(twitter_access_token, 
      twitter_access_token_secret )

  api = tweepy.API(auth)

  api.verify_credentials()

  api.update_status(toot)