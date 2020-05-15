# BroJack
Slow but very solid tool that checks for Broken Links Hijack.

![Image description](https://raw.githubusercontent.com/xlocux/brojack/master/brojack.png)

I've created circa 30 reports during the quarantine almost all P4.

![Bugcrowd reports](https://raw.githubusercontent.com/xlocux/brojack/master/reports.png)



-----------------------------------------------------------------------

## Installation:

$ git clone https://github.com/xlocux/brojack.git

$ cd brojack

$ pip install -r requirements.txt

------------------------------------------------------------------------


## Usage:

usage: brojack.py [-h] [--domain DOMAIN] [--list LIST] [--outfile OUTFILE] [--mobile] [--takeover] [--verbose]

eg: python brojack.py -l domainlist

Broken Link Hijack (BroJack) by Locu

optional arguments:
  -h, --help            show this help message and exit
  
  --domain DOMAIN, -d DOMAIN
                        Domain name of website you want to map. i.e. "https://github.com/xlocux"
                        
  --list LIST, -l LIST  Process a list of domains/urls from an input file
  
  --outfile OUTFILE, -o OUTFILE
                        Define output file to save results of stdout. i.e. "test.txt"
                        
  --mobile, -m          Change User-Agent to android mobile
  
  --takeover, -t        Check if domain is available
  
  --verbose, -v         Show verbose info


## ToDo:

MultiThreading



  ------------------------------------------------------------------------
  

