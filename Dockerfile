FROM python:3.8

WORKDIR /var/MusicBTW
ENV PYTHONIOENCODING="UTF-8" LANG="en_GB.UTF-8"
COPY bot ./bot/
COPY config ./config
COPY requirements.txt run.py ./

RUN apt-get update && apt-get install -y python3.8-dev libnacl-dev
RUN pip install -r requirements.txt

CMD ["python", "run.py"]