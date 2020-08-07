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

PTH = os.environ.get('PTH_A')
API_url = os.environ.get('API_URL')
username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")
credentials = HTTPBasicAuth(username, password)

# get environment vars from .env
ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN')
ACCESS_TOKEN_SECRET = os.environ.get('ACCESS_TOKEN_SECRET')
CONSUMER_KEY = os.environ.get('CONSUMER_KEY')
CONSUMER_SECRET = os.environ.get('CONSUMER_SECRET')
# Twitter authentication
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth, wait_on_rate_limit=True)

TODAY = str(date.today())

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
  res = requests.patch('https://amp.pharm.mssm.edu/biotoolstory/meta-api/' +"signatures/" + tool['id'], json=tool, auth=credentials)
  if not res.ok:
    print(res.text)
    return ("error")

  
def refresh():
  res = requests.get("https://amp.pharm.mssm.edu/biotoolstory/meta-api/optimize/refresh", auth=credentials)
  print(res.ok)
  res = requests.get("https://amp.pharm.mssm.edu/biotoolstory/meta-api/"+"optimize/status", auth=credentials)
  while not res.text == "Ready":
    time.sleep(1)
    res = requests.get("https://amp.pharm.mssm.edu/biotoolstory/meta-api"+"/optimize/status", auth=credentials)
  res = requests.get("https://amp.pharm.mssm.edu/biotoolstory/meta-api/"+"summary/refresh", auth=credentials)
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

  
if __name__=='main':
  if not os.path.isdir(os.path.join(os.path.join(PTH,'TwitterBot/screenshots'))):
    os.mkdir(os.path.join(PTH,'TwitterBot/screenshots'))
  # get tools
  res = requests.get(API_url%("signatures",""))
  tools_DB = res.json()
  for tool in tools_DB:
    if 'Article_Date' in tool['meta'].keys():
      if tool['meta']['Article_Date'] == TODAY:
        print(tool['meta']['PMID'])
        tool = testURL(tool)
        if ('Tweeted' not in tool['meta'].keys()) & ('url_status' in tool['meta'].keys()):
          
          if tool['meta']['url_status'] != 'error' & all([ x in tool['meta'].keys() for x in ['Tool_Name','tool_homepage_url','Article_Date']  ]):
            message ="The #BioToolStroy Bot discovered a new bioinformatics tool that was published on {} called {} \n{} \n{} \n{} \n"
            message = message + "Similar tools can be found at: https://amp.pharm.mssm.edu/biotoolstory/ \n"
            message = message + "@maayanlab #bioinformatics"
            message = message.format( 
                                      datetime.strptime(tool['meta']['Article_Date'], '%Y-%m-%d').strftime("%m-%d-%Y"),
                                      tool['meta']['Tool_Name'], 
                                      u"\U0001F517 " + tool['meta']['tool_homepage_url'],
                                      u"\U0001F4DC " + 'https://pubmed.ncbi.nlm.nih.gov/'+str(tool['meta']['PMID'][0]),
                                      u"\U0001F310 " + 'https://amp.pharm.mssm.edu/biotoolstory/#/ToolSearch/Tools?q={"search":["'+tool['id']+'"]}',
                                      )
            # capture webpage
            browser = init_selenium(CHROMEDRIVER_PATH,windowSize='1080,200')
            output = os.path.join(PTH,'TwitterBot/screenshots/',tool['meta']['Tool_Name']+".jpg")
            url = tool['meta']['tool_homepage_url']
            screenshot = link_to_screenshot(link = url, output = output , browser=browser)
            # tweet
            if screenshot is not None:
              api.update_with_media(screenshot, message)
              os.remove(os.path.join(PTH,'TwitterBot/screenshots/',tool['meta']['Tool_Name']+".jpg"))
              tool['meta']['Tweeted'] = 1
              update(tool)
    time.sleep(1200) # tweet every 20 min
  refresh()
