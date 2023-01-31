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

## Usage

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

## Notes

- The application is a cobbled together proof of concept.  There is limited error handling, it is sensitive and trusting to its input.  There are security issues (eg: trusting content sourced from a forum, trusting content sourced from OpenAI) and potentially content issues from generating text without review.  Use at your own risk.
- The code does build URLs and folders based the variables specified in your .env file, however, the code may have to be tweaked for your environment.  