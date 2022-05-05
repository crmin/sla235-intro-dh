import csv
import sqlite3
import sys


def read_data_from_db(path):
    conn = sqlite3.connect(path, isolation_level=None)
    cur = conn.cursor()
    data = cur.execute('SELECT title, body FROM scrap').fetchall()
    return data

def main():
    sep = read_data_from_db('./sep.db')
    iep = read_data_from_db('./iep.db')
    data = sep + iep
    with open('title_body.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerows(data)

if __name__ == '__main__':
    main()
