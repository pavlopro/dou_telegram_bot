from telebot import types

# кнопка "На Головну" застосовується в розділі "Обрані"
to_main_menu = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
main_butt = types.KeyboardButton('« На головну')
to_main_menu.add(main_butt)

# кнопки навігації
navigate_menu = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
back_butt = types.KeyboardButton('‹ Назад')
favourite = types.KeyboardButton('Обрані вакансії')
subscribe = types.KeyboardButton('Оформити підписку')
navigate_menu.add(main_butt, back_butt)
navigate_menu.add(favourite)
navigate_menu.add(subscribe)

# кнопка "На Головну, Назад та Обрані" зявляється після натискання "Підписатись на оновлення"'
head_menu = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
head_menu.add(main_butt, back_butt)
head_menu.add(favourite)

# Start кнопка
start_menu = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
start_menu.add(types.KeyboardButton("Оновити"))

# Кнопки головного меню
menu = ('Вакансії','Обрані вакансії', "Мої підписки", "Стрічка")
main_menu = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
for key in menu:
    main_menu.add(types.KeyboardButton(key))

# Кнопки міст
cities = ('Львів', 'Київ', 'Харків', 'Одеса', 'Дніпро', 'Запоріжжя', 'Чернігів', 'Івано-Франківськ', 'Суми', 'Черкаси',
          'Чернівці', 'Вінниця', 'Хмельницький', 'Херсон')
cities_menu = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
cities_menu.add(main_butt, back_butt)
for key in cities:
    cities_menu.add(types.KeyboardButton(key))

# Кнопки категорій
pro_tech_menu = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True, row_width=2)
pro_tech = ('Java', 'Python', '.NET', 'Ruby', 'PHP', 'iOS/macOS', 'C++', 'QA', 'Front End', 'Project Manager',
            'Дизайн', 'Product Manager', 'Маркетинг', 'Analyst', 'DevOps', '1С', 'Blockchain', 'Data Science', 'DBA',
            'Embedded', 'ERP/CRM', 'Golang', 'HR', 'Node.js', 'React Native', 'Unity', 'Sales', 'Scala', 'Security',
            'SEO', 'Support', 'Technical Writer', 'Системный администратор')
pro_tech_menu.add(main_butt)
for key in pro_tech:
    pro_tech_menu.add(types.KeyboardButton(key))

# Кнопки досвіду
experience_menu = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
experience = ('< 1 року', '1…3 роки', '3…5 років', '5+ років')
experience_menu.add(main_butt, back_butt)
for key in experience:
    experience_menu.add(types.KeyboardButton(key))

vacancy_add_menu = types.InlineKeyboardMarkup(row_width=1)
add_button = types.InlineKeyboardButton("Додати до обраних", callback_data='add_vacancy')
vacancy_add_menu.add(add_button)

vacancy_del_menu = types.InlineKeyboardMarkup(row_width=1)
del_button = types.InlineKeyboardButton("Вилучити з обраних", callback_data='del_vacancy')
vacancy_del_menu.add(del_button)

subscription_del_menu = types.InlineKeyboardMarkup(row_width=1)
del_subs_button = types.InlineKeyboardButton("Скасувати підписку", callback_data='delete_subscription')
subscription_del_menu.add(del_subs_button)
