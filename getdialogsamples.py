import requests
import os
from dotenv import load_dotenv
import json
import shutil
from mutagen.mp3 import MP3
import subprocess
from pydub import AudioSegment

load_dotenv()
ELEVENLABS_API_KEY=str(os.getenv("ELEVENLABS_API_KEY"))

CHUNK_SIZE = 1024
PAUSE_BETWEEN_SEGMENTS=0.3

dialogsegmentid=0
dialogdetails =[]

def generate_sample(name, dialog):
  global dialogsegmentid
  global identifier
  global dialogdetails
  url=""
  rachelurl = "https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM"
  billurl = "https://api.elevenlabs.io/v1/text-to-speech/pqHfZKP75CvOlQylNhV4"
  if 'Eliza' in name:
      print("Eliza says " + dialog)
      url=rachelurl
  elif 'Alan' in name:
      print("Alan says " + dialog)
      url=billurl
  else:
      return
  
  headers = {
  "Accept": "audio/mpeg",
  "Content-Type": "application/json",
  "xi-api-key": ELEVENLABS_API_KEY
  }

  outputfilename="./draft/"+identifier+"/"+str(dialogsegmentid)+"_"+name+".mp3"
  data = {
    "text": dialog,
      "model_id": "eleven_multilingual_v2",
    "voice_settings": {
      "stability": .5,
      "similarity_boost": .75,
      "use_speaker_boost": True
    }
  }

  response = requests.post(url, json=data, headers=headers)
  with open(outputfilename, 'wb') as f:
      for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
          if chunk:
             f.write(chunk)
  print(outputfilename)
  wavfilename = outputfilename.replace('.mp3','.wav')
  subprocess.run(["ffmpeg","-i",outputfilename, wavfilename])

  sample = MP3(outputfilename)
  print(sample.info.length)
  dialogsampledetails = {
      "dialogsegmentid": dialogsegmentid,
      "name": name,
      "length": sample.info.length,
      "filename": wavfilename
  } 
  dialogdetails.append(dialogsampledetails)
  dialogsegmentid=dialogsegmentid+1

def combine_samples():
  if len(dialogdetails)<2:
      print("Too few samples")
      exit()
  path="./draft/"+identifier+"/"

  for index, dialogsampledetails in enumerate(dialogdetails):
    if (index==0):
      print("Creating base snippet 0 and 1")
      shutil.copy(dialogsampledetails['filename'],path+dialogsampledetails['name']+"_dialog.wav")
      #######LOOK AT THIS LINE TO PREPAD ALAN SAMPLE
      subprocess.run(["ffmpeg","-i",dialogdetails[1]['filename'],'-af','areverse,apad=pad_dur='+str(dialogdetails[0]['length']+PAUSE_BETWEEN_SEGMENTS)+',areverse',path+dialogdetails[1]['name']+"_dialog.wav"])
    if (index>=2):
      print("Merging snippet "+str(index))
      #Weird thing #1 - ffmpeg can't merge WAV files without converting them first?
      outputsound = AudioSegment.from_wav(path+dialogsampledetails['name']+"_dialog.wav") + AudioSegment.from_wav(dialogsampledetails['filename'])
      outputsound.export(path+dialogsampledetails['name']+'_dialog_temp.wav', format="wav")
      shutil.copy(path+dialogsampledetails['name']+'_dialog_temp.wav',path+dialogsampledetails['name']+'_dialog.wav')
      os.remove(path+dialogsampledetails['name']+'_dialog_temp.wav')
    if index+1<len(dialogdetails):
      print("Adding silence to snippet "+str(index+1))
      subprocess.run(["ffmpeg","-i",path+dialogsampledetails['name']+'_dialog.wav','-af','apad=pad_dur='+str(dialogdetails[index+1]['length']+PAUSE_BETWEEN_SEGMENTS),path+dialogsampledetails['name']+'_dialog_temp.wav'])
      shutil.copy(path+dialogsampledetails['name']+'_dialog_temp.wav',path+dialogsampledetails['name']+'_dialog.wav')
      os.remove(path+dialogsampledetails['name']+'_dialog_temp.wav')


articlesettingsfile = open("./currentarticle/prompt.json")
articlesettings = json.load(articlesettingsfile)
identifier=articlesettings['identifier']
articlesettingsfile.close()

dialogfile = open("./draft/"+identifier+"/"+identifier+".json")
dialog = json.load(dialogfile)
dialogfile.close()


for dialogsegment in dialog['dialog']:
    for name in dialogsegment:
        generate_sample(name, dialogsegment[name])

combine_samples()



