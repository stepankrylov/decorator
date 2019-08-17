import requests
import time
import json
from datetime import datetime
import os

def param_logger(path):

    def logger(old_func):

        count = 0
        def new_func(*args, **kwargs):
            nonlocal count, path
            count += 1
            t_start = datetime.now()
            old_func(*args, **kwargs)
            t_finish = datetime.now()
            data = old_func(*args, **kwargs)
            file_name = f'{old_func.__name__}-{datetime.now().strftime("%Y.%m.%d %H.%M.%S")}-{count}.txt'
            full_path = os.path.join(path, file_name)
            with open(full_path, 'w', encoding='utf-8') as file:
                file.write('Название функции: ' + str(old_func.__name__) + '\n')
                file.write('Дата теста: ' + str(datetime.now().strftime("%d.%m.%Y")) + '\n')
                file.write('Номер теста: № ' + str(count) + '\n')
                file.write('Аргументы:' + '\n' + 'args:' + str(args) + ' \n' + 'kwargs:' + str(kwargs) + '\n')
                file.write('Время начала теста: ' + str(t_start.strftime("%H:%M:%S:%f")) + '\n')
                file.write('Время окончания теста: ' + str(t_finish.strftime("%H:%M:%S:%f")) + '\n')
                file.write('Результат выполнения функции: ' + str(data) + '\n')
                file.write('Время исполнения функции: ' + str(t_finish - t_start) + '\n')
            return data

        return new_func
        
    return logger

@param_logger('d:/PYTHON/decorator/logs')
def spy_game(TOKEN, params, id):  
    
    friends_get_params = params.copy()
    friends_get_params['user_id'] = id
    response = requests.get('https://api.vk.com/method/users.get', params=friends_get_params)
    print('Пользователь: ', response.json()['response'][0]['first_name'],  response.json()['response'][0]['last_name'])

    response = requests.get('https://api.vk.com/method/friends.get', params=friends_get_params)
    ids_user_friends = response.json()['response']['items']

    response = requests.get('https://api.vk.com/method/groups.get', params=friends_get_params)
    groups_user = response.json()['response']['items']

    pause = 0.34
    group_list = []
    progress_complete = 0

    for id_friend in ids_user_friends:
        
        progress_complete += (1/len(ids_user_friends))*100
        print('Выполнено: ', round(progress_complete, 1), '%')

        friends_get_params['user_id'] = id_friend
        response = requests.get('https://api.vk.com/method/users.get', params=friends_get_params)
        try:
            response = requests.get('https://api.vk.com/method/groups.get', params=friends_get_params)
            groups_user_friend = response.json()['response']['items']
        except KeyError:
            pass
        group_list += groups_user_friend
        time.sleep(pause)

    groups = set(groups_user).difference(set(group_list))

    file_list = []
    friends_get_params['extended'] = 1
    friends_get_params['fields'] = 'members_count'

    for id_group in groups:
        friends_get_params['group_id'] = id_group  
        response = requests.get('https://api.vk.com/method/groups.getById', params=friends_get_params)
        id_groups = response.json()['response'][0]['id']
        name_groups = response.json()['response'][0]['name']
        member_count_groups = response.json()['response'][0]['members_count']
        file_dict = {'name': name_groups, 'id': id_groups, 'members_count': member_count_groups}
        file_list.append(file_dict)
        time.sleep(pause)

    with open('groups.json', 'w', encoding='UTF-8') as file:
        json.dump(file_list, file, ensure_ascii=False)

    return file_dict

if __name__ == "__main__":
    TOKEN = '31a86da3c08ccd684276f1cdf7728e6e5428ededa073225ebcc10386881f291a138383412f3940faf77ef'
    spy_game(TOKEN, {
            'access_token': TOKEN,
            'order': 'hints',
            'v': '5.52'
            }, id=171691064)