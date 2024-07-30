from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import time
from lxml import html
from dingtalkchatbot.chatbot import DingtalkChatbot
from datetime import datetime

# Initialize Selenium WebDriver
options = Options()
options.add_argument("--headless")
options.add_argument("--log-level=3")  # Suppress logs
driver = webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()), options=options)

def get_page(url):
    driver.get(url)
    time.sleep(5)  # Wait for the page to load
    return driver.page_source

def project_info(page_source):
    data_html = html.fromstring(page_source)
    name = data_html.xpath("/html/head/title/text()")

    # 查找第一个视频链接
    video_xpath = "/html/body/ytd-app/div[1]/ytd-page-manager/ytd-browse/ytd-two-column-browse-results-renderer/div[1]/ytd-rich-grid-renderer/div[6]/ytd-rich-grid-row[1]/div/ytd-rich-item-renderer/div/ytd-rich-grid-media/div[1]/div[3]/div[2]/h3/a"
    video = data_html.xpath(video_xpath)[0]
    title = video.xpath('.//text()')[0]
    link = 'https://www.youtube.com' + video.get('href')
    date = data_html.xpath('//*[@id="metadata-line"]/span[2]/text()')[0]

    return {
        "Name": name,
        "Title": title,
        "Link": link,
        "Published at": date
    }

def dingtalk_robot(webhook,secret, results):
    chatbot = DingtalkChatbot(webhook,secret)
    now_time = datetime.now().strftime('%Y.%m.%d %H:%M:%S')

    message = "\n\n".join(results)
    chatbot.send_markdown(
        title='当前最新视频',
        text=f'### 当前最新视频\n\n'
             f'{message}\n\n'
             f'**发送时间:**  {now_time}\n',
        is_at_all=True
    )

urls = [
    'https://www.youtube.com/@AIsuperdomain/videos',
    'https://www.youtube.com/@01coder30/videos',
    'https://www.youtube.com/@MervinPraison/videos',
    'https://www.youtube.com/@shoufu/videos',
    'https://www.youtube.com/@GiantCutie-CH/videos',
    'https://www.youtube.com/@crypto2head/videos',
    'https://www.youtube.com/@airdropvip/videos/videos'
]

results = []
for url in urls:
    page_source = get_page(url)
    info = project_info(page_source)
    result = "\n".join([f"{key}: {value}\n" for key, value in info.items()])
    results.append(result)
print(results)

driver.quit()

webhook = "https://oapi.dingtalk.com/robot/send?access_token=0f1525f004ecfaac561f6161902f0d126bc37a7cacc9dda0cd43ba9c46648e86"
secret = 'SEC14ed7e917f464a5f0e53d252374525db61f3d7ee083cce902c0cfdd8423817cf'
dingtalk_robot(webhook=webhook ,secret = secret, results=results)
