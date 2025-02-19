FROM python:3.12
ENV PYTHONUNBUFFERED 1
COPY ./requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
