import requests
import os
import pathlib
import textwrap
import google.generativeai as genai

from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from dotenv import load_dotenv
from IPython.display import display
from IPython.display import Markdown


def to_markdown(text):
  text = text.replace('•', '  *')
  return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

# 你的 Telegram Bot API Token
TELEGRAM_BOT_TOKEN = '6629240655:AAFhcqgyO-sPw8zat08zUTLj65jJeBUicHY'

# 你的 Gemini API Token
GEMINI_API_TOKEN = 'AIzaSyBaLoVDMAGNMHYbZYJz37w8MUgojKnFvjQ'

# 加载 .env 文件中的环境变量
load_dotenv('.env')

os.environ["http_proxy"] = "http://127.0.0.1:10809"
os.environ["https_proxy"] = "http://127.0.0.1:10809"
os.environ["all_proxy"] = "socks5://127.0.0.1:10809"

# 配置 genai
genai.configure(api_key=GEMINI_API_TOKEN)

#available Gemini models:gemini-pro/gemini-pro-vision
#for m in genai.list_models():
#  if 'generateContent' in m.supported_generation_methods:
#    print(m.name)

# 创建 GenerativeModel 实例
model = genai.GenerativeModel('gemini-pro')
chat = model.start_chat(history=[])
chat

# 对话循环
while True:
    # 获取用户输入并发送消息
    user_input = input("用户：")  # 在本地运行时，可以手动输入用户的消息
    if user_input.lower() == "exit":
        print("对话结束。")
        break  # 如果用户输入"exit"，则结束对话循环
    response = chat.send_message(user_input)

    # 打印模型生成的回复
    print("模型回复：", response.text)