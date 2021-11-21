FROM python:3.8

WORKDIR /usr/app
RUN apt-get update && \
    apt-get -y install netcat vim
ADD ./requirements.txt ./
RUN pip install -r requirements.txt
ADD ./ ./
RUN chmod +x *.sh
# ENTRYPOINT [ "./kafka-wait.sh" ]
CMD ["python3", "-u", "producer.py"]
