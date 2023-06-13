import pandas as pd
from main import clean_data_test, getid, clean_text, vk


def save_data():
    df = pd.DataFrame(columns=['text', 'tag'])
    data = pd.read_excel('vk_groups.xlsx')
    # vk_api ругается если слишком часто получать id группы через ссылку
    # но отдельным генератором id_vk получить id групп можно(дебилизм)
    urls = [getid(url) for url in data['ссылка'] if 'https' in url]
    idx = 0
    for url in urls:
        try:
            for i in get_train_posts(url, 100):
                curr_data = {'text': i, 'tag': data['тематика'][idx]}
                df.loc[len(df)] = curr_data
            idx += 1
        except:
            pass
    print(df)
    df['text'] = list(map(clean_text, df['text']))
    df.to_csv('train_data.csv', index=False, lineterminator='', header=True)
    clean_data_test()


def get_train_posts(id_group, amount):
    try:
        response = vk.wall.get(
            owner_id='-' + str(id_group), count=amount, extended=1)
        posts = response['items']
        if response['count'] != 0:
            # выбор только не рекламных постов
            post_texts = [post['text'] for post in posts if not post.get('marked_as_ads')]
            post_texts = [clean_text(post) for post in post_texts if clean_text(post) != '']
            return post_texts
    except:
        pass


save_data()