from mastodon import Mastodon
from dotenv import load_dotenv
import os
import json
import openai
import tweepy
import argparse
import re

def gettoot():
  global toot
  tweetprompt="Write a tweet with less than 200 characters introducing a blog post titled: "+title
  print(tweetprompt)

  try:
    response = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": tweetprompt},
        ],
    )
  except openai.error.OpenAIError as e:
    print("Error")
    print(e.http_status)
    print(e.error)
    exit(1)
    
  toot=response['choices'][0]['message']['content'].replace('"','')
  #sometimes, ChatGPT inserts example placeholder URLs.  This replaces it with correct URL.
  toot = re.sub(r'http\S+', post_url, toot)

  #if there was no placeholder, find another spot
  if post_url not in toot:
    #contains tags
    if "#" in toot:
        desiredposition = len(toot)
        spacesharp=desiredposition
        space=desiredposition
        while spacesharp==space:
            desiredposition=space
            spacesharp=toot.rfind(" #",1,desiredposition)
            space=toot.rfind(" ",1,desiredposition)
        toot=toot[0:desiredposition]+"\n"+post_url+"\n"+toot[desiredposition:].strip()
    else:
        toot=toot+"\n"+post_url

  print("\n\nToot:\n")
  print(toot)
  print("Length: "+str(len(toot)))


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
post_url=site_url +"post/"+ identifier + "/" 

f = open(filename)
data = json.load(f)
title=data['title']

openai.api_key = os.getenv("OPENAI_API_KEY")

toot=''
maxtries=10
numtries=1
while (numtries<maxtries):
  print("attempt "+str(numtries))
  gettoot()
  if len(toot)<280:
    numtries=maxtries
  else:
    print("too long for twitter, try again")  
  numtries=numtries+1

if args.noninteractive==False:
  print("\n\nPost to Mastodon and Twitter? y/n")
  proceed = input()
  if "n" in proceed:
    quit()
    
mastodon_access_token = os.getenv("MASTODON_ACCESS_TOKEN")

if len(mastodon_access_token)>5:
  print("Posting to Mastodon")
  mastodon = Mastodon(access_token = mastodon_access_token,api_base_url = "https://botsin.space/")
  mastodon.toot(toot)

twitter_consumer_key = os.getenv("TWITTER_CONSUMER_KEY")
twitter_consumer_secret = os.getenv("TWITTER_CONSUMER_SECRET")
twitter_access_token = os.getenv("TWITTER_ACCESS_TOKEN")
twitter_access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

if len(twitter_consumer_key)>5:
  #if too long... skip twitter
  if len(toot)<280:
    print("Posting to Twitter")
    # Authenticate to Twitter
    auth = tweepy.OAuthHandler(twitter_consumer_key, 
        twitter_consumer_secret)
    auth.set_access_token(twitter_access_token, 
        twitter_access_token_secret )

    api = tweepy.API(auth)

    api.verify_credentials()

    api.update_status(toot)
