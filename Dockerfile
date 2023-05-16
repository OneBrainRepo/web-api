FROM tiangolo/uvicorn-gunicorn:python3.10

RUN apt-get update -y

COPY ./requirements.txt requirements.txt
RUN pip install -U pip
RUN pip install --no-cache-dir -r requirements.txt