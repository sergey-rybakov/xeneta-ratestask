FROM python:3.9.0rc2-buster
WORKDIR /app
ADD . /app
RUN pip3 install -r requirements.txt
CMD ["uwsgi", "api.ini"]
RUN export FLASK_APP=front.py