# BioToolStory Twitter Bot

# collect tool that their Atricle_Date is today
import pandas as pd
from pandas.io.json import json_normalize
import os
import json
import datetime
import sys
import time
from datetime import datetime
from datetime import timedelta
import re
from dotenv import load_dotenv
import numpy as np
import ast
import requests
import time
import tweepy
from requests.auth import HTTPBasicAuth
from datetime import date
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from time import sleep

load_dotenv(verbose=True)

CHROMEDRIVER_PATH='/usr/local/bin/chromedriver'

PTH = os.environ.get('PTH_A') # PTH = '/home/maayanlab/Tools/'
API_url = os.environ.get('API_URL')
username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")
credentials = HTTPBasicAuth(username, password)

# get environment vars from .env
ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN')
ACCESS_TOKEN_SECRET = os.environ.get('ACCESS_TOKEN_SECRET')
CONSUMER_KEY = os.environ.get('CONSUMER_KEY')
CONSUMER_SECRET = os.environ.get('CONSUMER_SECRET')

#BITLY_TOKEN = os.environ.get('BITLY_TOKEN')
MAAYAN_KEY = os.environ.get('MAAYAN_KEY')

# Twitter authentication
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth, wait_on_rate_limit=True)

dry_run = str(sys.argv[1]) # set to 0 if you wat to post tweets
YESTERDAY = str(sys.argv[2]).replace("/","-")


def init_selenium(CHROMEDRIVER_PATH, windowSize='1080,1080'):
  print('Initializing selenium...')
  options = Options()
  options.add_argument('--headless')
  options.add_argument('--hide-scrollbars')
  options.add_argument('--no-sandbox')
  options.add_argument('--disable-extensions')
  options.add_argument('--dns-prefetch-disable')
  options.add_argument('--disable-gpu')
  options.add_argument('--window-size={}'.format(windowSize))
  driver = webdriver.Chrome(
    executable_path=CHROMEDRIVER_PATH,
    options=options,
  )
  return driver


def link_to_screenshot(link=None, output=None, zoom='100 %', browser=None):
  print('Capturing screenshot for enrichr...')
  time.sleep(2)
  browser.get(link)
  time.sleep(3)
  browser.execute_script("document.body.style.zoom='{}'".format(zoom))
  time.sleep(3)
  os.makedirs(os.path.dirname(output), exist_ok=True)
  browser.save_screenshot(output)
  return output


# update tool data
def update(tool):
  res = requests.patch('https://maayanlab.cloud/biotoolstory/metadata-api/' +"signatures/" + tool['id'], json=tool, auth=credentials)
  if not res.ok:
    print(res.text)
    return ("error")

  
def refresh():
  res = requests.get("https://maayanlab.cloud/biotoolstory/biotoolstory/meta-api/optimize/refresh", auth=credentials)
  print(res.ok)
  res = requests.get("https://maayanlab.cloud/biotoolstory/metadata-api/"+"optimize/status", auth=credentials)
  while not res.text == "Ready":
    time.sleep(1)
    res = requests.get("https://maayanlab.cloud/biotoolstory/metadata-api"+"/optimize/status", auth=credentials)
  res = requests.get("https://maayanlab.cloud/biotoolstory/metadata-api/"+"summary/refresh", auth=credentials)
  print(res.ok)


# test if url is available
def testURL(tool):
  if 'url_status' in tool['meta'].keys():
    url = tool['meta']['tool_homepage_url']
    try:
      request = requests.head(url,allow_redirects=False, timeout=10)
      status = request.status_code
    except:
      status = "error"
    tool['meta']['url_status'] = str(status)
  return(tool)


def short_url(url):
  if len(url) > 33:
    payload = {
          'url': url,
          'apikey': str(MAAYAN_KEY)    
      }
    response = requests.post('https://maayanlab.cloud/turl/api/register', json=payload)
    data = response.json()
    if 'shorturl' in data.keys(): 
      short_link = data['shorturl']
    else: 
      short_link = None
    # short url with bitly
    # headers = {
    #     'Authorization': 'Bearer' + str(BITLY_TOKEN),
    #     'Content-Type': 'application/json',
    # }
    # params = {
    #     "long_url": url
    # }
    # response = requests.post("https://api-ssl.bitly.com/v4/shorten", json=params, headers=headers)
    # data = response.json()
    # if 'link' in data.keys(): 
    #   short_link = data['link']
    # else: 
    #   short_link = None
  else:
    short_link = url
  return(short_link)


if  __name__ == "__main__":
  flg = False
  print("searching to tweet new tools")
  if not os.path.isdir(os.path.join(os.path.join(PTH,'TwitterBot/screenshots'))):
    os.mkdir(os.path.join(PTH,'TwitterBot/screenshots'))
  # get tools
  res = requests.get(API_url%("signatures",""))
  tools_DB = res.json()
  for tool in tools_DB:
    if 'Article_Date' in tool['meta'].keys() and tool['meta']['Year'] >= 2020:
      print(tool['meta']['PMID'])
      tool = testURL(tool)
      if ('Tweeted' not in tool['meta'].keys()) & ('url_status' in tool['meta'].keys()):
        if (tool['meta']['url_status'] != 'error') & (all([ x in tool['meta'].keys() for x in ['Tool_Name','tool_homepage_url'] ])):
          message ="The #bioinformatics tool #{}, available at {} was published {}\n"
          message = message + "{} is listed here {}\n"
          message = message + "Similar tools can be found at https://maayanlab.cloud/biotoolstory\n"
          message = message + "@maayanlab #BioToolStory"
          link = short_url('https://maayanlab.cloud/biotoolstory/#/ToolSearch/Tools?q={"search":["'+tool['id']+'"]}')
          if link == None:
            continue
          message = message.format( 
                                    tool['meta']['Tool_Name'], 
                                    tool['meta']['tool_homepage_url'],
                                    'https://pubmed.ncbi.nlm.nih.gov/'+str(tool['meta']['PMID'][0]),
                                    tool['meta']['Tool_Name'],
                                    link,
                                    )
          # capture webpage
          browser = init_selenium(CHROMEDRIVER_PATH,windowSize='1080,200')
          output = os.path.join(PTH,'TwitterBot/screenshots/',tool['id']+".png")
          url = tool['meta']['tool_homepage_url']
          screenshot = link_to_screenshot(link = url, output = output , browser=browser)
          # tweet
          if dry_run == '1':
            file1 = open(os.path.join(PTH,"TwitterBot/tweet.txt"),"w")
            file1.write(message) 
            file1.close()
            print(message)
          else:  
            if screenshot is not None:
              flg = True 
              stat = api.update_with_media(screenshot, message)
              os.remove(os.path.join(PTH,'TwitterBot/screenshots/',tool['id']+".png"))
              tool['meta']['Tweeted'] = 'https://twitter.com/i/web/status/' + stat._json['data']['id_str']
              update(tool)
              print("tweet was posted")
              time.sleep(1200) # tweet every 20 min
  if flg:
    print("done.")
    refresh()
  else:
    print("no new tools were found.")
