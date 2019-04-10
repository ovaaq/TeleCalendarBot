from telegram.ext import Updater, CommandHandler, MessageHandler,    Filters, InlineQueryHandler, Job
import requests
import re
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import schedule
import time

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
group_chat_id = <GROUP_ID>
telegram_bot_toker = <TOKEN>
TERVETULOA = 'moi'
HELP = "help"
EI_TAPAHTUMIA = "ei tapahtumia"

skripti_id = "7" #Google calendar color blue
poikki_id = "6" #Google calendar color orange
ilmo_id = "11" #Google calendar color red

def getEvents(daysMax):
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    limit = (datetime.datetime.utcnow() + datetime.timedelta(days=daysMax)).isoformat() + 'Z'

    events_result = service.events().list(calendarId='primary', timeMin=now, timeMax=limit,
                                        maxResults=60, singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])
    return(events)

def getToday():
    events = getEvents(1)
    poikki = False
    skripti = False
    ilmo = False
    noEvents = EI_TAPAHTUMIA
    message = ""
    for event in events:
        color = event.get("colorId")
        if color == skripti_id:
            skripti = True
        if color == poikki_id:
            poikki = True
        if color == ilmo_id:
            ilmo = True

    if not poikki and not skripti and not ilmo:
        message = noEvents

    if skripti:
        message = message + "<b>Skriptin tapahtumat:</b>"

        for event in events:
            color = event.get("colorId")
            if color == skripti_id:
                name = event.get("summary")
                start = event['start'].get('dateTime')
                format = datetime.datetime.strptime(start, "%Y-%m-%dT%H:%M:%S%z")
                date = format.strftime("%d.%m.%Y, %H:%M")
                oneEvent = "\n\n" + "<b>MIKÄ</b>: " + name + "\n" + "<b>MISSÄ</b>: " + event.get(
                    "location") + "\n" + "<b>MILLOIN</b>: " + date + "\n" + '<b>INFO</b>: <a href="' + event.get(
                    "htmlLink") + '">Täältä</a>'
                message = message + oneEvent
        if poikki or ilmo:
            message = message + "\n\n"

    if poikki:
        message = message + "<b>Poikkitieteellistä:</b>"

        for event in events:
            color = event.get("colorId")
            if color == poikki_id:
                name = event.get("summary")
                start = event['start'].get('dateTime')
                format = datetime.datetime.strptime(start, "%Y-%m-%dT%H:%M:%S%z")
                date = format.strftime("%d.%m.%Y, %H:%M")
                oneEvent = "\n\n" + "<b>MIKÄ</b>: " + name + "\n" + "<b>MISSÄ</b>: " + event.get(
                    "location") + "\n" + "<b>MILLOIN</b>: " + date + "\n" + '<b>INFO</b>: <a href="' + event.get(
                    "htmlLink") + '">Täältä</a>'
                message = message + oneEvent
        if ilmo:
            message = message + "\n\n"

    if ilmo:
        message = message + "<b>Muista ilmoittautua:</b>"

        for event in events:
            color = event.get("colorId")
            if color == ilmo_id:
                name = event.get("summary")
                start = event['start'].get('dateTime')
                format = datetime.datetime.strptime(start, "%Y-%m-%dT%H:%M:%S%z")
                date = format.strftime("%d.%m.%Y, %H:%M")
                oneEvent = "\n\n" + "<b>MIKÄ</b>: " + name + "\n" + "<b>MILLOIN</b>: " + date + "\n" + '<b>INFO</b>: <a href="' + event.get(
                    "htmlLink") + '">Täältä</a>'
                message = message + oneEvent

    return(message)

def getManyDays(howManyDays):
    events = getEvents(howManyDays)
    poikki = False
    skripti = False
    ilmo = False
    noEvents = EI_TAPAHTUMIA
    message = ""

    for event in events:
        color = event.get("colorId")
        if color == skripti_id:
            skripti = True
        if color == poikki_id:
            poikki = True
        if color == ilmo_id:
            ilmo = True

    if not poikki and not skripti and not ilmo:
        message = noEvents

    if skripti:
        message = message + "<b>Skriptin tapahtumat:</b>\n"

        for event in events:
            color = event.get("colorId")
            if color == skripti_id:
                start = event['start'].get('dateTime')
                format = datetime.datetime.strptime(start, "%Y-%m-%dT%H:%M:%S%z")
                date = format.strftime("%d.%m.%Y")
                name = event.get("summary")
                info = '<a href="' + event.get("htmlLink") + '">Lue lisää</a>'
                message = message + name + " - " + date + " - " + info + "\n"
        if poikki or ilmo:
            message = message + "\n"

    if poikki:
        message = message + "<b>Poikkitieteellistä:</b>\n"

        for event in events:
            color = event.get("colorId")
            if color == poikki_id:
                start = event['start'].get('dateTime')
                format = datetime.datetime.strptime(start, "%Y-%m-%dT%H:%M:%S%z")
                date = format.strftime("%d.%m.%Y")
                name = event.get("summary")
                info = '<a href="' + event.get("htmlLink") + '">Lue lisää</a>'
                message = message + name + " - " + date + " - " + info + "\n"
        if ilmo:
            message = message + "\n"

    if ilmo:
        message = message + "<b>Muista ilmoittautua:</b>\n"

        for event in events:
            color = event.get("colorId")
            if color == ilmo_id:
                start = event['start'].get('dateTime')
                format = datetime.datetime.strptime(start, "%Y-%m-%dT%H:%M:%S%z")
                date = format.strftime("%d.%m.%Y")
                name = event.get("summary")
                info = '<a href="' + event.get("htmlLink") + '">Lue lisää</a>'
                message = message + name + " - " + date + " - " + info + "\n"

    return(message)

def nowEvents(bot, update):
    message = getToday()
    chat_id = update.message.chat_id
    bot.send_message(parse_mode='HTML', chat_id=chat_id, text=message)

def weekEvents(bot, update):
    message = getManyDays(6)
    chat_id = update.message.chat_id
    bot.send_message(parse_mode='HTML', chat_id=chat_id, text=message)

def monthEvents(bot, update):
    message = getManyDays(29)
    chat_id = update.message.chat_id
    bot.send_message(parse_mode='HTML', chat_id=chat_id, text=message)

def twoMonthEvents(bot, update):
    message = getManyDays(59)
    chat_id = update.message.chat_id
    bot.send_message(parse_mode='HTML', chat_id=chat_id, text=message)

def sendMondayReminder(bot, update):
    events = getEvents(6)
    poikki = False
    skripti = False
    ilmo = False
    message = getManyDays(6)
    chat_id = group_chat_id
    for event in events:
        color = event.get("colorId")
        if color == skripti_id:
            skripti = True
        if color == poikki_id:
            poikki = True
        if color == ilmo_id:
            ilmo = True
    if skripti or ilmo or poikki:
        bot.send_message(parse_mode='HTML', chat_id=chat_id, text=message)

def sendTodayReminder(bot, update):
    events = getEvents(1)
    poikki = False
    skripti = False
    ilmo = False
    message = getToday()
    chat_id = group_chat_id
    for event in events:
        color = event.get("colorId")
        if color == skripti_id:
            skripti = True
        if color == poikki_id:
            poikki = True
        if color == ilmo_id:
            ilmo = True
    if skripti or ilmo or poikki:
        bot.send_message(parse_mode='HTML', chat_id=chat_id, text=message)

def empty_message(bot, update):
    message = TERVETULOA
    chat_id = update.message.chat_id
    bot.send_message(parse_mode='HTML', chat_id=chat_id, text=message)

def guide(bot, update):
    message = HELP
    chat_id = update.message.chat_id
    bot.send_message(parse_mode='HTML', chat_id=chat_id, text=message)

def main():
    updater = Updater(telegram_bot_toker)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('nyt',nowEvents))
    dp.add_handler(CommandHandler('viikko',weekEvents))
    dp.add_handler(CommandHandler('kk',monthEvents))
    dp.add_handler(CommandHandler('2kk',twoMonthEvents))
    dp.add_handler(CommandHandler('help',guide))
    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, empty_message))
    updater.job_queue.run_daily(sendMondayReminder, days=(0,), time=datetime.time(7,00,00))
    updater.job_queue.run_daily(sendTodayReminder, days = (1,2,3,4,5,6), time=datetime.time(7,00,00))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
