import requests
from bs4 import BeautifulSoup
import json

URL = "https://www.instyle.com/look-of-the-day"

headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/118.0'}

page = requests.get(URL, headers=headers)
soup = BeautifulSoup(page.content, "html.parser")
lookoftheday = soup.find(id='mntl-card-list-items_2-0')
URL = lookoftheday.attrs['href']
page = requests.get(URL, headers=headers)
soup = BeautifulSoup(page.content, "html.parser")
imagesection=soup.find(id='figure-article_1-0')
images = imagesection.findAll('img')
imageurl = images[1].attrs['src']
print("Getting " + imageurl)
imagebinary=requests.get(imageurl)

print("Saving ./currentarticle/seedimage.jpg")
file = open("./currentarticle/seedimage.jpg", 'wb')
file.write(imagebinary.content)
file.close()

outputprompt = {
  "sourceurl": URL,
  "sourceimageurl": imageurl,
  "expectedgender": "female" #we provide this clue, it facilitates building the image generation prompt
}

jsonoutputprompt = json.dumps(outputprompt)

filename="./currentarticle/prompt.json"
print("Creating " + filename)
with open(filename, 'w') as f:
  f.write(jsonoutputprompt)