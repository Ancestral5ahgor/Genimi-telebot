import os
import traceback
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import google.generativeai as genai
#from IPython.display import display
#from IPython.display import Markdown
from telegram.ext import InlineQueryHandler
from telegram import InlineQueryResultArticle, InputTextMessageContent


# 你的 Telegram Bot API Token
TELEGRAM_BOT_TOKEN = ''

# 你的 Gemini API Token
GEMINI_API_TOKEN = ''

# 初始化 Telegram bot 客户端
updater = Updater(token=TELEGRAM_BOT_TOKEN, use_context=True, request_kwargs={'connect_timeout': 10, 'read_timeout': 10})
dispatcher = updater.dispatcher

# 加载 .env 文件中的环境变量
load_dotenv('.env')

#os.environ["http_proxy"] = "http://127.0.0.1:10809"
#os.environ["https_proxy"] = "http://127.0.0.1:10809"
#os.environ["all_proxy"] = "socks5://127.0.0.1:10809"

# 配置 genai
genai.configure(api_key=GEMINI_API_TOKEN)

# 创建 GenerativeModel 实例
model = genai.GenerativeModel('gemini-pro')
chat = model.start_chat(history=[])

# 处理 /start 命令
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('欢迎使用Gemini机器人！发送任何消息获取Gemini API的回复。')

# 处理用户消息
def handle_message(update: Update, context: CallbackContext) -> None:
    user_message = update.message.text

    # 获取消息发送者的 ID 和聊天 ID
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id

    # 使用 Gemini API 生成回复
    gemini_response = get_gemini_response(user_message)

    # 将 Gemini API 的回复发送给用户
    #update.message.reply_text(gemini_response)
    # 检查消息是否在群组聊天中发送
    if chat_id < 0:  # chat_id 小于 0 表示是群组
        # 使用 reply_to_message() 方法回复消息
        update.message.reply_text(
            gemini_response,
            parse_mode='HTML',  # 增加 parse_mode 参数
            reply_to_message_id=update.message.message_id,
        )
    else:
        update.message.reply_text(gemini_response)


# 处理群组中通过 @机器人 提到的消息
def handle_inline_query(update: Update, context: CallbackContext) -> None:
    query = update.inline_query.query
    if not query:
        return

    # 使用 Gemini API 生成回复
    gemini_response = get_gemini_response(query)

    # 在群组中回复提到机器人的消息
    update.inline_query.answer([
        InlineQueryResultArticle(
            id='1',
            title='Gemini Response',
            input_message_content=InputTextMessageContent(gemini_response),
        )
    ])

# 添加 InlineQuery 处理程序
inline_query_handler = InlineQueryHandler(handle_inline_query)
dispatcher.add_handler(inline_query_handler)

# 获取 Gemini API 的回复
def get_gemini_response(user_message: str) -> str:
    global chat

    try:
        # 发送用户输入的消息
        response = chat.send_message(user_message, safety_settings=[
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
        ])

        # 返回模型生成的回复
        return response.text
    except Exception as e:
        # 打印详细的错误信息
        traceback.print_exc()

        # 返回更具体的错误信息
        return f"An error occurred while processing your request: {str(e)}"

# 添加命令处理程序
start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

# 添加消息处理程序
message_handler = MessageHandler(Filters.text & ~Filters.command, handle_message)
dispatcher.add_handler(message_handler)

# 启动 Telegram bot 客户端
updater.start_polling()

# 保持运行
updater.idle()
