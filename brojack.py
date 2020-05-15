#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Broken Link Hijack (BroJack)
# By Locu

from bs4 import BeautifulSoup
import requests
import requests.exceptions
from urllib.parse import urlsplit
from urllib.parse import urlparse
from collections import deque
from colorama import Fore, Style
import re
import sys
import os
import subprocess
import argparse

class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'

motd = 'Broken Link Hijack (BroJack) by Locu '

parser = argparse.ArgumentParser(description=motd)
parser.add_argument('--domain', '-d', help='Domain name of website you want to map. i.e. "https://bio.locu.uk"')
parser.add_argument('--list', '-l', help='Process a list of domains/urls from an input file')
parser.add_argument('--outfile', '-o', help='Define output file to save results of stdout. i.e. "test.txt"')
parser.add_argument('--mobile', '-m', action="store_true", help='Change User-Agent to android mobile')
parser.add_argument('--takeover', '-t', action="store_true", help='Check if domain is available')
parser.add_argument('--verbose', '-v', action="store_true", help='Show verbose info')
parser.parse_args()

if len(sys.argv)<2:
	print('eg: python %s -l domainlist' % sys.argv[0])
	args = parser.parse_args(['-h'])
else:
	args = parser.parse_args()

args = parser.parse_args()
domain = args.domain
dlist = args.list
outfile = args.outfile
mobile = args.mobile
takeover = args.takeover
verbose = args.verbose

if domain:
  print(color.BOLD + "Domain:", color.YELLOW, domain, color.END)
if dlist:
  print(color.BOLD + "Domain list file:", color.YELLOW, dlist, color.END)
if outfile:
  print(color.BOLD + "Output file:", color.YELLOW, outfile, color.END)
if mobile:
  print(color.BOLD + "User Agent Mobile:", color.YELLOW, mobile, color.END)
if takeover:
  print(color.BOLD + "Takeover Check:", color.YELLOW, takeover, color.END)
if verbose:
  print(color.BOLD + "Verbose:", color.YELLOW, verbose, color.END)        

print()
broken_urls = set()
external_urls = set()
local_urls = set()
processed_urls = set()
domains = set()

def crawler(domain, outfile):
    try:
        new_urls = deque([domain])
       
        while len(new_urls):

            url = new_urls.popleft()
            processed_urls.add(url)

            
            if mobile is True:
              headers = ({'User-Agent':'Mozilla/5.0 (Linux; Android 9; SM-G960F Build/PPR1.180610.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/74.0.3729.157 Mobile Safari/537.36'})
            else:
              headers = ({'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'})
            try:
              #print (headers)
              response = requests.get(url,headers = headers,timeout=5)
            except (requests.exceptions.InvalidSchema,requests.exceptions.MissingSchema,requests.exceptions.ReadTimeout,requests.exceptions.Timeout,requests.exceptions.TooManyRedirects):
              if verbose is True:
                print(color.PURPLE +"Invalid %s" % url,color.END)
              continue
            except (requests.exceptions.ConnectionError, requests.exceptions.InvalidURL,requests.exceptions.ConnectTimeout,requests.exceptions.HTTPError):
              if verbose is True:
                print(color.BOLD,color.RED +"Broken %s" % url, color.END)
              broken_urls.add(url)
              continue
            
            parts = urlsplit(url)
            base = "{0.netloc}".format(parts)
            strip_base = base.replace("www.", "")
            base_url = "{0.scheme}://{0.netloc}".format(parts)
            path = url[:url.rfind('/')+1] if '/' in parts.path else url

            soup = BeautifulSoup(response.text, "lxml")

            for link in soup.find_all('a'):

                anchor = link.attrs["href"] if "href" in link.attrs else ''

                if anchor.startswith('/'):
                    local_link = base_url + anchor
                    local_urls.add(local_link)
                elif strip_base in anchor:
                    local_urls.add(anchor)
                elif not anchor.startswith('http'):
                    local_link = path + anchor
                    local_urls.add(local_link)
                else:
                  external_urls.add(anchor)
                  check_broken(anchor,url)

                  
            for i in local_urls:
                if not i in new_urls and not i in processed_urls:
                    new_urls.append(i)

        print()
        if outfile is not None:
          return report_file(outfile, processed_urls, local_urls, external_urls, broken_urls)
        else:
          return report(local_urls, external_urls, broken_urls)

    
    except KeyboardInterrupt:
        sys.exit()

def check_domain(domain):
    try:
      url = ("https://domainr.com/?q=" + domain)
      response = requests.get(url,timeout=5)
      soup = BeautifulSoup(response.text, "lxml")
      res = str(soup.find("div", { "class" : "domain-status" }))

      if "Available" not in res:
        print(domain + color.RED  +  ' --> Taken',color.END)
      elif "Taken" not in res:
        print(domain + color.BLUE  + ' --> Available',color.END)
      else:
        print ('Something goes wrong with Domainer *-*')
    except Exception as e:
      print (e)
      pass
        

def check_broken(url,url_origin):
    try:
      response = requests.get(url,timeout=5)
    except (requests.exceptions.InvalidSchema,requests.exceptions.MissingSchema,requests.exceptions.ReadTimeout,requests.exceptions.Timeout,requests.exceptions.TooManyRedirects):
      if verbose is True:
        print(color.BOLD,color.GREEN +"Origin %s" % url_origin, color.END)
        print(color.PURPLE +"Invalid %s" % url,color.END)
      pass
    except (requests.exceptions.ConnectionError, requests.exceptions.InvalidURL,requests.exceptions.ConnectTimeout,requests.exceptions.HTTPError):
      if takeover is True:
        domain = url.split("//")[-1].split("/")[0].split('?')[0].replace("www.", "")
        if not domain in domains:
          print(color.BOLD,color.GREEN +"Origin %s" % url_origin, color.END)
          domains.add(domain)
          check_domain(domain)
      else:
        print(color.BOLD,color.GREEN +"Origin %s" % url_origin, color.END)
        print(color.BOLD,color.RED +"Broken %s" % url, color.END)
      pass
    except Exception as e:
      print(e)
      pass
		

def report_file(outfile, processed_urls, local_urls, external_urls, broken_urls):
    with open(outfile, 'w') as f:
        print(
            "--------------------------------------------------------------------", file=f)
        print("Local URLs:", file=f)
        for j in local_urls:
            print(j, file=f)
        print(
            "--------------------------------------------------------------------", file=f)
        print("External URLs:", file=f)
        for x in external_urls:
            print(x, file=f)
        print("--------------------------------------------------------------------", file=f)
        print("Broken URL's:", file=f)
        for z in broken_urls:
          print(z, file=f)


def report(local_urls, external_urls, broken_urls):
    if len(external_urls) > 0:
      print("External URLs:")
      for x in external_urls:
        print(x)


if args.list:	
  domain_list = filter(None, open(dlist, 'r').read().splitlines())
  for d in domain_list:
    print(color.BOLD, color.DARKCYAN, "Processing %s" % d, color.END)
    crawler(d, outfile)
else:
  crawler(domain, outfile)

