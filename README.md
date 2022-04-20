# Philosophy Wiki Scraper
> SLA235 Introduction to Digital Humanities Team Project

[Stanford Encyclopedia of Philosophy (SEP)](https://plato.stanford.edu/)와
[Internet Encyclopedia of Philosophy (IEP)](https://iep.utm.edu/)에서 문서들을 스크래핑합니다.

## How to use
### Prerequisite
* 실행을 위해서 파이썬 3.9 이상이 필요합니다.
* 아래 명령을 통해 패키지를 설치해야합니다
    ```
        pip install -r requirements.txt
    ```
    또는 virtualenv 환경에서 사용할 수도 있습니다.
### Run
* `scrap.py`를 실행해서 스크래핑을 진행합니다. 결과는 `sep.db`와 `iep.db`에 저장됩니다.
    ```
    python scrap.py
    ```
* 결과는 sqlite3로 저장되며, table schema는 아래와 같습니다.
    ```
        id integer PRIMARY KEY,
        uri TEXT,
        title TEXT,
        abstract TEXT,
        contents TEXT,
        body TEXT,
        bibliography TEXT
    ```