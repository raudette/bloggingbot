import requests
from bs4 import BeautifulSoup
import os
import openai
from openai import OpenAI

from dotenv import load_dotenv
import json

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_unique_filename(filename):
    postrootfolder = os.getenv("POST_ROOT_FOLDER")
    base_name, extension = os.path.splitext(filename)
    count = 1
    while os.path.exists(postrootfolder + filename):
        filename = f"{base_name}_{count}{extension}"
        count += 1
    return filename

maxlength=28000
mincommentlength=250
maxarticleage=22 #in hours
currenttopcomments=0
topcommentedurl = ""

URL = "https://news.ycombinator.com/"
page = requests.get(URL)
soup = BeautifulSoup(page.content, "html.parser")
linkrows = soup.find_all("span", {"class": "subline"})

for linkrow in linkrows:
  itemlink=""
  articleage=0
  numcomments=0
  cells=linkrow.find_all("a")
  for cell in cells:
    if "item" in cell.attrs['href']:
      itemlink=cell.attrs['href']
      if "hours ago" in cell.text:
        articleage=int(''.join(filter(str.isdigit, cell.text)))
      if "day ago" in cell.text:
        articleage=int(''.join(filter(str.isdigit, cell.text)))*24
      if "days ago" in cell.text:
        articleage=int(''.join(filter(str.isdigit, cell.text)))*24
      if "comments" in cell.text:
        numcomments = int(''.join(filter(str.isdigit, cell.text)))
  #check for article freshness
  if articleage <= maxarticleage:
    #we want one with lots of comments  
    if numcomments>currenttopcomments:
      currenttopcomments=numcomments
      topcommentedurl=itemlink


print("Getting: " + URL + topcommentedurl)

page= requests.get(URL + topcommentedurl)
soup = BeautifulSoup(page.content, "html.parser")

comments = soup.find_all("div", {"class": "commtext c00"})

allcommenttext=""
for comment in comments:
  if len(comment.text)>mincommentlength:
    if len(allcommenttext+comment.text)+5<maxlength:
      allcommenttext=allcommenttext+" "+comment.text.strip()


blogprompt = "Write a thoughtful article about this discussion you just read.  Don't reference the discussion itself, write about the content of the discussion: \n\n " + allcommenttext +"\n\n"

try:
  response = client.chat.completions.create(model="gpt-4o-mini",
  messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "identify 2 keywords from the following text:\n" + allcommenttext},
    ])
except openai.OpenAIError as e:
  print("Error")
  print(e.http_status)
  print(e.error)
  exit(1)

keywords = ''.join(filter(str.isalpha, response.choices[0].message.content.lower())).replace("keyword","")[0:15]

try:
  response = client.chat.completions.create(model="gpt-4o-mini",
  messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Identify and describe an object from this text with fewer than 10 words:\n" + allcommenttext},
    ])
except openai.OpenAIError as e:
  print("Error")
  print(e.http_status)
  print(e.error)
  exit(1)

imageprompt = response.choices[0].message.content

print("Prompt: " + blogprompt)
print("Keywords: " + keywords)

identifier=generate_unique_filename(keywords)
print("Identifier: " + identifier)

outputprompt = {
  "prompt": blogprompt,
  "identifier": identifier,
  "tags": "Technology",
  "imageprompt": imageprompt,
  "sourceurl": URL + topcommentedurl
}

jsonoutputprompt = json.dumps(outputprompt)

filename="./currentarticle/prompt.json"
print("Creating " + filename)
with open(filename, 'w') as f:
  f.write(jsonoutputprompt)
