# Dataset Card for Zhihu KOL Question Answering

## Dataset Description

This dataset is prepared to train Open Assistant with Chinese most popular
Question Answering website [Zhihu](https://www.zhihu.com/). So far, only the QA
from KOL (Key Opinion Leader) are recorded and prepared. Later on, we will
expand to other general topics.

### Example:

```
Q: ChatGPT 这个项目会开源吗？
A: 别开源了，开源就有中国名字了: HarmonyGPT.2014年6月21日，特斯拉公司在全球范围内公开了271项专利，其中发明专利263项。随即，2014年7月23日，乐视汽车成立；2014年11月, 蔚来汽车成立；2015年1月9日, 小鹏汽车成立；2015年7月, 理想汽车成立.

Q: TensorFlow 真的要被 PyTorch 比下去了吗？
A: 当我找到一个tf的代码，我的第一反应就是这货大概率跑不起来.

```

### Source data:

The source of QA is from some KOL found on Zhihu website. So far there is no
rule determining who should be included and who should not. We plan to gradually
bring in more KOLs into this dataset.

### How to download data and upload it to Huggingface:

### Install requirements

`pip install -r requirements.txt`

### Install Playwright [headless browser](https://playwright.dev/python/docs/intro)

`playwright install`

Run the following commands to install necessary library if needed
`sudo apt-get install libatk1.0-0 libatk-bridge2.0-0 libcups2 libatspi2.0-0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libxkbcommon0 libpango-1.0-0 libcairo2 libasound2`

### Download data based on single KOL url token

`python main.py`

### Download data based on roundtable topics

`python scrape_by_topic.py`

### Convert to Parquet

`python convert_parquet.py`

### Upload to HF

`python upload_hf.py`

Special thanks to MLMonkATGY for providing the end_to_end_auto_scrape script.
