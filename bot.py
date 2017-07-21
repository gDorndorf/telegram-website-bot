from telegram.ext import Updater, CommandHandler, Job
import config_private as config
from urllib.request import urlopen
import hashlib
import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

def websiteHash(url):
    response = urlopen(url)
    html = response.read()
    return hashlib.md5(html).hexdigest()

def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="I'm a bot, please talk to me!")

def performCheck(bot, job):

    """Function to Check the Website and inform the user"""
    siteHash=websiteHash(job.context["url"])
    if not (job.context["siteHash"]==siteHash):
        bot.send_message(job.context["chat_id"], text='Es gab aenderungen'+
                         'an der Website '+job.context["url"])
        job.context["siteHash"]=siteHash
    
def set(bot, update, args, job_queue, chat_data):

    """Adds a job to the queue

    Stolen from
    https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/timerbot.py
    """

    chat_id = update.message.chat_id

    try:
        jobContext={}
        jobContext["chat_id"]=chat_id
        jobContext["url"]=args[0]
        #jobContext["siteHash"]=0
        jobContext["siteHash"]=websiteHash(jobContext["url"])
        job = job_queue.run_repeating(performCheck, 6, context=jobContext)

        chat_data['job'] = job

        update.message.reply_text('Surveillance successfully set!')

    except (IndexError, ValueError):

        update.message.reply_text('Failure! Plese use as /set <url>')

def unset(bot, update, chat_data):

    """Removes the job if the user changed their mind"""

    if 'job' not in chat_data:
        update.message.reply_text('You have no active surveillance')
        return

    job = chat_data['job']
    job.schedule_removal()
    del chat_data['job']

    update.message.reply_text('Surveillance canceled!')



def error(bot, update, error):

    logger.warning('Update "%s" caused error "%s"' % (update, error))

    
def main():

    updater = Updater(config.token)
    # Get the dispatcher to register handlers
    
    dp = updater.dispatcher

    # on different commands - answer in Telegram

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", start))
    dp.add_handler(CommandHandler("set", set,
                                  pass_args=True,
                                  pass_job_queue=True,
                                  pass_chat_data=True))
    dp.add_handler(CommandHandler("unset", unset, pass_chat_data=True))



    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
    # SIGABRT. This should be used most of the time, since start_polling() is
    # non-blocking and will stop the bot gracefully.
    updater.idle()





if __name__ == '__main__':
    main()
#start_handler = CommandHandler('start', start)
#dispatcher.add_handler(start_handler)
#updater.start_polling()
