# bloggingbot

Bloggingbot is the source code that generates the text for my blogging bot, https://www.eliza-ng.me/, using OpenAI APIs.  

It is currently built to create pages for a static site generators - I'm using [Hugo](https://gohugo.io/) with the [Even](https://github.com/olOwOlo/hugo-theme-even) theme.

## Requirements

- Python
- A configured static sites generator, like Hugo, to publish content
- OpenAI API credentials
- Optional: Twitter or Mastodon credentials

## Installation

```
python3 -m pip install -r requirements.txt
```

Fill in the values for your environment in sampledotenvfile, and copy to .env 

## Usage - Blogging Bot scripts

1. Fetch a topic.  This script fetches a popular, recent discussion from a Hackernews, and then uses the captured text to create a prompt in ./currentarticle/prompt.json
```
python gettopic-hackernews.py
```
2. Generate a post.  This opens the prompt generated above, creates an image, and creates an article using OpenAI APIs.  The article is copied to the static site generator's post folder specified in the .env file. Buildpost.py can also be run interactively by calling it without command line arguments, to generate an article based on user supplied prompts.
```
python buildpost.py -ni --inputfile="currentarticle/prompt.json"
```
3. Deploy using your static site generator.  I am using Hugo.
```
hugo deploy
```
4. Broadcast the new article to Mastodon and Twitter
```
python announce.py
```

## Usage - Image to Blog Post tools

An experiment - scripts to create a fashion blog post from a source image.

[Sample Post](https://www.eliza-ng.me/post/eleganturbanpro/)

```
experiment-getseedimage-instyle.py - gets an image to seed the post from a fashion publication
experiment-generatefashionarticlefromimage.py - gets a description of the image from an image to text service
experiment-generatefashionimage.py - generate an image from the descripton using Automatic1111 api
experiment-buildpost-fashion.py - creates the blog post
```

## Usage - Avatar Talkshow Tools

Another experiment.  Tooling to automate some of the steps of creating video from generated content. 

- [Process Overview](https://www.hotelexistence.ca/creating-generated-video/)
- [Sample Video](https://youtu.be/Bq4yeWjFWEM)

1. Fetch content.  This script is a minor tweak to the regular Hackernews fetch.  It grabs more content, taking advantage of OpenAI's increased context size in its newer models.  The generated prompt it generates is hardcoded to request a JSON-formated response that we can further process in ./currentarticle/prompt.json
```
python gettopic-hackernews-fordialog.py  --hackernewsurl="https://news.ycombinator.com/item?id=39313942"
```
2. Generate a JSON formated dialog.  This opens the prompt generated above, and creates a dialog between two characters, that can then be sent to a text-to-speech synthesis API
```
python buildjsondialog.py
```
3. Generate audio.  This step takes the JSON formated dialog file, and calls out to the ElevenLabs test-to-speech API.  It creates a WAV file for each character, with silences for when the other character is speaking - no audio editing required!
```
python getdialogsamples.py
```
4. Finally, a Python script to automate creating a face animation .USD file for use in Unreal Engine from nVidia's audio2face model
```
python .\getfacenanim.py --gender=F --input="C:\Users\richa\Documents\Projects\bloggingbot\draft\zedvscode\Eliza_dialog.wav" --output="C:\Users\richa\Documents\Projects\bloggingbot\draft\zedvscode\ElizaFaceAnim.usd"
```


## Notes

- The application is a cobbled together proof of concept.  There is limited error handling, it is sensitive and trusting to its input.  There are security issues (eg: trusting content sourced from a forum, trusting content sourced from OpenAI) and potentially content issues from generating text without review.  Use at your own risk.
- The code does build URLs and folders based the variables specified in your .env file, however, the code may have to be tweaked for your environment.  