import vk_api
import logging
from aiogram import Bot, Dispatcher, executor, types
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import asyncio
import psycopg2
from django.urls import reverse
from multiprocessing import Process
from django.http import HttpResponseRedirect


def send_msq_vk(vk_chat, msq):
    session = vk_api.VkApi(token='d9b97cbd079b801a1c8c1fc85a295865f861913439f1c407fe18269be5393d724999b3596ec081b1bc85e')
    session.method('messages.send', {'chat_id': vk_chat, 'message': msq, 'random_id': 0})


async def send_msq_tg(tg_chat, msg):
    bot = Bot(token='1930547591:AAF8qqEECajgZiNwepLuQQiJPygCikFAIgY')
    await bot.send_message(chat_id=tg_chat, text=msg)
    await bot.close()


def VK():
    tg_chat = -568578461
    while True:
        try:
            session = vk_api.VkApi(token='d9b97cbd079b801a1c8c1fc85a295865f861913439f1c407fe18269be5393d724999b3596ec081b1bc85e')
            longPoll = VkBotLongPoll(session, 206623626)
            for event in longPoll.listen():
                if event.type == VkBotEventType.MESSAGE_NEW:
                    if event.from_chat:
                        msq = event.object['text']
                        user = event.object['from_id']
                        vk_chat = event.chat_id
                        session_api = session.get_api()
                        user_get = session_api.users.get(user_ids=user)
                        user_get = user_get[0]
                        full_name = user_get['first_name'] + " " + user_get['last_name']
                        BD = psycopg2.connect(database="postgres", user="postgres", password="", host="localhost", port="5432")
                        base = BD.cursor()
                        base.execute("INSERT INTO Work_w (from_s, chat_from, chat_to, user_s, msq) VALUES (%s, %s, %s, %s, %s)", ("VK", vk_chat, tg_chat, full_name, msq))
                        BD.commit()
                        base.close()
                        BD.close()
                        msq = "Сообщение от " + str(full_name) + ":" + '\n' + str(msq) + '\n'
                        asyncio.run(send_msq_tg(tg_chat, msq))
        except:
            pass


def TG():
    vk_chat = 1
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token='1930547591:AAF8qqEECajgZiNwepLuQQiJPygCikFAIgY')
    dp = Dispatcher(bot)
    while True:
        try:
            @dp.message_handler()
            async def MSQ(message: types.Message):
                msq = message.text.split()
                user = message["from"]
                user = user["last_name"] + " " + user["first_name"]
                rar = message["from"]
                tg_chat = message["chat"]
                tg_chat = tg_chat["id"]
                if msq[0] == '/vk' and msq[1] and not rar["is_bot"]:
                    del msq[0]
                    msg = ""
                    for i in msq:
                        msg += i + ' '
                    msq = "Сообщение от " + user + ":" + '\n' + msg
                    BD = psycopg2.connect(database="postgres", user="postgres", password="", host="localhost", port="5432")
                    base = BD.cursor()
                    base.execute("INSERT INTO Work_w (from_s, chat_from, chat_to, user_s, msq) VALUES (%s, %s, %s, %s, %s)", ("TG", tg_chat, vk_chat, user, msg))
                    BD.commit()
                    base.close()
                    BD.close()
                    send_msq_vk(vk_chat, msq)
            executor.start_polling(dp, skip_updates=True)
        except:
            pass


def index(request):
    pr1 = Process(target=VK)
    pr2 = Process(target=TG)
    pr1.start()
    pr2.start()
    return HttpResponseRedirect(reverse('index'))
