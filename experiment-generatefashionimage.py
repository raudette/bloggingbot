import json
import requests
import io
import base64
from PIL import Image, PngImagePlugin

url = "http://localhost:7860"

inputfile="./currentarticle/prompt.json"
f = open(inputfile)
articledetails = json.load(f)

payload = {
    "prompt": articledetails['imageprompt'],
    "steps": 150,
    "Sampler": "DPM++ 2M Karras",
    "CFG scale": 7, 
#    "Seed": 1024661444, 
    "Size": "1024x1024", 
    "Model": "epicphotogasm_x"
#    "Model": "sd_xl_base_1.0"
}

response = requests.post(url=f'{url}/sdapi/v1/txt2img', json=payload)

r = response.json()

extraspayload = {
#  "resize_mode": 0,
#  "show_extras_results": True,
  "gfpgan_visibility": 0.8,
  "codeformer_visibility": 0.8,
  "codeformer_weight": 0.05,
  "upscaling_resize_w": 1024,
  "upscaling_resize_h": 1024,
#  "upscaling_resize": 4,
#  "upscaling_crop": True,
  "upscaler_1": "Lanczos",
#  "upscaler_2": "None",
#  "extras_upscaler_2_visibility": 0,
  "upscale_first": True,
  "image": r['images'][0]
}

response2 = requests.post(url=f'{url}/sdapi/v1/extra-single-image', json=extraspayload)

r2 = response2.json()

image = Image.open(io.BytesIO(base64.b64decode(r['images'][0])))
image.save('./currentarticle/'+articledetails["identifier"]+'.jpg')
image = Image.open(io.BytesIO(base64.b64decode(r2['image'])))
image.save('./currentarticle/'+articledetails["identifier"]+'_up.jpg')

articledetails['image']=articledetails["identifier"]+'_up.jpg'

jsonoutputprompt = json.dumps(articledetails)

filename="./currentarticle/prompt.json"
print("Creating " + filename)
with open(filename, 'w') as f:
  f.write(jsonoutputprompt)