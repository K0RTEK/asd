import vk_api
import re
import pandas as pd
import joblib
import psycopg2
import asyncio
import aiohttp
import yaml
from datetime import datetime
import os


with open('config.yaml', 'r') as file:
    config: dict = yaml.safe_load(file)
with open(os.path.join('C:\Flask Project\static\id_vk', 'vk.txt'), 'r') as group:
    group_id = group.read()

conn = psycopg2.connect(
    host=config['database']['host'],
    port=config['database']['port'],
    sslmode=config['database']['sslmode'],
    dbname=config['database']['dbname'],
    user=config['database']['user'],
    password=config['database']['password'],
    target_session_attrs=config['database']['target_session_attrs']
)

# тут надо написать input(), я заебался каждый раз вставлять ссылку




session = vk_api.VkApi(token=config['api-key']['key_3'])
session_2 = vk_api.VkApi(token=config['api-key']['key_2'])
session_3 = vk_api.VkApi(token=config['api-key']['key_4'])
vk = session.get_api()
vk_2 = session_2.get_api()
vk_3 = session_3.get_api()
model = joblib.load('text_model.pkl')
# Создаем курсор для выполнения запросов
cur = conn.cursor()


# получает Id по короткой ссылке интовым значением вида 123123123
def getid(group_url):
    return session.method("utils.resolveScreenName", {"screen_name": group_url[group_url.rfind("/") + 1::]})[
        'object_id']


async def get_group_members(group_id):
    url = 'https://api.vk.com/method/groups.getMembers'
    params = {
        'group_id': group_id,
        'v': '5.131',
        'access_token': config['api-key']['key_2'],
        'fields': 'id'
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            data = await resp.json()
            if 'response' in data:
                members = data['response']['items']
                ids = [member['id'] for member in members]
                return ids
            else:
                return []


async def get_all_group_members(group_ids):
    tasks = [get_group_members(group_id) for group_id in group_ids]
    results = await asyncio.gather(*tasks)
    return results


async def data():
    with open(os.path.join('C:\Flask Project\static\id_vk', 'vk.txt'), 'r') as group:
        group_id = group.read()
    group_ids = [getid(group_id)]
    data_array = {}
    all_group_members = await get_all_group_members(group_ids)
    for group_members in all_group_members:
        for member_id in group_members:
            url = 'https://api.vk.com/method/users.get'
            params = {
                'user_id': member_id,
                'v': '5.131',
                'access_token': config['api-key']['key_2'],
                'fields': 'is_closed'
            }
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as resp:
                    data = await resp.json()
            if 'response' in data and data['response']:
                is_closed = data['response'][0]['is_closed']
                if not is_closed:
                    url = 'https://api.vk.com/method/groups.get'
                    params = {
                        'user_id': member_id,
                        'v': '5.131',
                        'access_token': config['api-key']['key_3'],
                        'extended': 1,
                        'filter': 'groups',
                        'count': 1000
                    }
                    async with aiohttp.ClientSession() as session:
                        async with session.get(url, params=params) as resp:
                            data = await resp.json()
                    if 'response' in data:
                        groups = data['response']['items']
                        if 5 <= len(groups) <= 100:
                            g_ids = [group['id'] for group in groups]
                            print(g_ids)
                            data_array[member_id] = {key: value for key, value in
                                                     zip(g_ids, [get_group_posts(group['id'], 5) for group in groups if
                                                                 get_group_posts(group['id'], 1) is not None and (
                                                                     member_id, group) not in increment_insert()])}
                            print(data_array)
        print(data_array)
        return data_array


def increment_insert():
    cur.execute("SELECT user_id, vk_group_id FROM user_vk_group")
    rows = cur.fetchall()
    return rows


def clean_text(text):
    # Удалить все вхождения "id12345" или "club12345" в тексте
    text = re.sub(r"(id|club)\d+", "", text)

    # Удалить все ссылки из текста
    pattern = r'https?://\S+|www\.\S+|\S+@\S+'

    text = re.sub(pattern, '', text)

    text = re.sub(r'[^a-zA-Zа-яА-ЯёЁ0-9]', ' ', text)

    text = " ".join(text.split())

    return text


def find_most_frequent_word(words):
    word_counts = {}
    for word in words:
        if word.isalpha():
            if word not in word_counts:
                word_counts[word] = 1
            else:
                word_counts[word] += 1
    try:
        most_frequent_word = max(word_counts, key=word_counts.get)
    except:
        return None
    return most_frequent_word


# получение постов с группы с условиями
def get_group_posts(id_group, amount):
    try:
        response = vk.wall.get(
            owner_id='-' + str(id_group), count=amount, extended=1)
        posts = response['items']
        if response['count'] != 0:
            # выбор только не рекламных постов
            post_texts = [post['text']
                          for post in posts if not post.get('marked_as_ads')]
            post_texts = [clean_text(post)
                          for post in post_texts if clean_text(post) != '']
            post_texts = [model.predict([text])[0] for text in post_texts]
            post_texts = find_most_frequent_word(post_texts)
            print(post_texts)
            return post_texts
    except:
        pass


def get_user_posts(id_group):
    response = vk_2.wall.get(owner_id=id_group, count=10, extended=1)
    posts = response['items']
    if response['count'] != 0:
        # выбор только не рекламных постов
        dates = [datetime.fromtimestamp(post['date']).strftime(
            '%Y-%m-%d %H:%M:%S') for post in posts]
        post_texts = [post['text']
                      for post in posts if not post.get('marked_as_ads')]
        post_texts = [clean_text(post)
                      for post in post_texts if clean_text(post) != '']
        post_texts = [model.predict([text])[0] for text in post_texts]
        post_texts = [find_most_frequent_word(
            post_texts) for i in range(len(post_texts))]
        result = {key: value for key, value in zip(dates, post_texts)}
        return result
    else:
        return {'1970-01-01 00:00:00': 'Записи отсутствуют'}




def get_subscribers_info():
    with open(os.path.join('C:\Flask Project\static\id_vk', 'vk.txt'), 'r') as group:
        group_id = group.read()
    try:
        offset = 0
        next_offset = 1000
        all_members = []
        open_members = []
        while True:

            members = vk.groups.getMembers(group_id=getid(group_id), offset=offset)['items']
            if not members:
                break
            all_members.extend(members)
            not_closed = [i for i in vk.users.get(user_ids=members) if i['is_closed'] != False]
            open_members.extend(not_closed)
            offset += next_offset
        return len(all_members), len(open_members), len(all_members) - len(open_members)
    except:
        print("Ошибка")


def get_amount_of_posts():
    with open(os.path.join('C:\Flask Project\static\id_vk', 'vk.txt'), 'r') as group:
        group_id = group.read()
    posts = vk_3.wall.get(owner_id='-' + str(getid(group_id)), extended=1)
    return posts['count']


def get_group_photo():
    with open(os.path.join('C:\Flask Project\static\id_vk', 'vk.txt'), 'r') as group:
        group_id = group.read()
    group_info = vk.groups.getById(group_id=getid(group_id), fields=['photo_200', 'name'])
    avatar_url = group_info[0]['photo_200']
    name = group_info[0]['name']
    return avatar_url, name


def get_top_10_posts():
    with open(os.path.join('C:\Flask Project\static\id_vk', 'vk.txt'), 'r') as group:
        group_id = group.read()
    try:
        # Обработка полученных данных
        posts_likes = {}
        sliced_posts_likes = {}
        count_2 = 0
        offset = 0
        count = 100
        while True:
            posts = vk_3.wall.get(owner_id='-' + str(getid(group_id)), extended=1, count=count, offset=offset)
            if not posts['items']:
                break
            for post in posts['items']:
                post_id = f"https://vk.com/wall-{getid(group_id)}_{post['id']}"
                likes_count = post['likes']['count']
                posts_likes[post_id] = likes_count
            offset += count
        posts_likes_sorted = dict(sorted(posts_likes.items(), key=lambda x: x[1], reverse=True))
        for k, v in posts_likes_sorted.items():
            if count_2 < 10:
                sliced_posts_likes[k] = v
                count_2 += 1
        return sliced_posts_likes

    except vk_api.VkApiError as e:
        print('Произошла ошибка при работе с API:', e)
        return {}


# не понятно почему удаление пропусков в датафрейме не работает в функции save_data(), но работает отдельно
# в этой функции, поэтому ее не трогать
def clean_data_test():
    df = pd.read_csv('train_data.csv')
    df = df.dropna()
    df.to_csv('train_data.csv', index=False, lineterminator='', header=True)