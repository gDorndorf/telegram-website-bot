from telegram.ext import Updater, CommandHandler, RegexHandler, Job
import config_private as config
from urllib.request import urlopen
import hashlib
import logging
import pickle
import os.path
import string
import random
import time
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

dataFile="data.pkl"
data = {}
data["admin_id"] = -1
data["job_data"] = {}
data["update_time"] = 60*5 #in Seconds
jobs = {}
admin_token=''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
def save_obj(obj, name ):
    with open(name, 'w+b') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)
        
def load_obj(name ):
    with open(name, 'rb') as f:
        return pickle.load(f)

def saveData():
    save_obj(data, dataFile)
    
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
    else:
        bot.edit_message_text(text="Last Checked "+time.strftime("%A %d. %b %Y, %H:%M:%S %Z"),chat_id=job.context["chat_id"],message_id=job.context["message_id"])
    
def set(bot, update, args, job_queue):

    """Adds a job to the queue

    Stolen from
    https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/timerbot.py
    """

    chat_id = update.message.chat_id

    if update.message.chat_id in jobs:
        update.message.reply_text('You have an active surveillance, please cancel first')
        return
    
    try:
        jobContext={}
        jobContext["chat_id"]=chat_id
        jobContext["url"]=args[0]
        #jobContext["siteHash"]=0
        jobContext["siteHash"]=websiteHash(jobContext["url"])
        jobContext["message_id"]=-1
        print("Set surveillance for url "+jobContext["url"]+" for user "+update.effective_user.username)
        job = job_queue.run_repeating(performCheck, data["update_time"], context=jobContext)
        data["job_data"][chat_id]=jobContext
        jobs[chat_id] = job
        update.message.reply_text('Surveillance successfully set!')
        jobContext["message_id"]=update.message.reply_text("Surveillance set up at "+time.strftime("%A %d. %b %Y, H:%M:%S %Z")).message_id
        saveData()
    except (IndexError, ValueError):
        update.message.reply_text('Failure! Plese use as /set <url>')

def admin(bot, update, job_queue):
    global data
    global admin_token
    chat_id=update.message.chat_id
    if data["admin_id"]==-1:
        if update.message.text==("admin verify "+admin_token):
            data["admin_id"]=update.message.chat_id
            update.message.reply_text("Success, you are now __ADMIN__\n\nI am at your command.")
            return
    if data["admin_id"]==chat_id:
        update.message.reply_text("Hello __ADMIN__!")
    else:
        update.message.reply_text("Nice trym but you are not __ADMIN__!\nThis incient will be reportet!")
        
def unset(bot, update):
    """Removes the job if the user changed their mind"""
    if update.message.chat_id not in jobs:
        update.message.reply_text('You have no active surveillance')
        return

    job = jobs[update.message.chat_id]
    job.schedule_removal()
    del jobs[update.message.chat_id]
    del data["job_data"][update.message.chat_id]

    update.message.reply_text('Surveillance canceled!')
    saveData()


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
                                  pass_job_queue=True))
    dp.add_handler(CommandHandler("unset", unset))
    dp.add_handler(RegexHandler("admin", admin,
                                  pass_job_queue=True))

    
    # log all errors
    dp.add_error_handler(error)
    if os.path.isfile(dataFile):
        global data
        data=load_obj(dataFile)
        print("Load jobs for UserIds:")
        for chat_id, jobDat in data["job_data"].items():
            print(chat_id)
            jobs[chat_id]=updater.job_queue.run_repeating(performCheck, data["update_time"], context=jobDat)
        print("done")

    if data["admin_id"] == -1:
        global admin_token
        print("CRITICAL WARNING: No Admin-Chat is set,\n"+
              "   to verify as Admin, please send \"admin verify "+admin_token+"\" to the Bot\n"+
              "   The first one to send this, will be the Admin\n"+
              "   If somehow anyone but you gets admin, delete data.pkl")
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
