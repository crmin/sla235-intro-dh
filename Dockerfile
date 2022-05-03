FROM python:3.10-bullseye
COPY . /root/
WORKDIR /root/
RUN pip install -r requirements.txt
ENTRYPOINT python scrap.py