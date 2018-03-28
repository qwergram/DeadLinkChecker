# Norton Pengra - npengra317@gmail.com

import io
import os
import csv
import asyncio
import argparse
import requests
import concurrent.futures

from urllib.parse import urlparse
from bs4 import BeautifulSoup

VERBOSE = False


def debug(*args, **kwargs):
    if VERBOSE:
        print(*args, **kwargs)


class LinkChecker(object):

    def __init__(self, url, output, threads, timeout):
        self.timeout = timeout
        self.url = urlparse(url)
        self.domain = self.url.netloc
        self.scheme = self.url.scheme + '://'
        self.path = self.url.path
        self.links = []
        self.bad_links = []
        self.file_name = output
        self.threads = threads
        self.completed = 0

    def ping(self, path, method="get"):

        if path.startswith('#'):
            # It's the same page
            return ''
        if path.startswith('/'):
            # It's a new relative path (begins with slash)
            target = self.scheme + self.domain + path
        elif path.startswith('http://') or path.startswith('https://'):
            # It's a new link
            target = path
        elif path.startswith('javascript:'):
            # It's a JS command
            return ''
        elif path.startswith('windows-feedback'):
            # It's a windows feedback tool link
            return ''
        elif self.path.endswith('/'):
            # It's a relative path taht doesn't begin with a slash and we're in a folder
            target = self.scheme + self.domain + self.path + path
        else:
            # It's a relative path and we're in a file
            target = self.scheme + self.domain + \
                self.path[:len(self.path) - self.path[::-1].index('/')]

        target = target.strip()

        """
        Occasionally, 406ish errors will occur. The headers will prevent these errors.
        """

        headers = {
            "User-Agent": "PengraBot Accessibility Tester/1.0"
        }

        try:
            if method == "get":
                response = requests.get(
                    target, headers=headers, timeout=self.timeout)
            elif method == "head":
                response = requests.head(
                    target, headers=headers, timeout=self.timeout)
            else:
                raise Exception("Unknown verb: %s" % method)
            if response.ok:
                self.completed += 1
                debug("Done #{}:".format(self.completed), target)
                return response.text

            # Retry 404s Sometimes HEAD requests return 404s when GET requests don't.
            elif method != 'get':
                debug("Retrying #{}:".format(self.completed), target)
                return self.ping(path, 'get')

            self.bad_links.append(
                [target, response.status_code, response.reason])
        except requests.exceptions.ConnectionError as e:
            # Retry Connection
            if method != 'get':
                debug("Retrying #{}:".format(self.completed), target)
                return self.ping(path, 'get')
            self.bad_links.append([target, '', str(e)])
        except requests.exceptions.ReadTimeout as e:
            # Retry Timeouts
            if method != 'get':
                debug("Retrying #{}:".format(self.completed), target)
                return self.ping(path, 'get')
            self.bad_links.append([target, '', 'Timeout'])

        self.completed += 1
        debug("Done #{} w/ Errors:".format(self.completed), target)

        # Uncomment next line to break program upon finding bad links.
        # raise Exception("Bad link: %s [%s %s]" % (target, response.status_code, response.reason))

    def rip(self):
        self.soup = BeautifulSoup(self.ping(self.path), "lxml")
        for link in self.soup.find_all('a'):
            link = link.get('href')
            if link and link not in self.links:
                self.links.append(link)

    async def check(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.threads) as executor:
            loop = asyncio.get_event_loop()
            futures = [
                loop.run_in_executor(
                    executor,
                    self.ping,
                    link,
                    "head"
                ) for link in self.links
            ]
            for _ in await asyncio.gather(*futures):
                pass

    def report(self):
        mode = 'a' if os.path.exists(self.file_name) else 'w'
        with io.open(self.file_name, mode, newline="") as handle:
            cursor = csv.writer(handle, quoting=csv.QUOTE_ALL)
            if mode == 'w':
                cursor.writerow(["URL", "STATUS", "REASON"])
            for bad_link in self.bad_links:
                cursor.writerow(bad_link)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Generate a report of a website\'s dead links. Make sure you have a good connection to begin with!')
    parser.add_argument('links', nargs='*',
                        help='Links to test. Seperate links by space.')
    parser.add_argument('-output', default="output.csv",
                        help='Specify the path of the report (csv file) Default: "./output.csv". If the file exists, then it will be appended to.')
    parser.add_argument('-workers', default=20, type=int,
                        help='Maximum number of threads for url requests. Default: 20')

    parser.add_argument('-timeout', default=5.0, type=float,
                        help='Timeout (seconds) per request. Default: 5 (seconds)')
    parser.add_argument('-verbose', default=False, type=bool,
                        help='Display debug messages. Default: False.')

    args = parser.parse_args()
    VERBOSE = args.verbose

    loop = asyncio.get_event_loop()

    for link in args.links:
        handle = LinkChecker(link, args.output, args.workers, args.timeout)
        handle.rip()
        loop.run_until_complete(handle.check())
        handle.report()
