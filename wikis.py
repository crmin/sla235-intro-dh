import string
import sys

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

        return entry_links

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
        contents_md = markdownify(soup.find(id='toc').decode_contents(), strip=['a', 'hr'], bullets='-').strip()
        return self._convert_md_to_dict(contents_md)

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
        soup = BeautifulSoup(html_body, 'lxml')
        return markdownify(
            soup.find(id='bibliography').decode_contents().replace('\n', ''),
            strip=['a', 'hr'],
            heading_style='ATX'
        ).strip()


class IEP(SiteBase):
    def get_page_uris(self, verbose: bool=False) -> list[str]:
        """모든 페이지 uri를 list type으로 반환하도록 함

        Args:
            verbose (bool, optional): 스크랩 진행 상황을 표시. Defaults to False.

        Returns:
            list[str]: page uri list
        """
        links = []
        if verbose:
            print(self.__class__.__name__, 'scrap contents: ', end='')
            sys.stdout.flush()
        for sub_group in string.ascii_lowercase:
            if verbose:
                print(sub_group, end='')
            sys.stdout.flush()
            # 알파벳으로 그룹된 별도 페이지가 존재하므로 순회하면서 링크 수집
            resp = self.session.get(f'https://iep.utm.edu/{sub_group}/')
            soup = BeautifulSoup(resp.text, 'lxml')

            contents_group = soup.find(class_='entry-content')
            all_links = [link.get('href', '') for link in contents_group.find_all('a')]

            for link in all_links:
                # 절대주소 형식이면서 외부 사이트 연결은 수집 대상에서 제외함
                is_abs_addr = link.startswith('http://') or link.startswith('https://')  # 절대 주소 형식인지 확인
                if is_abs_addr and not link.startswith('https://iep.utm.edu/'):
                    continue
                if not is_abs_addr:  # 절대 주소 형식이 아닌 경우 절대 주소 형식으로 변환
                    link = f'https://iep.utm.edu/{link}'
                links.append(link)
        if verbose:
            print('')
        return links

    def get_title_in_page(self, html_body: str) -> str:
        """page에서 title을 추출

        Args:
            html_body (str): page html body

        Returns:
            str: page의 title
        """
        soup = BeautifulSoup(html_body, 'lxml')
        return soup.find(class_='entry-content').find('h1').text

    def _abstract_with_title(self, md_body: str) -> str:
        """Table of Contents title이 있어서 abtract의 끝을 분명히 알 수 있는 경우에 대한 파싱

        Args:
            md_body (str): page markdown body

        Returns:
            str: abstract 문자열 (markdown)
        """
        before_toc, _ = md_body.split('### Table of Contents')
        lines = []
        for line in before_toc.split('\n'):
            if line.strip().startswith('# '):  # page title
                continue
            lines.append(line)
        return '\n'.join(lines)

    def _abstract_without_title(self, md_body: str) -> str:
        """Table of Contents title이 없어서 abstract의 끝을 휴리스틱하게 알 수 있는 경우에 대한 파싱

        list 태그가 보이기 전까지를 묶어서 abstract라고 가정

        Args:
            md_body (str): page markdown body

        Returns:
            str: abstract 문자열 (markdown)
        """
        lines = []
        for line in md_body.split('\n'):
            line = line.strip()
            if line.startswith('# '):  # page title
                continue
            if len(line) > 0 and line[0] in ('*', '-', '+') + tuple(string.digits):  # list in markdown
                # *, -, +: ul / 0, 1, 2, .., 9: ol
                break
            lines.append(line)
        return '\n'.join(lines)

    def get_abstract_in_page(self, html_body: str) -> str:
        """page에서 abstract를 추출

        Args:
            html_body (str): page html body

        Returns:
            str: page의 abstract
        """
        soup = BeautifulSoup(html_body, 'lxml')  # 본문만 markdown으로 변환하기 위함
        md = markdownify(
            soup.find(class_='entry-content').decode_contents(),
            strip=['a', 'em', 'img'],
            heading_style='ATX'
        )
        # _toc_without_title()가 더 범용적으로 동작하지만 _toc_with_title()가 특정 상황에서 더 정확한 결과를 반환할 것이라고 예측
        if '### Table of Contents' in md:
            return self._abstract_with_title(md)
        else:
            return self._abstract_without_title(md)

    def _toc_with_title(self, md_body: str) -> str:
        """Table of Contents title에 이어서 목차 리스트가 시작하는 경우에 대한 파싱

        Args:
            md_body (str): page markdown body

        Returns:
            str: 목차 문자열 (markdown)
        """
        _, after_toc = md_body.split('### Table of Contents')
        tocs = []
        toc_start = False  # list가 끝나면 중단하도록 하기 위한 flag
        for line in after_toc.split('\n'):
            line = line.strip()
            if len(line) > 0 and line[0] in ('*', '-', '+') + tuple(string.digits):  # list in markdown
                # *, -, +: ul / 0, 1, 2, .., 9: ol
                tocs.append(line)
                if not toc_start:
                    toc_start = True  # list가 시작되면 flag를 True로 변경
            elif toc_start:  # list가 시작되었는데 지금 읽은 문자열이 list가 아니라면 toc가 종료되었다고 판단
                break
        return '\n'.join(tocs).strip()

    def _toc_without_title(self, md_body: str) -> str:
        """Table of Contents title 없이 바로 목차 리스트가 시작하는 경우에 대한 파싱

        Args:
            md_body (str): page markdown body

        Returns:
            str: 목차 문자열 (markdown)
        """
        tocs = []
        toc_start = False  # list가 끝나면 중단하도록 하기 위한 flag
        for line in md_body.split('\n'):
            line = line.strip()
            if len(line) > 0 and line[0] in ('*', '-', '+') + tuple(string.digits):  # list in markdown
                # *, -, +: ul / 0, 1, 2, .., 9: ol
                tocs.append(line)
                if not toc_start:
                    toc_start = True  # list가 시작되면 flag를 True로 변경
            elif toc_start:  # list가 시작되었는데 지금 읽은 문자열이 list가 아니라면 toc가 종료되었다고 판단
                break
        return '\n'.join(tocs).strip()

    def get_contents_in_page(self, html_body: str) -> str:
        """page에서 목차(table of contents)를 추출

        Args:
            html_body (str): page html body

        Returns:
            str: page의 목차
        """
        soup = BeautifulSoup(html_body, 'lxml')  # 본문만 markdown으로 변환하기 위함
        md = markdownify(
            soup.find(class_='entry-content').decode_contents(),
            strip=['a', 'em'],
            heading_style='ATX',
            bullets='-'
        )
        # _contents_without_title()가 더 범용적으로 동작하지만 _contents_with_title()가 특정 상황에서 더 정확한 결과를 반환할 것이라고 예측
        contents_md = ''
        if '### Table of Contents' in md:
            contents_md = self._toc_with_title(md)
        else:
            contents_md = self._toc_without_title(md)
        return self._convert_md_to_dict(contents_md)

    def _body_with_title(self, md_body: str) -> str:
        """Table of Contents title이 존재하는 경우 body 파싱

        Args:
            md_body (str): page markdown body

        Returns:
            str: 목차 문자열 (markdown)
        """
        _, after_toc = md_body.split('### Table of Contents')
        body_lines = []
        toc_start = False  # list의 종료를 확인하기 위한 flag
        body_start = False  # list가 종료되면 True로 변경되어서 본문임을 확인할 수 있도록 하는 flag
        for line in after_toc.split('\n'):
            line = line.strip()
            if len(line) > 0 and line[0] in ('*', '-', '+') + tuple(string.digits):  # list in markdown
                # *, -, +: ul / 0, 1, 2, .., 9: ol
                if not toc_start:
                    toc_start = True  # list가 시작되면 flag를 True로 변경
            elif toc_start:  # list가 시작되었는데 지금 읽은 문자열이 list가 아니라면 toc가 종료되었다고 판단
                body_start = True  # -> 이후부터 본문 내용
            if not body_start:  # 아직 본문이 아니라면 아무 작업도 수행하지 않고 계속 진행
                continue
            if line.startswith('#') and 'reference' in line.lower():  # Reference 시작하면 탈출
                break
            if len(line) == 1 and line[0] == '>':  # 인용문인데 내용이 없는 경우 무시하도록 함
                continue
            body_lines.append(line)
        return '\n'.join(body_lines).strip()

    def _body_without_title(self, md_body: str) -> str:
        """Table of Contents title이 존재하지 않는 경우 body 파싱

        Args:
            md_body (str): page markdown body

        Returns:
            str: 목차 문자열 (markdown)
        """
        body_lines = []
        toc_start = False  # list의 종료를 확인하기 위한 flag
        body_start = False  # list가 종료되면 True로 변경되어서 본문임을 확인할 수 있도록 하는 flag
        for line in md_body.split('\n'):
            line = line.strip()
            if len(line) > 0 and line[0] in ('*', '-', '+') + tuple(string.digits):  # list in markdown
                # *, -, +: ul / 0, 1, 2, .., 9: ol
                if not toc_start:
                    toc_start = True  # list가 시작되면 flag를 True로 변경
            elif toc_start:  # list가 시작되었는데 지금 읽은 문자열이 list가 아니라면 toc가 종료되었다고 판단
                body_start = True  # -> 이후부터 본문 내용
            if not body_start:  # 아직 본문이 아니라면 아무 작업도 수행하지 않고 계속 진행
                continue
            if line.startswith('#') and 'reference' in line.lower():  # Reference 시작하면 탈출
                break
            if len(line) == 1 and line[0] == '>':  # 인용문인데 내용이 없는 경우 무시하도록 함
                continue
            body_lines.append(line)
        return '\n'.join(body_lines).strip()

    def get_body_in_page(self, html_body: str) -> str:
        """page에서 본문(body) 추출

        Args:
            html_body (str): page html body

        Returns:
            str: page의 본문
        """
        soup = BeautifulSoup(html_body, 'lxml')  # 본문만 markdown으로 변환하기 위함
        md = markdownify(
            soup.find(class_='entry-content').decode_contents(),
            strip=['a', 'img'],
            heading_style='ATX'
        )
        # _body_without_title()가 더 범용적으로 동작하지만 _body_with_title()가 특정 상황에서 더 정확한 결과를 반환할 것이라고 예측
        if '### Table of Contents' in md:
            return self._body_with_title(md)
        else:
            return self._body_without_title(md)

    def get_bibliography_in_page(self, html_body: str) -> str:
        """page에서 인용문(bibliography) 추출

        Args:
            html_body (str): page html body

        Returns:
            str: page의 인용문
        """
        soup = BeautifulSoup(html_body, 'lxml')  # 본문만 markdown으로 변환하기 위함
        md = markdownify(
            soup.find(class_='entry-content').decode_contents(),
            strip=['a', 'img', 'em'],
            heading_style='ATX'
        )
        lines = []
        is_reference = False
        for line in md.split('\n'):
            if line.startswith('#') and 'reference' in line.lower():
                is_reference = True
                continue  # 해당 line은 title이므로 다음 line부터 작업
            if not is_reference:
                continue

            if line.startswith('#'):  # reference가 끝남
                break
            lines.append(line)
        return '\n'.join(lines).strip()
