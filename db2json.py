import json
import sqlite3
import sys


def read_data_from_db(path):
    conn = sqlite3.connect(path, isolation_level=None)
    cur = conn.cursor()
    data = cur.execute('SELECT title, abstract, contents FROM scrap').fetchall()
    return [dict(zip(('title', 'abstract', 'contents'), each)) for each in data]

def reformat(db_list):
    data = {}
    for each in db_list:
        title = each['title']

        if title in data:
            print(f'[WARN] duplicated title: {title}')
            sys.stdout.flush()

        data[title] = {
            'contents': json.loads(each['contents']),
            'abstract': each['abstract'].strip(),
        }
    return data

def main():
    sep = read_data_from_db('./sep.db')
    iep = read_data_from_db('./iep.db')
    data = reformat(sep + iep)
    with open('title_abstract_contents.json', 'w') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

if __name__ == '__main__':
    main()
