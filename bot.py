import requests
import logging
import os
import telegram.ext
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from bs4 import BeautifulSoup

TOKEN = os.environ["TOKEN"]
PORT = int(os.environ.get('PORT', 5000))

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def start(update, context):
    update.message.reply_text('Я буду отправлять тебе посты с сайта FAPL.ru')


def help(update, context):
    update.message.reply_text('Help is not correctly set yet')


# Accessing articles from fapl.ru
def list_articles():
    url = "http://fapl.ru"
    page_response = requests.get(url, timeout=5)
    page_content = BeautifulSoup(page_response.content, "html.parser")
    article_links = []
    for item in page_content.find_all('div', {'class': 'block news'}):
        article_links.append(url + item.find('a').get('href'))
    article_links.insert(0, url + page_content.find('div', {'class': 'block'}).find('a').get('href'))
    return article_links


def check_for_updates(context):
    global max_id
    new_link = "http://fapl.ru/posts/" + str(max_id + 1) + "/"
    if new_link in list_articles():
        context.bot.send_message(chat_id="@faplrubot", text=new_link)
        max_id += 1

    # last_id = job.context
    # new_id = max_id + 1
    # new_link = "http://fapl.ru/" + str(new_id) + "/"
    # new_response = requests.get(new_link)
    # new_content = BeautifulSoup(new_response.content, 'html.parser')
    # if new_content.find('body').text.strip() != "Такой новости не существует!":
    #     context.bot.send_message(chat_id=240817442, text=new_link)
    #     max_id += 1

    # last_article = job.context
    # last_article_id = int(last_article[21:-1])
    # recent_article = list_articles()[1]
    # if last_article != recent_article:
    #     context.bot.send_message(chat_id=240817442, text=recent_article)


def send_article(update, context):
    articles = list_articles()
    update.message.reply_text(articles[1])


def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    # Initialize
    updater = Updater("TOKEN", use_context=True)
    dp = updater.dispatcher
    job_queue = updater.job_queue

    global max_id
    max_id = 0
    for link in list_articles():
        article_id = int(link[21:-1])
        if article_id > max_id:
            max_id = article_id

    # last_article = "http://fapl.ru/posts/" + str(max_id) + "/"

    job_queue.run_repeating(check_for_updates, 60, 5)



    # Command Handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("last_article", send_article))

    # Error handler
    dp.add_error_handler(error)

    # Start the bot
    # updater.start_polling()
    updater.start_webhook(listen="0.0.0.0", port=int(PORT), url_path="TOKEN")
    updater.bot.setWebhook('https://faplru-bot.herokuapp.com/' +
                           'TOKEN')

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully
    updater.idle()


if __name__=='__main__':
    main()