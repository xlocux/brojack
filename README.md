# BroJack

A powerful and reliable tool for detecting Broken Link Hijacking vulnerabilities. BroJack now features multithreading for significantly improved performance!

![BroJack Tool](https://raw.githubusercontent.com/xlocux/brojack/master/brojack.png)

During the quarantine period, I created approximately 30 vulnerability reports using this tool, most of which were rated P4.

![Bugcrowd reports](https://raw.githubusercontent.com/xlocux/brojack/master/reports.png)

## What is Broken Link Hijacking?

Broken Link Hijacking (BLH) occurs when a website links to an external domain that has expired or is no longer registered. Attackers can register these domains and potentially serve malicious content to users who click on these broken links.

## Features

- Multithreaded scanning for faster performance
- Automatic dependency installation
- Domain availability checking
- Mobile user-agent spoofing
- Exclusion list support
- Detailed verbose output
- Process multiple domains from a list

-----------------------------------------------------------------------

## Installation:

```bash
git clone https://github.com/xlocux/brojack.git
cd brojack
pip install -r requirements.txt
```

The tool will also automatically install any missing dependencies when run.

------------------------------------------------------------------------

## Usage:

```
usage: brojack.py [-h] [--domain DOMAIN] [--list LIST] [--outfile OUTFILE]
                  [--mobile] [--takeover] [--exclusions] [--verbose]
                  [--threads THREADS]
```

### Broken Link Hijack (BroJack) by Locu

#### Optional Arguments:
  `-h, --help`            
  Show this help message and exit
  
  `--domain DOMAIN, -d DOMAIN`  
  Domain name of website you want to scan, e.g., "https://github.com/xlocux"
                        
  `--list LIST, -l LIST`  
  Process a list of URLs from an input file
  
  `--outfile OUTFILE, -o OUTFILE`  
  Define output file to save available domains (requires -t flag)
                        
  `--mobile, -m`  
  Change User-Agent to Android mobile
  
  `--takeover, -t`  
  Check if domains are available for registration
  
  `--exclusions, -x`  
  Use exclusions domains list from exclusions.dat
  
  `--verbose, -v`  
  Show detailed information during scanning
  
  `--threads THREADS, -th THREADS`  
  Number of threads to use (default: 10)

### Examples:

Scan a single domain with 20 threads:
```bash
python brojack.py -d https://example.com -t -v -th 20
```

Process a list of domains:
```bash
python brojack.py -l domain_list.txt -t -o results
```

------------------------------------------------------------------------

## Support the Project

If you find this tool useful in your bug bounty hunting or security research, consider supporting the development:

<a href="https://www.buymeacoffee.com/Locu" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-white.png" alt="Buy Me A Coffee"></a>

