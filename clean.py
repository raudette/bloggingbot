import shutil
import json
from dotenv import load_dotenv
import os

load_dotenv()

postrootfolder=str(os.getenv("POST_ROOT_FOLDER"))

f = open("currentarticle/prompt.json")
data = json.load(f)
identifier=data['identifier']

draftfolder="./draft/" + identifier
postfolder=postrootfolder + identifier

print("Deleting folders")
print(draftfolder)
print(postfolder)
shutil.rmtree(draftfolder)
shutil.rmtree(postfolder)
