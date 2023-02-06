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

blogprompt = "Write a blog post about this text: \n\n " + allcommenttext +"\n\n"

response = openai.Completion.create(
  model="text-davinci-003",
  prompt="identify 2 keywords from the following text:\n" + allcommenttext,
  temperature=0.7,
  max_tokens=30,
  top_p=1,
  frequency_penalty=0,
  presence_penalty=1
)

keywords = ''.join(filter(str.isalpha, response.choices[0].text.lower())).replace("keyword","")[0:15]

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
