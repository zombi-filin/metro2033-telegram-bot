# -*- coding: utf-8 -*-

import config
import metro2033_bot
import telebot
import telemoji as emj
from threading import Thread
import time

#
game_bot = metro2033_bot.Metro2033Bot(config.VK_USER_ID, config.VK_USER_AUTH)

#
telegram_bot = telebot.TeleBot(config.TELEGRAM_BOT_TOKEN)
# 

#
btn_main = f'{emj.bar_chart} Главная'
btn_status = f'{emj.bar_chart} Статус'
btn_action = f'{emj.joystick} Действия'
btn_settings = f'{emj.control_knobs} Настройки'

btn_action_reload = f'{emj.recycle} Обновить данные'
btn_action_gift = f'{emj.gift} Отправить падарок'
btn_action_goods = f'{emj.tent} Торговцы'

btn_action_move = f'{emj.runner} Перейти на др. станцию'
btn_action_move_1 = None
loc_action_move_1 = None
btn_action_move_2 = None
loc_action_move_2 = None
btn_action_move_3 = None
loc_action_move_3 = None
btn_action_move_4 = None
loc_action_move_4 = None

btn_taxi = f'{emj.oncoming_taxi} Такси'
btn_taxi_group_1 = f'А Б В К'
btn_taxi_group_2 = f'Н П Р'
btn_taxi_group_3 = f'С Т У Ф Ц Ч'
btn_taxi_cancel = f'{emj.x} Отмена такси'

btn_taxi_1 = f'Павелецкая'
btn_taxi_2 = f'Новокузнецкая'
btn_taxi_3 = f'Театральная'
btn_taxi_4 = f'Тверская'
btn_taxi_5 = f'Павелецкая (Г)'
btn_taxi_6 = f'Чеховская'
btn_taxi_7 = f'Боровицкая'
btn_taxi_8 = f'Библ. Ленина'
btn_taxi_9 = f'Полянка'
btn_taxi_10 = f'Третьяковская'
btn_taxi_11 = f'Кропоткинская'
btn_taxi_12 = f'Парк культуры (К)'
btn_taxi_13 = f'Парк культуры (Г)'
btn_taxi_14 = f'Киевская'
btn_taxi_15 = f'Киевская (Г)'
btn_taxi_16 = f'Пушкинская'
btn_taxi_17 = f'Кузнецкий Мост'
btn_taxi_18 = f'Китай-город'
btn_taxi_19 = f'Тургеневская'
btn_taxi_20 = f'Сухаревская'
btn_taxi_21 = f'Проспект мира'
btn_taxi_22 = f'Рижская'
btn_taxi_23 = f'Алексеевская'
btn_taxi_24 = f'ВДНХ'
btn_taxi_25 = f'Цветной бульвар'
btn_taxi_26 = f'Фрунзенская'
btn_taxi_27 = f'Коммунистическая'
btn_taxi_28 = f'Университет'
btn_taxi_29 = f'Пр. Вернадского'

btn_action_pets_feed = f'{emj.dog2} Кормить питомца'
btn_action_pets_feed_1 = f'{emj.cut_of_meat} {emj.one}'
btn_action_pets_feed_5 = f'{emj.cut_of_meat} {emj.five}'
btn_action_pets_feed_10 = f'{emj.cut_of_meat} {emj.keycap_ten}'

btn_settings_job = f'{emj.hammer_and_pick} Работа'
btn_settings_job_0 = f'{emj.x} Не работать'
btn_settings_job_1 = f'{emj.pig} Корм. свиней 30м'
btn_settings_job_2 = f'{emj.mushroom} Соб. грибы 1ч'
btn_settings_job_3 = 'Уп. чай 2ч'
btn_settings_job_4 = 'Чист. оружие 5ч'
btn_settings_job_5 = 'Патр. станцию 8ч'

btn_settings_trip = f'{emj.bust_in_silhouette} Задания начстанции'
btn_settings_trip_0 = f'{emj.x} Не брать'
btn_settings_trip_1 = None
btn_settings_trip_2 = None
btn_settings_trip_3 = None

btn_settings_foe = f'{emj.crossed_swords} Поединки'
btn_settings_foe_none = f'{emj.x} Не атаковать'
btn_settings_foe_friends = f'Друзья'
btn_settings_foe_static = f'Статичный противник'
btn_settings_foe_winner = f'Победитель'
btn_settings_foe_arena = f'Арена'

btn_settings_pets = f'{emj.dog2} Вызов питомца'
btn_settings_pets_yes = f'{emj.white_check_mark} Вызывать'
btn_settings_pets_no = f'{emj.x} Не вызывать'

# 

def bot_message(message):
    '''
    '''
    telegram_bot.send_message(
        chat_id = config.TELEGRAM_CHAT_ID,
        text = message
    )

game_bot.messanger = bot_message

def bot_status():
    '''
        Запрос статуса
    '''
    main_menu = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width = 3)
    main_menu.add(
        telebot.types.KeyboardButton(btn_status),
        telebot.types.KeyboardButton(btn_action),
        telebot.types.KeyboardButton(btn_settings)
    )

    telegram_bot.send_message(
        chat_id = config.TELEGRAM_CHAT_ID,
        text = game_bot.telegram_bot_status(),
        reply_markup = main_menu
    )

def bot_action():
    '''
        Запрос меню 'Действия'
    '''
    action_menu = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    action_menu.row(
        telebot.types.KeyboardButton(btn_action_reload),
        telebot.types.KeyboardButton(btn_action_move),
        telebot.types.KeyboardButton(btn_taxi),
    )
    action_menu.row(
        telebot.types.KeyboardButton(btn_action_pets_feed),
        telebot.types.KeyboardButton(btn_action_gift),
        telebot.types.KeyboardButton(btn_action_goods),
    )
    action_menu.row(
        telebot.types.KeyboardButton(btn_main)
    )

    telegram_bot.send_message(
        chat_id = config.TELEGRAM_CHAT_ID,
        text = 'Действия',
        reply_markup = action_menu
    )

def bot_action_reload():
    '''
        Команда перезагрузка данных
    '''
    game_bot.game_data['reload'] = 0
    bot_status()

def bot_action_move():
    '''
    '''
    global btn_action_move_1
    global loc_action_move_1
    global btn_action_move_2
    global loc_action_move_2
    global btn_action_move_3
    global loc_action_move_3
    global btn_action_move_4
    global loc_action_move_4

    btn_action_move_1 = None
    loc_action_move_1 = None
    btn_action_move_2 = None
    loc_action_move_2 = None
    btn_action_move_3 = None
    loc_action_move_3 = None
    btn_action_move_4 = None
    loc_action_move_4 = None

    action_move_menu = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    
    from_loc = game_bot.int(f'player.loc')
    for tunnel_id in game_bot.element(f'data.tunnels'):
        if game_bot.int(f'data.tunnels.{tunnel_id}.from') == from_loc:
            to_loc = game_bot.int(f'data.tunnels.{tunnel_id}.dest')
        elif game_bot.int(f'data.tunnels.{tunnel_id}.dest') == from_loc:
            to_loc = game_bot.int(f'data.tunnels.{tunnel_id}.from')
        else:
            continue
        
        home = ''
        if game_bot.int(f'player.home')==to_loc:
            home = f'{emj.tent} '

        # TODO Переделать на globals()[]
        if btn_action_move_1 is None:
            btn_action_move_1 = home + game_bot.str(f'data.stations.{to_loc}.name')
            loc_action_move_1 = to_loc
            action_move_menu.add(telebot.types.KeyboardButton(btn_action_move_1))
        elif btn_action_move_2 is None:
            btn_action_move_2 = home + game_bot.str(f'data.stations.{to_loc}.name')
            loc_action_move_2 = to_loc
            action_move_menu.add(telebot.types.KeyboardButton(btn_action_move_2))
        elif btn_action_move_3 is None:
            btn_action_move_3 = home + game_bot.str(f'data.stations.{to_loc}.name')
            loc_action_move_3 = to_loc
            action_move_menu.add(telebot.types.KeyboardButton(btn_action_move_3))
        elif btn_action_move_4 is None:
            btn_action_move_4 = home + game_bot.str(f'data.stations.{to_loc}.name')
            loc_action_move_4 = to_loc
            action_move_menu.add(telebot.types.KeyboardButton(btn_action_move_4))

    action_move_menu.add(telebot.types.KeyboardButton(btn_main))
    
    telegram_bot.send_message(
        chat_id = config.TELEGRAM_CHAT_ID,
        text = 'Доступные для перемещения станции',
        reply_markup = action_move_menu
    )

def bot_action_move_set(loc):
    '''
    '''
    game_bot.api_user_move(loc)
    bot_status()

def bot_action_pets_feed():
    '''
    '''
    pets_feed_menu = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    pets_feed_menu.row(
        telebot.types.KeyboardButton(btn_action_pets_feed_1),
        telebot.types.KeyboardButton(btn_action_pets_feed_5),
        telebot.types.KeyboardButton(btn_action_pets_feed_10),
    )
    pets_feed_menu.row(telebot.types.KeyboardButton(btn_main))

    telegram_bot.send_message(
        chat_id = config.TELEGRAM_CHAT_ID,
        text = game_bot.get_pets_status(),
        reply_markup = pets_feed_menu
    )

def bot_action_pets_feed_set(num):
    '''
    '''
    # TODO: Переделать когда будет много питомцев
    game_bot.api_pets_feed(1, num)
    bot_action_pets_feed()

def bot_action_gift():
    '''
    '''
    game_bot.send_gift_online_user()
    bot_status()

def bot_action_goods():
    '''
    '''
    telegram_bot.send_message(
        chat_id = config.TELEGRAM_CHAT_ID,
        text = game_bot.get_list_goods()
    )
    bot_action()

def bot_settings():
    '''
    '''
    settings_menu = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    
    settings_menu.row(
        telebot.types.KeyboardButton(btn_settings_trip),
        telebot.types.KeyboardButton(btn_settings_job),
    )

    settings_menu.row(
        telebot.types.KeyboardButton(btn_settings_foe),
        telebot.types.KeyboardButton(btn_settings_pets),
    )
    settings_menu.row(
        telebot.types.KeyboardButton(btn_main)
    )

    telegram_bot.send_message(
        chat_id = config.TELEGRAM_CHAT_ID,
        text = 'Управление ботом',
        reply_markup = settings_menu
    )

def bot_settings_job():
    '''
    '''
    job_menu = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    job_menu.row(telebot.types.KeyboardButton(btn_settings_job_0))
    job_menu.row(
        telebot.types.KeyboardButton(btn_settings_job_1),
        telebot.types.KeyboardButton(btn_settings_job_2),
        telebot.types.KeyboardButton(btn_settings_job_3),
    )
    job_menu.row(
        telebot.types.KeyboardButton(btn_settings_job_4),
        telebot.types.KeyboardButton(btn_settings_job_5)
    )
    job_menu.row(telebot.types.KeyboardButton(btn_main))

    if int(game_bot.config['job_index']) == 0:
        job_name = 'Нет'
    else:
        job_name = game_bot.get_job_name(game_bot.config['job_index'])
    telegram_bot.send_message(
        chat_id = config.TELEGRAM_CHAT_ID,
        text = f'Работа на станции: {job_name}',
        reply_markup = job_menu
    )

def bot_settings_job_set(job_id):
    '''
    '''
    game_bot.config['job_index'] = int(job_id)
    game_bot.config_save()

    bot_status()

def bot_settings_trip():
    '''
    '''
    global btn_settings_trip_1
    global btn_settings_trip_2
    global btn_settings_trip_3

    player_loc = game_bot.str(f'player.loc')
    for idx in [1,2,3]:
        trip_id = str(player_loc) + str(idx)

        if trip_id in game_bot.element('trip'):
            qid = game_bot.str(f'trip.{trip_id}.qid')
            mob_id = game_bot.str(f'data.quests.{qid}.mob')
            btn_settings_trip_x = game_bot.str(f'data.mobs.{mob_id}.name')
            btn_settings_trip_x = btn_settings_trip_x + f' {emj.zap} ' + game_bot.str(f'data.quests.{qid}.time')
            globals()[f'btn_settings_trip_{idx}'] = btn_settings_trip_x            
        else:
            globals()[f'btn_settings_trip_{idx}'] = None   


    trip_menu = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    trip_menu.row(telebot.types.KeyboardButton(btn_settings_trip_0))
    if btn_settings_trip_1 is not None:
        trip_menu.row(
            telebot.types.KeyboardButton(btn_settings_trip_1),
            telebot.types.KeyboardButton(btn_settings_trip_2),
            telebot.types.KeyboardButton(btn_settings_trip_3),
        )
    trip_menu.row(telebot.types.KeyboardButton(btn_main))

    telegram_bot.send_message(
        chat_id = config.TELEGRAM_CHAT_ID,
        text = f'Задания начстанции',
        reply_markup = trip_menu
    )

def bot_settings_trip_set(trip_index):
    '''
    '''
    game_bot.config['trip_index'] = int(trip_index)
    game_bot.config_save()

    bot_status()

def bot_settings_foe():
    '''
    '''

    if game_bot.config['fray_mode'] is None:
        text = btn_settings_foe_none
    elif game_bot.config['fray_mode'] == 'friends':
        text = btn_settings_foe_friends
    elif game_bot.config['fray_mode'] == 'static':
        text = btn_settings_foe_static
    elif game_bot.config['fray_mode'] == 'winner':
        text = btn_settings_foe_winner
    elif game_bot.config['fray_mode'] == 'arena':
        text = btn_settings_foe_arena

    foe_menu = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width = 1)
    foe_menu.add(
        telebot.types.KeyboardButton(btn_settings_foe_none),
        telebot.types.KeyboardButton(btn_settings_foe_friends),
        telebot.types.KeyboardButton(btn_settings_foe_winner),
        telebot.types.KeyboardButton(btn_settings_foe_static),
        telebot.types.KeyboardButton(btn_settings_foe_arena),
        telebot.types.KeyboardButton(btn_main)
    )

    telegram_bot.send_message(
        chat_id = config.TELEGRAM_CHAT_ID,
        text = text,
        reply_markup = foe_menu
    )

def bot_settings_foe_set(mode):
    '''
    '''
    game_bot.config['fray_mode'] = mode
    game_bot.config_save()

    bot_status()

def bot_settings_pets():
    '''
    '''
    settings_pets_menu = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    settings_pets_menu.row(
        telebot.types.KeyboardButton(btn_settings_pets_yes),
        telebot.types.KeyboardButton(btn_settings_pets_no)
    )
    settings_pets_menu.row(
        telebot.types.KeyboardButton(btn_main)
    )
    telegram_bot.send_message(
        chat_id = config.TELEGRAM_CHAT_ID,
        text = btn_settings_pets_yes if game_bot.config['use_pet'] else btn_settings_pets_no,
        reply_markup = settings_pets_menu
    )

def bot_settings_pets_set(mode):
    '''
    '''
    game_bot.config['use_pet'] = mode
    game_bot.config_save()

    bot_status()

def bot_taxi():
    '''
    '''
    taxi_group_menu = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    taxi_group_menu.row(
        telebot.types.KeyboardButton(btn_taxi_group_1),
        telebot.types.KeyboardButton(btn_taxi_group_2),
        telebot.types.KeyboardButton(btn_taxi_group_3),
    )
    taxi_group_menu.row(
        telebot.types.KeyboardButton(btn_taxi_cancel)
    )    
    taxi_group_menu.row(
        telebot.types.KeyboardButton(btn_main)
    )
    telegram_bot.send_message(
        chat_id = config.TELEGRAM_CHAT_ID,
        text = 'Такси',
        reply_markup = taxi_group_menu
    )

def bot_taxi_group(group_id):
    '''
    '''
    taxi_group_menu = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    
    if group_id==1:
        taxi_group_menu.row(
            telebot.types.KeyboardButton(btn_taxi_23),
            telebot.types.KeyboardButton(btn_taxi_15)
        )
        taxi_group_menu.row(
            telebot.types.KeyboardButton(btn_taxi_8),
            telebot.types.KeyboardButton(btn_taxi_18)
        )
        taxi_group_menu.row(
            telebot.types.KeyboardButton(btn_taxi_7),
            telebot.types.KeyboardButton(btn_taxi_27)
        )
        taxi_group_menu.row(
            telebot.types.KeyboardButton(btn_taxi_24),
            telebot.types.KeyboardButton(btn_taxi_11)
        )
        taxi_group_menu.row(
            telebot.types.KeyboardButton(btn_taxi_14),
            telebot.types.KeyboardButton(btn_taxi_17)
        )
    elif group_id==2:
        taxi_group_menu.row(
            telebot.types.KeyboardButton(btn_taxi_2),
            telebot.types.KeyboardButton(btn_taxi_9)
        )
        taxi_group_menu.row(
            telebot.types.KeyboardButton(btn_taxi_1),
            telebot.types.KeyboardButton(btn_taxi_29)
        )
        taxi_group_menu.row(
            telebot.types.KeyboardButton(btn_taxi_5),
            telebot.types.KeyboardButton(btn_taxi_21)
        )
        taxi_group_menu.row(
            telebot.types.KeyboardButton(btn_taxi_12),
            telebot.types.KeyboardButton(btn_taxi_16)
        )
        taxi_group_menu.row(
            telebot.types.KeyboardButton(btn_taxi_13),
            telebot.types.KeyboardButton(btn_taxi_22)
        )   
    else:
        taxi_group_menu.row(
            telebot.types.KeyboardButton(btn_taxi_20),
            telebot.types.KeyboardButton(btn_taxi_28)
        )
        taxi_group_menu.row(
            telebot.types.KeyboardButton(btn_taxi_4),
            telebot.types.KeyboardButton(btn_taxi_26)
        )
        taxi_group_menu.row(
            telebot.types.KeyboardButton(btn_taxi_3),
            telebot.types.KeyboardButton(btn_taxi_25)
        )
        taxi_group_menu.row(
            telebot.types.KeyboardButton(btn_taxi_10),
            telebot.types.KeyboardButton(btn_taxi_6)
        )
        taxi_group_menu.row(
            telebot.types.KeyboardButton(btn_taxi_19),
        )  

    taxi_group_menu.row(
        telebot.types.KeyboardButton(btn_main)
    )
    telegram_bot.send_message(
        chat_id = config.TELEGRAM_CHAT_ID,
        text = 'Такси',
        reply_markup = taxi_group_menu
    )

def bot_taxi_set(loc):
    '''
    '''
    game_bot.taxi = loc

    bot_status()

# 
@telegram_bot.message_handler(commands=['start'])
def start(message):
    if message.chat.id != config.TELEGRAM_CHAT_ID: return
    bot_status()
    
#
@telegram_bot.message_handler(content_types=['text'])
def get_text_messages(message):
    telegram_bot.delete_message(chat_id = message.chat.id, message_id = message.id)
    if message.chat.id != config.TELEGRAM_CHAT_ID: return 
    if message.text in [btn_main, btn_status]:
        bot_status()
    elif message.text == btn_action:
        bot_action()
    elif message.text == btn_action_reload:
        bot_action_reload()
    elif message.text == btn_action_move:
        bot_action_move()
    elif message.text == btn_action_move_1:
        bot_action_move_set(loc_action_move_1)
    elif message.text == btn_action_move_2:
        bot_action_move_set(loc_action_move_2)
    elif message.text == btn_action_move_3:
        bot_action_move_set(loc_action_move_3)
    elif message.text == btn_action_move_4:
        bot_action_move_set(loc_action_move_4)
    elif message.text == btn_action_pets_feed:
        bot_action_pets_feed()
    elif message.text == btn_action_pets_feed_1:
        bot_action_pets_feed_set(1)
    elif message.text == btn_action_pets_feed_5:
        bot_action_pets_feed_set(5)
    elif message.text == btn_action_pets_feed_10:
        bot_action_pets_feed_set(10)
    elif message.text == btn_action_gift:
        bot_action_gift()
    elif message.text == btn_action_goods:
        bot_action_goods()
    elif message.text == btn_settings:
        bot_settings()
    elif message.text == btn_settings_job:
        bot_settings_job()
    elif message.text == btn_settings_job_0:
        bot_settings_job_set(0)
    elif message.text == btn_settings_job_1:
        bot_settings_job_set(1)
    elif message.text == btn_settings_job_2:
        bot_settings_job_set(2)
    elif message.text == btn_settings_job_3:
        bot_settings_job_set(3)
    elif message.text == btn_settings_job_4:
        bot_settings_job_set(4)
    elif message.text == btn_settings_job_5:
        bot_settings_job_set(5)
    elif message.text == btn_settings_trip:
        bot_settings_trip()
    elif message.text == btn_settings_trip_0:
        bot_settings_trip_set(0)
    elif message.text == btn_settings_trip_1:
        bot_settings_trip_set(1)
    elif message.text == btn_settings_trip_2:
        bot_settings_trip_set(2)
    elif message.text == btn_settings_trip_3:
        bot_settings_trip_set(3)
    elif message.text == btn_settings_foe:
        bot_settings_foe()
    elif message.text == btn_settings_foe_none:
        bot_settings_foe_set(None)
    elif message.text == btn_settings_foe_friends:
        bot_settings_foe_set('friends')
    elif message.text == btn_settings_foe_static:
        bot_settings_foe_set('static')
    elif message.text == btn_settings_foe_arena:
        bot_settings_foe_set('arena')
    elif message.text == btn_settings_foe_winner:
        bot_settings_foe_set('winner')
    elif message.text == btn_settings_pets:
        bot_settings_pets()
    elif message.text == btn_settings_pets_yes:
        bot_settings_pets_set(True)
    elif message.text == btn_settings_pets_no:
        bot_settings_pets_set(False)
    elif message.text == btn_taxi:
        bot_taxi()
    elif message.text == btn_taxi_cancel:
        bot_taxi_set(None)
    elif message.text == btn_taxi_group_1:
        bot_taxi_group(1)
    elif message.text == btn_taxi_group_2:
        bot_taxi_group(2)
    elif message.text == btn_taxi_group_3:
        bot_taxi_group(3)
    elif message.text == btn_taxi_1:
        bot_taxi_set(1)
    elif message.text == btn_taxi_2:
        bot_taxi_set(2)
    elif message.text == btn_taxi_3:
        bot_taxi_set(3)
    elif message.text == btn_taxi_4:
        bot_taxi_set(4)
    elif message.text == btn_taxi_5:
        bot_taxi_set(5)
    elif message.text == btn_taxi_6:
        bot_taxi_set(6)
    elif message.text == btn_taxi_7:
        bot_taxi_set(7)
    elif message.text == btn_taxi_8:
        bot_taxi_set(8)
    elif message.text == btn_taxi_9:
        bot_taxi_set(9)
    elif message.text == btn_taxi_10:
        bot_taxi_set(10)
    elif message.text == btn_taxi_11:
        bot_taxi_set(11)
    elif message.text == btn_taxi_12:
        bot_taxi_set(12)
    elif message.text == btn_taxi_13:
        bot_taxi_set(13)
    elif message.text == btn_taxi_14:
        bot_taxi_set(14)
    elif message.text == btn_taxi_15:
        bot_taxi_set(15)
    elif message.text == btn_taxi_16:
        bot_taxi_set(16)
    elif message.text == btn_taxi_17:
        bot_taxi_set(17)
    elif message.text == btn_taxi_18:
        bot_taxi_set(18)
    elif message.text == btn_taxi_19:
        bot_taxi_set(19)
    elif message.text == btn_taxi_20:
        bot_taxi_set(20)
    elif message.text == btn_taxi_21:
        bot_taxi_set(21)
    elif message.text == btn_taxi_22:
        bot_taxi_set(22)
    elif message.text == btn_taxi_23:
        bot_taxi_set(23)
    elif message.text == btn_taxi_24:
        bot_taxi_set(24)
    elif message.text == btn_taxi_25:
        bot_taxi_set(25)
    elif message.text == btn_taxi_26:
        bot_taxi_set(26)
    elif message.text == btn_taxi_27:
        bot_taxi_set(27)
    elif message.text == btn_taxi_28:
        bot_taxi_set(28)
    elif message.text == btn_taxi_29:
        bot_taxi_set(29)
        
#
scheduleThread = Thread(target = game_bot.loop)
scheduleThread.daemon = True
scheduleThread.start()
#

'''
# Старая версия с обработкой ошибки
while True:
    try:
        telegram_bot.polling(none_stop=True)
    except Exception as e:
        time.sleep(15)
'''

# Без обработки ошибок
telegram_bot.polling(none_stop=True)