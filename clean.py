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

print("Delete folders (y/n)?")
print(draftfolder)
print(postfolder)
proceed = input()
if "y" in proceed:
    print("Deleting")
    shutil.rmtree(draftfolder)
    shutil.rmtree(postfolder)
else:
    print("Nothing deleted")