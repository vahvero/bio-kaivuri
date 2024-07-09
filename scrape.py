from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
from urllib.error import HTTPError
from urllib.request import urlopen
import json
import logging
import time
import sys

__date__ = "2024-07-09"
__author__ = "github.com/vahvero"

stream_handler = logging.StreamHandler(sys.stderr)
file_handler = logging.FileHandler(filename="scrape.log")


stream_handler.setLevel(logging.WARNING)
file_handler.setLevel(logging.INFO)

logging.basicConfig(
    handlers=(stream_handler, file_handler),
    level=logging.DEBUG,
)

logger = logging.getLogger(__name__)


BASE_URL = "https://healthtech.teknologiateollisuus.fi"
"""URL source target"""


class CompanyListParser(HTMLParser):
    """Parses companies from source"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__company_urls = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            elem = attrs[0]
            if elem[0] == "href" and elem[1].startswith("/fi/jasenet/jasenluettelo/"):
                self.__company_urls.append(BASE_URL + attrs[0][1])

    @property
    def company_urls(self):
        return self.__company_urls


class CompanyPageParser(HTMLParser):
    """Parses company keywords from company page"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.handle_next = False
        self.__keywords = []

    @property
    def keywords(self):
        return self.__keywords

    def handle_data(self, data):
        if data == "Avainsanat":
            self.handle_next = True
            return

        if self.handle_next and len(data) > 12:
            out = data.replace(": ", "").split(",")
            out = list(
                filter(
                    lambda x: x != "",
                    map(
                        lambda x: x.replace("\\xc3\\xa4", "ä")
                        .replace("\\xc3\\xb6", "ö")
                        .replace("\\xc2\\xa0", "")
                        .replace("xc2\\xa0", "")
                        .strip(),
                        out,
                    ),
                )
            )
            self.__keywords = out
            self.handle_next = False

    def reset(self):
        self.handle_next = False
        self.__keywords = []
        super().reset()


def parse_company_page(url):
    urlparser = CompanyPageParser()
    logger.info("Requesting %s", url)
    company_name = url
    try:
        response = urlopen(url)
        urlout = response.read()
        urlparser.feed(str(urlout))
    except HTTPError as exp:
        logger.error(f"Error requesting %s: '%s'", url, exp)
        return None
    return company_name, tuple(urlparser.keywords)


if __name__ == "__main__":
    parser = CompanyListParser()
    with urlopen(BASE_URL + "/fi/jasenet-members-0") as response:

        parser.feed(str(response.read()))

    start = time.perf_counter()
    with ThreadPoolExecutor() as executor:
        results = executor.map(parse_company_page, parser.company_urls)
        out = {elem[0]: elem[1] for elem in results if elem}

    end = time.perf_counter()
    logger.critical("Executed thread scrape in: %.2fs", end - start)

    with open("company_kw.json", "w") as fobj:
        json.dump(
            out,
            fobj,
            ensure_ascii=False,
        )
