#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Broken Link Hijack (BroJack)
# By Locu

import sys
import os
import subprocess
import importlib.util

# Function to check if a package is installed
def is_package_installed(package_name):
    spec = importlib.util.find_spec(package_name)
    return spec is not None

# Check and install required dependencies
required_packages = {
    'beautifulsoup4': 'bs4',
    'requests': 'requests',
    'colorama': 'colorama',
    'tldextract': 'tldextract',
    'lxml': 'lxml'
}

missing_packages = []
for package, import_name in required_packages.items():
    if not is_package_installed(import_name):
        missing_packages.append(package)

if missing_packages:
    print("Installing missing dependencies:", ", ".join(missing_packages))
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_packages)
        print("Dependencies installed successfully!")
    except Exception as e:
        print(f"Error installing dependencies: {e}")
        print("Please install the following packages manually:")
        for pkg in missing_packages:
            print(f"  pip install {pkg}")
        sys.exit(1)

from bs4 import BeautifulSoup
import requests
import requests.exceptions
from urllib.parse import urlsplit
from urllib.parse import urlparse
from collections import deque
from colorama import Fore, Style
import tldextract
import re
import argparse
from datetime import datetime
import threading
import queue
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

class Color:
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

class BroJack:
    def __init__(self):
        self.broken_urls = set()
        self.external_urls = set()
        self.local_urls = set()
        self.processed_urls = set()
        self.domains = set()
        self.exclusion = set()
        self.url_queue = queue.Queue()
        self.lock = threading.Lock()
        self.tf = datetime.now().strftime("%d-%m-%Y_%I-%M-%S_%p")
        
        # Parse arguments
        self.parse_arguments()
        
        # Load exclusions if needed
        if self.exclusions:
            with open('exclusions.dat') as file:
                self.exclusion = [i.strip() for i in file]
    
    def parse_arguments(self):
        motd = 'Broken Link Hijack (BroJack) by Locu '
        parser = argparse.ArgumentParser(description=motd)
        parser.add_argument('--domain', '-d', help='Domain name of website you want to map. i.e. "https://github.com/xlocux"')
        parser.add_argument('--list', '-l', help='Process a list of urls from an input file')
        parser.add_argument('--outfile', '-o', help='Define output file to save available domain, -t flag required')
        parser.add_argument('--mobile', '-m', action="store_true", help='Change User-Agent to android mobile')
        parser.add_argument('--takeover', '-t', action="store_true", help='Check if domain is available')
        parser.add_argument('--exclusions', '-x', action='store_true', help='Use exclusions domains list')
        parser.add_argument('--verbose', '-v', action="store_true", help='Show verbose info')
        parser.add_argument('--threads', '-th', type=int, default=10, help='Number of threads to use (default: 10)')
        
        if len(sys.argv) < 2:
            print('eg: python %s -l domainlist' % sys.argv[0])
            args = parser.parse_args(['-h'])
        else:
            args = parser.parse_args()
        
        self.domain = args.domain
        self.dlist = args.list
        self.outfile = args.outfile
        self.mobile = args.mobile
        self.takeover = args.takeover
        self.exclusions = args.exclusions
        self.verbose = args.verbose
        self.threads = args.threads
        
        # Print configuration
        self.print_config()
    
    def print_config(self):
        if self.domain:
            print(Color.BOLD + "Domain:", Color.YELLOW, self.domain, Color.END)
        if self.dlist:
            print(Color.BOLD + "Domain list file:", Color.YELLOW, self.dlist, Color.END)
        if self.outfile:
            print(Color.BOLD + "Output file:", Color.YELLOW, self.outfile, Color.END)
        if self.mobile:
            print(Color.BOLD + "User Agent Mobile:", Color.YELLOW, self.mobile, Color.END)
        if self.takeover:
            print(Color.BOLD + "Takeover Check:", Color.YELLOW, self.takeover, Color.END)
        if self.exclusions:
            print(Color.BOLD + "Exclusion List:", Color.YELLOW, self.exclusions, Color.END)
        if self.verbose:
            print(Color.BOLD + "Verbose:", Color.YELLOW, self.verbose, Color.END)
        print(Color.BOLD + "Threads:", Color.YELLOW, self.threads, Color.END)
        print()
    
    def get_user_agent(self):
        if self.mobile:
            return {'User-Agent': 'Mozilla/5.0 (Linux; Android 9; SM-G960F Build/PPR1.180610.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/74.0.3729.157 Mobile Safari/537.36'}
        else:
            return {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'}
    
    def process_url(self, url):
        if url in self.processed_urls:
            return
        
        with self.lock:
            self.processed_urls.add(url)
        
        try:
            response = requests.get(url, headers=self.get_user_agent(), timeout=5)
            
            parts = urlsplit(url)
            base = "{0.netloc}".format(parts)
            strip_base = base.replace("www.", "")
            base_url = "{0.scheme}://{0.netloc}".format(parts)
            path = url[:url.rfind('/')+1] if '/' in parts.path else url
            
            soup = BeautifulSoup(response.text, "lxml")
            
            new_local_urls = set()
            for link in soup.find_all('a'):
                anchor = link.attrs["href"] if "href" in link.attrs else ''
                
                if anchor.startswith('/'):
                    local_link = base_url + anchor
                    new_local_urls.add(local_link)
                elif strip_base in anchor:
                    new_local_urls.add(anchor)
                elif not anchor.startswith('http'):
                    local_link = path + anchor
                    new_local_urls.add(local_link)
                else:
                    with self.lock:
                        self.external_urls.add(anchor)
                    self.check_broken(anchor, url)
            
            with self.lock:
                for local_url in new_local_urls:
                    if local_url not in self.processed_urls and local_url not in self.local_urls:
                        self.local_urls.add(local_url)
                        self.url_queue.put(local_url)
            
        except (requests.exceptions.InvalidSchema, requests.exceptions.MissingSchema, 
                requests.exceptions.ReadTimeout, requests.exceptions.Timeout, 
                requests.exceptions.TooManyRedirects, requests.exceptions.ChunkedEncodingError):
            if self.verbose:
                print(Color.PURPLE + "Invalid %s" % url, Color.END)
        except (requests.exceptions.ConnectionError, requests.exceptions.InvalidURL, 
                requests.exceptions.ConnectTimeout, requests.exceptions.HTTPError):
            if self.verbose:
                print(Color.BOLD, Color.RED + "Broken %s" % url, Color.END)
            with self.lock:
                self.broken_urls.add(url)
        except Exception as e:
            print(f"Error processing {url}: {str(e)}")
    
    def check_domain(self, domain, url_origin):
        try:
            url = ("https://domainr.com/?q=" + domain)
            response = requests.get(url, timeout=5)
            soup = BeautifulSoup(response.text, "lxml")
            res = str(soup.find("div", {"class": "domain-status"}))
            
            if "Available" not in res:
                print(domain + Color.RED + ' --> Taken', Color.END)
            elif "Taken" not in res:
                print(domain + Color.BLUE + ' --> Available', Color.END)
                if self.outfile is not None:
                    with self.lock:
                        with open(self.outfile + self.tf, 'a') as f:
                            f.write("Origin: " + url_origin + "\n Domain: " + domain + "\n")
            else:
                print('Something goes wrong with Domainer *-*')
        except Exception as e:
            print(e)
    
    def check_broken(self, url, url_origin):
        try:
            response = requests.get(url, timeout=5)
        except (requests.exceptions.InvalidSchema, requests.exceptions.MissingSchema, 
                requests.exceptions.ReadTimeout, requests.exceptions.Timeout, 
                requests.exceptions.TooManyRedirects, requests.exceptions.ChunkedEncodingError):
            if self.verbose:
                print(Color.BOLD, Color.GREEN + "Origin %s" % url_origin, Color.END)
                print(Color.PURPLE + "Invalid %s" % url, Color.END)
        except (requests.exceptions.ConnectionError, requests.exceptions.InvalidURL, 
                requests.exceptions.ConnectTimeout, requests.exceptions.HTTPError):
            if self.takeover:
                dextract = tldextract.extract(url)
                domain = "{}.{}".format(dextract.domain, dextract.suffix)
                
                with self.lock:
                    if domain not in self.domains:
                        if self.exclusions:
                            if domain not in self.exclusion:
                                print(Color.BOLD, Color.GREEN + "Origin %s" % url_origin, Color.END)
                                self.domains.add(domain)
                                self.check_domain(domain, url_origin)
                            elif self.verbose:
                                print(Color.BOLD, Color.RED + "Excluded %s" % domain, Color.END)
                        else:
                            print(Color.BOLD, Color.GREEN + "Origin %s" % url_origin, Color.END)
                            self.domains.add(domain)
                            self.check_domain(domain, url_origin)
            else:
                print(Color.BOLD, Color.GREEN + "Origin %s" % url_origin, Color.END)
                print(Color.BOLD, Color.RED + "Broken %s" % url, Color.END)
        except Exception as e:
            print(e)
    
    def crawler(self, domain):
        try:
            # Initialize with the starting domain
            self.url_queue.put(domain)
            
            # Create thread pool
            with ThreadPoolExecutor(max_workers=self.threads) as executor:
                futures = []
                
                # Process URLs until queue is empty
                while True:
                    try:
                        # Get URLs from queue with timeout to check if we're done
                        try:
                            url = self.url_queue.get(timeout=1)
                            future = executor.submit(self.process_url, url)
                            futures.append(future)
                        except queue.Empty:
                            # Check if all futures are done and queue is empty
                            if all(future.done() for future in futures) and self.url_queue.empty():
                                break
                            continue
                    except KeyboardInterrupt:
                        print("\nCrawling interrupted by user.")
                        break
            
            print("\nCrawling completed.")
            self.report()
            
        except KeyboardInterrupt:
            print("\nCrawling interrupted by user.")
            sys.exit()
    
    def report(self):
        if len(self.external_urls) > 0:
            print("External URLs:")
            for x in self.external_urls:
                print(x)
    
    def run(self):
        if self.dlist:
            domain_list = filter(None, open(self.dlist, 'r').read().splitlines())
            for d in domain_list:
                print(Color.BOLD, Color.DARKCYAN, "Analyzing %s" % d, Color.END)
                # Reset sets for each domain
                self.broken_urls = set()
                self.external_urls = set()
                self.local_urls = set()
                self.processed_urls = set()
                self.domains = set()
                self.url_queue = queue.Queue()
                self.crawler(d)
        else:
            self.crawler(self.domain)

if __name__ == "__main__":
    brojack = BroJack()
    brojack.run()

