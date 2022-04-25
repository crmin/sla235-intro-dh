import sqlite3
import time
from abc import ABC, abstractmethod
from io import StringIO

import requests
import yaml


class SiteBase(ABC):
    headers = {
        'User-Agent': (
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
            '(KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'
        ),
    }

    TABLE_CREATION_SQL = (
        'CREATE TABLE scrap '
        '(id integer PRIMARY KEY, uri TEXT, title TEXT, abstract TEXT, contents TEXT, body TEXT, bibliography TEXT)'
    )

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    @abstractmethod
    def get_page_uris(self) -> list[str]:
        """모든 페이지 uri를 list type으로 반환하도록 함

        Returns:
            list[str]: page uri list
        """
        pass

    @abstractmethod
    def get_title_in_page(self, html_body: str) -> str:
        """page에서 title을 추출

        Args:
            html_body (str): page html body

        Returns:
            str: page의 title
        """
        pass

    @abstractmethod
    def get_abstract_in_page(self, html_body: str) -> str:
        """page에서 abstract를 추출

        Args:
            html_body (str): page html body

        Returns:
            str: page의 abstract
        """
        pass

    @abstractmethod
    def get_contents_in_page(self, html_body: str) -> str:
        """page에서 목차(table of contents)를 추출

        Args:
            html_body (str): page html body

        Returns:
            str: page의 목차
        """
        pass

    @abstractmethod
    def get_body_in_page(self, html_body: str) -> str:
        """page에서 본문(body) 추출

        Args:
            html_body (str): page html body

        Returns:
            str: page의 본문
        """
        pass

    @abstractmethod
    def get_bibliography_in_page(self, html_body: str) -> str:
        """page에서 인용문(bibliography) 추출

        Args:
            html_body (str): page html body

        Returns:
            str: page의 인용문
        """
        pass

    def scrap(self, path: str) -> None:
        """앞서 재정의된 메소드를 이용해서 스크래핑 진행

        Args:
            path (str): 스크래핑 결과가 저장될 파일 경로, sqlite3로 저장됨
        """
        print(self.__class__.__name__, 'Create database file')
        conn = sqlite3.connect(path, isolation_level=None)
        cur = conn.cursor()
        cur.execute(self.TABLE_CREATION_SQL)

        page_uris = self.get_page_uris()
        page_uris_len = len(page_uris)
        print(self.__class__.__name__, f'Get {page_uris_len} page uris')

        for idx, page_uri in enumerate(page_uris):
            print(self.__class__.__name__, f'> [{idx + 1}/{page_uris_len}] Scrap {page_uri}')
            resp = self.session.get(page_uri)
            title = self.get_title_in_page(resp.text)
            abstract = self.get_abstract_in_page(resp.text)
            contents = self.get_contents_in_page(resp.text)
            body = self.get_body_in_page(resp.text)
            bibliography = self.get_bibliography_in_page(resp.text)
            cur.execute(
                'INSERT INTO scrap (uri, title, abstract, contents, body, bibliography) VALUES (?, ?, ?, ?, ?, ?)',
                (page_uri, title, abstract, contents, body, bibliography),
            )
            conn.commit()
            time.sleep(0.25)
        print(self.__class__.__name__, 'All page scrapped.')

    def _convert_md_to_dict(self, md: str) -> dict:
        """markdown 형태의 list를 dict로 변환

        Args:
            md (str): list markdown, list symbol은 모두 hyphen(-)이어야 함

        Returns:
            dict: dict로 파싱된 결과
        """
        # md 리스트를 yaml로 읽어서 dict로 변환
        # 마지막에 개행 문자가 없으면 마지막 항목은 dict type으로 생성되지 않음
        # 마지막에 개행 문자가 여러개 있으면 yaml 파싱에서 에러 발생
        # 모든 trailing new line을 없앤 후 하나만 추가하는 방식으로 함
        prettified_md = (md.strip() + '\n').replace('\n', ':\n').replace('\t', '  ')
        yaml_list = yaml.load(StringIO(prettified_md), yaml.FullLoader)
        return yaml_list
