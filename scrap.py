import sys
from threading import Thread

from colorama import Fore

from wikis import SEP, IEP


def scrap(wikiClass, path, color):
    wiki = wikiClass()
    wiki.scrap(path, color)
    print(f'** Scrap done: {wikiClass.__name__}')
    sys.stdout.flush()


def main():
    sep_thread = Thread(target=scrap, args=(SEP, 'sep.db', Fore.CYAN), name='sep')
    sep_thread.start()
    iep_thread = Thread(target=scrap, args=(IEP, 'iep.db', Fore.MAGENTA), name='iep')
    iep_thread.start()

    sep_thread.join()
    iep_thread.join()


if __name__ == '__main__':
    main()