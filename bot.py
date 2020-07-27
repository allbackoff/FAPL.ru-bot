import logging
import os

import requests
from bs4 import BeautifulSoup
from telegram.ext import Updater

TOKEN = os.environ["TOKEN"]
CHANNEL_NAME = os.environ["CHANNEL_NAME"]
PORT = int(os.environ.get('PORT', 5000))

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


# Accessing articles from FAPL.ru
def list_articles():
    url = "http://fapl.ru"
    page_response = requests.get(url, timeout=5)
    page_content = BeautifulSoup(page_response.content, "html.parser")
    article_links = []
    for item in page_content.find_all('div', {'class': 'block news'}):
        article_links.append(url + item.find('a').get('href'))
    article_links.insert(0, url + page_content.find('div', {'class': 'block'}).find('a').get('href'))
    return article_links


# Checks whether there is new article and sends to channel if true
def check_for_updates(context):
    global max_id
    new_link = "http://fapl.ru/posts/" + str(max_id + 1) + "/"
    if new_link in list_articles():
        context.bot.send_message(chat_id=CHANNEL_NAME, text=new_link)
        max_id += 1
    # context.bot.send_message(chat_id=CHANNEL_NAME, text="[inline URL](http://www.example.com/)", parse_mode="MarkdownV2")


def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    # Initialize bot
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    job_queue = updater.job_queue

    # Set the id of latest article to keep track of
    global max_id
    max_id = 0
    for link in list_articles():
        article_id = int(link[21:-1])
        if article_id > max_id:
            max_id = article_id

    # Job queue for every minute
    job_queue.run_repeating(check_for_updates, 60, 5)

    # Error handler
    dp.add_error_handler(error)

    # Start the bot
    updater.start_webhook(listen="0.0.0.0", port=int(PORT), url_path=TOKEN)
    updater.bot.setWebhook('https://faplru-bot.herokuapp.com/' +
                           TOKEN)

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully
    updater.idle()


if __name__ == '__main__':
    main()
