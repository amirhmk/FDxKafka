FROM python:3.8


WORKDIR /usr/app
ADD ./requirements.txt ./
RUN apt-get update && \
    apt-get -y --force-yes install netcat vim && \
    python -m pip install --upgrade pip && \
    pip install -r requirements.txt && \
    useradd -ms /bin/bash -g users sfu && \
    chown -R sfu:users /usr/app && \
    mkdir /usr/app/data && \
    chown -R sfu:users /usr/app/data
USER sfu
COPY --chown=sfu:users python ./python
CMD ["python", "-u", "python/consumer.py"]
