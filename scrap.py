from wikis import SEP, IEP

def main():
    resp = SEP()
    # resp.scrap()
    print(resp.get_page_uris())
    print(len(resp.get_page_uris()))


if __name__ == '__main__':
    main()