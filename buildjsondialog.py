import os
import openai
from dotenv import load_dotenv
import shutil
from datetime import datetime
import requests
import argparse
import json

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
articleprompt=""
articletext=""
identifier=""

def getarticle():
  global articletext
  global articleprompt

  try:
    response = openai.chat.completions.create(
      model="gpt-4-1106-preview",
      response_format={ "type": "json_object" },
      messages=[
            {"role": "system", "content": "You are a helpful assistant designed to output JSON."},
            {"role": "user", "content": articleprompt},
        ],
    )
  except openai.OpenAIError as e:
    print("Error")
    print(e)
    exit(1)

  #print(response)
  print("Finish reason: ")
  print(response.choices[0].finish_reason)
  #articletext=response.choices[0].text
  articletext = response.choices[0].message.content

  with open("./draft/"+ identifier+"/"+identifier+".json", 'w') as f:
    f.write(articletext)

print("Building dialog")
inputfile = "./currentarticle/prompt.json" #args.inputfile
if len(inputfile)>1:
  # Opening JSON file
  f = open(inputfile)
  data = json.load(f)
  identifier=data['identifier']
  articleprompt=data['prompt']
  os.mkdir("./draft/"+ identifier)
  shutil.copyfile("./currentarticle/prompt.json","./draft/"+identifier+"/prompt.json")

  getarticle()
else:
  print("No input")