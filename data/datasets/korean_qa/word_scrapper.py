import datetime
from collections import deque

import requests
from bs4 import BeautifulSoup
from openpyxl import Workbook


# word locater class
class WordLocator:
    def __init__(self, url: str):
        # sends get method to url -> receive requests.Response
        self._root = url
        self._wb = Workbook()
        self._locate = []
        self._located_webpages = []
        self._crawled = set(url[:-1] for url in open("./result/txt_located.txt", "r", encoding="utf-8").readlines())

    def crawl_for_word(self, start, word):
        """
        BST through web pages.
        for each web page, extract visible text,
          1. if word in page, append url to _webpages
          2. find all non-visited internal links and add to queue
        """
        sheet = self._wb.active
        sheet.append(["Instruction", "Response", "Source", "MetaData"])
        filename = f"./result/{datetime.datetime.today().strftime('%Y-%m-%d-%H-%M')}__crawled_data.xlsx"
        f_located = open("./result/txt_located.txt", "a", encoding="utf-8")

        q = deque()
        q.append(self._root + start)
        visited = set()
        visited_index = set()
        cnt = 0

        while q and cnt != 1000:
            # Search for visible text tags and locate word
            url = q.pop()
            print(url)

            if url.startswith(self._root):
                visited.add(url[len(self._root) :])
            else:
                visited.add(self._root + url)

            visited.add(url)
            webpage = requests.get(url, headers={"User-agent": "Mozilla/5.0"})
            soup = BeautifulSoup(webpage.content, "html.parser")

            # Crawl Data
            instruction = soup.find("div", class_="c-heading__content")
            title = soup.find("div", class_="title")
            if title and instruction and (word in instruction.get_text().strip() or word in title.get_text().strip()):
                print(url if url.startswith(self._root) else self._root + url)
                f_located.write(url + "\n")
                instruction = instruction.get_text().strip()
                title = title.get_text().strip()
                if not instruction[0].isnumeric():
                    responses = soup.find_all("div", class_="se-module-text")
                    for response in responses:
                        response_spans = response.find_all("span")
                        txt = ""
                        for response_span in response_spans:
                            txt += response_span.get_text()

                        print(f"============================\n{title}\n{instruction}\n\n{txt}\n\n")
                        cnt += 1
                        sheet.append([title + ". " + instruction, txt, "Naver Kin", url])
                        self._wb.save(filename)

            # find all valid neighbor and add to queue
            for link in soup.find_all("a"):
                neighbor = link.get("href")
                if neighbor and neighbor.startswith("/qna/detail.naver?d1id="):
                    neighbor = self._root + neighbor
                    # must consider relative and absolute routing.
                    if neighbor not in visited and neighbor not in self._crawled:
                        q.append(neighbor)
                elif neighbor and neighbor.startswith("/qna/list.naver?") and neighbor[-2:] not in visited_index:
                    neighbor = self._root + neighbor
                    visited_index.add(neighbor[-2:])
                    q.append(neighbor)


if __name__ == "__main__":
    word_locator = WordLocator("https://kin.naver.com")
    word_locator.crawl_for_word("/qna/list.naver", "")
