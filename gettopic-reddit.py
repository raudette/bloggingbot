import praw
import datetime
import os
import openai
from dotenv import load_dotenv
import json
import argparse

#used to sort posts by upvotes
def getups(elem):
  if hasattr(elem, 'ups'):
    return elem.ups
  else:
    return 0

load_dotenv()

parser = argparse.ArgumentParser()
parser.add_argument("--inputfile", help="define subreddit with input file", type=str)
args = parser.parse_args()

inputfile = args.inputfile

if inputfile is None:
  currentfolder=os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
  inputfile=currentfolder+ '/gettopic-redditconfig-sample1.json'

#get your API key from https://www.reddit.com/prefs/apps
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    password=os.getenv("REDDIT_CLIENT_PASSWORD"),
    user_agent=os.getenv("REDDIT_CLIENT_AGENT"),
    username=os.getenv("REDDIT_CLIENT_USERNAME")
)

# JSON file defines what subreddit to pull
f = open(inputfile)
config = json.load(f)
subreddit = config['subreddit']
# subreddit posts are categorized - reddit calls this flair
interestingtopics = []
for category in config['categories']:
  interestingtopics.append(category)
maxagehours=config['maxagehours']
minagehours=config['minagehours']
tags=config['tags']

allcommenttext=""
maxlength=14000
mincommentlength=250

RedditURL=""

submissions=reddit.subreddit(subreddit).new(limit=100)
mostcomments=0
mostcommentedindex=0

#find a submission that meets our age and category criteria, collect the comments of the most commented one
for index, submission in enumerate(submissions):
  interestingtopics = ['Buying','Investing','Discussion','Requesting Advice','New Construction','House','News']
  if (submission.link_flair_text) in interestingtopics:
    howlongago = datetime.datetime.utcnow() - datetime.datetime.fromtimestamp(submission.created_utc)
    #check for fresh content
    if (minagehours*60*60) <= (howlongago.total_seconds()) < (maxagehours*60*60):
      numcomments= len(submission.comments.list())
      if numcomments > mostcomments:
        mostcomments=numcomments
        mostcommentedindex=index
        #get upvoted verbose comments
        all_comments = submission.comments.list()
        all_comments.sort(key=getups,reverse=True)
        for comment in all_comments:
          if hasattr(comment, 'body'):
            if len(comment.body)>mincommentlength:
              if len(allcommenttext+comment.body)+5<maxlength:
                allcommenttext=allcommenttext+" "+comment.body.strip()
        RedditURL="https://www.reddit.com" + submission.permalink
        allcommenttext=allcommenttext.replace('\r', ' ').replace('\n', ' ')

openai.api_key = os.getenv("OPENAI_API_KEY")

blogprompt = "Write a blog post about this text: \n\n " + allcommenttext +"\n\n"

try:
  response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
          {"role": "system", "content": "You are a helpful assistant"},
          {"role": "user", "content": "identify 2 keywords from the following text:\n" + allcommenttext},
      ],
  )
except openai.error.OpenAIError as e:
  print("Error")
  print(e.http_status)
  print(e.error)
  exit(1)

keywords = ''.join(filter(str.isalpha, response['choices'][0]['message']['content'].lower())).replace("keyword","")[0:15]

print("Prompt: " + blogprompt)
print("Keywords: " + keywords)

outputprompt = {
  "prompt": blogprompt,
  "identifier": keywords,
  "tags": tags,
  "sourceurl": RedditURL
}

jsonoutputprompt = json.dumps(outputprompt)

filename="./currentarticle/prompt.json"
print("Creating " + filename)
with open(filename, 'w') as f:
  f.write(jsonoutputprompt)