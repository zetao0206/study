import requests
from lxml import html
from datetime import datetime
import psycopg2
from psycopg2 import sql
from dingtalkchatbot.chatbot import DingtalkChatbot

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
    price = data_html.xpath('//*[@id="main-banner"]/div/div[2]/div[1]/div[1]/span/text()')


    return {
        "bitcoin_price": price
    }

#store Bitcoin price in the PostgreSQL database
def datasaving(info):
    if not info["bitcoin_price"]:
        print("No price information available to store.")
        return None

    price = info["bitcoin_price"]
    timestamp = datetime.now()

    # Connect to the database
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    cursor = conn.cursor()

    # Insert the data
    insert_query = "INSERT INTO bitcoin_prices (price, timestamp) VALUES (%s, %s)"
    cursor.execute(insert_query, (price, timestamp))
    
    # Commit the transaction and close the connection
    conn.commit()
    cursor.close()
    conn.close()

    print(f"Inserted Bitcoin price: ${price} at {timestamp}")


def post_to_dingtalk(webhook, secret, message):
    chatbot = DingtalkChatbot(webhook, secret)
    now_time = datetime.now().strftime('%Y.%m.%d %H:%M:%S')

    chatbot.send_markdown(
        title='Hourly Bitcoin Price',
        text=f'### 比特币价格最新消息\n\n'
             f'{message}\n\n'
             f'**发送时间:**  {now_time}\n',
        is_at_all=True
    )


url = "https://bitcoinprices.org/"
page = get_page(url)
message = ""
info = project_info(page)
for key,value in info.items():
    now_time = datetime.now().strftime('%Y.%m.%d %H:%M:%S')
    print(f"{key}:{value} Current Time:" + now_time +"\n")
    message += "\n".join([f"比特币价格:{value}\n" for value in info.items()])



# Database connection parameters
DB_NAME = "bitcoin" 
DB_USER = "postgres" 
DB_PASSWORD = "5119"
DB_HOST = "localhost"  
DB_PORT = "5432"  

#send data to database
datasaving(info)
webhook = "https://oapi.dingtalk.com/robot/send?access_token=0f1525f004ecfaac561f6161902f0d126bc37a7cacc9dda0cd43ba9c46648e86"
secret = 'SEC14ed7e917f464a5f0e53d252374525db61f3d7ee083cce902c0cfdd8423817cf'
post_to_dingtalk(webhook, secret, message)