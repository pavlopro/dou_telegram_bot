import telebot
import os
from pytz import utc
from config import TOKEN, DATABASELINK
from flask import Flask, request
from parcer import get_vacancy_list, get_artickle_list
from dbdriver import cursor, connection
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ProcessPoolExecutor
from navigation import navigate_menu, menu, main_menu, cities, cities_menu, pro_tech, pro_tech_menu, experience, \
    experience_menu, start_menu, vacancy_add_menu, vacancy_del_menu, to_main_menu, head_menu, subscription_del_menu
from utils import create_url

jobstores = {
    'default': SQLAlchemyJobStore(url=DATABASELINK,
                                  tablename='apscheduler_jobs')
}
executors = {
    'default': {'type': 'threadpool', 'max_workers': 20},
    'processpool': ProcessPoolExecutor(max_workers=5)
}
job_defaults = {'coalesce': False,
                'max_instances': 3
                }


bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)
scheduler = BackgroundScheduler(daemon=True)
scheduler.configure(jobstores=jobstores, executors=executors, job_defaults=job_defaults, timezone=utc)
scheduler.start()


def get_new_vacancy(user_id, chat_id, pro_lang, exp, city, url):
    remote_vacancy_list = get_vacancy_list(url)
    remote_vacancy_list = [link[2] for link in remote_vacancy_list]
    cursor.execute("""SELECT vacancy_urls
                      FROM subscriptions
                      WHERE user_id = %s AND chat_id = %s AND pro_lang = %s AND exp = %s AND city = %s""",
                   (user_id, chat_id, pro_lang, exp, city))
    vacancy_urls, = cursor.fetchone() or ([],)
    list_vacancy_urls = vacancy_urls.split(',') if vacancy_urls else []
    print(scheduler.get_jobs())
    print(list_vacancy_urls)
    if remote_vacancy_list:
        for vacancy in remote_vacancy_list:
            if vacancy not in list_vacancy_urls:
                bot.send_message(chat_id, vacancy, parse_mode='html', reply_markup=vacancy_add_menu)
                users_vacancy_links = ','.join(list_vacancy_urls) + ',' + vacancy if list_vacancy_urls else vacancy
                cursor.execute("""UPDATE subscriptions
                                  SET vacancy_urls = %s
                                  WHERE user_id = %s AND chat_id = %s AND pro_lang = %s AND exp = %s AND city = %s""",
                               (users_vacancy_links, user_id, chat_id, pro_lang, exp, city))
                connection.commit()


@bot.message_handler(commands=['start'])
def welcome(message):
    welcome_message = f"<i>Вітаю</i> <b>{message.from_user.first_name}</b>!\n" \
                      f"<i>Я</i> - <b>Dou</b>!, <i>бот який допоможе тобі швидко та зручно отримати необхідну " \
                      f"інформацію з Dou.ua. \nНа даний час я знаю про багато актуальних вакансій, " \
                      f"які реалізовані в розділі «Вакансії».</i>\n\n" \
                      f"<i>Отож не зволікай! Мерщій клікай та обирай свою найкращу вакансію!</i>"

    cursor.execute("""INSERT INTO users (chat_id, user_id, state, pro_lang, exp, city, first_name, last_name) 
                        VALUES (%s, %s, Null, Null, Null, Null, %s, %s)
                        ON CONFLICT (user_id) DO UPDATE SET 
                        chat_id = %s,
                        user_id = %s,
                        state = Null,
                        pro_lang = Null,
                        exp = Null,
                        city = NUll,
                        first_name = %s,
                        last_name = %s""", (message.chat.id, message.from_user.id, message.chat.first_name, message.chat.last_name,
                                            message.chat.id, message.from_user.id, message.chat.first_name, message.chat.last_name))
    connection.commit()

    return bot.send_message(message.chat.id, welcome_message, parse_mode='html', reply_markup=main_menu)


@bot.message_handler(content_types=['text'])
def message_handler(message):
    if message.text == 'Оновити':
        return welcome(message)
    cursor.execute("""SELECT *
                      FROM users
                      WHERE user_id = %s
                      AND chat_id = %s""", (message.from_user.id, message.chat.id))
    result = cursor.fetchone()
    if not result:
        return bot.send_message(message.chat.id, "Інформація застаріла. Оновіть щоб розпочати", parse_mode='html',
                                reply_markup=start_menu)
    else:
        result = {'chat_id': result[0],
                  'user_id': result[1],
                  'state': result[2],
                  'pro_lang': result[3],
                  'exp': result[4],
                  'city': result[5]}
    return message_handler_with_data(message, result)


def message_handler_with_data(message, result):
    if message.text == 'Вакансії':
        bot.send_message(message.chat.id, 'Виберіть напрямок', parse_mode='html', reply_markup=pro_tech_menu)
        cursor.execute("""UPDATE users
                          SET state = %s
                          WHERE user_id = %s
                          AND chat_id = %s""", (message.text, message.from_user.id, message.chat.id))
        connection.commit()

    elif message.text == 'Обрані вакансії':
        cursor.execute("""UPDATE users
                          SET state = %s
                          WHERE user_id = %s
                          AND chat_id = %s""",(message.text, message.from_user.id, message.chat.id))
        connection.commit()

        cursor.execute("""SELECT vacancy_url, title
                          FROM favorites
                          WHERE user_id = %s""", (message.from_user.id,))
        result = cursor.fetchall()
        if not result:
            bot.send_message(message.chat.id, "У вас немає обраних вакансій", parse_mode='html', reply_markup=to_main_menu)
        else:
            for vacancy in result:
                text_msg = f"<a href='{vacancy[0]}'>{vacancy[1]}</a>"
                bot.send_message(message.chat.id, text_msg, parse_mode='html', reply_markup=vacancy_del_menu)
            bot.send_message(message.chat.id, '‎', parse_mode='html', reply_markup=to_main_menu)

    elif message.text == 'Стрічка':
        cursor.execute("""UPDATE users
                         SET state = %s
                         WHERE user_id = %s
                         AND chat_id = %s""", (message.text, message.from_user.id, message.chat.id))
        connection.commit()
        article_list = get_artickle_list('https://dou.ua/lenta/')
        if article_list:
            for article in article_list:
                text_msg = f"<a href='{article[0]}'>{article[1].strip()}</a>"
                bot.send_message(message.chat.id, text_msg, parse_mode='html')

        bot.send_message(message.chat.id, '‎', parse_mode='html', reply_markup=to_main_menu)

    elif message.text == 'Мої підписки':
        cursor.execute("""UPDATE users
                             SET state = %s
                             WHERE user_id = %s
                             AND chat_id = %s""", (message.text, message.from_user.id, message.chat.id))
        connection.commit()

        cursor.execute("""SELECT CONCAT(pro_lang, ' ', city, ' ', exp)
                             FROM subscriptions
                             WHERE user_id = %s""", (message.from_user.id,))
        result = cursor.fetchall()
        if not result:
            bot.send_message(message.chat.id, "У вас немає активних підписок", parse_mode='html',
                             reply_markup=to_main_menu)
        else:
            for sub in result:
                bot.send_message(message.chat.id, sub[0], parse_mode='markdown', reply_markup=subscription_del_menu)
            bot.send_message(message.chat.id, '‎', parse_mode='html', reply_markup=to_main_menu)

    elif message.text == 'Оформити підписку':
        cursor.execute("""SELECT chat_id, user_id, pro_lang, exp, city, vacancy_urls
                          FROM users
                          WHERE user_id = %s""", (message.from_user.id,))
        result = cursor.fetchone()
        if result:
            chat_id = result[0]
            user_id = result[1]
            pro_lang = result[2]
            exp = result[3]
            city = result[4]
            vacancy_urls = result[5]

            cursor.execute("""SELECT subscribe
                              FROM subscriptions
                              WHERE user_id = %s AND chat_id = %s AND pro_lang = %s AND exp = %s AND city = %s""",
                           (user_id, chat_id, pro_lang, exp, city))
            subscribe, = cursor.fetchone() or (False,)
            if not subscribe:
                url = create_url(pro_lang, exp, city)
                unique_cron_id = str(chat_id)+str(user_id)+pro_lang+exp+city
                cursor.execute("""INSERT INTO subscriptions(user_id, chat_id, pro_lang, exp, city, vacancy_urls, url, cron_id, subscribe)
                                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, True)
                                   """, (user_id, chat_id, pro_lang, exp, city, vacancy_urls, url, unique_cron_id))
                connection.commit()
                scheduler.add_job(get_new_vacancy, 'interval', args=[chat_id, user_id, pro_lang, exp, city, url], minutes=15,
                                  replace_existing=True, id=unique_cron_id)
                bot.send_message(message.chat.id, f'‎Підписку оформлено', parse_mode='html',
                                 reply_markup=head_menu)
            else:
                bot.send_message(message.chat.id, '‎У вас вжє є активна підписка', parse_mode='html', reply_markup=head_menu)
            bot.send_message(message.chat.id, '‎', parse_mode='html', reply_markup=head_menu)

    elif message.text in ('« На головну',) and \
            result.get('chat_id') == message.chat.id and \
            result.get('user_id') == message.from_user.id and \
            (result.get('state') in menu or result.get('state') in pro_tech or result.get('state')
             in experience or result.get('state') in cities):
        bot.send_message(message.chat.id, 'Виберіть розділ', parse_mode='html', reply_markup=main_menu)
        cursor.execute("""UPDATE users
                          SET state = Null,
                              pro_lang = Null,
                              exp = Null,
                              city = Null
                          WHERE user_id = %s
                          AND chat_id = %s""", (message.from_user.id, message.chat.id))
        connection.commit()

    elif message.text in ('‹ Назад', ) and \
            result.get('chat_id') == message.chat.id and \
            result.get('user_id') == message.from_user.id and \
            (result.get('state') in menu or result.get('state') in pro_tech or result.get('state')
             in experience or result.get('state') in cities):
        current_state = result.get('state')
        current_pro_lang = result.get('pro_lang')
        current_exp = result.get('exp')
        current_cty = result.get('city')

        if current_state == current_pro_lang:
            bot.send_message(message.chat.id, "Виберіть напрямок", parse_mode='html', reply_markup=pro_tech_menu)
            cursor.execute("""UPDATE users
                              SET state = %s,
                                  pro_lang  = Null
                              WHERE user_id = %s
                              AND chat_id = %s""", (menu[0], message.from_user.id, message.chat.id))
            connection.commit()

        elif current_state == current_exp:
            bot.send_message(message.chat.id, 'Вкажіть досвід', parse_mode='html', reply_markup=experience_menu)
            cursor.execute("""UPDATE users
                              SET state = %s,
                                  exp = Null
                              WHERE user_id = %s
                              AND chat_id = %s""", (current_pro_lang, message.from_user.id, message.chat.id))
            connection.commit()

        elif current_state == current_cty:
            bot.send_message(message.chat.id, 'Вкажіть місто або оберіть зі списку', parse_mode='html',
                             reply_markup=cities_menu)
            cursor.execute("""UPDATE users
                              SET state = %s,
                                  city = Null
                               WHERE user_id = %s
                              AND chat_id = %s""",(current_exp, message.from_user.id, message.chat.id))
            connection.commit()

    elif message.text not in pro_tech and \
            result.get('chat_id') == message.chat.id and \
            result.get('user_id') == message.from_user.id and \
            result.get('state') in menu:
        bot.send_message(message.chat.id, 'Виберіть напрямок', parse_mode='html', reply_markup=pro_tech_menu)
    elif message.text in pro_tech:
        bot.send_message(message.chat.id, 'Вкажіть досвід', parse_mode='html', reply_markup=experience_menu)
        cursor.execute("""UPDATE users
                          SET state = %s,
                              pro_lang = %s
                          WHERE user_id = %s
                          AND chat_id = %s""", (message.text, message.text, message.from_user.id, message.chat.id))
        connection.commit()

    elif message.text not in experience and \
            result.get('chat_id') == message.chat.id and \
            result.get('user_id') == message.from_user.id and \
            result.get('state') in pro_tech:
        bot.send_message(message.chat.id, 'Вкажіть досвід', parse_mode='html', reply_markup=experience_menu)
    elif message.text in experience:
        bot.send_message(message.chat.id, 'Вкажіть місто або оберіть зі списку', parse_mode='html',
                         reply_markup=cities_menu)
        cursor.execute("""UPDATE users
                          SET state = %s,
                              exp = %s
                          WHERE user_id = %s
                          AND chat_id = %s""", (message.text, message.text, message.from_user.id, message.chat.id))
        connection.commit()

    elif message.text not in cities and \
            result.get('chat_id') == message.chat.id and \
            result.get('user_id') == message.from_user.id and \
            result.get('state') in experience:
        bot.send_message(message.chat.id, "Можливо ви допустили помилку у назві міста, або даного міста немає в базі "
                                          "даних. Будьласка спробуйте ще раз, або виберіть зі списку", parse_mode='html',
                         reply_markup=cities_menu)
    elif message.text in cities:
        city = message.text
        pro_lang = result['pro_lang']
        exp = result['exp']
        url = create_url(pro_lang, exp, city)
        vacancy_links = get_vacancy_list(url)
        if not vacancy_links:
            bot.send_message(message.chat.id, "Нажаль на даний час немає актуальних вакансій по заданим критеріям",
                             parse_mode='html', reply_markup=navigate_menu)
        else:
            for link in vacancy_links:
                text_msg = f"<a href='{link[2]}'>{link[0]} в {link[1]}</a>"
                bot.send_message(message.chat.id, text_msg, parse_mode='html',
                                 reply_markup=vacancy_add_menu, disable_notification=True)
            bot.send_message(message.chat.id, "‎", parse_mode='html',
                             reply_markup=navigate_menu)
        cursor.execute("""UPDATE users
                          SET state = %s,
                              city = %s,
                              vacancy_urls = %s
                          WHERE user_id = %s
                          AND chat_id = %s""", (message.text, message.text, ','.join([link[2] for link in vacancy_links]), message.from_user.id, message.chat.id))
        connection.commit()


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.data == 'add_vacancy':
        cursor.execute("""INSERT INTO favorites (user_id, vacancy_url, title) 
                            VALUES (%s, %s, %s)
                            ON CONFLICT (vacancy_url) DO NOTHING """,(call.from_user.id,
                                                                      call.message.json['entities'][0]['url'],
                                                                      call.message.text))
        connection.commit()
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode='html',
                              text=f"<a href='{call.message.json['entities'][0]['url']}'>{call.message.text}</a>")
        bot.answer_callback_query(callback_query_id=call.id, show_alert=True, text="Вакансію додано до обраних")

    elif call.data == 'del_vacancy':
        cursor.execute("""DELETE FROM favorites
                            WHERE user_id = %s
                            AND vacancy_url = %s""",(call.from_user.id, call.message.json['entities'][0]['url']))
        connection.commit()
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="Вакансію вилучено з обраних")

    elif call.data == 'delete_subscription':
        cursor.execute("""SELECT cron_id
                            FROM subscriptions
                            WHERE CONCAT(pro_lang, ' ', city, ' ', exp) = %s
                            AND user_id = %s""", (call.message.text, call.from_user.id))
        cron_id, = cursor.fetchone() or (False,)

        cursor.execute("""DELETE FROM subscriptions
                            WHERE cron_id = %s;
                        DELETE FROM apscheduler_jobs
                            WHERE id = %s;""", (cron_id,cron_id,))
        connection.commit()
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="Підписку скасовано")


@server.route("/" + TOKEN, methods=['POST'])
def get_message():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "POST", 200


@server.route("/")
def web_hook():
    bot.remove_webhook()
    bot.set_webhook(url="https://doutelegrambot.herokuapp.com/" + TOKEN)
    return "CONNECTED", 200


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
