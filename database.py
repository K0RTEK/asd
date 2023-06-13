import numpy as np
import asyncio
from main import get_user_posts, data, conn, get_top_10_posts, group_id,getid

# Создаем курсор для выполнения запросов
cur = conn.cursor()
user_vk_group = "INSERT INTO user_vk_group (user_id, vk_group_id, vk_group_url) VALUES (%s, %s, %s)"
vk_group_id_topic = "INSERT INTO vk_group_id_topic (vk_group_id, topic_group) VALUES (%s, %s)"
user_vk_characteristic = "INSERT INTO user_vk_characteristic (user_id, user_posts_date,topic_user) VALUES (%s, %s, %s)"
top_10_posts_by_group = "INSERT INTO top_10_posts_by_group (group_id, post_url, amount_of_likes) VALUES (%s, %s, %s)"

async def dato():
    return await data()


def users_subscriptions():
    # Получаем данные из словаря
    doto = asyncio.run(dato())
    for user_id, group_data in doto.items():
        for group_id, group_topic in group_data.items():
            # Задаем значения для user_vk_group

            values_user = (user_id, group_id)
            if values_user in user_vk_group_insert():
                pass
            else:
                values_user = (user_id, group_id, f"https://vk.com/public{group_id}")
                # Выполняем запрос на добавление данных в таблицу
                cur.execute(user_vk_group, values_user)
                # Фиксируем изменения в базе данных
                conn.commit()
        for group_id, group_topic in group_data.items():
            # Задаем значения для vk_group_id_topic
            values_group = (group_id, group_topic)
            if vk_group_id_topic_insert(values_group[0]) is None:
                pass
            else:
                # Выполняем запрос на добавление данных в таблицу
                cur.execute(vk_group_id_topic, values_group)
                # Фиксируем изменения в базе данных
                conn.commit()
        data_user = get_user_posts(user_id)
        for post_date, user_topic in dict(data_user).items():
            if (user_id, post_date) in user_id_insert():
                pass
            else:
                values_user_page = (user_id, post_date, user_topic)
                cur.execute(user_vk_characteristic, values_user_page)
                conn.commit()

    # Закрываем курсор и соединение
    cur.close()
    conn.close()


def vk_group_id_topic_insert(group_id):
    cur.execute("SELECT vk_group_id FROM vk_group_id_topic")
    rows = cur.fetchall()
    values_array = [row[0] for row in rows]
    new_arr = np.sort(values_array)
    index = np.searchsorted(new_arr, group_id)
    if index != len(new_arr) and new_arr[index] == group_id:
        return None
    else:
        return 1


def user_id_insert():
    cur.execute("SELECT user_id, user_posts_date FROM user_vk_characteristic")
    rows = cur.fetchall()
    rows = [(row[0], row[1].strftime('%Y-%m-%d %H:%M:%S')) for row in rows]
    return rows


def user_vk_group_insert():
    cur.execute("SELECT user_id, vk_group_id FROM user_vk_group")
    rows = cur.fetchall()
    return rows

def top_10_posts():
    g_id = getid(group_id)
    cur.execute(f"delete from top_10_posts_by_group where group_id = {g_id}")
    posts = get_top_10_posts()
    for post in posts.items():
        values_posts = (g_id, post[0], post[1])
        cur.execute(top_10_posts_by_group, values_posts)
        conn.commit()


top_10_posts()
# users_subscriptions()