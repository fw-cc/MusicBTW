FROM python:3.9

WORKDIR /var/MusicBTW
ENV PYTHONIOENCODING="UTF-8" LANG="en_GB.UTF-8"
COPY . ./

RUN pip install -r requirements.txt

CMD ["python", "run.py"]