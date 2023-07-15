from __future__ import annotations

import dataclasses
import re
import time
from dataclasses import dataclass
from typing import List, Union

import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
from loguru import logger
from playwright.sync_api import Locator, Page, sync_playwright
from tqdm import tqdm


@dataclass
class Content_Data:
    question_id: int
    answer_id: int
    author_id: str
    question_title: str
    content: str
    upvotes: str
    answer_creation_time: str


def get_answer_content(qid: int, aid: int, question_str: str) -> str:
    """
    根据回答ID和问题ID获取回答内容
    Parameters
    ----------
    qid : 问题ID
    aid : 回答ID
    例如一个回答链接为: https://www.zhihu.com/question/438404653/answer/1794419766
    其 qid 为 438404653
    其 aid 为 1794419766
    注意,这两个参数均为字符串
    Return
    ------
    str : 回答内容
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1 Mobile/15E148 Safari/604.1",
        "Host": "www.zhihu.com",
    }
    url = f"https://www.zhihu.com/question/{qid}/answer/{aid}"
    response = requests.get(url, headers=headers)

    soup = BeautifulSoup(response.text, "html.parser")
    content = " ".join([p.text.strip() for p in soup.find_all("p")])
    """
    "<meta itemProp="dateCreated" content="2023-02-20T13:19:30.000Z"/>"
    last time from meta tag with item prop attributes seems to be the post creation datetime. I verified by looking at page online

    """
    answer_creation_time_div = soup.find_all(
        "meta",
        {"itemprop": "dateCreated"},
    )
    answer_creation_time_content = ""
    if len(answer_creation_time_div) > 0:
        answer_creation_time_content = answer_creation_time_div[-1].attrs["content"]
    upvotes = (
        soup.find(
            "button",
            {"class": "Button VoteButton VoteButton--up"},
        )
        .get_text()
        .replace("\u200b", "")
    )
    author_ids = soup.find_all(
        "meta",
        {"itemprop": "url"},
    )
    author_id_div = [x for x in author_ids if "/people/" in x.attrs["content"]]
    author_id = author_id_div[0].attrs["content"]
    return Content_Data(
        question_id=qid,
        answer_id=aid,
        author_id=author_id,
        question_title=question_str,
        content=content,
        upvotes=upvotes,
        answer_creation_time=answer_creation_time_content,
    )


def get_all_href(page: Union[Page, Locator]) -> List[str]:
    hrefs = page.evaluate(
        """() => {
            let links = document.querySelectorAll('[href]');
            let hrefs = [];
            for (let link of links) {
                hrefs.push(link.href);
            }
            return hrefs;
        }"""
    )
    valid_hrefs = [x for x in hrefs if isinstance(x, str) and "https://" in x]
    return valid_hrefs


"""
Scrape people from round table topics. Save a list of zhihu people profile url to csv
"""


def scrape_people_roundtable():
    headless = False
    all_ppl_df = pd.DataFrame()
    roundtable_topic_scrolldown = 20
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless, timeout=60000)
        page = browser.new_page()
        page.goto("https://zhihu.com/roundtable")
        # Scroll down roundtable topic to get more topic urls
        for _ in range(roundtable_topic_scrolldown):
            page.keyboard.down("End")
            page.wait_for_timeout(1000)

        hrefs = get_all_href(page)
        relevent_hrefs = [x for x in hrefs if "https://www.zhihu.com/roundtable/" in x]
        np.random.shuffle(relevent_hrefs)
        # Earlier round table topic might not have started yet. The offset roundtable topic is arbitrary.

        starting_offset = 4
        for topic_url in tqdm(relevent_hrefs[starting_offset:]):
            try:
                page.goto(topic_url)
                all_hrefs = get_all_href(page)
                people_urls = [x for x in all_hrefs if "/people/" in x]
                latest_people_id = pd.DataFrame({"people_id": people_urls})
                all_ppl_df = pd.concat([all_ppl_df, latest_people_id])
            except Exception as e1:
                logger.error(e1)

            all_ppl_df.to_csv("people.csv")


"""
End to end auto scrape topics from round table
"""


def end_to_end_auto_scrape():
    headless = False
    pattern = r"/question/\d+/answer/\d+"
    all_payloads = []
    roundtable_topic_scrolldown = 20
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless, timeout=60000)
        page = browser.new_page()
        page.goto("https://zhihu.com/roundtable")
        # Scroll down roundtable topic to get more topic urls
        for _ in range(roundtable_topic_scrolldown):
            page.keyboard.down("End")
            page.wait_for_timeout(1000)

        hrefs = get_all_href(page)
        relevent_hrefs = [x for x in hrefs if "https://www.zhihu.com/roundtable/" in x]
        np.random.shuffle(relevent_hrefs)
        # Earlier round table topic might not have started yet. The offset roundtable topic is arbitrary.

        starting_offset = 4
        for topic_url in tqdm(relevent_hrefs[starting_offset:]):
            try:
                page.goto(topic_url)
                all_hrefs = get_all_href(page)
                question_urls = set([x for x in all_hrefs if "/question/" in x and "waiting" not in x])
                # people_urls = [x for x in all_hrefs if "/people/" in x]
                for qId in question_urls:
                    qUrl = qId.replace("?write", "")

                    page.goto(qUrl)
                    question_title = page.locator(".QuestionHeader-title").all_inner_texts()[0]
                    all_hrefs = get_all_href(page.locator(".QuestionAnswers-answers"))
                    # search for all question-answer url
                    matches_question_answer_url = set(
                        [s for s in all_hrefs if isinstance(s, str) and re.search(pattern, s)]
                    )

                    for k in matches_question_answer_url:
                        elem = k.split("/")
                        qId = int(elem[-3])
                        aId = int(elem[-1])

                        complete_content_data = get_answer_content(qId, aId, question_title)

                        content_data_dict = dataclasses.asdict(complete_content_data)
                        all_payloads.append(content_data_dict)
                        time.sleep(1)
            except Exception as e1:
                logger.error(e1)
            tmp_df = pd.json_normalize(all_payloads)
            print(tmp_df)
            tmp_df.to_csv("zhihu.csv")


if __name__ == "__main__":
    # scrape_people_roundtable()
    end_to_end_auto_scrape()
