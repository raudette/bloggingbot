from mastodon import Mastodon
from dotenv import load_dotenv
import os
import json
import openai
from openai import OpenAI
import tweepy
import argparse
import re

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def gettoot():
  global toot
  #tweetprompt="Write a tweet with less than 200 characters introducing a blog post titled: "+title
  tweetprompt="Write a thoughtful and humorous tweet, with less than 200 characters, introducing this article:\n\n"+articletext
  print(tweetprompt)

  try:
    response = client.chat.completions.create(model="gpt-4o",
    messages=[
          {"role": "system", "content": "You were born in 1975 in Kalamazoo, Michigan.  You are an American researcher and hacker, and hold a Ph.D in electrical engineering from MIT.  You have written books about reverse engineering.  You are a resident advisor and mentor to an early stage hardware accelerator and venture capital firm."},
          {"role": "user", "content": tweetprompt},
      ])
  except openai.OpenAIError as e:
    print("Error")
    print(e.http_status)
    print(e.error)
    exit(1)

  toot=response.choices[0].message.content.replace('"','')
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


postrootfolder=str(os.getenv("POST_ROOT_FOLDER"))
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
articletext=data['articletext']

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
twitter_bearer_token = os.getenv("TWITTER_BEARER_TOKEN")

if len(twitter_consumer_key)>5:
  #if too long... skip twitter
  if len(toot)<280:
    print("Posting to Twitter")
    # Authenticate to Twitter
    client = tweepy.Client(bearer_token=twitter_bearer_token, 
                          access_token=twitter_access_token, 
                          access_token_secret=twitter_access_token_secret, 
                          consumer_key=twitter_consumer_key,
                          consumer_secret=twitter_consumer_secret)

    client.create_tweet(text=toot)
