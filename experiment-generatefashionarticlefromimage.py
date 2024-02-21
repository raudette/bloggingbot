import requests
import os
import openai
from dotenv import load_dotenv
import json
import base64
import io
from PIL import Image


load_dotenv()

def generate_unique_filename(filename):
    postrootfolder = os.getenv("POST_ROOT_FOLDER")
    base_name, extension = os.path.splitext(filename)
    count = 1
    while os.path.exists(postrootfolder + filename):
        filename = f"{base_name}_{count}{extension}"
        count += 1
    return filename

def get_image_base64_encoding(image_path: str) -> str:
    """
    Function to return the base64 string representation of an image
    """
    with open(image_path, 'rb') as file:
        image_data = file.read()
    image_extension = os.path.splitext(image_path)[1]
    base64_encoded = base64.b64encode(image_data).decode('utf-8')
    return f"data:image/{image_extension[1:]};base64,{base64_encoded}"

def callgpt(prompt):
  try:
    response = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": prompt},
        ],
    )
  except openai.error.OpenAIError as e:
    print("Error")
    print(e.http_status)
    print(e.error)
    exit(1)
  return response['choices'][0]['message']['content']

def asticaAPI(endpoint, payload, timeout):
    response = requests.post(endpoint, data=json.dumps(payload), timeout=timeout, headers={ 'Content-Type': 'application/json', })
    if response.status_code == 200:
        return response.json()
    else:
        return {'status': 'error', 'error': 'Failed to connect to the API.'}

# API configurations
asticaAPI_key = os.getenv("ASTICA_API_KEY") # visit https://astica.ai
asticaAPI_timeout = 25 # in seconds. "gpt" or "gpt_detailed" require increased timeouts
asticaAPI_endpoint = 'https://vision.astica.ai/describe'
asticaAPI_modelVersion = '2.1_full' # '1.0_full', '2.0_full', or '2.1_full'

#if 1 == 1:
#    asticaAPI_input = 'https://astica.ai/example/asticaVision_sample.jpg' # use https image input (faster)
#else:
#    asticaAPI_input = get_image_base64_encoding('image.jpg')  # use base64 image input (slower)
asticaAPI_input= get_image_base64_encoding('./currentarticle/seedimage.jpg')

# vision parameters:  https://astica.ai/vision/documentation/#parameters
asticaAPI_visionParams = 'gpt,describe,objects,faces'  # comma separated, defaults to "all". 
asticaAPI_gpt_prompt = '' # only used if visionParams includes "gpt" or "gpt_detailed"
asticaAPI_prompt_length = '90' # number of words in GPT response

'''    
    '1.0_full' supported visionParams:
        describe
        objects
        categories
        moderate
        tags
        brands
        color
        faces
        celebrities
        landmarks
        gpt               (Slow)
        gpt_detailed      (Slower)

    '2.0_full' supported visionParams:
        describe
        describe_all
        objects
        tags
        describe_all 
        text_read 
        gpt             (Slow)
        gpt_detailed    (Slower)
        
    '2.1_full' supported visionParams:
        Supports all options 
        
'''

# Define payload dictionary
asticaAPI_payload = {
    'tkn': asticaAPI_key,
    'modelVersion': asticaAPI_modelVersion,
    'visionParams': asticaAPI_visionParams,
    'input': asticaAPI_input,
}

# call API function and store result
asticaAPI_result = asticaAPI(asticaAPI_endpoint, asticaAPI_payload, asticaAPI_timeout)

# print API output
print('\nastica API Output:')
print(json.dumps(asticaAPI_result, indent=4))
print('=================')
print('=================')
# Handle asticaAPI response
if 'status' in asticaAPI_result:
    # Output Error if exists
    if asticaAPI_result['status'] == 'error':
        print('Output:\n', asticaAPI_result['error'])
    # Output Success if exists
    if asticaAPI_result['status'] == 'success':
        if 'caption_GPTS' in asticaAPI_result and asticaAPI_result['caption_GPTS'] != '':
            print('=================')
            print('GPT Caption:', asticaAPI_result['caption_GPTS'])
        if 'caption' in asticaAPI_result and asticaAPI_result['caption']['text'] != '':
            print('=================')
            print('Caption:', asticaAPI_result['caption']['text'])
        if 'CaptionDetailed' in asticaAPI_result and asticaAPI_result['CaptionDetailed']['text'] != '':
            print('=================')
            print('CaptionDetailed:', asticaAPI_result['CaptionDetailed']['text'])
        if 'objects' in asticaAPI_result:
            print('=================')
            print('Objects:', asticaAPI_result['objects'])
else:
    print('Invalid response')
    exit(1)


# remove references not related to the primary person in this passage:
# create a title for the outfit described here:
# Write a paragraph from the following text as it would appear in InStyle magazine, and only writing about the model's clothing.  You can name the model:
# Write a paragraph from the following text as it would appear in InStyle magazine, and only writing about the model's clothing.  Don't reference her age.  You can name the model:

openai.api_key = os.getenv("OPENAI_API_KEY")

#not super critical, but so we can reference articles back from the source, we'll load these & so we can preserve them in the prompt file
inputfile="./currentarticle/prompt.json"
f = open(inputfile)
sourcedetails = json.load(f)

#personandoutfitprompt = "Describe the woman's outfit and appearance in the following text, without referencing the text: \n\n " + asticaAPI_result['caption_GPTS']
personandoutfitprompt= "Enumerate words describing clothing in this paragraph in a comma separated list.  Do not provide an introduction sentence:\n\n " + asticaAPI_result['caption_GPTS']
if "female" in sourcedetails['expectedgender']:
  personandoutfit = "Female model, " + callgpt(personandoutfitprompt) + ",urban scene"
else:
  personandoutfit = "Male model, " + callgpt(personandoutfitprompt) + ",urban scene"
headlineprompt = "Create a title for the outfit described here: \n\n " + personandoutfit
headline=callgpt(headlineprompt).replace('"','')
articleprompt = "Write a paragraph from the following text as it would appear in InStyle magazine.  Only write about the model's clothing.  Do not reference age.  Do not mention InStyle. You can name the model: \n\n " + asticaAPI_result['caption_GPTS']
article=callgpt(articleprompt)

keywords = ''.join(filter(str.isalpha, headline.lower())).replace("keyword","")[0:15]

print("Keywords: " + keywords)

identifier=generate_unique_filename(keywords)
print("Identifier: " + identifier)

outputprompt = {
  "sourceurl": sourcedetails['sourceurl'],
  "sourceimageurl": sourcedetails['sourceimageurl'],
  "expectedgender": sourcedetails['expectedgender'], #we provide this clue, it facilitates building the image generation prompt
  "img2txt": asticaAPI_result['caption_GPTS'],
  "title": headline,
  "article": article,
  "identifier": identifier,
  "tags": "FashioNg",
  "imageprompt": personandoutfit,
}

jsonoutputprompt = json.dumps(outputprompt)

filename="./currentarticle/prompt.json"
print("Creating " + filename)
with open(filename, 'w') as f:
  f.write(jsonoutputprompt)
