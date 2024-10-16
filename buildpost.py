import os
import openai
from openai import OpenAI
from dotenv import load_dotenv
import shutil
from datetime import datetime
import urllib.request
import argparse
import json

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

postrootfolder=str(os.getenv("POST_ROOT_FOLDER"))
author=str(os.getenv("AUTHOR"))

identifier="default"
title=""
tags="" 
imageprompt=""
articleprompt=""
articletext=""
iArticleRevision=0
iImageRevision=0
sourceurl=""

def pusharticle():
  global identifier
  global title
  global iArticleRevision
  global sourceurl
  filename="./draft/"+identifier+"/index."+str(iArticleRevision)+".md"
  print("Creating" + filename)
  with open(filename, 'w') as f:
    f.write('---\n')
    f.write('title: "'+title+'"\n')
    now = datetime.now()
    currenttime=now.strftime("%Y-%m-%dT%H:%M:%S")
    f.write('date: '+ currenttime +'+05:00\n')
    f.write('lastmod: '+ currenttime +'+05:00\n')
    f.write('draft: false\n')
    f.write('tags: ["'+tags+'"]\n')
    f.write('author: "'+author+'"\n')
    f.write('images: ["/post/'+identifier+'/'+identifier+'.png"]\n')
    f.write('autoCollapseToc: false\n')
    f.write('\n')
    f.write('---\n')
    f.write('\n')
    endoffirstparagraph=0
    if "\n" in articletext[5:]:
      endoffirstparagraph = articletext.index("\n", 5)
      f.write(articletext[0:endoffirstparagraph])
    f.write('{{% center %}}\n')
    f.write('![img](./'+identifier+'.png "img")\n')
    f.write('{{% /center %}}\n')
    #look for the end of the first paragraph
    f.write(articletext[endoffirstparagraph:])
    f.write('\n')
    f.write('\n')

  destinationfile=postrootfolder + identifier + "/index.md"
  print("Pushing "+destinationfile)
  shutil.copyfile(filename,destinationfile)
  iArticleRevision=iArticleRevision+1


def setidentifier():
  global identifier
  print("Enter post identifier (used for folder, etc)")
  identifier = input()
  print("folder draft/" + identifier)
  print("folder " + postrootfolder + identifier)
  print("")
  print("Proceed y/n")
  proceed = input()
  if "n" in proceed:
    setidentifier()
  setupfolders()

def setupfolders():
  global identifier
  os.mkdir("./draft/"+ identifier)
  os.mkdir(postrootfolder+ identifier)

def settitle():
  global title
  print("Enter post title")
  title = input()
  print("title: " + title)
  print("")
  print("Proceed y/n")
  proceed = input()
  if "n" in proceed:
    settitle()

def settags():
  global tags
  print("Enter comma-separated post tags")
  tags = input()
  print("tags: " + tags)
  print("")
  print("Proceed y/n")
  proceed = input()
  if "n" in proceed:
    settags()

def setimageprompt():
  global imageprompt
  global identifier
  global iImageRevision

  if len(imageprompt)<1:
    print("Enter post image prompt")
    imageprompt = input()
    print("image prompt: " + imageprompt)
    print("")

  getimage()

  print("Proceed with this image, hit y, to generate a new image, hit n, retry same prompt r")
  proceed = input()
  if "n" in proceed:
    imageprompt=""
    setimageprompt()
  if "r" in proceed:
    setimageprompt()

def getimage():
  global imageprompt
  global identifier
  global iImageRevision

  try:
    response = client.images.generate(prompt=imageprompt,
    model="dall-e-3",
    n=1,
    size="1024x1024")
    image_url = response.data[0].url
    versionfilename="./draft/"+identifier+"/"+identifier+"."+str(iImageRevision)+".png"
    print("Retrieving "+image_url)
    print("Writing to "+versionfilename)
    urllib.request.urlretrieve(image_url, versionfilename)
  except openai.OpenAIError as e:
    print("Error")
    print(e.http_status)
    print(e.error)
    versionfilename="./NoImageGenerated.png"  
  finalfilename=postrootfolder + identifier + "/" + identifier + ".png"
  print("Pushing "+finalfilename)
  shutil.copyfile(versionfilename,finalfilename)
  iImageRevision=iImageRevision+1
  pusharticle()  

def setarticleprompt():
  global articleprompt

  if len(articleprompt)<1:
    print("Enter article prompt")
    articleprompt = input()
    print("article prompt: " + articleprompt)
    print("")

  getarticle()

  print("Proceed with this article, hit y, to generate a new article, hit n, retry same prompt r")
  proceed = input()
  if "n" in proceed:
    articleprompt=""
    setarticleprompt()
  if "r" in proceed:
    setarticleprompt()


def getarticle():
  global articletext
  global articleprompt

  try:
    response = client.chat.completions.create(model="gpt-4o",
    messages=[
          {"role": "system", "content": "You were born in 1975 in Kalamazoo, Michigan.  You are an American researcher and hacker, and hold a Ph.D in electrical engineering from MIT.  You have written books about reverse engineering.  You are a resident advisor and mentor to an early stage hardware accelerator and venture capital firm."},
          {"role": "user", "content": articleprompt},
      ])

  except openai.OpenAIError as e:
    print("Error")
    print(e.http_status)
    print(e.error)
    exit(1)

  #print(response)
  print("Finish reason: ")
  print(response.choices[0].finish_reason)
  #articletext=response.choices[0].text
  articletext = response.choices[0].message.content

  #get rid of surplus title added by latest version of GPT-3.5-turbo
  if articletext[0:7]=='Title: ':
    endoffirstparagraph = articletext.index("\n\n", 0)+2
    articletext=articletext[endoffirstparagraph:]



  pusharticle()  

def createtitle():
  global articletext
  global title

  try:
    response = client.chat.completions.create(model="gpt-4o",
    messages=[
          {"role": "system", "content": "You are a journalist"},
          {"role": "user", "content": "Create a catchy title for the following blog text:\n" + articletext},
      ])
  except openai.OpenAIError as e:
    print("Error")
    print(e.http_status)
    print(e.error)
    exit(1)

  title=response.choices[0].message.content.replace('"','')
  #latest version of GPT3.5 has annoying habit of putting Title: in the Title - let's get rid of it
  title=title.replace('Title: ','')

  pusharticle()  

def archivesources():
  global identifier
  global imageprompt
  global articleprompt
  global sourceurl
  global title

  archivesources = {
    "articleprompt": articleprompt,
    "imageprompt": imageprompt,
    "sourceurl": sourceurl,
    "title": title,
    "articletext":articletext
  }

  jsonarchivesources = json.dumps(archivesources)

  draftcopy="./draft/"+ identifier + "/" + identifier + ".json"
  destinationfile=postrootfolder + identifier + "/" + identifier + ".json"
  print("Archiving Sources: " + draftcopy)
  with open(draftcopy, 'w') as f:
    f.write(jsonarchivesources)
  shutil.copyfile(draftcopy,destinationfile)



parser = argparse.ArgumentParser()

parser.add_argument("--identifier", help="folder and article name", type=str)
parser.add_argument("--title", help="article title", type=str)
parser.add_argument("--tags", help="tags to categorize articles", type=str)
parser.add_argument("--imageprompt", help="prompt to generate image", type=str)
parser.add_argument("--articleprompt", help="prompt to generate text", type=str)
parser.add_argument("--sourceurl", help="source url used to seed article", type=str)
parser.add_argument("--inputfile", help="set identifier and prompt by input", type=str)
parser.add_argument("-ni", "--noninteractive", help="use command line arguments", action='store_true')
parser.add_argument("-f", "--file", help="use ", action='store_true')

args = parser.parse_args()

if args.noninteractive:
  print("Building article")
  inputfile = args.inputfile
  if len(inputfile)>1:
    # Opening JSON file
    f = open(inputfile)
    data = json.load(f)
    identifier=data['identifier']
    articleprompt=data['prompt']
    tags=data['tags']
    sourceurl=data['sourceurl']
    imageprompt=data['imageprompt']
  else:
    identifier=args.identifier
    articleprompt=args.articleprompt
    tags=str(args.tags)
    sourceurl=str(args.sourceurl)
    imageprompt=str(args.imageprompt)
  title=str(args.title)
  setupfolders()
  getarticle()
  if title=="None":
    createtitle()
  if imageprompt=="None":
    imageprompt="photo to accompany a blog post titled: " + title
  getimage()
  archivesources()
else:
  setidentifier()
  settags()
  settitle()
  setimageprompt()
  setarticleprompt()
  archivesources()
