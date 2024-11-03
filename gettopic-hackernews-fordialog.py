import requests
from bs4 import BeautifulSoup
import os
import openai
from dotenv import load_dotenv
import json
import argparse

load_dotenv()

def generate_unique_filename(filename):
    postrootfolder = os.getenv("POST_ROOT_FOLDER")
    base_name, extension = os.path.splitext(filename)
    count = 1
    while os.path.exists(postrootfolder + filename):
        filename = f"{base_name}_{count}{extension}"
        count += 1
    return filename

maxlength=14000*4 #I think 14000 this represents a context window of 4096 for gpt-3.x - let's try 4x for gpt4-32k
mincommentlength=250
maxarticleage=22 #in hours
currenttopcomments=0
topcommentedurl = ""

parser = argparse.ArgumentParser()

parser.add_argument("--hackernewsurl", help="Sets Hacker News URL (ie: https://news.ycombinator.com/item?id=38981254)", type=str)

args = parser.parse_args()


hardcodeurl =  args.hackernewsurl 

page= requests.get(hardcodeurl)
soup = BeautifulSoup(page.content, "html.parser")

comments = soup.find_all("div", {"class": "commtext c00"})

allcommenttext=""
for comment in comments:
  if len(comment.text)>mincommentlength:
    if len(allcommenttext+comment.text)+5<maxlength:
      allcommenttext=allcommenttext+" "+comment.text.strip()

openai.api_key = os.getenv("OPENAI_API_KEY")

blogprompt = "Create a dialog between two talk show hosts, Eliza and Alan, discussing this Hackernews thread for their talk show, \"Musings This Week\", using the following template: {  \"dialog\": [    {      \"Eliza\": \"\"    },    {      \"Alan\": \"\"    }  ]}  \n\n " + allcommenttext +"\n\n"

try:
  response = openai.chat.completions.create (
    model="gpt-3.5-turbo",
    messages=[
          {"role": "system", "content": "You are a helpful assistant"},
          {"role": "user", "content": "identify 2 keywords from the following text:\n" + allcommenttext[0:14000]},
      ],
  )
except openai.OpenAIError as e:
  print("Error")
  print(e)
  exit(1)

#imageprompt = response['choices'][0]['message']['content'].lower()
keywords = ''.join(filter(str.isalpha, response.choices[0].message.content.lower())).replace("keyword","")[0:15]

print("Prompt: " + blogprompt)
print("Keywords: " + keywords)

identifier=generate_unique_filename(keywords)
print("Identifier: " + identifier)

outputprompt = {
  "prompt": blogprompt,
  "identifier": identifier,
  "tags": "Technology",
  "sourceurl": hardcodeurl
}

jsonoutputprompt = json.dumps(outputprompt)

filename="./currentarticle/prompt.json"
print("Creating " + filename)
with open(filename, 'w') as f:
  f.write(jsonoutputprompt)
