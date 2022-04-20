import sys
from threading import Thread

from wikis import SEP, IEP


def scrap(wikiClass, path):
    wiki = wikiClass()
    wiki.scrap(path)
    print(f'** Scrap done: {wikiClass.__name__}')
    sys.stdout.flush()


def main():
    sep_thread = Thread(target=scrap, args=(SEP, 'sep.db'))
    sep_thread.start()
    iep_thread = Thread(target=scrap, args=(IEP, 'iep.db'))
    iep_thread.start()

    sep_thread.join()
    iep_thread.join()


if __name__ == '__main__':
    main()