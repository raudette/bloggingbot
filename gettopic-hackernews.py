import requests
from bs4 import BeautifulSoup
import os
import openai
from dotenv import load_dotenv
import json

load_dotenv()

maxlength=14000
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

comments = soup.find_all("span", {"class": "commtext c00"})

allcommenttext=""
for comment in comments:
  if len(comment.text)>mincommentlength:
    if len(allcommenttext+comment.text)+5<maxlength:
      allcommenttext=allcommenttext+" "+comment.text.strip()

openai.api_key = os.getenv("OPENAI_API_KEY")

blogprompt = "Write an article about this text: \n\n " + allcommenttext +"\n\n"

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
  "tags": "Technology",
  "sourceurl": URL + topcommentedurl
}

jsonoutputprompt = json.dumps(outputprompt)

filename="./currentarticle/prompt.json"
print("Creating " + filename)
with open(filename, 'w') as f:
  f.write(jsonoutputprompt)
