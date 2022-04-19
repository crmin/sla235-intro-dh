from bs4 import BeautifulSoup
from markdownify import markdownify

from base import SiteBase


class SEP(SiteBase):
    def get_page_uris(self) -> list[str]:
        """모든 페이지 uri를 list type으로 반환하도록 함

        Returns:
            list[str]: page uri list
        """
        resp = self.session.get('https://plato.stanford.edu/contents.html')
        soup = BeautifulSoup(resp.text, 'lxml')

        all_links = [link.get('href', '') for link in soup.find_all('a')]  # a 태그의 href 속성 값만 가져옴 (실제 주소 속성)
        # entries로 시작하는 uri만 필터링, href는 상대 주소이므로 절대 주소로 변경해서 스크래핑이 가능하도록 함
        entry_links = [f'https://plato.stanford.edu/{link}' for link in all_links if link.startswith('entries/')]

        return entry_links[:1]  # TODO: FIXME: Remove slicing

    def get_title_in_page(self, html_body: str) -> str:
        """page에서 title을 추출

        Args:
            html_body (str): page html body

        Returns:
            str: page의 title
        """
        soup = BeautifulSoup(html_body, 'lxml')
        return soup.find('h1').text

    def get_abstract_in_page(self, html_body: str) -> str:
        """page에서 abstract를 추출

        Args:
            html_body (str): page html body

        Returns:
            str: page의 abstract
        """
        soup = BeautifulSoup(html_body, 'lxml')
        return soup.find(id='preamble').text

    def get_contents_in_page(self, html_body: str) -> str:
        """page에서 목차(table of contents)를 추출

        Args:
            html_body (str): page html body

        Returns:
            str: page의 목차
        """
        soup = BeautifulSoup(html_body, 'lxml')
        return markdownify(soup.find(id='toc').decode_contents(), strip=['a', 'hr']).strip()

    def get_body_in_page(self, html_body: str) -> str:
        """page에서 본문(body) 추출

        Args:
            html_body (str): page html body

        Returns:
            str: page의 본문
        """
        soup = BeautifulSoup(html_body, 'lxml')
        return markdownify(
            soup.find(id='main-text').decode_contents().replace('\n', ''),
            strip=['a', 'hr'],
            heading_style='ATX'
        ).strip()

    def get_bibliography_in_page(self, html_body: str) -> str:
        """page에서 인용문(bibliography) 추출

        Args:
            html_body (str): page html body

        Returns:
            str: page의 인용문
        """
        pass


class IEP(SiteBase):
    def get_page_uris(self) -> list[str]:
        """모든 페이지 uri를 list type으로 반환하도록 함

        Returns:
            list[str]: page uri list
        """
        pass

    def get_title_in_page(self, html_body: str) -> str:
        """page에서 title을 추출

        Args:
            html_body (str): page html body

        Returns:
            str: page의 title
        """
        pass

    def get_abstract_in_page(self, html_body: str) -> str:
        """page에서 abstract를 추출

        Args:
            html_body (str): page html body

        Returns:
            str: page의 abstract
        """
        pass

    def get_contents_in_page(self, html_body: str) -> str:
        """page에서 목차(table of contents)를 추출

        Args:
            html_body (str): page html body

        Returns:
            str: page의 목차
        """
        pass

    def get_body_in_page(self, html_body: str) -> str:
        """page에서 본문(body) 추출

        Args:
            html_body (str): page html body

        Returns:
            str: page의 본문
        """
        pass

    def get_bibliography_in_page(self, html_body: str) -> str:
        """page에서 인용문(bibliography) 추출

        Args:
            html_body (str): page html body

        Returns:
            str: page의 인용문
        """
        pass