import requests
from lxml import html
from dingtalkchatbot.chatbot import DingtalkChatbot
from datetime import datetime

# 获取网页内容的函数
def get_page(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response
    else:
        print("无法获取页面:", response.status_code)
        return None

# 提取项目信息的函数
def project_info(page):
    page.encoding = "utf-8"  # 设置页面编码为 UTF-8
    data_html = html.fromstring(page.text)
    
    # 提取所需部分的内容
    daily_rank_url = data_html.xpath('//ul/li/a/@href')[0]
    best_project = data_html.xpath('//blockquote/p/text()')[0]
    project_url = data_html.xpath('//ul/li/a/@href')[1]
    open_source_date = data_html.xpath('//ul/li[contains(text(), "开源时间")]/text()')[0]
    stars = data_html.xpath('//ul/li[contains(text(), "开源Stars")]/text()')[0]
    daily_growth = data_html.xpath('//ul/li[contains(text(), "日Star增长量")]/text()')[0]

    return {
        "daily_rank_url": daily_rank_url,
        "best_project": best_project,
        "project_url": project_url,
        "open_source_date": open_source_date,
        "stars": stars,
        "daily_growth": daily_growth
    }

def ranking_info(page):
    page.encoding = "utf-8"  # 设置页面编码为 UTF-8
    data_html = html.fromstring(page.text)
    rankings = []

    # Extract and format the ranking information
    for i in range(1, 21):
        if i <=3:
            rank = str(i)
        else:
            rank = data_html.xpath("//markdown-accessiblity-table/table/tbody/tr["+str(i)+"]/td[1]/text()")
        name = data_html.xpath("//markdown-accessiblity-table/table/tbody/tr["+str(i)+"]/td[3]/a/@href")
        star = data_html.xpath("//markdown-accessiblity-table/table/tbody/tr["+str(i)+"]/td[4]/text()")
        daily_increase = data_html.xpath("//markdown-accessiblity-table/table/tbody/tr["+str(i)+"]/td[5]/text()")
        weekly_increase = data_html.xpath("//markdown-accessiblity-table/table/tbody/tr["+str(i)+"]/td[6]/text()")

        # Format each ranking entry
        formatted_rank = {
            "排名": rank[0],
            "项目名": name[0],
            "星": star[0],
            "今日增长量": daily_increase[0],
            "上周增长量": weekly_increase[0]
        }
        rankings.append(formatted_rank)

    return rankings

def format_rankings(rankings):
    formatted = ""
    for rank in rankings:
        formatted += (
            f"排名: {rank['排名']}\n"
            f"项目名: {rank['项目名']}\n\n"
            f"星: {rank['星']}\n"
            f"今日增长量: {rank['今日增长量']}\n"
            f"上周增长量: {rank['上周增长量']}\n\n"
        )
    return formatted

def post_to_dingtalk(webhook, secret, message):
    chatbot = DingtalkChatbot(webhook, secret)
    now_time = datetime.now().strftime('%Y.%m.%d %H:%M:%S')

    chatbot.send_markdown(
        title='GitHub Daily Rank',
        text=f'### GitHub Daily Rank\n\n'
             f'{message}\n\n'
             f'**发送时间:**  {now_time}\n',
        is_at_all=True
    )

# 要抓取的页面 URL
url = "https://github.com/OpenGithubs/github-daily-rank"
page = get_page(url)
message = ""
if page:
    info = project_info(page)
    message += "\n".join([f"{value}\n" for key, value in info.items()])
    message += "\n\n"
    rank = ranking_info(page)
    message += format_rankings(rank)

webhook = "https://oapi.dingtalk.com/robot/send?access_token=0f1525f004ecfaac561f6161902f0d126bc37a7cacc9dda0cd43ba9c46648e86"
secret = 'SEC14ed7e917f464a5f0e53d252374525db61f3d7ee083cce902c0cfdd8423817cf'
post_to_dingtalk(webhook, secret, message)

