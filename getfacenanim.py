import requests
import os
from dotenv import load_dotenv
import argparse

load_dotenv()

parser = argparse.ArgumentParser()

parser.add_argument("--gender", help="Sets model gender - F (default) or M", type=str)
parser.add_argument("--input", help="inputsoundfile", type=str)
parser.add_argument("--output", help="output USD file", type=str)

args = parser.parse_args()

gender=args.gender.lower()
soundfilepath=os.path.dirname(args.input)
soundfile = os.path.basename(args.input)
exportdirectory=os.path.dirname(args.output)
faceanimname = os.path.basename(args.output)
headers = {
"Accept": "accept: application/json",
"Content-Type": "application/json"
}

# Load pre-setup USD
print("Load pre-setup USD")
url = "http://localhost:8011/A2F/USD/Load"
malefile=str(os.getenv("MALEA2FFILE"))
femalefile=str(os.getenv("FEMALEA2FFILE"))

if gender=='m':
    file=malefile
else:
    file=femalefile

data = {
  "file_name": file
}

response = requests.post(url, json=data, headers=headers)

if response.status_code != 200:
    print("Error loading base file")
    exit(1)


#set soundfile path
print("set soundfile path")
url='http://localhost:8011/A2F/Player/SetRootPath'
data = {
  "a2f_player": "/World/audio2face/Player",
  "dir_path": soundfilepath
}

response = requests.post(url, json=data, headers=headers)

if response.status_code != 200:
    print("Error setting soundfile path")
    exit(1)

#set soundfile
print("set soundfile")
url= "http://localhost:8011/A2F/Player/SetTrack"
data = {
  "a2f_player": "/World/audio2face/Player",
  "file_name": soundfile,
  "time_range": [
    0,
    -1
  ]
}    

response = requests.post(url, json=data, headers=headers)

if response.status_code != 200:
    print("Error setting soundfile")
    exit(1)
#export face anim
print("Export face anim")
url="http://localhost:8011/A2F/Exporter/ExportBlendshapes"
data = {
  "solver_node": "/World/audio2face/BlendshapeSolve",
  "export_directory": exportdirectory,
  "file_name": faceanimname,
  "format": "usd",
  "batch": False,
  "fps": 30
}

response = requests.post(url, json=data, headers=headers)

if response.status_code != 200:
    print("Error exporting face anim")
    exit(1)

print("Face anim exported, filename "+ faceanimname)