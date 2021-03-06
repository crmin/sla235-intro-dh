import json
import sqlite3
import sys
import time
from abc import ABC, abstractmethod
from io import StringIO
from itertools import count

import requests
from colorama import Style


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

    def scrap(self, path: str, color) -> None:
        """앞서 재정의된 메소드를 이용해서 스크래핑 진행

        Args:
            path (str): 스크래핑 결과가 저장될 파일 경로, sqlite3로 저장됨
        """
        print(self.__class__.__name__, 'Create database file')
        sys.stdout.flush()
        conn = sqlite3.connect(path, isolation_level=None)
        cur = conn.cursor()
        cur.execute(self.TABLE_CREATION_SQL)

        page_uris = self.get_page_uris()
        page_uris_len = len(page_uris)
        print(f'{color}{self.__class__.__name__} Get {page_uris_len} page uris{Style.RESET_ALL}')
        sys.stdout.flush()

        for idx, page_uri in enumerate(page_uris):
            print(f'{color}{self.__class__.__name__} > [{idx + 1}/{page_uris_len}] Scrap {page_uri}{Style.RESET_ALL}')
            sys.stdout.flush()
            for try_count in count(1):  # 5초 이내에 응답을 받지 못해서 timeout이 발생하면 재시도
                try:
                    resp = self.session.get(page_uri, timeout=5)
                except requests.exceptions.ReadTimeout:
                    print(f'{color}{self.__class__.__name__} Timeout: {page_uri}, try: {try_count}{Style.RESET_ALL}')
                    time.sleep(0.25)
                    continue
                break
            title = self.get_title_in_page(resp.text)
            abstract = self.get_abstract_in_page(resp.text)
            contents = json.dumps(self.get_contents_in_page(resp.text))
            body = self.get_body_in_page(resp.text)
            bibliography = self.get_bibliography_in_page(resp.text)
            cur.execute(
                'INSERT INTO scrap (uri, title, abstract, contents, body, bibliography) VALUES (?, ?, ?, ?, ?, ?)',
                (page_uri, title, abstract, contents, body, bibliography),
            )
            conn.commit()
            time.sleep(0.25)
        print(f'{color}{self.__class__.__name__} All page scrapped.{Style.RESET_ALL}')
        sys.stdout.flush()

    def _split_toc_lines(self, toc_content):
        return toc_content.replace('\n-', '\n\n-').split('\n\n')

    def _split_toc_depth(self, toc_lines):
        toc_depths = toc_lines.split('\n')
        current_depth = toc_depths[0]
        next_depths = []
        for next_depth in toc_depths[1:]:
            next_depths.append(next_depth[1:])
        return current_depth, '\n'.join(next_depths)

    def _parse_toc(self, toc_content):
        if toc_content.strip() == '':
            return []

        toc_list = []
        for toc_lines in self._split_toc_lines(toc_content):
            current_depth, next_depths = self._split_toc_depth(toc_lines)
            toc_list.append({
                'content': current_depth,
                'subcontent': self._parse_toc(next_depths),
            })
        return toc_list

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
        return self._parse_toc(md)
