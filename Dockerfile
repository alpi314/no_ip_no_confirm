FROM selenium/standalone-chrome

USER root

WORKDIR /usr/src/app
COPY . . 

RUN apt-get update && apt-get install -y python3-pip

RUN pip3 install --no-cache-dir -r requirements.txt

CMD [ "python", "./confirm.py" ]