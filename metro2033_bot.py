# -*- coding: utf-8 -*-

import hashlib
import json
import os
import random
import requests
import time
import zlib
import zipfile
import telemoji as emj

DEF_SESSION = '*' # раньше было так
DEF_SESSION = 'develop'

#--------------------------------------------------------------
#   Вспомогательные функции
#--------------------------------------------------------------

def is_today(timestamp):
    '''
        Проверка `timestamp` на принаддежность текущего дня
    '''
    time_utc = time.gmtime()
    time_cort = (time_utc.tm_year, time_utc.tm_mon, time_utc.tm_mday, 3, 0, 0, time_utc.tm_wday, time_utc.tm_yday, time_utc.tm_isdst)
    today_midnight = time.mktime(time_cort)
    return int(timestamp) >= int(today_midnight)

def str_to_time(time_str):
    '''
        Перевод строки в timestamp
    '''
    struct_time = time.strptime(str(time_str), '%Y-%m-%d %H:%M:%S')
    return int(time.mktime(struct_time))

def update(dest, src):
    '''
        Обновление `dest` данными из `src`
    '''
    for src_key in src:
        if src_key in dest and isinstance(dest[src_key], dict) and isinstance(src[src_key], dict):
            update(dest[src_key], src[src_key])
        else:
            dest[src_key] = src[src_key]

def get_path(file_name):
    '''
        Возвращает полный путь к файлу `file_name`
    '''
    return __file__.replace(__name__+'.py', str(file_name))

#--------------------------------------------------------------
#   Бот
#--------------------------------------------------------------

class Metro2033Bot:
    active = True
    api_url = 'http://vk.metrogame.net/metro/vk/vk_metro.php'
    config = { }
    config_file_name = 'metro2033_bot.cfg'
    error_code = 0
    fray_friends_exist = True
    friends_list = []
    game_data = { }
    gift_received_exist = True
    gift_thank_exist = True
    gifted_count = 0
    json_zip_file_name = 'metro2033_json.zip'
    pals_file_name = 'metro2033_bot.pals'
    log_file_name = 'metro2033_bot.log'
    robbed_count = 0
    sess = DEF_SESSION
    static_foe = None
    taxi = None
    try_pine_look = False
    tunnels = {}
    messanger = None
    unarmed_friends = []
    VK_id = ''
    VK_auth = ''

    #----------------------------------------------------------
    #   Инициализация
    #----------------------------------------------------------
    
    def __init__ (self, VK_id, VK_auth):
        '''
            Инициализация
        '''
        self.log('Инициализация бота')
        self.VK_id = VK_id
        self.VK_auth = VK_auth
        
        f = open(get_path(self.pals_file_name))
        friends_str = f.readlines()[0]
        f.close()

        self.friends_list = friends_str.split(',')
        
        random.shuffle(self.friends_list)

        self.config_load()
    
    #----------------------------------------------------------
    #   Вспомогательные методы
    #----------------------------------------------------------

    def delta_time(self,str_path):
        '''
            Возвращает форматированное дельту времеми между параметром `str_path` и текущем времени 
        '''
        delta_value = self.int(str_path) - self.int(f'time')
        delta_obj = time.gmtime(delta_value if delta_value >= 0 else 0)
        return time.strftime('%H:%M:%S',delta_obj)

    def search(self, path=[]):
        '''
            Построение маршрута
        '''
        result = False
        last = path[-1]
        for id in self.tunnels[last]:
            if path.count(id) > 0:
                continue
            path.append(id)
            if str(id) == str(self.taxi):
                return True
            result = result or self.search(path)
            if result:
                return True
            path.remove(id)
        return result

    def taxi_drive(self):
        '''
            Движение такси
        '''
        path = [self.str(f'player.loc')]
        if self.search(path):
            self.api_user_move(path[1])
        
        # Вывод маршрута для отладки 
        # for id in path:
        #   print(self.str(f'data.stations.{id}.name'))

    def is_VIP(self):
        '''
            Возвращает префикс "Код Метро2033"
        '''
        return self.int(f'player.stat.49.data') >= self.int(f'time')
    
    def get_job_name(self, job_id):
        '''
            Возвращает название работы по `job_id`
        '''
        if int(job_id) == 1:
            return 'Кормить свиней'
        elif int(job_id) == 2:
            return 'Собирать грибы'
        elif int(job_id) == 3:
            return 'Упаковывать чай'
        elif int(job_id) == 4:
            return 'Чистить оружие'
        elif int(job_id) == 5:
            return 'Патрулировать станцию'
        else:
            return ''

    def get_station_name(self, path):
        '''
            Возвращает наименование станции по id взятому по path
        '''
        id = self.str(path)
        return  self.str(f'data.stations.{id}.name')

    def get_trip_id(self):
        '''
            Возвращает доступный id задания начстанции
        '''
        if (self.int(f'player.ctx') != 0) or (int(self.config['trip_index']) == 0):
            return ''
        
        trip_id = self.str(f'player.loc') + str(self.config['trip_index'])
        if trip_id not in self.element(f'trip'):
            return ''
        
        qid = self.str(f'trip.{trip_id}.qid')
        if self.int(f'player.energy') < self.int(f'data.quests.{qid}.time'):
            return ''
        
        return trip_id
    
    def int(self, str_path):
        '''
            Возвращает числовое представление значения по пути `str_path`
        '''
        return int(self.element(str_path))

    def str(self, str_path):
        '''
            Возвращает строковое представление значения по пути `str_path`
        '''
        return str(self.element(str_path))

    def exist(self, str_path):
        '''
            Проверяет наличие объекта по пути `str_path`
        '''
        path = str_path.split('.')
        index = 0 
        ret_element = self.game_data
        while index < len(path):
            if path[index] not in ret_element:
                return False
            ret_element = ret_element[path[index]]
            index = index + 1
        return True

    def element(self, str_path):
        '''
            Возвращает объект по пути `str_path`
        '''
        path = str_path.split('.')
        index = 0 
        ret_element = self.game_data
        while index < len(path):
            if path[index] not in ret_element:
                return []
            ret_element = ret_element[path[index]]
            index = index + 1
        return ret_element
    
    def get_pets_status(self):
        '''
            Возвращает данные о питомцах и корме
        '''
        status = ''
        for pet_id in self.element(f'player.pets'):
            status = status + f'{emj.dog2} ' + self.str(f'player.pets.{pet_id}.nick')
            status = status + f' {emj.zap} ' + self.str(f'player.pets.{pet_id}.food')
        return status + f'\n{emj.cut_of_meat} Корм: ' + self.str(f'player.sack.15.num')

    def telegram_bot_status(self):
        '''
            Возвращает статус для телеграмма
        '''
        if self.active:
            status = f'{emj.green_circle} Включен {emj.stopwatch} ' + self.delta_time(f'reload') + '\n\n'
            
            player_loc = self.int(f'player.loc')
            status = status + f'{emj.metro} ' +  self.get_station_name(f'player.loc') + '\n'

            status = status + f'{emj.bust_in_silhouette} ' 
            trip_id = str(player_loc) + str(self.config['trip_index'])

            if trip_id not in self.element('trip'):
                trip_id = ''

            if (int(self.config['trip_index']) != 0) and (trip_id != ''):
                qid = self.str(f'trip.{trip_id}.qid')
                mob_id = self.str(f'data.quests.{qid}.mob')
                status = status + self.str(f'data.mobs.{mob_id}.name')
                status = status + ' (' + self.str(f'data.quests.{qid}.time') + ')'
            else:
                status = status + 'Нет'

            status = f'{status} {emj.zap} ' + self.str(f'player.energy')
            
            if (self.int(f'player.ctx') == 2) and (self.int(f'time') < self.int(f'tunn.arrived')):
                status = status + f' {emj.stopwatch} ' + self.delta_time(f'tunn.arrived')
            
            status = status + '\n'

            status = status + f'{emj.hammer_and_pick} '
            if self.int(f'jobs.job') > 0:
                status = status + self.get_job_name(self.int(f'jobs.job')) + f' {emj.stopwatch} ' + self.delta_time(f'jobs.finished')
            else:
                status = status + 'Нет'
            status = status + f'\n{emj.gift} ' + str(self.today_gift_send_count()) + ' / ' + str(self.today_gift_send_limit())
            status = status + '\n\n'


            status = status + f'{emj.crossed_swords} ' + (self.str(f'sign.81.size') if is_today(self.str(f'sign.82.at')) else '0')
            status = status + f' / ' + ('100' if self.is_VIP() else '50')
            status = status + f' {emj.trophy} ' + (self.str(f'sign.82.size') if is_today(self.str(f'sign.82.at')) else '0')
            if is_today(self.str(f'sign.82.at')):
                status = status + f' {emj.stopwatch} ' + self.delta_time(f'player.stat.51.data')
            
            clan_id = self.int(f'player.ally.clan')
            if self.int(f'time') < self.int(f'clan.{clan_id}.started'):
                status = status + f'\n\n{emj.fire} Начало клановой войны {emj.stopwatch}' + self.delta_time(f'clan.{clan_id}.started')
            elif self.int(f'time') < self.int(f'clan.{clan_id}.stopped'):
                status = status + f'\n\n{emj.fire} Клановая война {emj.stopwatch}' + self.delta_time(f'clan.{clan_id}.stopped')
                status = status + f'\n{emj.crossed_swords} ' + self.str(f'player.ally.fray_runs') + f' {emj.gun} ' + self.str(f'player.ally.fray_score')

            status = status + '\n\n' + self.get_pets_status()

            status = status + f'\n\n{emj.scroll} Квесты:\n'
            
            if self.int(f'tskd.pass') != 1:
                taskd_id = self.str(f'tskd.task')
                status = status + self.str(f'data.tasks.{taskd_id}.goal')
                status = status + ' [ ' + self.str(f'tskd.size')
                status = status + ' / ' + self.str(f'data.tasks.{taskd_id}.size') + f' ] {emj.stopwatch}\n'

            for task_id in self.element(f'task'):
                status = status + self.str(f'data.tasks.{task_id}.goal')
                status = status + ' [ ' + self.str(f'task.{task_id}.size') 
                status = status + ' / ' + self.str(f'data.tasks.{task_id}.size') + ' ]\n'
        else:
            status = f'{emj.red_circle} Выключен'
        return status
    
    def get_list_goods(self):
        '''
            Возвращает список товаров у продавцов
        '''
        goods_charact = {'health':'Здоровье', 'armour':'Защита','mrks':'Меткость', 'endr':'Выносливость', 'luck':'Ярость'}
        goods = {}
        for id in self.element(f'shop'):
            idx = self.int(f'shop.{id}.idx')
            if idx not in goods:
                item = self.element(f'data.goods.{idx}')
                if int(item['gems'] > 0):
                    continue
                item_description = str(item['name']) + '\n'
                item_description = item_description + emj.moneybag + str(item['gold'])
                
                sack_idx = int(int(item['part'])/10)
                if not self.exist(f'player.sack.{sack_idx}'):
                    continue
                player_item_idx = self.element(f'player.sack.{sack_idx}.idx')
                player_item = self.element(f'data.goods.{player_item_idx}')
                add_item = False
                for charact in goods_charact:
                    if (charact in item) and (charact in player_item):
                        delta_charact = int(item[charact]) - int(player_item[charact])
                        item_description = item_description + '\n' + goods_charact[charact] + ': ' + ('+' if delta_charact > 0 else '') +str(delta_charact)
                        if delta_charact>0:
                            add_item = True
                if not add_item:
                    continue
                    pass
                goods[idx] = item_description
            group_id = int(int(id)/10)
            
            goods[idx] = goods[idx] + '\n' + str(group_id)
        goods_sorted = dict(sorted(goods.items()))
        goods_message = ''
        for idx in goods_sorted:
            goods_message = goods_message + ('' if goods_message == '' else '\n\n') + goods_sorted[idx]
        return goods_message
    
    def today_gift_send_count(self):
        '''
            Возвращает количество отправленых сегодня подарков
        '''
        if is_today(self.int(f'sign.102.at')):
            return self.int(f'sign.102.size')
        else:
            return 0
    
    def today_gift_send_limit(self):
        '''
            Возвращает максимальное количество отправлений подарков
        '''
        return int(20 if self.is_VIP() else 10)

    def send_gift_online_user(self):
        '''
            Отправка случайному другу который недавно заходил
        '''
        if self.today_gift_send_count() >= (self.today_gift_send_limit()):
            return
        
        random.shuffle(self.friends_list)

        for friend_id in self.friends_list:
            if friend_id not in self.element(f'units'):
                continue
            if 'visited' not in self.element(f'units.{friend_id}') :
                continue
            if  (self.int(f'time') - str_to_time(self.str(f'units.{friend_id}.visited'))) > 2 * 24 * 60 * 60:
                continue
            if is_today(self.int(f'units.{friend_id}.gifted')):
                continue
            self.api_gift_send(0, friend_id, 1)
            return
        self.messanger('Нет подходящих пользователей для отправки')
    
    def check_loot(self, response):
        '''
            Отправка сообщения в телеграмм если получен лут
        '''
        if 'loot' in response:
            loot_id = 170000 + int(list(response['loot'].keys())[0])
            loot_name = self.str(f'data.goods.{loot_id}.name')
            craft_id = self.int(f'data.goods.{loot_id}.craft')
            craft_name = self.str(f'data.craft.{craft_id}.name')
            self.messanger(f'{emj.package} {craft_name}.{loot_name}')
    
    def in_event(self, timestamp, event_name):
        '''
            Проверка вхождения timestamp в пределы события event_name
        '''
        if not self.exist(f'data.events.{event_name}'):
            return False
        return (int(timestamp) > self.int(f'data.events.{event_name}.min')) and (int(timestamp) < self.int(f'data.events.{event_name}.max'))

    #----------------------------------------------------------
    #   Логирование
    #----------------------------------------------------------

    def log(self, message, telegram = None):
        '''
            Добавление в лог `message`
        '''
        if telegram:
            self.messanger(message)

        f = open(get_path(self.log_file_name), 'a', encoding = 'utf-8')
        message = time.strftime('[%d.%m.%Y %H:%M:%S] ') + str(message)
        print(message)
        f.write(message + '\n')
        f.close()

    def json_log(self, method, json_data):
        '''
            Добавление JSON данных в архив
        '''
        file_name = str(int(time.time())) + f'.{method}.json'
        zf = zipfile.ZipFile(
            file = get_path(self.json_zip_file_name),
            mode = 'a',
            compression = zipfile.ZIP_DEFLATED,
            compresslevel = 5
        )
        zf.writestr(file_name, json.dumps(json_data))
        zf.close()
    
    #----------------------------------------------------------
    #   Конфиг
    #----------------------------------------------------------

    def config_load(self):
        '''
            Загрузка конфига
        '''
        if os.path.isfile(get_path(self.config_file_name)):
            f = open(get_path(self.config_file_name),'r')
            config_data = f.readlines()[0]
            self.config = json.loads(config_data)
            self.log('Загружен конфиг')
        else:
            self.config = {
                'fray_mode' : None,
                'job_index' : 0,
                'trip_index' : 0,
                'use_pet': False
            }
            self.log('Загружен конфиг по умолчанию')

    def config_save(self):
        '''
            Сохранение конфига
        '''
        f = open(get_path(self.config_file_name), 'w')
        f.write(json.dumps(self.config))
        f.close()
        self.log('Сохранение конфига')

    #----------------------------------------------------------
    # Бесконечный цыкл
    #----------------------------------------------------------

    def loop(self):
        '''
            Главный цикл в отдельном потоке
        '''
        while True:
            
            if not(self.active) : 
                # Бот деактивирован
                continue
            
            #--------------------------------------------------
            #   Увеличиваем таймер
            #--------------------------------------------------

            begin_timestamp = time.time()
            while (time.time() - begin_timestamp) < 1:
                #  Ждем разницу с началом цикла в 1 секунду
                pass
              
            if 'time' in self.game_data:
                # Увеличиваем таймер
                self.game_data['time'] = self.int(f'time') + 1
            
            # Поиск не взятых заданий
            take_task = None 
            if self.exist(f'tskd.pass') and self.int(f'tskd.pass') == -1:
                take_task = self.str(f'tskd.task')

            if take_task is None and self.exist(f'task'):
                for task_id in self.element(f'task'):
                    if self.int(f'task.{task_id}.pass') == -1:
                        take_task = task_id
                        break

            if self.exist('player'):
                clan_id = self.int(f'player.ally.clan')

            #--------------------------------------------------
            #   Базовая логика
            #--------------------------------------------------

            #  Нет сессии
            if self.sess == DEF_SESSION:
                self.api_user_auth()

            # Недействительная сессия
            elif self.error_code == 1203:
                self.log('Недействительная сессия')
                self.sess = DEF_SESSION

            # Время обновить данные
            elif self.int(f'time') >= self.int('reload'):
                self.log('Обновление данных')
                self.sess = DEF_SESSION

            # Ежедневный бонус
            elif self.int(f'player.bon') == 0:
                self.api_user_bonus_upgrade()
            
            # Проверка подарков
            elif self.try_pine_look:
                self.try_pine_look = False
                loc = self.int(f'player.loc')
                if self.in_event(self.int(f'time'),'pine') and self.exist(f'pine.{loc}') and not is_today(self.int(f'pine.{loc}.looked')):
                    self.api_pine_look()
                if self.in_event(self.int(f'time'),'anniv') and self.exist(f'pine.{loc}') and not self.in_event(self.int(f'pine.{loc}.looked'),'anniv'):
                    self.api_pine_look()

            # Подверждаем задания
            elif take_task is not None:
                self.api_task_take(take_task)

            # Начинаем работу
            elif (int(self.config['job_index']) > 0) and (self.int(f'jobs.job') == 0) and (self.int(f'player.home') == self.int(f'player.loc')):
                self.api_jobs_take(self.config['job_index'])
            
            # Забираем зарплату
            elif (self.int(f'jobs.job') > 0) and (self.int(f'time') > self.int(f'jobs.finished')):
                self.api_jobs_earn()
            
            # Вызов питомца
            elif self.int(f'player.ctx') == 1 and self.config['use_pet'] and self.int(f'player.pets.1.food') > 0 and len(self.element(f'fray.foe')) == 2:
                self.api_fray_summon()

            # Завершение поединка
            elif self.int(f'player.ctx') == 1:
                self.api_fray_stop()

            # Патруль
            elif self.int(f'player.ctx') == 5:
                tunn_loc = self.int(f'tunn.loc')
                guard = self.element(f'data.guards.{tunn_loc}')
                if str(guard['cond']) == 'come':
                    # Проходная станция
                    self.api_tunn_duty()
                elif str(guard['cond']) == 'pass':
                    # По пропускам
                    stat_data = self.int(f'player.stat.40.data')
                    if (stat_data & 1 << int(guard['data']) - 1) != 0:
                        # Есть пропуск
                        self.api_tunn_duty()
                    else:
                        self.api_tunn_back()
                else:
                    # Атакуем патруль
                    self.api_tunn_fray()
            
            # Клановые войны
            elif (self.int(f'player.ctx') == 0) and (self.int(f'time') > self.int(f'clan.{clan_id}.started')) and (self.int(f'time') < self.int(f'clan.{clan_id}.stopped')):
                self.api_clan_fight()

            # Поединки
            elif (self.int(f'player.ctx') == 0) and (self.int(f'time') > self.int(f'player.stat.51.data')) and (self.config['fray_mode'] is not None):
                if self.config['fray_mode'] == 'friends' and self.fray_friends_exist:
                    # Атака друзей
                    friend_foe = ''
                    for friend_id in self.friends_list:
                        if self.unarmed_friends.count(friend_id) > 0:
                            continue
                        if friend_id not in self.game_data['units']:
                            continue
                        unit = self.game_data['units'][friend_id]
                        if int(unit['level']) > self.int(f'player.level'):
                            continue
                        if is_today(unit['frayed']):
                            continue
                        friend_foe = friend_id
                        break
                    if friend_foe == '':
                        self.fray_friends_exist = False
                    else:
                        self.api_fray_start(11, friend_foe, 0)
                        if self.error_code == 1202:
                            self.unarmed_friends.append(friend_foe)
                elif (self.config['fray_mode'] == 'winner'):
                    self.api_fray_start(21, '177712343', 0)
                elif (self.config['fray_mode'] == 'static') and (self.static_foe is not None):
                    self.api_fray_start(21, self.static_foe, 0)
                elif (self.config['fray_mode'] == 'arena') or (self.config['fray_mode'] == 'static'):
                    # Арена
                    if ('foe' not in self.game_data) or (self.str(f'foe') == ''):
                        self.api_fray_arena()
                    else:
                        diff_point = 25 # TODO перенести в настройки
                        player_ap = self.int(f'player.ap')
                        player_accuracy = self.int(f'player.stat.1.data')
                        player_endurance = self.int(f'player.stat.2.data')
                        player_fury = self.int(f'player.stat.3.data')
                        
                        foe = self.str(f'foe')

                        enemy_ap = self.int(f'units.{foe}.ap')
                        enemy_accuracy = self.int(f'units.{foe}.stat.1.data')
                        enemy_endurance = self.int(f'units.{foe}.stat.2.data')
                        enemy_fury = self.int(f'units.{foe}.stat.3.data')

                        attack = True # TODO attack = settings.FrayFrac[enemy_frac]
                        attack = attack and ((player_accuracy + player_ap) - (enemy_accuracy + enemy_ap) > diff_point)
                        attack = attack and ((player_endurance + player_ap) - (enemy_endurance + enemy_ap) > diff_point)
                        attack = attack and ((player_fury + player_ap) - (enemy_fury + enemy_ap) > diff_point)
                        
                        if attack:
                            self.api_fray_start(21, self.str(f'foe'), 0)
                        else:
                            self.log('Не подходящий соперник')
                            self.game_data['foe'] = ''
            
            # Такси
            elif (self.int(f'player.ctx') == 0) and (self.taxi is not None):
                if int(self.taxi) == self.int(f'player.loc'):
                    self.taxi = None
                else:
                    self.taxi_drive()

            # Обыск палаток
            elif self.robbed_count < 10:
                pal_vip = ''
                pal = ''
                for friend_id in self.friends_list:
                    if friend_id not in self.game_data['units']:
                        continue
                    unit = self.game_data['units'][friend_id]
                    if 'visited' not in unit :
                        continue
                    if  (self.int(f'time') - str_to_time(unit['visited'])) > 2 * 24 * 60 * 60:
                        continue
                    if is_today(unit['robbed']):
                        continue
                    if ('49' in unit['stat']) and (int(unit['stat']['49']['data']) > self.int(f'time')):
                        pal_vip = friend_id
                        break
                    else:
                        pal = friend_id
                if (pal_vip == '') and (pal == ''):
                    self.robbed_count = 10
                else:
                    self.api_user_frisk(pal_vip if pal_vip != '' else pal)
            
            # Открытие подарков
            elif self.gift_received_exist:
                gift_received_id = ''
                for gift_id in self.game_data['player']['gift']:
                    gift = self.game_data['player']['gift'][gift_id]
                    if (int(gift['expired']) > self.int(f'time')) and (int(gift['state']) == 0):
                        gift_received_id = gift_id
                        break
                if gift_received_id == '':
                    self.gift_received_exist = False
                else:
                    self.api_gift_open(gift_received_id)
            
            # Отправление благодарности
            elif (self.gift_thank_exist) and (self.today_gift_send_count() < self.today_gift_send_limit()):
                gift_received_id = ''
                gift_received_doer = ''
                for gift_id in self.game_data['player']['gift']:
                    gift = self.game_data['player']['gift'][gift_id]
                    unit = self.game_data['units'][gift['doer']]
                    if (int(gift['expired']) > self.int(f'time')) and (int(gift['state']) == 1) and (not is_today(unit['gifted'])):
                        gift_received_id = gift_id
                        gift_received_doer = gift['doer']
                        break
                if gift_received_id == '':
                    self.gift_thank_exist = False
                else:
                    self.api_gift_send(gift_received_id, gift_received_doer, '1')
            
            # Берем задание начстанции
            elif self.get_trip_id() != '':
                self.api_trip_take(self.get_trip_id())
            
            # Проехали тунель
            elif (self.int(f'player.ctx') == 2) and (self.int(f'time') > self.int(f'tunn.arrived')):
                self.api_tunn_pass()

    #----------------------------------------------------------
    #   Подготовка и отправка запроса
    #----------------------------------------------------------

    def server_request(self, data):
        '''
            Отправка POST запроса
        '''
        
        data['hash'] = random.randint(1, 4294967295)
        data['sess'] = self.sess
        data['user'] = self.VK_id + self.VK_auth
        
        data = dict(sorted(data.items()))

        for_md5 = json.dumps(data)\
            .replace(' ', '')\
            .replace('{', '')\
            .replace('}', '')\
            .replace(',"', '')\
            .replace('"', '')\
            .replace(':', '=')
        
        data['auth'] = hashlib.md5(for_md5.encode()).hexdigest()
        data['user'] = self.VK_id
        
        response = requests.post(self.api_url, data)
        response_data = zlib.decompress(response.content)
        response_json = json.loads(response_data)
        
        self.json_log(data['method'], response_json)

        if 'error' in response_json:
            self.error_code = int(response_json['error']['code'])
        else:
            self.error_code = 0
            
            if data['method'] == 'user.auth': 
                self.game_data.clear()
            
            update(self.game_data, response_json)

            if ('player' in response_json) and ('loc' in response_json['player']):
                self.try_pine_look = True
        return response_json
    
    #----------------------------------------------------------
    #   Методы обращения с api сервером Метро2033
    #----------------------------------------------------------
    
    def api_clan_fight(self):
        '''
            Атака в клановой войне
        '''
        self.log('Атака в клановой войне')
        
        data = {
            'method' : 'clan.fight',
            'pay': 0
        }

        self.server_request(data) 

    #----------------------------------------------------------
    
    def api_clan_reload(self):
        '''
            Обновление информации о клане
        '''
        self.log('Обновление информации о клане')
        
        data = {
            'method' : 'clan.reload'
        }

        self.server_request(data) 

    #----------------------------------------------------------
    
    def api_clan_trophy(self):
        '''
            Забираем награду в конце клановой войны
        '''
        self.log('Забираем награду в конце клановой войны')
        
        data = {
            'method' : 'clan.trophy'
        }

        self.server_request(data) 

    #----------------------------------------------------------
    
    # TODO method:"fray.ammo" idx: skip:
    
    #----------------------------------------------------------

    def api_fray_arena(self):
        '''
            Поиск противника на арене
        '''
        
        self.log('Поиск на арене')
        
        data = {
            'method' : 'fray.arena',
        }

        self.server_request(data) 
    
    #----------------------------------------------------------
    
    def api_fray_start(self, ctx, user_id, mode):
        '''
            Начало поединка
        '''
        
        if int(ctx) == 11:
            self.log(f'Атакуем друга #{user_id}')
        else:
            self.log(f'Атакуем #{user_id}')
        
        data = {
            'ctx' : ctx,
            'foe' : user_id,
            'method' : 'fray.start',
            'mode' : mode,
            'pay' : '0'
        }

        self.server_request(data)
        
        if self.error_code == 0:
            if self.int(f'fray.win') == 1:
                if self.int(f'fray.ctx') == 21:
                    self.static_foe = user_id
                self.log('Победа')
            else:
                if self.int(f'fray.ctx') == 21:
                    self.static_foe = None
                self.log('Поражение')

    #----------------------------------------------------------

    def api_fray_stop(self):
        '''
            Завершение поединка
        '''

        self.log('Завершение поединка')
        
        data = {
            'method' : 'fray.stop',
        }

        response = self.server_request(data)
        self.check_loot(response)

        self.game_data['foe'] = ''
    
    #----------------------------------------------------------

    def api_fray_summon(self):
        '''
            Вызов питомца в поединок
        '''
        self.log('Вызов питомца')
        data = {
            'method' : 'fray.summon',
            'skip': '0'
        }

        self.server_request(data)

    #----------------------------------------------------------

    def api_gift_open(self, gift_id):
        '''
            Открытие подарка
        '''
        
        self.log(f'Открытие подарка #{gift_id}')
        
        data = {
            'gid' : gift_id,
            'method' : 'gift.open',
        }
        self.server_request(data)
    
    #----------------------------------------------------------
    
    def api_gift_send(self, gift_id, user_id, gift_type):
        '''
            Отправка подарка
        '''

        self.log(f'Отправка подарка #{user_id}')
        
        data = {
            'discount': '0',
            'gid' : gift_id,
            'method' : 'gift.send',
            'type' : gift_type,
            'uid' : user_id,
        }
        self.server_request(data)
    
    #----------------------------------------------------------
    
    def api_jobs_earn(self):
        '''
            Забрать зарплату
        '''

        self.log('Забираем зарплату')
        
        data = {
            'method' : 'jobs.earn',
        }

        self.server_request(data)
    
    #----------------------------------------------------------

    def api_jobs_stop(self):
        '''
            Прерывание работы
        '''
        
        self.log('Прерываем работу')
        
        data = {

            'method' : 'jobs.stop',
        }

        self.server_request(data)

    #----------------------------------------------------------
    
    def api_jobs_take(self, job_id):
        '''
            Начало работы
        '''

        self.log('Начинаем работу ' + self.get_job_name(job_id))
        
        data = {
            'job': job_id,
            'method' : 'jobs.take',
        }

        self.server_request(data)
    
    #----------------------------------------------------------

    def api_pets_feed(self, slot, num):
        '''
            Кормление питомца
        '''

        self.log(f'Кормление питомца #{slot} {num}')
        
        data = {
            'method' : 'pets.feed',
            'num' : num,
            'slot': slot,
        }

        self.server_request(data)
    #----------------------------------------------------------

    def api_pine_look(self):
        '''
            Открытие подарка
        '''
        loc_name = self.get_station_name(f'player.loc')

        self.log(f'Открываем подарок на "{loc_name}"',telegram = True)
        
        data = {
            'method' : 'pine.look'
        }

        response = self.server_request(data)
        if 'error' in response:
            self.log(f'Ошибка', telegram=True)
        else:
            self.log(f'Успешно', telegram=True)

    #----------------------------------------------------------
    
    # TODO method:"task.stations" - обновление заданий 

    #----------------------------------------------------------
   
    def api_task_take(self, task):
        '''
            Подверждение нового задания
        '''

        self.log(f'Подтверждаем задание #{task}')
        
        data = {
            'method' : 'task.take',
            'task': task,
        }

        self.server_request(data)
    
    #----------------------------------------------------------
    
    def api_trip_take(self, pos):
        '''
            Начать выполнение задания начстанции
        '''
        
        self.log(f'Выполняем задание начстанции #{pos}')
        
        data = {
            'method' : 'trip.take',
            'pos': pos,
        }
        
        self.server_request(data)

    #----------------------------------------------------------

    def api_tunn_back(self):
        '''
            Выход со станции
        '''
        tunn_loc_name = self.get_station_name(f'tunn.loc')

        self.log(f'Патруль, уходим со станции "{tunn_loc_name}"', True)

        data = {
            'method' : 'tunn.back'
        }

        self.server_request(data)

    #----------------------------------------------------------

    def api_tunn_duty(self):
        '''
            Вход на станцию
        '''
        tunn_loc_name = self.get_station_name(f'tunn.loc')

        self.log(f'Входим на станцию "{tunn_loc_name}"', True)

        data = {
            'method' : 'tunn.duty',
            'pay' : '0'
        }

        self.server_request(data)

    #----------------------------------------------------------

    def api_tunn_fray(self):
        '''
            Атака патруля
        '''
        tunn_loc_name = self.get_station_name(f'tunn.loc')

        self.log(f'Атакуем патруль на станции "{tunn_loc_name}"', True)

        data = {
            'method' : 'tunn.fray'
        }

        self.server_request(data)

    #----------------------------------------------------------

    def api_tunn_pass(self):
        '''
            Выход из тунеля
        '''
        
        self.log('Проехали тунель')

        data = {
            'method' : 'tunn.pass',
            'pay' : '0'
        }

        self.server_request(data)

    #----------------------------------------------------------

    def api_user_auth(self):
        '''
            Авторизация и получение сессии
        '''
        
        self.log('Авторизация')

        pals = ','.join(self.friends_list)

        data = {
            'group': '1',
            'lmenu' : '1',
            'method' : 'user.auth',
            'pals' : pals
        }
        response = self.server_request(data)
        
        if 'sess' not in response: return

        self.sess = response['sess']
        self.game_data['reload'] = int(response['time']) + 60 * 60
        self.fray_friends_exist = True
        self.gift_received_exist = True
        self.gift_thank_exist = True
        self.gifted_count = 0
        self.robbed_count = 0
        for unit_id in self.game_data['units']:
            unit = self.game_data['units'][unit_id]
            if 'gifted' in unit and is_today(unit['gifted']):
                self.gifted_count = self.gifted_count + 1
            if 'robbed' in unit and is_today(unit['robbed']):
                self.robbed_count = self.robbed_count + 1
        
        # Заполнение tunnels
        self.tunnels = {}
        for tunnel_id in self.game_data['data']['tunnels']:
            from_id = self.str(f'data.tunnels.{tunnel_id}.from')
            dest_id = self.str(f'data.tunnels.{tunnel_id}.dest')
            if from_id not in self.tunnels:
                self.tunnels[from_id] = []
            self.tunnels[from_id].append(dest_id)
            if dest_id not in self.tunnels:
                self.tunnels[dest_id] = []
            self.tunnels[dest_id].append(from_id)
        pass

    #----------------------------------------------------------

    def api_user_bonus_upgrade(self):
        '''
            Открытие ежедневного бонуса
        '''
        
        self.log('Открытие ежедневного бонуса')
        
        data = {
            'method' : 'user.bonus.upgrade'
        }
        self.server_request(data)

    #----------------------------------------------------------

    def api_user_frisk(self, user_id):
        '''
            Обыск палатки user_id пользователя
        '''
        
        self.log(f'Обыск палатки #{user_id}')
        
        data = {
            'method' : 'user.frisk',
            'pal' : user_id
        }
        self.server_request(data)
        
        if self.error_code == 0:
            self.robbed_count = self.robbed_count + 1

    #----------------------------------------------------------

    def api_user_grow(self, stat):
        '''
            Увеличение характеристик
        '''
        
        self.log(f'Увеличение характеристики #{stat}')
        
        data = {
            'method' : 'user.grow',
            'stat' : stat
        }
        self.server_request(data)

    #----------------------------------------------------------
    
    # TODO method:"user.info" uids:"184534526"
    
    #----------------------------------------------------------
    
    def api_user_move(self, loc):
        '''
            Переход на другую станцию
        '''
        from_loc_name = self.get_station_name(f'player.loc')
        to_loc_name = self.str(f'data.stations.{loc}.name')
        self.log(f'Переход со станции "{from_loc_name}" на "{to_loc_name}"', True)
        
        data = {
            'loc' : loc,
            'method' : 'user.move',
        }
        self.server_request(data)
        
    #----------------------------------------------------------
    
    # TODO method:"user.ping"
    
    #----------------------------------------------------------