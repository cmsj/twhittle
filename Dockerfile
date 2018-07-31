FROM python:3

LABEL Name=twhittle Version=0.0.1

WORKDIR /app
ADD . /app

RUN python3 -m pip install -r requirements.txt
CMD [ "python", "./twhittle.py" ]
