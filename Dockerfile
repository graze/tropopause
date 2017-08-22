FROM python:3

RUN apt-get update && apt-get install -y \
    zip \
    groff \
    && apt-get clean; rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN pip install -U \
    awacs \
    awscli \
    boto3 \
    pycodestyle \
    pyflakes \
    pyyaml \
    requests \
    setuptools \
    troposphere[policy]

WORKDIR /python