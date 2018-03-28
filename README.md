# DeadLinkChecker
A quick script for testing dead links. 

## Installation & Requirements
1. Install Python 3.5+
2. Download [`link_checker.py`](https://raw.githubusercontent.com/qwergram/DeadLinkChecker/master/link_checker.py) to a location included in your PATH
3. Download [`requirements.txt`](https://raw.githubusercontent.com/qwergram/DeadLinkChecker/master/requirements.txt) and run `pip install -r requirements.txt` in the same local directory.
3. Execute `python link_checker.py <params>` from any terminal.

## How to Use
Execute `python link_checker.py -h` to pull up the following instructions:
```
usage: link_checker.py [-h] [-output OUTPUT] [-workers WORKERS]
                       [-timeout TIMEOUT] [-verbose VERBOSE]
                       [links [links ...]]

Generate a report of a website's dead links. Make sure you have a good
connection to begin with!

positional arguments:
  links             Links to test. Seperate links by space.

optional arguments:
  -h, --help        show this help message and exit
  -output OUTPUT    Specify the path of the report (csv file) Default:
                    "./output.csv". If the file exists, then it will be
                    appended to.
  -workers WORKERS  Maximum number of threads for url requests. Default: 20
  -timeout TIMEOUT  Timeout (seconds) per request. Default: 5 (seconds)
  -verbose VERBOSE  Display debug messages. Default: False.
```

**Example Commands:**
```
python link_checker.py https://packaging.python.org/tutorials/distributing-packages/

python link_checker.py https://developer.microsoft.com/en-us/windows/iot https://developer.microsoft.com/en-us/windows/iot/GetStarted.htm -output C:\SomeLocation\SomeFile.txt

python link_checker.py https://developer.microsoft.com/en-us/windows/iot/getstarted/prototype/selectdevice -workers 1

python link_checker.py https://developer.microsoft.com/en-us/windows/iot/getstarted/prototype/gettools https://developer.microsoft.com/en-us/windows/iot/Downloads https://support.microsoft.com/en-us/help/4023474/surface-troubleshoot-surface-pen-with-single-button-on-flat-edge

python .\link_checker.py https://developer.microsoft.com/en-us/windows/iot ht
tps://developer.microsoft.com/en-us/windows/iot/GetStarted.htm https://developer.microsoft.com/en-us/windows/iot/getstar
ted/prototype/selectdevice https://developer.microsoft.com/en-us/windows/iot/getstarted/prototype/gettools https://devel
oper.microsoft.com/en-us/windows/iot/Downloads https://support.microsoft.com/en-us/help/4023474/surface-troubleshoot-sur
face-pen-with-single-button-on-flat-edge -verbose True
```