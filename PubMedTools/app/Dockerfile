FROM python:3.7.4
  
RUN set -x \
  && echo "Preparing system..." \
  && apt-get -y update \
  && apt-get -y install \
    bsdtar \
    cron \
    sudo \
    unzip


ADD requirements.txt /app/requirements.txt

RUN set -x \
  && echo "Installing python dependencies..." \
  && pip install -r /app/requirements.txt \
  && rm /app/requirements.txt

ADD . /app/

RUN set -x \
  && chmod +x /app/main.sh

CMD [ "/app/main.sh" ]
