FROM tensorflow/tensorflow:1.15.0

COPY requirements.txt .

RUN pip install -r requirements.txt

ENTRYPOINT ["tail", "-f", "/dev/null"]